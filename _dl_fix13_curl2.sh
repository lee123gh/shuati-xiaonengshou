#!/bin/bash
# v2: 从 GitHub API 下载 fix13 最终版全部文件到 _live_verify3（修复 CRLF 问题，临时脚本）
cd "C:/Users/52202/.trae-cn/work/6a30feea10f5b2272f297683/shuati-xiaonengshou" || exit 1

python -c "
import json
comp=json.load(open('_api_compare.json',encoding='utf-8'))
for f in comp['files']: print(f['filename']+' '+f['sha'])
" | tr -d '\r' > _fix13_targets.txt

echo "目标清单:"; cat _fix13_targets.txt; echo "---开始下载---"

while read -r fn sha; do
  out="_live_verify3/$fn"
  mkdir -p "$(dirname "$out")"
  ok=$(python _blob_helper.py check "$out" "$sha")
  if [ "$ok" = "YES" ]; then echo "SKIP $fn (已存在且校验通过)"; continue; fi
  for t in 1 2 3 4 5 6; do
    curl -sS -m 180 -H "Accept: application/vnd.github+json" -H "User-Agent: smoke-check" \
      "https://api.github.com/repos/lee123gh/shuati-xiaonengshou/git/blobs/$sha" -o _tmp_blob2.json
    res=$(python _blob_helper.py decode _tmp_blob2.json "$sha" "$out")
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
    st='MISSING'; n=0
    if os.path.exists(p):
        d=open(p,'rb').read()
        h=hashlib.sha1(('blob %d\0'%len(d)).encode()+d).hexdigest()
        st='OK' if h==f['sha'] else 'BAD'
        n=len(d)
    if st!='OK': allok=False
    print(st, f['filename'], n)
print('ALL_OK' if allok else 'NOT_ALL_OK')
" | tr -d '\r'
