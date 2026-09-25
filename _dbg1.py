# -*- coding: utf-8 -*-
import os, re, json
D = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(D, '_live_verify3', 'banks', 'instructor.json')
text = open(path, encoding='utf-8-sig').read()
lines = text.split('\n')
print('total lines:', len(lines))
print('line3324..3332:')
for i in range(3320, 3333):
    print(i + 1, repr(lines[i]))
ANSWER_RE = re.compile(r'^\s*"answer":\s*"([^"]*)"')
found = None
for i in range(3321, 3332):
    m = ANSWER_RE.match(lines[i])
    if m and m.group(1).strip() == 'C':
        found = i
        break
print('found(0-based):', found, repr(lines[found]) if found is not None else None)
j = found
while j > 0 and '"type"' not in lines[j]:
    j -= 1
print('type line:', j + 1, repr(lines[j]))
k = j
while k > 0 and lines[k].strip() != '{':
    k -= 1
print('brace line:', k + 1, repr(lines[k]))
off = sum(len(l) + 1 for l in lines[:k])
print('off:', off, 'text[off-10:off+30]:', repr(text[off - 10:off + 30]))
sub = text[off:]
try:
    obj, end = json.JSONDecoder().raw_decode(sub.lstrip())
    print('decode OK:', json.dumps({kk: obj[kk] for kk in obj if kk != 'options'}, ensure_ascii=False)[:200])
except Exception as e:
    print('decode FAIL:', repr(e))
