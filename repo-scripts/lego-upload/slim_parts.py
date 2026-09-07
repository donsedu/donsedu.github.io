#!/usr/bin/env python3
"""依模型遞迴精簡 LDraw 零件庫（參數化版，GitHub Actions 用）

用法：
  python3 slim_parts.py <model.ldr> <parts_src_dir> <out_dir>
"""
import re, os, shutil, sys
from collections import deque

LINE1 = re.compile(r'^1\s+(\S+\s+){13}(\S+\.dat)', re.I)

def find_in_src(src, name):
    # LDraw 檔內引用用 \ 分隔子目錄 → 轉 /
    name = name.replace('\\', '/')
    cands = [name, name.lower(), os.path.basename(name), os.path.basename(name).lower()]
    seen = set()
    for c in cands:
        if c in seen:
            continue
        seen.add(c)
        p = os.path.join(src, c)
        if os.path.exists(p):
            return p
    return None

def refs_from(path):
    refs = set()
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            for line in f:
                m = LINE1.match(line.strip())
                if m:
                    refs.add(m.group(2).lower())
    except Exception:
        pass
    return refs

def slim(model_path, parts_src, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    queue = deque()
    with open(model_path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            m = LINE1.match(line.strip())
            if m:
                queue.append(m.group(2).lower())
    copied = set()
    missing = set()
    total = 0
    while queue:
        name = queue.popleft()
        if name in copied:
            continue
        src_path = find_in_src(parts_src, name)
        if not src_path:
            missing.add(name)
            continue
        rel = os.path.relpath(src_path, parts_src)
        dst = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src_path, dst)
        copied.add(name)
        total += 1
        for ref in refs_from(src_path):
            if ref not in copied:
                queue.append(ref)
    if missing:
        print(f'⚠️ 找不到 {len(missing)} 個零件: {sorted(missing)[:10]}')
    sz = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(out_dir) for fn in fns)
    print(f'✅ 精簡零件庫: {total} 檔 / {sz/1024:.1f} KB')
    return missing

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    missing = slim(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(1 if missing else 0)
