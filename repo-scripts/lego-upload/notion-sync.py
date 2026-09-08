#!/usr/bin/env python3
"""
Notion → viewer/models/index.json 同步器

讀 Notion「LEGO 模型目錄」(data source) 的「公開」模型，
合併現有 index.json 的技術欄位（steps/parts/fingerprint/added_at），
寫回 viewer/models/index.json —— Notion 是 metadata 權威（名稱/系列/tags/難度/年齡/說明/狀態）。

用法:
  NOTION_API_KEY=xxx python3 notion-sync.py <repo_root>

行為：
- 只登錄 Notion 狀態=公開 且 repo 內 models/<file> 實際存在的模型
- 不在 Notion 的舊登錄會被移除（Notion 控制顯示與否）
- Notion 補 metadata 欄位；技術欄位由舊 index.json（上傳 Actions 寫入）保留
"""
import json
import os
import sys
import urllib.request
import urllib.parse

DATA_SOURCE_ID = os.environ.get("NOTION_LEGO_DATA_SOURCE",
                                "473f0327-b672-4d85-879a-729f9b68805c")
API_VERSION = "2025-09-03"


def notion_query(data_source_id, api_key):
    """Query all rows (paginated)."""
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }
    rows = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            d = json.loads(resp.read().decode())
        rows.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return rows


def prop_text(props, key):
    """title / rich_text → plain text or None"""
    p = props.get(key)
    if not p:
        return None
    if p.get("type") == "title":
        arr = p.get("title") or []
    elif p.get("type") == "rich_text":
        arr = p.get("rich_text") or []
    else:
        return None
    return "".join(t.get("plain_text", "") for t in arr).strip() or None


def prop_select(props, key):
    p = props.get(key) or {}
    s = p.get("select")
    return s.get("name") if s else None


def prop_multi(props, key):
    p = props.get(key) or {}
    return [o.get("name") for o in (p.get("multi_select") or []) if o.get("name")]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    repo = os.path.abspath(sys.argv[1])
    api_key = os.environ.get("NOTION_API_KEY", "")
    if not api_key:
        print("❌ 缺少 NOTION_API_KEY env")
        return 1

    index_path = os.path.join(repo, "viewer", "models", "index.json")
    models_dir = os.path.join(repo, "viewer", "models")

    # 舊 index.json（技術欄位來源）
    old = {}
    if os.path.exists(index_path):
        try:
            for m in json.load(open(index_path, encoding="utf-8")):
                if m.get("file"):
                    old[m["file"]] = m
        except Exception:
            old = {}

    print("📡 讀取 Notion LEGO 模型目錄…")
    rows = notion_query(DATA_SOURCE_ID, api_key)
    print(f"   Notion 共 {len(rows)} 筆")

    merged = []
    for r in rows:
        props = r.get("properties", {})
        status = prop_select(props, "狀態")
        if status != "公開":
            continue
        file_raw = prop_text(props, "檔案名")
        name = prop_text(props, "名稱")
        if not file_raw or not name:
            print(f"   ⚠️ 跳過缺檔名/名稱的 record: {r.get('id')}")
            continue
        ldr_file = file_raw if file_raw.lower().endswith(".ldr") else file_raw + ".ldr"

        # 模型檔必須實際存在，避免線上壞卡
        if not os.path.exists(os.path.join(models_dir, ldr_file)):
            print(f"   ⚠️ 跳過「{name}」: models/{ldr_file} 不存在（先上傳模型）")
            continue

        entry = {
            "file": ldr_file,
            "name": name,
        }
        # 保留技術欄位
        old_entry = old.get(ldr_file) or {}
        for k in ("steps", "parts", "fingerprint", "added_at"):
            if old_entry.get(k) is not None:
                entry[k] = old_entry[k]
        # Notion metadata（空值省略）
        series = prop_select(props, "系列")
        if series:
            entry["series"] = series
        tags = prop_multi(props, "Tags")
        if tags:
            entry["tags"] = tags
        level = prop_select(props, "難度")
        if level:
            entry["level"] = level
        age = prop_select(props, "適合年齡")
        if age:
            entry["age"] = age
        desc = prop_text(props, "說明")
        if desc:
            entry["desc"] = desc
        merged.append(entry)
        missing = [k for k in ("steps", "parts", "added_at") if entry.get(k) is None]
        if missing:
            print(f"   ℹ️ 「{name}」尚無技術欄位 {missing}（等上傳流程登錄）")

    merged.sort(key=lambda m: m.get("added_at", ""), reverse=True)

    # 只有實際變更才寫檔（避免無意義 commit）
    changed = True
    if os.path.exists(index_path):
        try:
            if json.load(open(index_path, encoding="utf-8")) == merged:
                changed = False
        except Exception:
            pass

    if changed:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=1)
        print(f"✅ index.json 已更新（{len(merged)} 筆公開模型）")
        for m in merged:
            print(f"   - {m['name']} | {m['file']} | tags={m.get('tags', [])}")
    else:
        print(f"ℹ️ 無變更（{len(merged)} 筆公開模型）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
