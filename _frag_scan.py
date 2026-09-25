# -*- coding: utf-8 -*-
# 跨题污染扫描：题干中是否混入"其它题目选项/解析"的文本碎片（临时脚本）
import os, re, json

D = os.path.dirname(os.path.abspath(__file__))
VER3 = os.path.join(D, '_live_verify3')
FILES = ['lifeguard.json', 'lifeguard_senior.json', 'instructor.json', 'instructor_senior.json',
         'order_lifeguard.json', 'order_instructor.json', 'order_instructor_senior.json']

def walk_questions(data, out):
    if isinstance(data, list):
        for x in data: walk_questions(x, out)
    elif isinstance(data, dict):
        if isinstance(data.get('question'), str) and ('type' in data or 'answer' in data or 'options' in data):
            out.append(data)
        else:
            for x in data.values(): walk_questions(x, out)

def norm(s):
    return re.sub(r'[\s\u3000]', '', str(s or ''))

out = open(os.path.join(D, '_frag_scan_out.txt'), 'w', encoding='utf-8')
grand = 0
for f in FILES:
    p = os.path.join(VER3, 'banks', f)
    if not os.path.exists(p):
        continue
    qs = []
    walk_questions(json.load(open(p, encoding='utf-8-sig')), qs)
    # 选项池：按前5字符建索引（仅>=5字符的规范化选项文本）
    pool = {}
    for qi, q in enumerate(qs):
        for o in (q.get('options') or []):
            t = norm(o)
            if len(t) >= 5:
                pool.setdefault(t[:5], set()).add(t)
    def match_frags(stem):
        sn = norm(stem)
        found = set()
        i = 0
        L = len(sn)
        while i < L - 4:
            k5 = sn[i:i + 5]
            for frag in pool.get(k5, ()):
                if sn.startswith(frag, i):
                    found.add(frag)
            i += 1
        return found
    hits = []
    for qi, q in enumerate(qs):
        stem = str(q.get('question', ''))
        if len(norm(stem)) < 40:
            continue
        own = set(norm(o) for o in (q.get('options') or []))
        frags = match_frags(stem) - own
        # 只保留"强度"足够的：至少2个不同碎片
        if len(frags) >= 2:
            hits.append((qi + 1, q.get('type'), stem[:110], sorted(frags)[:6]))
    print('==== %s: 跨题碎片嫌疑 %d 条 ====' % (f, len(hits)), file=out)
    for (n, t, stem, frags) in hits[:80]:
        print('  #%d [%s] %s' % (n, t, stem), file=out)
        print('      碎片: %s' % ' / '.join(frags), file=out)
    grand += len(hits)
print('TOTAL', grand, file=out)
out.close()
print('done', grand)
