#!/usr/bin/env python3
"""模型指紋：辨識重複上傳（不管檔名怎麼改）

指紋 = SHA256( 零件 multiset（每種零件檔名 × 數量排序）+ 步驟數 )
同一個模型的不同匯出 → 相同零件組合與步驟 → 相同指紋。
"""
import re, hashlib, sys

LINE1 = re.compile(r'^1\s+(\S+\s+){13}(\S+\.dat)', re.I)

def fingerprint(ldr_path):
    """回傳 (fingerprint_hex, parts_multiset, steps)"""
    parts = {}
    steps = 0
    with open(ldr_path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            s = line.strip()
            if s.startswith('0 STEP'):
                steps += 1
                continue
            m = LINE1.match(s)
            if m:
                name = m.group(2).lower().replace('\\', '/')
                parts[name] = parts.get(name, 0) + 1
    # 零件 multiset → 穩定字串（排序）
    multiset = sorted(f'{k}x{v}' for k, v in parts.items())
    fp_src = '|'.join(multiset) + f'|steps:{steps}'
    fp = hashlib.sha256(fp_src.encode('utf-8')).hexdigest()[:24]
    return fp, parts, steps

if __name__ == '__main__':
    fp, parts, steps = fingerprint(sys.argv[1])
    print(f'fingerprint: {fp}')
    print(f'parts: {len(parts)} 種 / {sum(parts.values())} 個')
    print(f'steps: {steps}')
