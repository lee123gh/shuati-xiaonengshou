# -*- coding: utf-8 -*-
# git-blob 校验/解码辅助（临时脚本）
# 用法1: python _blob_helper.py check <file> <sha>          -> 输出 YES/NO
# 用法2: python _blob_helper.py decode <tmpjson> <sha> <out> -> 输出 OK <len> / MISMATCH / ERR ...
import sys, json, base64, hashlib, os

def git_blob_sha(data):
    h = hashlib.sha1()
    h.update(('blob %d\0' % len(data)).encode())
    h.update(data)
    return h.hexdigest()

mode = sys.argv[1].strip()

if mode == 'check':
    path, sha = sys.argv[2].strip(), sys.argv[3].strip()
    if os.path.exists(path):
        d = open(path, 'rb').read()
        print('YES' if git_blob_sha(d) == sha else 'NO')
    else:
        print('NO')
elif mode == 'decode':
    tmp, sha, out = sys.argv[2].strip(), sys.argv[3].strip(), sys.argv[4].strip()
    try:
        j = json.load(open(tmp, encoding='utf-8'))
        if 'content' not in j:
            print('ERR', str(j.get('message', 'no-content'))[:100])
            sys.exit(0)
        c = base64.b64decode(j['content'])
        h = git_blob_sha(c)
        if h == sha:
            open(out, 'wb').write(c)
            print('OK', len(c), 'bytes')
        else:
            print('MISMATCH', h[:12], 'len', len(c))
    except Exception as e:
        print('ERR', repr(e)[:100])
else:
    print('unknown mode')
