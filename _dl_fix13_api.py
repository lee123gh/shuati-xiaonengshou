# -*- coding: utf-8 -*-
# 从 GitHub API 下载 fix13 最终版全部8个文件到 _live_verify3（临时脚本）
import json, base64, hashlib, os, time, urllib.request

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, '_live_verify3')

comp = json.load(open(os.path.join(DIR, '_api_compare.json'), encoding='utf-8'))
targets = {}
for f in comp['files']:
    targets[f['filename']] = f['sha']
print('目标文件及期望sha:')
for k, v in targets.items():
    print(' ', k, v)


def git_blob_sha(data):
    h = hashlib.sha1()
    h.update(('blob %d\0' % len(data)).encode())
    h.update(data)
    return h.hexdigest()


def dl_blob(path, sha, outpath):
    if os.path.exists(outpath):
        d = open(outpath, 'rb').read()
        if git_blob_sha(d) == sha:
            print('SKIP OK', path)
            return True
    url = 'https://api.github.com/repos/lee123gh/shuati-xiaonengshou/git/blobs/' + sha
    for att in range(6):
        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'smoke-check'})
            with urllib.request.urlopen(req, timeout=240) as r:
                raw = r.read()
            j = json.loads(raw.decode('utf-8'))
            content = base64.b64decode(j['content'])
            h = git_blob_sha(content)
            if h != sha:
                print('HASH MISMATCH', path, h, 'try', att + 1)
                time.sleep(2)
                continue
            with open(outpath, 'wb') as f:
                f.write(content)
            print('OK', path, len(content), 'bytes, try', att + 1)
            return True
        except Exception as e:
            print('retry', att + 1, path, repr(e)[:120])
            time.sleep(3)
    print('FAIL', path)
    return False


ok = 0
for fn, sha in targets.items():
    outp = os.path.join(OUT, fn.replace('/', os.sep))
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    if dl_blob(fn, sha, outp):
        ok += 1
    time.sleep(1)

print('==== 完成', ok, '/', len(targets), '====')
for fn, sha in targets.items():
    outp = os.path.join(OUT, fn.replace('/', os.sep))
    st = 'MISSING'
    if os.path.exists(outp):
        d = open(outp, 'rb').read()
        st = 'OK' if git_blob_sha(d) == sha else 'BAD'
    print(st, fn, os.path.getsize(outp) if os.path.exists(outp) else 0)
