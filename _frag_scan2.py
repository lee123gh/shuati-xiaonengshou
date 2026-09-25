# -*- coding: utf-8 -*-
# 精化扫描：题干"句尾（最后一个句末标点之后）"混入 ≥2 个其它题目选项碎片、且无句末标点（临时脚本）
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

END = '。！？；;.!?'
out = open(os.path.join(D, '_frag_scan2_out.txt'), 'w', encoding='utf-8')
grand = 0
for f in FILES:
    p = os.path.join(VER3, 'banks', f)
    if not os.path.exists(p):
        continue
    qs = []
    walk_questions(json.load(open(p, encoding='utf-8-sig')), qs)
    pool = {}
    for q in qs:
        for o in (q.get('options') or []):
            t = norm(o)
            if len(t) >= 5:
                pool.setdefault(t[:5], set()).add(t)
    def match_frags(sn):
        found = set()
        i = 0
        while i < len(sn) - 4:
            k5 = sn[i:i + 5]
            for frag in pool.get(k5, ()):
                if sn.startswith(frag, i):
                    found.add(frag)
            i += 1
        return found
    hits = []
    for qi, q in enumerate(qs):
        stem = str(q.get('question', ''))
        sn = norm(stem)
        if len(sn) < 20:
            continue
        # 找最后一个句末标点的位置（在规范化串中）
        last = -1
        for ch in END:
            p2 = sn.rfind(ch)
            if p2 > last: last = p2
        tail = sn[last + 1:] if last >= 0 else sn
        if len(tail) < 10:
            continue
        frags = match_frags(tail)
        if len(frags) >= 2:
            hits.append((qi + 1, q.get('type'), stem[:120], ' / '.join(sorted(frags)[:6]), len(tail)))
    print('==== %s: 句尾碎片嫌疑 %d 条 ====' % (f, len(hits)), file=out)
    for (n, t, stem, frags, tl) in hits[:100]:
        print('  #%d [%s] (尾长%d) %s' % (n, t, tl, stem), file=out)
        print('      碎片: %s' % frags, file=out)
    grand += len(hits)
print('TOTAL', grand, file=out)
out.close()
print('done', grand)
