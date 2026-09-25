# -*- coding: utf-8 -*-
# 提取指定题目完整内容（用于人工核对）（临时脚本）
import os, json

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

# 按索引提取
BY_INDEX = {
    'instructor.json': [907, 1041, 3852, 4368, 4446],
    'instructor_senior.json': [896, 1017, 3435, 3513],
    'order_instructor.json': [1309],
    'order_instructor_senior.json': [1165, 1276],
    'lifeguard.json': [1264],
    'lifeguard_senior.json': [1264],
}
# 按题干关键词全库搜索（找同名题的所有拷贝）
BY_TEXT = ['爬泳的身体姿势特点不包括', '肩外侧划水的主要原因不包括', '纠正方法是']

out = open(os.path.join(D, '_extract_qs_out.txt'), 'w', encoding='utf-8')
cache = {}
for f in FILES:
    p = os.path.join(VER3, 'banks', f)
    if not os.path.exists(p):
        print('(未下载:%s)' % f, file=out)
        continue
    qs = []
    walk_questions(json.load(open(p, encoding='utf-8-sig')), qs)
    cache[f] = qs

for f, idxs in BY_INDEX.items():
    if f not in cache: continue
    for n in idxs:
        if n - 1 >= len(cache[f]): continue
        q = cache[f][n - 1]
        print('===== %s #%d =====' % (f, n), file=out)
        print('[type]', q.get('type'), '[answer]', q.get('answer'), file=out)
        print('[question]', q.get('question'), file=out)
        for oi, o in enumerate(q.get('options') or []):
            print('  %s. %s' % ('ABCDEFG'[oi], o), file=out)
        print('[explanation]', q.get('explanation'), file=out)
        print('', file=out)

print('\n########## 按题干关键词搜索 ##########', file=out)
for f, qs in cache.items():
    for i, q in enumerate(qs):
        qt = str(q.get('question', ''))
        for kw in BY_TEXT:
            if kw in qt:
                print('===== %s #%d (匹配:%s) =====' % (f, i + 1, kw), file=out)
                print('[answer]', q.get('answer'), file=out)
                print('[question]', qt[:180], file=out)
                for oi, o in enumerate(q.get('options') or []):
                    print('  %s. %s' % ('ABCDEFG'[oi], str(o)[:90]), file=out)
                print('[explanation]', str(q.get('explanation'))[:260], file=out)
                print('', file=out)
                break
out.close()
print('done')
