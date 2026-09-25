# -*- coding: utf-8 -*-
# fix13 答案改动复核：按 patch 给出的行号定位 24 处改动，打印完整题目上下文（临时脚本）
import os, re, json

D = os.path.dirname(os.path.abspath(__file__))
VER3 = os.path.join(D, '_live_verify3')
OUT = open(os.path.join(D, '_fix13_verify_out.txt'), 'w', encoding='utf-8')

# (文件, patch中新文件hunk起始行, 旧答案, 新答案)
TARGETS = [
    ('banks/instructor.json', 3324, 'B', 'C'),
    ('banks/instructor.json', 20711, 'B', 'A'),
    ('banks/instructor.json', 39178, 'A', 'D'),
    ('banks/instructor.json', 44376, 'B', 'C'),
    ('banks/instructor.json', 61478, 'B', 'A'),
    ('banks/instructor_senior.json', 3421, 'B', 'C'),
    ('banks/instructor_senior.json', 20084, 'B', 'A'),
    ('banks/instructor_senior.json', 31574, 'B', 'C'),
    ('banks/lifeguard.json', 1347, 'D', 'A'),
    ('banks/lifeguard.json', 15194, 'A', 'D'),
    ('banks/lifeguard.json', 28060, 'A', 'B'),
    ('banks/lifeguard_senior.json', 1347, 'D', 'A'),
    ('banks/lifeguard_senior.json', 15196, 'A', 'D'),
    ('banks/lifeguard_senior.json', 28063, 'A', 'B'),
    ('banks/order_instructor.json', 537, 'B', 'C'),
    ('banks/order_instructor.json', 9008, 'B', 'C'),
    ('banks/order_instructor.json', 29534, 'B', 'A'),
    ('banks/order_instructor_senior.json', 539, 'B', 'C'),
    ('banks/order_instructor_senior.json', 8923, 'B', 'C'),
    ('banks/order_lifeguard.json', 6270, 'B', 'D'),
    ('banks/order_lifeguard.json', 8408, 'B', 'D'),
    ('banks/order_lifeguard.json', 15906, 'A', 'D'),
    ('banks/order_lifeguard.json', 17433, 'A', 'C'),
    ('banks/order_lifeguard.json', 19080, 'A', 'B'),
]

ANSWER_RE = re.compile(r'^\s*"answer":\s*"([^"]*)"')

def walk_questions(data, out):
    if isinstance(data, list):
        for x in data: walk_questions(x, out)
    elif isinstance(data, dict):
        if isinstance(data.get('question'), str) and ('type' in data or 'answer' in data or 'options' in data):
            out.append(data)
        else:
            for x in data.values(): walk_questions(x, out)

cache = {}
def get_qs(f):
    if f not in cache:
        qs = []
        walk_questions(json.load(open(os.path.join(VER3, f), encoding='utf-8-sig')), qs)
        cache[f] = qs
    return cache[f]

def check_file(f, lineno, old, new):
    path = os.path.join(VER3, f)
    text = open(path, encoding='utf-8-sig').read()
    lines = text.split('\n')
    found = None
    for i in range(max(0, lineno - 3), min(len(lines), lineno + 7)):
        m = ANSWER_RE.match(lines[i])
        if m and m.group(1).strip() == new:
            found = i
            break
    if found is None:
        return '  !! 在行%d附近未找到 answer=%s' % (lineno, new)
    j = found
    while j > 0 and '"type"' not in lines[j]:
        j -= 1
    k = j
    while k > 0 and lines[k].strip() != '{':
        k -= 1
    off = sum(len(l) + 1 for l in lines[:k])
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[off:].lstrip())
    except Exception as e:
        return '  !! raw_decode失败: %r' % (e,)
    qs = get_qs(f)
    idx = None
    for qi, q in enumerate(qs):
        if q == obj or (q.get('question') == obj.get('question') and q.get('explanation') == obj.get('explanation')):
            idx = qi + 1
            break
    o = []
    o.append('  题号: %s 第 %s 题 | patch行%d | %s→%s' % (f, idx, lineno, old, new))
    o.append('  [题干] ' + str(obj.get('question', ''))[:180])
    opts = obj.get('options') or []
    for oi, op in enumerate(opts):
        o.append('    %s. %s' % ('ABCDEFG'[oi], str(op)[:90]))
    ans = str(obj.get('answer'))
    o.append('  [答案] %s  [选项数] %d %s' % (ans, len(opts), '' if not (ans and ans[0:1].isalpha() and ord(ans[0]) - 65 >= len(opts)) else '<<< 越界警告!'))
    o.append('  [解析] ' + str(obj.get('explanation', ''))[:240])
    return '\n'.join(o)

cur = None
any_missing = False
for f, ln, old, new in TARGETS:
    if f != cur:
        cur = f
        print('=' * 66, file=OUT)
        print('FILE:', f, file=OUT)
    if os.path.exists(os.path.join(VER3, f)):
        print(check_file(f, ln, old, new), file=OUT)
    else:
        print('  (文件尚未下载: %s 行%d %s→%s)' % (f, ln, old, new), file=OUT)
        any_missing = True
print('=' * 66, file=OUT)
print('MISSING_FILES' if any_missing else 'ALL_VERIFIED_FILES_PRESENT', file=OUT)
OUT.close()
print('done')
