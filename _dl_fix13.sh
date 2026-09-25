#!/bin/bash
cd "C:\Users\52202\.trae-cn\work\6a30feea10f5b2272f297683\shuati-xiaonengshou"
dl() {
  local path="$1" sha="$2" out="$3"
  for i in 1 2 3 4 5 6 7 8; do
    curl -sL "https://raw.githubusercontent.com/lee123gh/shuati-xiaonengshou/d3de8897dc70214e3b5fae8ba621a01fce44fe06/$path" -o "$out" --max-time 240
    local sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
    local h=$(git hash-object "$out" 2>/dev/null)
    if [ "$h" = "$sha" ]; then echo "OK $path size=$sz try=$i"; return 0; fi
    echo "try $i FAIL $path size=$sz hash=$h"
    sleep 2
  done
  return 1
}
dl "banks/instructor.json" "25da99a623cdd4cc3fc6aa313fc2dd8ebb20838f" "_live_verify2/banks/instructor.json"
dl "banks/instructor_senior.json" "b49c11065331a07a1db860b80fc815ddde9be8da" "_live_verify2/banks/instructor_senior.json"
echo "=== 最终校验 ==="
ls -la _live_verify2/banks/
echo "instructor.json hash: $(git hash-object _live_verify2/banks/instructor.json 2>/dev/null) 期望 25da99a623cdd4cc3fc6aa313fc2dd8ebb20838f"
echo "instructor_senior.json hash: $(git hash-object _live_verify2/banks/instructor_senior.json 2>/dev/null) 期望 b49c11065331a07a1db860b80fc815ddde9be8da"
echo "DONE"
