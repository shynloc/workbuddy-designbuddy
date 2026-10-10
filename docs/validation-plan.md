---
title: DesignBuddy Pre-development Validation Plan
status: DRAFT
last_updated: 2026-10-10
---

# 开发前验证计划

**目的**：用真实的 WorkBuddy 环境回答 [`open-questions.md`](open-questions.md) 中的平台问题，把 [`runtime-capabilities.md`](runtime-capabilities.md) 中的 `TO TEST` 项转为 `OBSERVED`（或得出否定结论）。验证完成之前，不在代码中用猜测替代这些答案。

## 1. 方法

### 测试载体

为了在 DesignBuddy 主体开发之前单独验证平台能力，准备以下几个最小的测试 Skill：

| 载体 | 用途 |
|---|---|
| `probe-skill` | 免费、私有或测试用的最小 Skill，包含一个能力探测脚本和若干 references/templates |
| `alpha-brand-system` / `beta-brand-system` | 两个手写的虚构品牌 Skill，用于测试调用和多品牌行为 |
| `paid-probe-skill` | 用于付费保护验证。如果平台允许，以最低价私有发布；或者使用平台提供的测试方式（见 PAID_SKILL_PROTECTION_VALIDATION.md） |

### 测试环境矩阵

| 环境 | 说明 |
|---|---|
| macOS（Apple Silicon）WorkBuddy 客户端 | 必测 |
| Windows 11 WorkBuddy 客户端：没有 Python 的干净机器 | 必测 |
| Windows 11 WorkBuddy 客户端：已安装 Python | 必测 |

### 证据记录

每条用例都记录以下内容，存放在 `validation/records/<case-id>-<env>-<date>.md`：

- 日期、客户端版本、操作系统；
- 原始提示词；
- Agent 实际调用的工具和命令；
- 输出截图或文字；
- 结论（PASS / FAIL / PARTIAL / N/A）。

## 2. 用例

### 级别说明

- **B = Blocker**：必须有结论，才能冻结相关架构。
- **H = High**。
- **N = Normal**。

### V-EN 运行环境

| ID | 级别 | 步骤 | 期望 / 记录内容 |
|---|---|---|---|
| V-EN-01 | B | 在 probe-skill 中依次执行 `python3 -c "import sys;print(sys.version)"`、`python -c ...`、`py -3 -c ...`、`node -e "console.log(process.version)"` | 记录各环境中可用的解释器，以及 Windows Store 占位程序的表现 |
| V-EN-02 | B | 执行 `echo $SHELL`、`$PSVersionTable`、`ver` 等用来识别 shell 的命令 | 确认 Windows 和 macOS 上实际使用的 shell |
| V-EN-03 | H | 运行一个只用标准库的脚本，测试 zipfile、json、pathlib、中文路径、带空格路径 | 全部正常 |
| V-EN-04 | B | 脚本通过 `Path(__file__).parent` 读取同一 Skill 内的 templates 文件 | 记录能否读取（免费状态下） |
| V-EN-05 | B | 记录当前工作目录；在其中创建 `designbuddy-workspace/test.json`；关闭会话后重开，检查文件是否还在 | 确认写入位置和持久性 |
| V-EN-06 | N | 检测指定字体（如"思源黑体 / Source Han Sans"）是否已安装，两个平台分别测试 | 确认可行的检测方式；不允许全盘扫描 |
| V-EN-07 | H | 上传 Logo（PNG/SVG）、PDF、PPTX，请 Agent 读取主色、字体名、版式 | 记录抽取能力的边界 |

### V-PK 包结构

| ID | 级别 | 步骤 | 期望 |
|---|---|---|---|
| V-PK-01 | B | 用 WB-OPDK 的 `validate_skill.py` 校验一个生成好的 Brand Skill | 通过 |
| V-PK-02 | H | 在根目录放 `DESIGN.md`、`assets/`，分别测试本地安装和开放平台上传解析 | 记录是否被拒绝或被忽略 |
| V-PK-03 | N | 在 frontmatter 中填写 `category: design`，查看开放平台表单的可选值 | 确认合法的可选值 |
| V-PK-04 | H | 分别安装 1MB、5MB、20MB 的 Skill 包，以及包含 200 个文件的包 | 记录上限 |

### V-IN 生成与安装

| ID | 级别 | 步骤 | 期望 |
|---|---|---|---|
| V-IN-01 | B | 在 probe-skill 中让 Agent 把完整的 `alpha-brand-system/` 写到 Workspace | 文件完整，编码正确 |
| V-IN-02 | B | 检查运行时 Agent 的可用工具中是否有安装或创建 Skill 的工具（让 Agent 列出自己的工具） | 记录工具名和参数 |
| V-IN-03 | B | 在 probe-skill 中指示调用内置 Skill Creator："把位于 X 的已有 Skill 原样安装" | 安装成功；**逐个文件比对内容是否被改写** |
| V-IN-04 | B | 用户手动发送"请安装位于 X 的 Skill" | 记录是否走原生安装、是否原样安装 |
| V-IN-05 | N | （仅记录可行性，不作为主路径）把 Skill 复制到 WorkBuddy 本地的 Skill 目录 | 记录能否被识别，以及需要什么权限 |
| V-IN-06 | H | 查找客户端是否有本地导入 ZIP 的入口 | 记录入口位置和操作步骤，用于制作 fallback 图文指引 |
| V-IN-07 | H | 安装 alpha 1.0.0 后，再安装 1.1.0 | 记录是覆盖、并存还是报错 |
| V-IN-08 | H | 安装后在当前会话和新会话中分别触发 | 记录生效时机 |

### V-RT 运行时行为

| ID | 级别 | 步骤 | 期望 |
|---|---|---|---|
| V-RT-01 | B | "给 Alpha 做一份 5 页的融资 PPT" | 触发 alpha；按路由读取了 ppt.md 等 references |
| V-RT-02 | H | 检查 Agent 是否按 Draft → QA → Fix → Final 执行 | 输出中有 QA 报告 |
| V-RT-03 | B | 10 条品牌明确的提示词（包括使用别名、英文名的情况） | 命中率 ≥ 90% |
| V-RT-04 | B | 10 条无品牌线索的设计请求 | 误套用率 ≤ 5%；被调用时先询问用户 |
| V-RT-05 | N | 分别设置 `disable-model-invocation: true` 和 `user-invocable: false` | 记录实际行为 |
| V-RT-06 | H | 给出 PPT 内容，只要求套用品牌 | 不改写业务内容 |
| V-RT-07 | B | 卸载 probe-skill 或 DesignBuddy 后使用 alpha | 正常工作 |
| V-RT-08 | H | 无 Python 的 Windows 环境下运行 alpha 的 QA | Agent 兜底完成 QA，并标注 UNVALIDATED |

### V-MB 多品牌

前提：同时安装 Alpha 和 Beta 两个 Brand Skill。

| ID | 级别 | 提示词 | 期望 |
|---|---|---|---|
| V-MB-01 | B | "做一份 PPT。" | 不随机选品牌；先询问用户，或不套用任何品牌 |
| V-MB-02 | B | "给 Alpha 做一份 PPT。" | 只使用 Alpha |
| V-MB-03 | B | "把 Beta 的文档改成 Alpha 风格。" | 识别出 source = Beta、target = Alpha；输出只遵循 Alpha |
| V-MB-04 | H | 同一会话先做 Alpha 的物料，再说"再做一张海报" | 可以沿用 Alpha，但需在回复中声明使用的是 Alpha |
| V-MB-05 | H | Alpha 和 Beta 的别名有部分重叠时 | 先询问用户 |
| V-MB-06 | N | 让 Alpha Skill 列出其他已安装的 Skill | 记录能否做到（架构不依赖这个能力） |

### V-OF Office 模板（Advanced）

| ID | 级别 | 步骤 | 期望 |
|---|---|---|---|
| V-OF-01 | H | Skill 包内放入 .potx/.dotx/.xltx，安装后检查文件哈希 | 文件完整 |
| V-OF-02 | H | 在 macOS Office 中打开，并基于模板新建文档 | 主题色、字体、母版正确 |
| V-OF-03 | H | 在 Windows Office 中执行同样的操作 | 同上 |
| V-OF-04 | N | 在 WPS 中执行同样的操作 | 记录兼容性 |
| V-OF-05 | H | 让 Brand Skill 基于模板生成 PPT | Agent 能找到并使用模板 |

### V-TK Token 成本

| ID | 级别 | 步骤 | 期望 |
|---|---|---|---|
| V-TK-01 | H | 对比安装 Brand Skill 前后，一次简单对话的 token 用量（如果平台可以查看） | references 不会被整体注入 |
| V-TK-02 | H | 测量单次 PPT 任务、海报任务的上下文加载量 | 不超过 PRD 中 NFR-03 的预算 |

### V-PP 付费保护

见 [`PAID_SKILL_PROTECTION_VALIDATION.md`](PAID_SKILL_PROTECTION_VALIDATION.md)，用例编号 V-PP-01..06。

## 3. 执行顺序

1. **第 1 轮（Blocker）**：先确认基础能力，再测安装，最后测调用行为。
   - 基础能力：V-EN-01/02/04/05、V-PK-01；
   - 安装：V-IN-01/02/03/04；
   - 调用行为：V-RT-01/03/04/07、V-MB-01/02/03；
   - 付费保护：V-PP-03/04/05。
2. **第 2 轮（High）**：其余 High 级用例。
3. **第 3 轮（Normal）**：边开发边补。

第 1 轮完成后，更新架构文档的状态，并冻结 H1–H5 的选择策略和编译器方案。

## 4. 退出标准

- 所有 Blocker 用例都有结论。
- runtime-capabilities.md 中没有任何"主路径依赖但仍为 TO TEST"的条目。
- 对于结论为 FAIL 的能力，架构中已经写明降级方案。
