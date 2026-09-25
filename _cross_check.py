# -*- coding: utf-8 -*-
# 独立交叉检查：搜索"解析指出某选项错误/不属于，但答案偏偏是该选项"的剩余矛盾（临时脚本）
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

NEG = r'(错误|不正确|不属于|不对|有误|不选|排除|不是)'
P1 = re.compile(r'选项\s*([A-D])[^。；;!？\n]{0,18}?' + NEG)
P2 = re.compile(r'([A-D])[^。；;!？\n]{0,6}?' + NEG)

out = open(os.path.join(D, '_cross_check_out.txt'), 'w', encoding='utf-8')
total_hits = 0
for f in FILES:
    p = os.path.join(VER3, 'banks', f)
    if not os.path.exists(p):
        print('(未下载:' + f + ')', file=out)
        continue
    qs = []
    walk_questions(json.load(open(p, encoding='utf-8-sig')), qs)
    hits = []
    for i, q in enumerate(qs):
        if q.get('type') != 'single': continue
        ans = str(q.get('answer', '')).strip()
        if not re.fullmatch(r'[A-D]', ans): continue
        expl = str(q.get('explanation', ''))
        if not expl: continue
        # 解析中"选项X…否定"命中
        neg_letters = set(m.group(1) for m in P1.finditer(expl))
        if not neg_letters:
            for m in P2.finditer(expl):
                neg_letters.add(m.group(1))
        if ans in neg_letters:
            hits.append((i + 1, ans, q.get('question', '')[:90], expl[:200]))
    print('==== %s: 嫌疑 %d 条 ====' % (f, len(hits)), file=out)
    for (n, a, qt, ex) in hits:
        print('  #%d [答案=%s] %s' % (n, a, qt), file=out)
        print('        解析: %s' % ex.replace('\n', ' '), file=out)
    total_hits += len(hits)
print('TOTAL_HITS', total_hits, file=out)
out.close()
print('done, hits=', total_hits)
