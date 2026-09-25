# -*- coding: utf-8 -*-
# 核对指定题的选项数组状态（临时脚本）
import os, json

D = os.path.dirname(os.path.abspath(__file__))
VER3 = os.path.join(D, '_live_verify3')

def walk_questions(data, out):
    if isinstance(data, list):
        for x in data: walk_questions(x, out)
    elif isinstance(data, dict):
        if isinstance(data.get('question'), str) and ('type' in data or 'answer' in data or 'options' in data):
            out.append(data)
        else:
            for x in data.values(): walk_questions(x, out)

IDS = {
    'lifeguard.json': [925, 926, 1708, 1717, 1729, 1797, 1822],
    'lifeguard_senior.json': [],
    'instructor.json': [28, 429, 1649, 1893, 3785, 3831, 3832, 3847, 3849, 3853, 3910, 4037, 4123, 4175, 4179, 4180],
    'instructor_senior.json': [2748, 2799, 2817, 2821, 2903, 2917, 2931, 2969, 2987, 2993, 3089, 3193, 3244, 3248, 3249, 3845, 3853, 3883, 4013, 4113, 4118, 4124],
    'order_instructor.json': [286, 287, 293, 301, 479, 581, 764, 847, 906],
    'order_lifeguard.json': [],
    'order_instructor_senior.json': [256, 279, 289, 422, 423, 437, 442, 487, 610, 749, 830, 871, 872, 1635, 1675, 1800, 1807, 1893, 1899],
}

out = open(os.path.join(D, '_check_opts_out.txt'), 'w', encoding='utf-8')
for f, idxs in IDS.items():
    if not idxs: continue
    p = os.path.join(VER3, 'banks', f)
    if not os.path.exists(p): continue
    qs = []
    walk_questions(json.load(open(p, encoding='utf-8-sig')), qs)
    print('########## %s' % f, file=out)
    for n in idxs:
        q = qs[n - 1]
        opts = q.get('options') or []
        stem = str(q.get('question', ''))
        selfhit = sum(1 for o in opts if len(str(o).strip()) >= 2 and str(o).strip() in stem)
        print('#%d [%s ans=%s opts=%d self=%d]' % (n, q.get('type'), q.get('answer'), len(opts), selfhit), file=out)
        for oi, o in enumerate(opts[:4]):
            print('   %s=%s' % ('ABCD'[oi], str(o)[:60]), file=out)
    print('', file=out)
out.close()
print('done')
