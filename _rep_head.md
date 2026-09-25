# 刷题小能手 · 真机冒烟检查报告（线上版 v20260924fix13）

- **检查对象**：[https://lee123gh.github.io/shuati-xiaonengshou/](https://lee123gh.github.io/shuati-xiaonengshou/)
- **检查基准**：线上最终版 **v20260924fix13**，对应仓库 commit `3322df8819`（检查期间作者连续推送 8 个提交，基准已切换为最终版；截至报告生成，该版本仍为线上最新）
- **快照校验**：8 个线上文件（index.html + 7 个题库）全部下载并通过 git-blob SHA-1 一致性校验（见附录 A）
- **题量**：7 个题库共 20106 题（lifeguard 2290 / lifeguard_senior 2290 / instructor 4926 / instructor_senior 4233 / order_lifeguard 1480 / order_instructor 2300 / order_instructor_senior 2587）

---

## 一、结论速览

| 检查项 | 结果 |
|---|---|
| 1. 判分逻辑全量仿真（20106 题，直接提取线上 index.html 的真实判分函数运行） | ✅ **0 失败**，判分逻辑无 bug |
| 2. fix13 的 24 处答案修正复核 | ✅ **24/24 全部正确**（均与解析一致） |
| 3. 剩余题目数据问题 | ⚠️ **约 172 处**：A 类 96 处（题干混入选项/解析/页面残留）+ B 类 76 处（题干尾部混入旧选项碎片，判断题为主）。不影响判分，但严重影响题目可读性与学习体验 |
| 4. 代码/体验问题 | ⚠️ **7 项**（C1 优先级最高：超时后取消交卷会每秒重复弹确认框） |
| 5. 安全提示 | ⚠️ 本地 git remote URL 内嵌明文访问令牌（C7，建议尽快吊销） |

---

## 二、fix13 修复内容复核（24 处，全部正确）

fix13（commit `3322df8819`）共修改 8 个文件、29 行：**24 处答案修正 + lifeguard.json / lifeguard_senior.json 两个文件首行补 BOM + index.html 3 处版本号**。逐条核对"新答案是否与解析一致"：

| 文件 | 题号 | 改动 | 题眼 | 复核结论 |
|---|---|---|---|---|
| instructor.json | 267 | B→C | 强调游泳安全的"重要性" | ✅ 与解析一致 |
| instructor.json | 1664 | B→A | 体育健身消费引导"不包括"项 | ✅ 与解析一致 |
| instructor.json | 3180 | A→D | 游泳锻炼"首先考虑"安全 | ✅ 与解析一致 |
| instructor.json | 3601 | B→C | 指导员定义"确保安全" | ✅ 与解析一致 |
| instructor.json | 4893 | B→A | 同 1664（重复题） | ✅ 与解析一致 |
| instructor_senior.json | 276 | B→C | 同 267 | ✅ 与解析一致 |
| instructor_senior.json | 1626 | B→A | 同 1664 | ✅ 与解析一致 |
| instructor_senior.json | 2565 | B→C | 同 3601 | ✅ 与解析一致 |
| lifeguard.json | 108 | D→A | 违约责任"不包括"罚款 | ✅（解析里"赔礼道歉"字样与新选项不对应，建议顺带改为"罚款"，小瑕疵） |
| lifeguard.json | 1234 | A→D | 游泳锻炼"首先考虑"安全 | ✅ 与解析一致 |
| lifeguard.json | 2247 | A→B | 警示牌是"必须"的标志牌 | ✅ 与解析一致 |
| lifeguard_senior.json | 108 | D→A | 同 lifeguard #108 | ✅ 与解析一致 |
| lifeguard_senior.json | 1234 | A→D | 同 lifeguard #1234 | ✅ 与解析一致 |
| lifeguard_senior.json | 2247 | A→B | 同 lifeguard #2247 | ✅ 与解析一致 |
| order_instructor.json | 41 | B→C | 同 3601 | ✅ 与解析一致 |
| order_instructor.json | 669 | B→C | 同 267 | ✅ 与解析一致 |
| order_instructor.json | 2229 | B→A | 同 1664 | ✅ 与解析一致 |
| order_instructor_senior.json | 41 | B→C | 同 3601 | ✅ 与解析一致 |
| order_instructor_senior.json | 653 | B→C | 同 267 | ✅ 与解析一致 |
| order_lifeguard.json | 475 | B→D | 观察区域划分（针对浅水场所） | ✅ 与解析一致 |
| order_lifeguard.json | 637 | B→D | 直接赴救 6 项技术环节 | ✅ 与解析一致 |
| order_lifeguard.json | 1204 | A→D | 同 1234 | ✅ 与解析一致 |
| order_lifeguard.json | 1321 | A→C | 救生杆主要作用 | ✅ 与解析一致 |
| order_lifeguard.json | 1444 | A→B | 违约责任"不包括"赔礼道歉 | ✅（选项 B 文字"赔礼道"缺字，建议补成"赔礼道歉"） |

> 另：lifeguard.json / lifeguard_senior.json 首行补加 UTF-8 BOM（对前端无害，`response.json()` 会按规范自行剥离）；
> index.html 3 处版本号 fix12→fix13（页面注释、`BANK_VERSION`、版本显示）。
> **结论：fix13 的 24 处修正全部验证正确，未引入新问题。**

---

## 三、A 类：96 处题干混入残留（主清单）
