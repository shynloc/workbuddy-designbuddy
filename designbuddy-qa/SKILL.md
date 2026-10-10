---
name: designbuddy-qa
display_name: "DesignBuddy QA（测试候选版）"
display_name_en: "DesignBuddy QA (Test Candidate)"
description: "DesignBuddy 的 QA 测试候选版（v0.1.3），不是商业正式版。当用户说“DesignBuddy QA”、“运行全量本地验收测试”、“QA RUN ALL”，或明确要求用 DesignBuddy QA 为某个品牌建立品牌设计系统、编译 Brand Skill、导出 Portable Design System 时使用。其他场景不要使用。"
description_zh: "DesignBuddy QA 测试候选版：品牌系统编译器（Brand IR → Brand Skill + Portable Design System + Preview）与内置全量验收测试。"
description_en: "DesignBuddy QA test candidate: brand system compiler (Brand IR → Brand Skill + Portable Design System + Preview) with a built-in acceptance test runner."
version: 0.1.3
author: "DesignBuddy"
user-invocable: true
disable-model-invocation: false
---

# DesignBuddy QA v0.1.3（测试候选版）

这是 DesignBuddy 的**测试候选版**，用于在真实 WorkBuddy 中验证功能，**不是商业正式版**。它包含两部分：

- **真实的品牌系统编译器**：品牌资料 → Brand IR（JSON，唯一事实来源）→ WorkBuddy Brand Skill、Portable Design System、Preview。
- **内置验收测试**：QA RUN ALL。

所有判断都由 `scripts/` 中的确定性程序完成。**不要凭印象罗列检查结果，也不要手写或临时设计模板和生成器。**

## 0. 先找到运行方式（每次会话只做一次）

1. 确定本 Skill 目录的绝对路径（即本文件所在的目录），下文记作 `<SKILL>`。
2. 依次尝试下面的命令，选第一个能输出 JSON 的，下文记作 `<PY>`：
   - `python3 "<SKILL>/scripts/designbuddy.py" version`
   - `python "<SKILL>/scripts/designbuddy.py" version`
   - `py -3 "<SKILL>/scripts/designbuddy.py" version`
3. 如果都失败：**不要安装任何东西，也不要谎报 PASS**。按 @references/qa-protocol.md 第 6 节输出 BLOCKED 报告。

所有命令都输出一个 JSON 对象。退出码含义：0 成功，1 校验或 QA 未通过，2 输入错误，3 环境不支持。

## 1. 入口 A：QA RUN ALL（用户说"DesignBuddy QA：运行全量本地验收测试"）

按 @references/qa-protocol.md 执行。核心命令：

```
<PY> "<SKILL>/scripts/designbuddy.py" run-all --out "<用户可见的输出目录>"
```

Agent 和人工测试项用 `record` 命令回填，不能改写脚本用例的结果。

全部回填完成后，最后执行 `finalize --run "<RUN>"`，对 agent-notes 做脱敏并重新检查。

## 2. 入口 B：为品牌建立设计系统（真实功能）

按 @references/design-workflow.md 执行。输入格式和命令见 @references/compiler-contract.md 。

```
init → status → gate G1..G4 → preview → gate G5 → gate G6 → build → 安装交接
```

## 3. 安装交接

按 @references/installation-handoff.md 执行：

- 安装任何 Skill 之前，必须向用户展示摘要并取得**明确确认**。
- 依次尝试 H1（原生工具）、H2（Skill Creator 原样安装）、H3（用户发一句话触发）、H4（ZIP 导入）。
- **禁止 H5**：不得直接写入 WorkBuddy 内部的 Skill 目录。

## 4. 安全边界

见 @references/safety.md 。要点：

- 不联网；
- 不读取与任务无关的本地文件；
- 不覆盖用户已有的 Skill；
- 不打包字体文件或未授权的素材；
- 不复制参考品牌的资产；
- 不发布、不收费、不操作开放平台后台。

## 5. 结果表述

- `PASS` 必须有实际执行证据。
- 做不到的写 `BLOCKED` 或 `NOT_TESTED`，不能写成 PASS。
- 本地未加密安装的测试结果，**不能**代表市场付费加密版的行为。
