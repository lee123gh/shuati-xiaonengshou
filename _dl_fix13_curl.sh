#!/bin/bash
# 从 GitHub API 下载 fix13 最终版全部文件到 _live_verify3（curl 版，带 git-blob-sha 校验，临时脚本）
cd "C:/Users/52202/.trae-cn/work/6a30feea10f5b2272f297683/shuati-xiaonengshou" || exit 1

python -c "
import json
comp=json.load(open('_api_compare.json',encoding='utf-8'))
for f in comp['files']: print(f['filename']+' '+f['sha'])
" > _fix13_targets.txt

echo "目标清单:"; cat _fix13_targets.txt; echo "---开始下载---"

while read -r fn sha; do
  out="_live_verify3/$fn"
  mkdir -p "$(dirname "$out")"
  ok=$(python -c "
import hashlib,os
p=r'$out'
if os.path.exists(p):
    d=open(p,'rb').read()
    h=hashlib.sha1(('blob %d\0'%len(d)).encode()+d).hexdigest()
    print('YES' if h=='$sha' else 'NO')
else: print('NO')
")
  if [ "$ok" = "YES" ]; then echo "SKIP $fn (已存在且校验通过)"; continue; fi
  for t in 1 2 3 4 5 6; do
    curl -sS -m 180 -H "Accept: application/vnd.github+json" -H "User-Agent: smoke-check" \
      "https://api.github.com/repos/lee123gh/shuati-xiaonengshou/git/blobs/$sha" -o _tmp_blob.json
    res=$(python -c "
import json,base64,hashlib
try:
    j=json.load(open('_tmp_blob.json',encoding='utf-8'))
    if 'content' not in j:
        print('ERR', str(j.get('message','no-content'))[:80]); raise SystemExit
    c=base64.b64decode(j['content'])
    h=hashlib.sha1(('blob %d\0'%len(c)).encode()+c).hexdigest()
    if h=='$sha':
        open(r'$out','wb').write(c)
        print('OK',len(c),'bytes')
    else:
        print('MISMATCH',h[:12],'len',len(c))
except SystemExit: pass
except Exception as e:
    print('ERR',repr(e)[:100])
")
    echo "$fn try$t: $res"
    case "$res" in OK*) break;; esac
    sleep 3
  done
done < _fix13_targets.txt

echo "=== 最终校验 ==="
python -c "
import json,hashlib,os
comp=json.load(open('_api_compare.json',encoding='utf-8'))
allok=True
for f in comp['files']:
    p=os.path.join('_live_verify3',f['filename'])
    if os.path.exists(p):
        d=open(p,'rb').read()
        h=hashlib.sha1(('blob %d\0'%len(d)).encode()+d).hexdigest()
        st='OK' if h==f['sha'] else 'BAD'
    else: st='MISSING'; d=b''
    if st!='OK': allok=False
    print(st, f['filename'], len(d))
print('ALL_OK' if allok else 'NOT_ALL_OK')
"
