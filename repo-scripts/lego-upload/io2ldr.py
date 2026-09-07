#!/usr/bin/env python3
"""LEGO .io → LDraw 轉換腳本
將 Bricklink Studio .io 檔解鎖、解壓，提取 model.ldr 供 buildinginstructions.js 使用。
含 Studio 匯出修正：子模型大小寫（submodel group → SubModel Group）。

用法：
  python3 io2ldr.py <輸入.io> [輸出目錄]

輸出：
  <輸出目錄>/model.ldr        ← 標準 LDraw 主模型
  <輸出目錄>/model2.ldr       ← BrickLink 格式（含 IsSubModel 標記）
  <輸出目錄>/thumbnail.png    ← 模型縮圖
"""
import sys, os, re, zipfile, shutil

# Bricklink Studio 舊版 .io 檔固定密碼
IO_PASSWORD = b"soho0909"

def fix_submodel_case(content):
    """修正 Studio 匯出 MPD 的子模型大小寫不一致：
    引用 'submodel group N'（小寫）vs 宣告 'SubModel Group N'（title case）
    """
    return re.sub(r'submodel group (\d)', lambda m: f'SubModel Group {m.group(1)}', content)

def ensure_mpd(content):
    """若 model.ldr 非 MPD（無 0 FILE 宣告），包成 MPD 主檔。

    buildinginstructions.js 對無 FILE 的純 LDraw：parse 的 defaultID = 完整
    model URL（含原始大寫，如 models/ESM-9656-xxx.ldr），但 LDRPartDescription
    建構時 this.ID = ID.toLowerCase() → getPartType 找不到 partTypes key
    （key 保留大寫）→ StepHandler 收到 null → crash「Cannot read properties
    of null (reading 'steps')」。包成 MPD 後 FILE 名在 parse 時統一
    toLowerCase，主模型 key 與查詢一致。
    """
    if re.search(r'^0 FILE\b', content, re.M):
        return content  # 已是 MPD，不需包裝
    content = content.lstrip('\ufeff')  # BOM 移除，改由輸出檔頭統一寫
    name_m = re.search(r'^0 Name:\s*(.+)', content, re.M)
    fname = name_m.group(1).strip() if name_m else 'model'
    fname = re.sub(r'[^\w\-.\u4e00-\u9fff ]+', '_', fname).strip() or 'model'
    return ('0 FILE ' + fname + '\r\n'
            + content.rstrip('\r\n') + '\r\n'
            + '0 NOFILE\r\n')

def convert(io_path, out_dir=None):
    io_path = os.path.abspath(io_path)
    if not os.path.exists(io_path):
        print(f"❌ 找不到檔案: {io_path}")
        return None

    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(io_path), 'converted')
    os.makedirs(out_dir, exist_ok=True)

    # 解鎖 + 解壓
    try:
        with zipfile.ZipFile(io_path) as z:
            z.setpassword(IO_PASSWORD)
            for info in z.infolist():
                data = z.read(info.filename)
                safe_name = os.path.basename(info.filename)
                with open(os.path.join(out_dir, safe_name), 'wb') as f:
                    f.write(data)
                print(f"  ✅ 解出: {safe_name} ({len(data)} bytes)")
    except RuntimeError:
        # 新版可能無密碼
        try:
            with zipfile.ZipFile(io_path) as z:
                for info in z.infolist():
                    data = z.read(info.filename)
                    safe_name = os.path.basename(info.filename)
                    with open(os.path.join(out_dir, safe_name), 'wb') as f:
                        f.write(data)
                    print(f"  ✅ 解出（無密碼）: {safe_name} ({len(data)} bytes)")
        except Exception as e:
            print(f"❌ 解壓失敗: {e}")
            return None
    except Exception as e:
        print(f"❌ 解壓失敗: {e}")
        return None

    model_ldr = os.path.join(out_dir, 'model.ldr')
    if not os.path.exists(model_ldr):
        print("❌ 沒有 model.ldr（可能不是有效的 .io 檔）")
        return None

    # 修正子模型大小寫 + 非 MPD 包裝（buildinginstructions.js 需要 0 FILE 主檔）
    with open(model_ldr, encoding='utf-8-sig') as f:
        content = f.read()
    fixed = ensure_mpd(fix_submodel_case(content))
    if fixed != content:
        with open(model_ldr, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print("  ✅ 子模型大小寫 / MPD 結構已修正")

    # 輸出摘要
    parts = [l for l in content.split('\n') if l.strip() and not l.startswith('0')]
    name_match = re.search(r'0 Name:\s*(.+)', content)
    name = name_match.group(1).strip() if name_match else os.path.basename(io_path)
    steps = len(re.findall(r'^0 STEP', content, re.M))

    print(f"\n✅ 轉換完成: {name}")
    print(f"  零件數: {len(parts)}")
    print(f"  步驟數: {steps}")
    print(f"  輸出: {out_dir}/")
    return model_ldr

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    io_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else None
    convert(io_path, out_dir)
