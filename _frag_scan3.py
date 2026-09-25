# -*- coding: utf-8 -*-
# 三级扫描：句尾被"其它题目选项碎片"覆盖 >=70% 且 >=2 个不相交碎片（临时脚本）
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
out = open(os.path.join(D, '_frag_scan3_out.txt'), 'w', encoding='utf-8')
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
    def match_spans(sn):
        spans = []
        i = 0
        while i < len(sn) - 4:
            k5 = sn[i:i + 5]
            for frag in pool.get(k5, ()):
                if sn.startswith(frag, i):
                    spans.append((i, i + len(frag), frag))
            i += 1
        return spans
    hits = []
    for qi, q in enumerate(qs):
        stem = str(q.get('question', ''))
        sn = norm(stem)
        if len(sn) < 20:
            continue
        last = -1
        for ch in END:
            p2 = sn.rfind(ch)
            if p2 > last: last = p2
        tail = sn[last + 1:] if last >= 0 else sn
        if len(tail) < 10:
            continue
        spans = match_spans(tail)
        if not spans: continue
        # 合并区间算覆盖率；挑最长不相交碎片
        iv = sorted(set((a, b) for a, b, _ in spans))
        merged = []
        for a, b in iv:
            if merged and a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        cover = sum(b - a for a, b in merged) / len(tail)
        if cover >= 0.7:
            fl = sorted(set(fr for _, _, fr in spans), key=len, reverse=True)
            hits.append((qi + 1, q.get('type'), stem[:120], ' / '.join(fl[:6]), round(cover, 2), len(tail)))
    print('==== %s: 高覆盖嫌疑 %d 条 ====' % (f, len(hits)), file=out)
    for (n, t, stem, frags, cov, tl) in hits[:100]:
        print('  #%d [%s] (覆盖%s 尾长%d) %s' % (n, t, cov, tl, stem), file=out)
        print('      碎片: %s' % frags, file=out)
    grand += len(hits)
print('TOTAL', grand, file=out)
out.close()
print('done', grand)
