// 冒烟检查脚本 v20260924fix12：数据校验 + 判分逻辑仿真（临时脚本，检查完可删）
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const OUT = [];
function out(s) { OUT.push(s); }

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
function normJudgeAns(a) { if (a === 'A') return '正确'; if (a === 'B') return '错误'; return a; }
function normMultiAns(a) { if (typeof a === 'string' && a && !a.includes('|')) return a.split('').join('|'); return a; }
function stripPrefix(t) { return String(t || '').replace(/^[A-Za-z][.、\s]\s*/, '').trim(); }

// ============ 第 1 部分：数据校验 ============
const problems = [];
let grandTotal = 0;
const fileStats = {};

files.forEach(f => {
    const p = path.join(dir, 'banks', f);
    if (!fs.existsSync(p)) { problems.push(`${f} [文件缺失]`); return; }
    let data;
    try { data = readJson(f); } catch (e) { problems.push(`${f} [JSON解析失败] ${e.message}`); return; }
    const qs = [];
    walkQuestions(data, qs);
    fileStats[f] = qs.length;
    grandTotal += qs.length;
    qs.forEach((q, i) => {
        const id = `${f}#${i + 1}`;
        const type = q.type;
        const opts = Array.isArray(q.options) ? q.options : [];
        if (!['single', 'multiple', 'judge'].includes(type)) problems.push(`${id} [类型异常] type=${JSON.stringify(type)}`);
        if (!q.question || !String(q.question).trim()) problems.push(`${id} [题干为空]`);
        let ans = q.answer;
        if (type === 'multiple') ans = normMultiAns(ans);
        if (type === 'judge') ans = normJudgeAns(ans);
        if (ans === undefined || ans === null || String(ans).trim() === '') problems.push(`${id} [答案为空] type=${type}`);
        if (type !== 'judge') {
            if (opts.length < 2) problems.push(`${id} [选项少于2] ${opts.length}个`);
            opts.forEach((o, oi) => { if (!String(o).trim()) problems.push(`${id} [选项${'ABCDEFG'[oi] || oi}为空]`); });
            const seen = new Map();
            opts.forEach((o, oi) => {
                const k = String(o).trim();
                if (seen.has(k)) problems.push(`${id} [选项重复] ${'ABCDEFG'[seen.get(k)]}=${'ABCDEFG'[oi]} "${k.slice(0, 25)}"`);
                else seen.set(k, oi);
            });
        }
        if (type === 'single') {
            const a = String(ans || '').trim();
            if (/^[A-D]$/.test(a)) {
                const idx = a.charCodeAt(0) - 65;
                if (idx >= opts.length) problems.push(`${id} [答案越界] answer=${a} 但只有${opts.length}个选项`);
            } else {
                const clean = stripPrefix(a);
                const hit = opts.some(o => stripPrefix(o) === clean || String(o).trim() === a.trim());
                if (!hit) problems.push(`${id} [文字答案无法匹配选项] answer="${a.slice(0, 30)}" options=${JSON.stringify(opts.slice(0, 4)).slice(0, 140)}`);
            }
        }
        if (type === 'multiple') {
            const letters = String(ans || '').split('|').map(t => t.trim()).filter(Boolean);
            if (!letters.length) problems.push(`${id} [多选答案为空]`);
            letters.forEach(L => { if (!/^[A-D]$/.test(L)) problems.push(`${id} [多选答案非字母] "${L}"`); });
            const uniq = new Set(letters);
            if (uniq.size !== letters.length) problems.push(`${id} [多选答案重复字母] ${ans}`);
            letters.forEach(L => { const idx = L.charCodeAt(0) - 65; if (idx >= opts.length && idx < 26) problems.push(`${id} [多选答案越界] ${ans}, 选项${opts.length}个`); });
        }
        if (type === 'judge') {
            const a = String(ans || '').trim();
            if (a !== '正确' && a !== '错误') problems.push(`${id} [判断题答案异常] "${a}" q=${String(q.question).slice(0, 35)}`);
        }
        // 题干疑似嵌入选项：题干包含 >=2 个选项文本（长度>=2）
        if (type !== 'judge' && String(q.question || '').length > 0) {
            const qtext = String(q.question);
            let hit = 0;
            opts.forEach(o => { const t = String(o).trim(); if (t.length >= 2 && qtext.includes(t)) hit++; });
            if (hit >= 2) problems.push(`${id} [题干疑似嵌入选项] 命中${hit}个选项文本 | ${qtext.slice(0, 70)}`);
        }
        if (!q.explanation || !String(q.explanation).trim()) problems.push(`${id} [无解析]`);
    });
});

out('===== 第1部分：数据校验 =====');
out(`题库总题数: ${grandTotal}`);
files.forEach(f => out(`  ${f}: ${fileStats[f] || 0} 题`));
const cat = {};
problems.forEach(p => { const m = p.match(/\[(.*?)\]/); const k = m ? m[1] : '其他'; cat[k] = (cat[k] || 0) + 1; });
out(`问题总数: ${problems.length}`);
out('问题分类统计:');
Object.entries(cat).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => out(`  ${k}: ${v}`));
out('--- 数据问题明细（全部）---');
problems.forEach(p => out(p));

// ============ 第 2 部分：判分逻辑仿真（用 index.html 的真实实现） ============
out('');
out('===== 第2部分：判分逻辑仿真 =====');
const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
const jsBlocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const js = jsBlocks[jsBlocks.length - 1];
function extractFn(name) {
    const start = js.indexOf('function ' + name);
    if (start < 0) throw new Error('未找到函数 ' + name);
    let i = js.indexOf('{', start), depth = 0;
    for (; i < js.length; i++) {
        if (js[i] === '{') depth++;
        else if (js[i] === '}') { depth--; if (depth === 0) return js.slice(start, i + 1); }
    }
    throw new Error('函数 ' + name + ' 括号不平衡');
}
const isAnswerCorrect = new Function(extractFn('isAnswerCorrect') + '\n; return isAnswerCorrect;')();
out('已提取 index.html 真实 isAnswerCorrect 函数');

let simTotal = 0, simFail = 0;
const simFailures = [];
files.forEach(f => {
    const p = path.join(dir, 'banks', f);
    if (!fs.existsSync(p)) return;
    const qs = [];
    walkQuestions(readJson(f), qs);
    qs.forEach((q, i) => {
        const id = `${f}#${i + 1}`;
        const type = q.type;
        const opts = Array.isArray(q.options) ? q.options : [];
        if (type === 'multiple') {
            const ans = normMultiAns(q.answer);
            if (typeof ans !== 'string' || !ans) return;
            const qq = Object.assign({}, q, { answer: ans });
            const letters = ans.split('|').map(t => t.trim()).filter(Boolean);
            if (!letters.length) return;
            simTotal++;
            const full = letters.join('|');
            if (!isAnswerCorrect(qq, full)) { simFail++; simFailures.push(`${id} [多选] 全选应判对但为错 ans=${ans}`); }
            // 漏选一个：若剩余仍>=1个字母，应判错
            if (letters.length >= 2) {
                const drop = letters.slice(0, -1).join('|');
                if (isAnswerCorrect(qq, drop)) { simFail++; simFailures.push(`${id} [多选] 漏选应判错但为对 ans=${ans} drop=${drop}`); }
            }
            // 多选一个（若还有空余字母）
            if (letters.length < opts.length) {
                let extra = null;
                for (let li = 0; li < opts.length; li++) { const L = String.fromCharCode(65 + li); if (!letters.includes(L)) { extra = L; break; } }
                if (extra) {
                    if (isAnswerCorrect(qq, full + '|' + extra)) { simFail++; simFailures.push(`${id} [多选] 多选应判错但为对 ans=${ans} extra=${extra}`); }
                }
            }
        } else if (type === 'judge') {
            const ans = normJudgeAns(q.answer);
            if (typeof ans !== 'string' || !ans) return;
            simTotal++;
            const qq = Object.assign({}, q, { answer: ans });
            if (!isAnswerCorrect(qq, ans)) { simFail++; simFailures.push(`${id} [判断] 答对答案应判对但为错 ans="${ans}"`); }
        } else if (type === 'single') {
            const a = String(q.answer || '').trim();
            if (/^[A-D]$/.test(a)) {
                simTotal++;
                if (!isAnswerCorrect(q, a)) { simFail++; simFailures.push(`${id} [单选] 字母答案自评应判对但为错 ans=${a}`); }
            } else if (a) {
                const clean = stripPrefix(a);
                let found = null;
                for (let oi = 0; oi < opts.length; oi++) {
                    if (stripPrefix(opts[oi]) === clean || String(opts[oi]).trim() === a) { found = String.fromCharCode(65 + oi); break; }
                }
                if (found) {
                    simTotal++;
                    if (!isAnswerCorrect(q, found)) { simFail++; simFailures.push(`${id} [单选] 文字答案映射为${found}后应判对但为错 ans="${a.slice(0, 25)}"`); }
                } else {
                    simTotal++;
                    simFail++;
                    simFailures.push(`${id} [单选-不可解] 文字答案匹配不到任何选项，用户无法答对 ans="${a.slice(0, 30)}"`);
                }
            }
        }
    });
});
out(`仿真题数: ${simTotal}, 失败: ${simFail}`);
simFailures.slice(0, 400).forEach(s => out('SIMFAIL ' + s));
if (simFailures.length > 400) out(`... 其余 ${simFailures.length - 400} 条省略`);

fs.writeFileSync(path.join(dir, '_smoke_scan_results.txt'), OUT.join('\n'), 'utf8');
console.log(`完成: 数据问题 ${problems.length} 个, 仿真失败 ${simFail} 个`);
console.log('分类统计: ' + JSON.stringify(cat));
console.log('结果已写入 _smoke_scan_results.txt');
