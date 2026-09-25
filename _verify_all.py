# -*- coding: utf-8 -*-
# 全面核对：临时目录里所有 json/html 文件的 git-blob-sha，与 fix13 期望值对照（临时脚本）
import os, json, hashlib

D = os.path.dirname(os.path.abspath(__file__))

# fix13 期望 sha（来自 compare API，new blob sha）
comp = json.load(open(os.path.join(D, '_api_compare.json'), encoding='utf-8'))
fix13 = {f['filename']: f['sha'] for f in comp['files']}

def blob_sha(p):
    d = open(p, 'rb').read()
    return hashlib.sha1(('blob %d\0' % len(d)).encode() + d).hexdigest()

rev = {v: k for k, v in fix13.items()}
for sub in ['_live_verify2', '_live_verify3', '_live_banks', '_live_verify']:
    root = os.path.join(D, sub)
    if not os.path.isdir(root): continue
    print('#### ' + sub)
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not (fn.endswith('.json') or fn.endswith('.html') or fn.endswith('.txt')): continue
            full = os.path.join(dirpath, fn)
            size = os.path.getsize(full)
            if size == 0: continue
            if fn.endswith('.txt'):
                continue
            h = blob_sha(full)
            tag = ''
            if h in rev:
                tag = '== FIX13: ' + rev[h]
            rel = os.path.relpath(full, D)
            print('  %-60s %9d  %s %s' % (rel, size, h[:12], tag))
    print('')
