#!/usr/bin/env python3
"""LEGO 上傳主流程（GitHub Actions + 本機共用）

輸入 uploads/ 的 .io → 產出（不 commit）：
  1. viewer/models/<safe>.ldr
  2. viewer/ldraw_parts/ 併入新零件
  3. viewer/models/index.json 登錄
  4. viewer/index.html 更新（最多 3 張卡片）
  5. viewer/upload-result.json（首頁 banner 顯示）

用法：
  python3 process.py <io_path> <repo_root> [--parts-src <dir>]

重複偵測：與 viewer/models/index.json 的 fingerprint 比對
  - 相同指紋 → 不新增，寫 upload-result.json {status:duplicate}，回傳 exit 3
環境變數：LEGO_PARTS_SRC（完整零件庫，缺省用 --parts-src / repo 內 .parts_cache）
"""
import sys, os, json, re, shutil, subprocess, unicodedata
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io2ldr
import slim_parts
import fingerprint as fp_mod

def safe_filename(name, max_len=40):
    """模型名 → 安全檔名（ascii-ish，保留識別性）"""
    name = unicodedata.normalize('NFKC', name).strip()
    # 保留中英文數字與 -_，其餘轉 _
    name = re.sub(r'[^\w\-]+', '_', name, flags=re.UNICODE)
    name = re.sub(r'_+', '_', name).strip('_')
    # 若全中文轉拼音太難——用英文部分優先；全中文就留中文檔名（GitHub Pages 支援）
    if not name:
        name = 'model'
    return name[:max_len]

def log(msg):
    print(msg, flush=True)

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    io_path = os.path.abspath(sys.argv[1])
    repo = os.path.abspath(sys.argv[2])
    parts_src = os.environ.get('LEGO_PARTS_SRC') or None
    # --parts-src 參數
    if '--parts-src' in sys.argv:
        parts_src = sys.argv[sys.argv.index('--parts-src') + 1]

    viewer = os.path.join(repo, 'viewer')
    models_dir = os.path.join(viewer, 'models')
    ldraw_dir = os.path.join(viewer, 'ldraw_parts')
    thumbs_dir = os.path.join(viewer, 'thumbnails')
    index_path = os.path.join(models_dir, 'index.json')
    result_path = os.path.join(viewer, 'upload-result.json')
    index_html = os.path.join(viewer, 'index.html')

    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(thumbs_dir, exist_ok=True)

    # ===== 1. 轉換 .io → model.ldr =====
    work = os.path.join(repo, 'uploads', '.work_' + os.path.basename(io_path))
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    log(f'🔓 解鎖轉換: {os.path.basename(io_path)}')
    model_ldr = io2ldr.convert(io_path, work)
    if not model_ldr:
        _fail(result_path, 'conversion_failed', '無法解壓或缺少 model.ldr（確定是 Bricklink Studio 匯出的 .io 檔？）')
        shutil.rmtree(work)
        return 2

    # ===== 2. 模型資訊 + 指紋 =====
    content = open(model_ldr, encoding='utf-8', errors='ignore').read()
    name_m = re.search(r'0 Name:\s*(.+)', content)
    raw_name = name_m.group(1).strip() if name_m else os.path.splitext(os.path.basename(io_path))[0]
    fp, parts, steps = fp_mod.fingerprint(model_ldr)
    safe = safe_filename(raw_name)
    ldr_file = safe + '.ldr'
    log(f'📦 模型: {raw_name} | {sum(parts.values())} 零件 / {steps} 步驟')
    log(f'🔍 指紋: {fp}')

    # ===== 3. 讀 index.json + 重複偵測 =====
    index = []
    if os.path.exists(index_path):
        try:
            index = json.load(open(index_path))
        except Exception:
            index = []
    dup = next((m for m in index if m.get('fingerprint') == fp), None)
    if dup:
        log(f'⚠️ 重複上傳: 與「{dup["name"]}」相同（指紋一致）')
        _write_json(result_path, {
            'status': 'duplicate',
            'name': raw_name,
            'existing': dup['name'],
            'fingerprint': fp,
            'at': datetime.now(timezone.utc).isoformat(),
        })
        shutil.rmtree(work)
        return 3

    # ===== 4. 精簡零件庫並併入 =====
    if not parts_src:
        parts_src = os.path.join(repo, '.parts_cache')
    slim_out = os.path.join(work, 'slim_parts')
    missing = slim_parts.slim(model_ldr, parts_src, slim_out)
    if missing:
        _fail(result_path, 'parts_missing', f'缺少 {len(missing)} 個零件（{sorted(missing)[:5]}）——請檢查 Studio 外掛或回報')
        shutil.rmtree(work)
        return 2
    # 併入現有庫（不刪舊檔）
    for dp, _, fns in os.walk(slim_out):
        rel = os.path.relpath(dp, slim_out)
        for fn in fns:
            dst = os.path.join(ldraw_dir, rel, fn) if rel != '.' else os.path.join(ldraw_dir, fn)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(dp, fn), dst)
    log(f'🧩 零件庫併入完成（現有 {sum(len(f) for _,_,f in os.walk(ldraw_dir))} 檔）')

    # ===== 5. 放模型 =====
    dst_ldr = os.path.join(models_dir, ldr_file)
    shutil.copy2(model_ldr, dst_ldr)
    log(f'💾 模型存檔: models/{ldr_file}')

    # ===== 6. 縮圖（thumb.js 外部呼叫）=====
    thumb_png = os.path.join(thumbs_dir, safe + '.png')
    thumb_js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thumb.js')
    log('📸 產生縮圖...')
    try:
        r = subprocess.run(['node', thumb_js, os.path.join('viewer', 'models', ldr_file), thumb_png],
                           cwd=repo, capture_output=True, text=True, timeout=180)
        if r.returncode != 0 or not os.path.exists(thumb_png):
            log('縮圖失敗: ' + r.stdout[-500:] + r.stderr[-500:])
            raise RuntimeError('thumb failed')
        log(f'✅ 縮圖: {safe}.png')
    except Exception as e:
        _fail(result_path, 'thumb_failed', f'縮圖產生失敗: {e}')
        shutil.rmtree(work)
        return 2

    # ===== 7. 登錄 index.json =====
    index = [m for m in index if m.get('file') != ldr_file]  # 同名覆蓋舊登錄
    entry = {
        'file': ldr_file,
        'name': raw_name,
        'steps': steps,
        'parts': sum(parts.values()),
        'fingerprint': fp,
        'added_at': datetime.now(timezone.utc).isoformat(),
    }
    index.append(entry)
    index.sort(key=lambda m: m.get('added_at', ''), reverse=True)
    _write_json(index_path, index)

    # ===== 8. 更新 index.html（最多 3 卡）=====
    recent = index[:3]
    cards = []
    for m in recent:
        cards.append(f'''    <a class="card" href="custom_instructions.htm?model={m['file'][:-4]}">
      <img class="thumb" src="thumbnails/{m['file'][:-4]}.png" alt="{m['name']}">
      <div class="card-body">
        <div class="card-name">{m['name']}</div>
        <div class="card-meta"><span class="pill">🧱 {m['steps']} 步驟</span><span class="pill">📋 互動 3D</span></div>
      </div>
    </a>''')
    html = _page_html(cards)
    open(index_html, 'w', encoding='utf-8').write(html)

    # ===== 9. 結果 =====
    _write_json(result_path, {
        'status': 'ok',
        'name': raw_name,
        'file': ldr_file,
        'url': f'custom_instructions.htm?model={safe}',
        'steps': steps,
        'parts': sum(parts.values()),
        'at': datetime.now(timezone.utc).isoformat(),
    })
    shutil.rmtree(work)
    log(f'🎉 完成: {raw_name} 已上線')
    return 0

def _page_html(cards):
    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>LEGO 組裝圖</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Noto Sans TC', 'PingFang TC', sans-serif;
    background: #14161a; color: #e8e6e1;
    min-height: 100vh;
  }}
  .wrap {{ max-width: 960px; margin: 0 auto; padding: 48px 24px; }}
  .top {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
  h1 {{ font-size: 22px; font-weight: 900; letter-spacing: 1px; }}
  .sub {{ color: #8b8f98; font-size: 13px; margin-bottom: 28px; }}
  .upload-btn {{
    display: inline-flex; align-items: center; gap: 6px;
    background: #e8722a; color: #fff; text-decoration: none;
    font-size: 14px; font-weight: 800; padding: 8px 18px; border-radius: 999px;
    transition: 0.2s; border: none; cursor: pointer;
  }}
  .upload-btn:hover {{ background: #d4621f; }}
  .banner {{
    border-radius: 12px; padding: 12px 16px; margin-bottom: 20px; font-size: 14px; display: none;
  }}
  .banner.ok {{ background: #1d3524; border: 1px solid #2d5a3a; color: #8fd6a4; display: block; }}
  .banner.dup {{ background: #3a2b1d; border: 1px solid #5a4a2d; color: #e0c68f; display: block; }}
  .banner.err {{ background: #3a1d1d; border: 1px solid #5a2d2d; color: #e0a08f; display: block; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }}
  .card {{
    background: #1e2126; border-radius: 14px; overflow: hidden;
    border: 1px solid #2a2e35; transition: 0.2s; text-decoration: none; color: inherit;
    display: block;
  }}
  .card:hover {{ transform: translateY(-3px); border-color: #e8722a; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
  .thumb {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; background: #b0b4bc; display: block; }}
  .card-body {{ padding: 14px 16px; }}
  .card-name {{ font-size: 15px; font-weight: 800; margin-bottom: 6px; }}
  .card-meta {{ font-size: 12px; color: #8b8f98; }}
  .card-meta .pill {{ background: #2a2e35; padding: 2px 10px; border-radius: 999px; margin-right: 6px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <h1>🧱 LEGO 組裝圖</h1>
    <a class="upload-btn" href="https://github.com/donsedu/donsedu.github.io/upload/main/uploads" target="_blank">＋ 上傳組裝圖</a>
  </div>
  <div class="sub">最近上傳的組裝圖（點開可 3D 旋轉、逐步組裝）</div>
  <div id="banner" class="banner"></div>
  <div class="grid">
{chr(10).join(cards)}
  </div>
</div>
<script>
fetch('upload-result.json', {{ cache: 'no-store' }}).then(r => r.json()).then(d => {{
  const b = document.getElementById('banner');
  if (d.status === 'ok') {{
    b.className = 'banner ok';
    b.textContent = '✅ 「' + d.name + '」已上線！重整後的卡片就是它。';
  }} else if (d.status === 'duplicate') {{
    b.className = 'banner dup';
    b.textContent = '⚠️ 剛剛上傳的「' + d.name + '」與已存在的「' + d.existing + '」相同——未重複加入。';
  }} else if (d.status === 'conversion_failed' || d.status === 'parts_missing' || d.status === 'thumb_failed') {{
    b.className = 'banner err';
    b.textContent = '❌ 上傳處理失敗：' + (d.message || '不明原因');
  }}
}}).catch(() => {{}});
</script>
</body>
</html>
'''

def _write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

def _fail(result_path, status, message):
    _write_json(result_path, {'status': status, 'message': message,
                              'at': datetime.now(timezone.utc).isoformat()})

if __name__ == '__main__':
    sys.exit(main())
