// 生成冒烟检查报告（临时脚本）：数据问题清单 + 代码问题清单
const fs = require('fs');
const path = require('path');
const dir = __dirname;

const files = ['lifeguard.json', 'lifeguard_senior.json', 'instructor.json', 'instructor_senior.json',
    'order_lifeguard.json', 'order_instructor.json', 'order_instructor_senior.json'];

function readJson(f) { return JSON.parse(fs.readFileSync(path.join(dir, 'banks', f), 'utf8').replace(/^\uFEFF/, '')); }
function walkQuestions(data, outArr) {
    if (Array.isArray(data)) data.forEach(x => walkQuestions(x, outArr));
    else if (data && typeof data === 'object') {
        if (typeof data.question === 'string' && (data.type || data.answer !== undefined || data.options)) outArr.push(data);
        else Object.values(data).forEach(x => walkQuestions(x, outArr));
    }
}

// 从扫描结果中取出全部被标记的 id
const flagged = fs.readFileSync(path.join(dir, '_smoke_scan_results.txt'), 'utf8').split('\n')
    .filter(l => l.includes('[题干疑似嵌入选项]'))
    .map(l => { const m = l.match(/^([\w.]+)#(\d+) /); return m ? { f: m[1], n: parseInt(m[2]) } : null; })
    .filter(Boolean);

// 经人工甄别后确认是误报的条目（题干正常提及选项词，如"反蛙泳""手指""握拳"等）
const FALSE_SET = new Set([
    'lifeguard.json#304', 'lifeguard.json#360', 'lifeguard.json#844', 'lifeguard.json#1003', 'lifeguard.json#1172', 'lifeguard.json#1268',
    'lifeguard_senior.json#304', 'lifeguard_senior.json#360', 'lifeguard_senior.json#844', 'lifeguard_senior.json#1003', 'lifeguard_senior.json#1172', 'lifeguard_senior.json#1268',
    'instructor.json#1081', 'instructor.json#1387', 'instructor.json#2226', 'instructor.json#2286', 'instructor.json#2769', 'instructor.json#2936', 'instructor.json#3018', 'instructor.json#3111', 'instructor.json#3215', 'instructor.json#3791', 'instructor.json#4375', 'instructor.json#4500',
    'instructor_senior.json#1056', 'instructor_senior.json#1329', 'instructor_senior.json#1350', 'instructor_senior.json#1755', 'instructor_senior.json#2005', 'instructor_senior.json#3567',
    'order_lifeguard.json#127', 'order_lifeguard.json#570', 'order_lifeguard.json#817', 'order_lifeguard.json#843', 'order_lifeguard.json#1253',
    'order_instructor.json#236', 'order_instructor.json#1206', 'order_instructor.json#1363', 'order_instructor.json#1700',
    'order_instructor_senior.json#1329', 'order_instructor_senior.json#2005'
]);

const cache = {};
function getQ(f, n) {
    if (!cache[f]) { const qs = []; walkQuestions(readJson(f), qs); cache[f] = qs; }
    return cache[f][n - 1];
}
const norm = s => String(s || '').replace(/[\s\u3000]/g, '');

// 分类规则
function classify(q, stem) {
    const artifacts = /转发截图|截图收藏|下转题|到底了|pl\d|\uFF04|\$|40"|6:/.test(stem) || stem.includes('只 ');
    const exp = norm(q.explanation || '');
    let expHit = false;
    if (exp.length >= 16) {
        for (let i = 0; i + 16 <= exp.length; i += 4) {
            if (stem.includes(exp.slice(i, i + 16))) { expHit = true; break; }
        }
    }
    const ns = norm(stem);
    const opts = (q.options || []).map(o => norm(o)).filter(o => o.length >= 1);
    let run = 0, bestRun = 0;
    for (let i = 0; i < opts.length; i++) {
        for (let j = 0; j < opts.length; j++) {
            if (i === j) continue;
            if (ns.includes(opts[i] + opts[j])) bestRun = Math.max(bestRun, 2);
        }
    }
    if (artifacts) return 'A1';
    if (expHit) return 'A2';
    if (bestRun >= 2) return 'A3';
    return 'A4';
}
const CAT = {
    'A1': ['题干混入页面/OCR残留', '删除题干中的控件、页码等残留文字，保留题目正文'],
    'A2': ['题干混入解析片段', '删除题干中重复的解析文字，恢复到"（）"填空为止'],
    'A3': ['题干混入选项文本', '删除题干尾部重复的选项文本；若选项数组同时被切碎需重建选项'],
    'A4': ['题干残留待复核', '人工复核题干多余片段后清理']
};

const rows = [];
let nA = 0;
flagged.forEach(({ f, n }) => {
    const key = f + '#' + n;
    if (FALSE_SET.has(key)) return;
    const q = getQ(f, n);
    if (!q) return;
    const stem = String(q.question);
    let cat = classify(q, stem);
    if (key === 'order_lifeguard.json#112') cat = 'A1';
    const [name, sug] = CAT[cat];
    let stemShow = stem.replace(/\|/g, '\\|');
    if (stemShow.length > 70) stemShow = stemShow.slice(0, 70) + '…';
    rows.push({ key, name, stemShow, sug });
    nA++;
});

// 按文件分组输出
const byFile = {};
rows.forEach(r => { const f = r.key.split('#')[0]; (byFile[f] = byFile[f] || []).push(r); });

let md = [];
md.push('## 一、题目数据问题（真错题）——共 ' + nA + ' 处');
md.push('');
md.push('> 发现方式：脚本全量扫描 7 个题库（20106 题）中"题干包含 ≥2 个选项文本 / 解析片段 / 页面残留"的题目，再逐条人工甄别。');
md.push('> 另有约 40 处为误报（题干正常提及选项词，如"反蛙泳""手指""握拳"），已排除。');
md.push('');
Object.keys(byFile).forEach(f => {
    md.push('### ' + f + '（' + byFile[f].length + ' 处）');
    md.push('');
    md.push('| 题号 | 问题类型 | 题干摘要 | 修改建议 |');
    md.push('|---|---|---|---|');
    byFile[f].forEach(r => {
        md.push('| ' + r.key.split('#')[1] + ' | ' + r.name + ' | ' + r.stemShow + ' | ' + r.sug + ' |');
    });
    md.push('');
});

fs.writeFileSync(path.join(dir, '_report_data_section.md'), md.join('\n'), 'utf8');
console.log('数据问题（排除误报后）: ' + nA + ' 处');
console.log('按文件统计: ' + JSON.stringify(Object.fromEntries(Object.entries(byFile).map(([k, v]) => [k, v.length]))));
console.log('按类型统计:' + JSON.stringify(rows.reduce((a, r) => { a[r.name] = (a[r.name] || 0) + 1; return a; }, {})));
