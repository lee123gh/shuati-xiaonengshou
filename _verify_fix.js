// 临时验证脚本：验证 index_fixed.html 的三项严重问题修复（验证后可删除）
const fs = require('fs');
const path = require('path');

const dir = __dirname;
const html = fs.readFileSync(path.join(dir, 'index_fixed.html'), 'utf8');
const js = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).pop();

// 从修复文件中直接提取真实函数实现
function extractFn(name) {
    const start = js.indexOf('function ' + name);
    if (start < 0) throw new Error('未找到函数 ' + name);
    // 从函数名开始，做花括号配对找到函数结尾
    let i = js.indexOf('{', start), depth = 0;
    for (; i < js.length; i++) {
        if (js[i] === '{') depth++;
        else if (js[i] === '}') { depth--; if (depth === 0) return js.slice(start, i + 1); }
    }
    throw new Error('函数 ' + name + ' 括号不平衡');
}

const code = extractFn('parseMulti') + '\n' + extractFn('normJudge') + '\n' + extractFn('isAnswerCorrect') + '\n; return { parseMulti, normJudge, isAnswerCorrect };';
const { parseMulti, normJudge, isAnswerCorrect } = new Function(code)();

let allPass = true;
function check(label, cond) {
    console.log((cond ? 'PASS' : 'FAIL') + ' - ' + label);
    if (!cond) allPass = false;
}

// 测试1: 多选题 "ABD" 连写格式（题库真实格式）
check('多选 答案ABD + 作答A|B|D => 判对', isAnswerCorrect({ type: 'multiple', answer: 'ABD' }, 'A|B|D') === true);
check('多选 答案ABD + 作答A|B|D|C => 判错', isAnswerCorrect({ type: 'multiple', answer: 'ABD' }, 'A|B|D|C') === false);
check('多选 答案ABD + 漏选A|B => 判错', isAnswerCorrect({ type: 'multiple', answer: 'ABD' }, 'A|B') === false);
check('多选 答案AB|D + 乱序D|A|B => 判对(顺序无关)', isAnswerCorrect({ type: 'multiple', answer: 'AB|D' }, 'D|A|B') === true);

// 测试2: 判断题 A/B 历史格式兼容
check('判断 答案B + 作答错误 => 判对', isAnswerCorrect({ type: 'judge', answer: 'B' }, '错误') === true);
check('判断 答案A + 作答正确 => 判对', isAnswerCorrect({ type: 'judge', answer: 'A' }, '正确') === true);
check('判断 答案正确 + 作答正确 => 判对', isAnswerCorrect({ type: 'judge', answer: '正确' }, '正确') === true);
check('判断 答案B + 作答正确 => 判错', isAnswerCorrect({ type: 'judge', answer: 'B' }, '正确') === false);

// 测试3: 按钮事件修复（静态检查）
check('无残留 .onclick = prevSequentialQuestion', !js.includes('.onclick = prevSequentialQuestion'));
check('无残留 .onclick = nextSequentialQuestion', !js.includes('.onclick = nextSequentialQuestion'));

// 全量扫描真实题库：88 道多选 + A/B 判断题
const banks = ['lifeguard.json', 'lifeguard_senior.json', 'instructor.json', 'instructor_senior.json',
    'order_lifeguard.json', 'order_instructor.json', 'order_instructor_senior.json'];
let multiTotal = 0, multiOK = 0, judgeAB = 0, judgeABOK = 0;
function walk(o, out) {
    if (Array.isArray(o)) o.forEach(x => walk(x, out));
    else if (o && typeof o === 'object') {
        if ('question' in o && ('answer' in o || 'options' in o)) out.push(o);
        else Object.values(o).forEach(x => walk(x, out));
    }
}
banks.forEach(b => {
    const p = path.join(dir, 'banks', b);
    if (!fs.existsSync(p)) return;
    const flat = [];
    walk(JSON.parse(fs.readFileSync(p, 'utf8')), flat);
    flat.forEach(q => {
        const type = (q.type === 'multiple') ? 'multiple' : ((q.type === 'judge') ? 'judge' : null);
        if (type === 'multiple' && q.answer) {
            multiTotal++;
            const letters = parseMulti(q.answer);
            const full = letters.join('|');
            const dropped = letters.slice(0, -1).join('|'); // 漏选一项
            const exactOK = isAnswerCorrect(q, full);
            const missingRejected = letters.length < 2 ? true : !isAnswerCorrect(q, dropped);
            if (exactOK && missingRejected) multiOK++;
        }
        if (type === 'judge' && (q.answer === 'A' || q.answer === 'B')) {
            judgeAB++;
            const expected = q.answer === 'A' ? '正确' : '错误';
            if (isAnswerCorrect(q, expected)) judgeABOK++;
        }
    });
});
console.log('全量扫描: 多选 ' + multiOK + '/' + multiTotal + ' 通过; A/B格式判断题 ' + judgeABOK + '/' + judgeAB + ' 兼容通过');
check('全部多选判分正确', multiOK === multiTotal);
check('全部A/B判断题兼容', judgeABOK === judgeAB);

console.log(allPass ? '=== 全部自测通过 ===' : '=== 存在失败项 ===');
process.exit(allPass ? 0 : 1);
