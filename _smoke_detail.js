// 导出被标记题目的完整明细，便于逐条甄别（临时脚本）
const fs = require('fs');
const path = require('path');
const dir = __dirname;

const ids = fs.readFileSync(path.join(dir, '_smoke_scan_results.txt'), 'utf8').split('\n')
    .filter(l => l.includes('[题干疑似嵌入选项]'))
    .map(l => { const m = l.match(/^([\w.]+)#(\d+) /); return m ? { f: m[1], i: parseInt(m[2]) - 1 } : null; })
    .filter(Boolean);

function readJson(f) { return JSON.parse(fs.readFileSync(path.join(dir, 'banks', f), 'utf8').replace(/^\uFEFF/, '')); }
function walkQuestions(data, outArr) {
    if (Array.isArray(data)) data.forEach(x => walkQuestions(x, outArr));
    else if (data && typeof data === 'object') {
        if (typeof data.question === 'string' && (data.type || data.answer !== undefined || data.options)) outArr.push(data);
        else Object.values(data).forEach(x => walkQuestions(x, outArr));
    }
}

const cache = {};
const lines = [];
ids.forEach(({ f, i }) => {
    if (!cache[f]) { const qs = []; walkQuestions(readJson(f), qs); cache[f] = qs; }
    const q = cache[f][i];
    if (!q) { lines.push(`=== ${f}#${i + 1} === 未找到`); return; }
    lines.push(`=== ${f}#${i + 1} ===`);
    lines.push(`[type] ${q.type} | [answer] ${JSON.stringify(q.answer)}`);
    lines.push(`[question] ${String(q.question).replace(/\n/g, '\\n')}`);
    lines.push(`[options] ${JSON.stringify(q.options || [])}`);
    const ex = String(q.explanation || '');
    lines.push(`[explanation] ${ex.length > 120 ? ex.slice(0, 120) + '…' : ex}`);
    lines.push('');
});
fs.writeFileSync(path.join(dir, '_embedded_detail.txt'), lines.join('\n'), 'utf8');
console.log('已输出 ' + ids.length + ' 条明细到 _embedded_detail.txt');
