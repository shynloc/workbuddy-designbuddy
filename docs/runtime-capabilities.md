---
title: WorkBuddy Runtime Capabilities Ledger (DesignBuddy)
status: LIVING DOCUMENT
last_updated: 2026-10-10
---

# Runtime Capabilities Ledger

这份台账记录 DesignBuddy 依赖的每一项 WorkBuddy 平台和运行时能力，以及每项能力当前的**证据等级**。

**规则：**

- 代码和文档中引用某项平台能力时，必须先在这里有对应条目。
- 状态为 `UNVERIFIED` 或 `TO TEST` 的能力，不得在代码中当作确定事实使用。必须通过能力探测，或者提供降级方案。
- 证据发生变化时，更新本表，并在页尾的变更记录里登记。

## 证据等级

| 等级 | 含义 |
|---|---|
| `OFFICIAL` | 官方文档明确规定 |
| `OBSERVED` | 真实环境实测 |
| `DERIVED` | 基于上述信息推导出的工程判断 |
| `EXPERIMENTAL` | 已设计，未充分验证 |
| `UNVERIFIED` / `TO TEST` | 无证据，待验证 |
| `STALE` | 上游已变化，待复核 |

## A. Skill 包与开放平台

| # | 能力 | 状态 | 证据 / 来源 | 验证用例 |
|---|---|---|---|---|
| A1 | Skill 结构：`SKILL.md` 必须有；`references/`、`scripts/`、`templates/` 可选 | `OFFICIAL` | https://open.workbuddy.cn/docs/skill（WB-OPDK `10-skill/specification.md`，2026-10-07 核验） | — |
| A2 | frontmatter 必填字段：description、description_zh、description_en、version、author；可选字段：name、allowed-tools、disable-model-invocation、user-invocable；官方示例中还出现 display_name、display_name_en、category | `OFFICIAL` | 同上 | V-PK-03 |
| A3 | 在 SKILL.md 中用 `@references/xxx.md` 引用 references | `OFFICIAL` | 同上 | — |
| A4 | scripts 由 AI 通过 Bash 执行 | `OFFICIAL`（措辞为"Bash"） | 同上。Windows 上实际使用什么 shell 未知，见 B2 | V-EN-02 |
| A5 | 符合上述结构的 ZIP 能被开放平台解析，并进入审核 | `OBSERVED` | WB-OPDK `95-validation/wechat-article-publishing-skill.md` | — |
| A6 | 根目录可以有官方结构以外的文件或目录（DESIGN.md、assets/ 等） | `UNVERIFIED` | 发布包实测时去掉了 README/CHANGELOG | V-PK-02 |
| A7 | Skill 包的大小、文件数上限，以及能否包含二进制文件（字体、.potx 等） | `UNVERIFIED` | — | V-PK-04, V-OF-01 |
| A8 | `category` 字段的可选值是否包含 `design` | `UNVERIFIED` | 开放平台前端文案中，专家类目里出现过 design（"设计"）选项；Skill 的 category 是否相同未确认 | V-PK-03 |

## B. 运行环境

| # | 能力 | 状态 | 证据 | 验证用例 |
|---|---|---|---|---|
| B1 | WorkBuddy 同时提供 macOS 和 Windows 客户端 | `OBSERVED` | 产品负责人提供 | — |
| B2 | Windows 上执行命令所用的 shell（bash / Git Bash / PowerShell / cmd） | `UNVERIFIED` | — | V-EN-02 |
| B3 | 用户机器上是否有可用的 `python3` / `python` / `py` / `node` | `UNVERIFIED`（因机器而异） | 必须在运行时探测 | V-EN-01, V-EN-03 |
| B4 | Skill 运行时的当前工作目录，以及能否在其中写入文件 | `UNVERIFIED` | — | V-EN-05 |
| B5 | Skill 能否读取自身包内的 references/scripts/templates（Agent 读取，或脚本按相对路径读取） | `UNVERIFIED`（付费状态下尤其不确定） | — | V-PP-04, V-EN-04 |
| B6 | 能否检测某个字体是否已安装（只查询，不扫描全盘） | `UNVERIFIED` | — | V-EN-06 |
| B7 | Agent 能否读取用户上传的图片、PDF、PPT 中的视觉信息 | `UNVERIFIED`（依赖 WorkBuddy 的模型和工具） | — | V-EN-07 |

## C. Skill 生成与安装

| # | 能力 | 状态 | 证据 | 验证用例 |
|---|---|---|---|---|
| C1 | WorkBuddy 能在对话中创建并安装 Skill | `OBSERVED` | 产品负责人实测（2026-10），使用内置的 Skill Creator | — |
| C2 | WorkBuddy 内置 Skill Creator 这个 Skill | `OBSERVED` | 同上 | — |
| C3 | 第三方 Skill（DesignBuddy）运行时，能把另一个 Skill 的完整文件写到磁盘 | `TO TEST` | 依赖 B4 | V-IN-01 |
| C4 | H1：Agent 有可直接调用的原生"安装 Skill"工具 | `TO TEST` | — | V-IN-02 |
| C5 | H2：第三方 Skill 引导调用 Skill Creator，原样安装已生成的 Skill（不改写内容） | `TO TEST` | — | V-IN-03 |
| C6 | H3：由用户发出一句指令，触发原生安装指定路径的 Skill | `TO TEST` | — | V-IN-04 |
| C7 | H4：通过 UI 手动导入 ZIP | `UNVERIFIED`（本地导入入口未确认） | 开放平台上传 ZIP 属于"发布"，与本地安装不同 | V-IN-06 |
| C8 | H5：直接写入 WorkBuddy 本地 Skill 目录后能被识别 | `TO TEST`（不优先） | — | V-IN-05 |
| C9 | 同名 Skill 的升级、覆盖行为 | `TO TEST` | — | V-IN-07 |
| C10 | 安装后无需重启即可在当前或新会话中生效 | `TO TEST` | — | V-IN-08 |

## D. 调用行为

| # | 能力 | 状态 | 证据 | 验证用例 |
|---|---|---|---|---|
| D1 | 模型根据 description 自动调用 Skill | `OFFICIAL`（文档说明 description 用于判断何时激活）；命中质量 `TO TEST` | Skill 官方文档 | V-RT-03, V-RT-04 |
| D2 | `disable-model-invocation`、`user-invocable` 的实际效果 | `OFFICIAL`（语义）/ `TO TEST`（行为） | 同上 | V-RT-05 |
| D3 | 多个 Brand Skill 同时安装时的调用与消歧 | `TO TEST` | — | V-MB-01..05 |
| D4 | 一个 Skill 能否得知其他已安装的 Skill | `UNVERIFIED` | 架构不依赖此能力（D-07） | V-MB-06 |
| D5 | 卸载 DesignBuddy 后，Brand Skill 仍然正常工作 | `TO TEST` | — | V-RT-07 |
| D6 | references 按需加载（而不是安装时全部注入上下文） | `UNVERIFIED` | 决定 token 预算是否成立 | V-TK-01 |

## E. 付费与保护

| # | 能力 | 状态 | 证据 | 验证用例 |
|---|---|---|---|---|
| E1 | 技能和专家可以设置付费：一次性买断或按月订阅 | `OBSERVED`（开放平台前端文案） | open.workbuddy.cn 页面 i18n 文案（2026-10-10 抓取）："发布付费技能 · 支持一次性买断或按月订阅" | — |
| E2 | 价格为 1–9999 的整数；付费方式上架后不可更改；改价次数每年有限 | `OBSERVED`（前端文案） | 同上 | 提交时复核 |
| E3 | 开通收款的条件：已认证、无违规、已有 ≥1 个审核通过的技能或专家 | `OBSERVED`（前端文案） | 同上；产品负责人满足这些条件 | — |
| E4 | 费用：内测期间平台服务费 1%，微信支付手续费 0.6% | `OBSERVED`（前端文案，可能变化） | 同上 | 提交时复核 |
| E5 | UI 显示"付费能力必须加密，不可关闭"，以及"一定技术防护但无法完全避免泄漏，且用户不可使用自定义模式调用" | `OBSERVED`（仅 UI 文案） | 同上 | — |
| E6 | 加密或保护的实际效果，以及在哪一层实现 | `UNVERIFIED` | — | V-PP-01..06 |
| E7 | "自定义模式"的含义，以及它对 DesignBuddy 交互的影响 | `UNVERIFIED` | — | V-PP-05 |

## F. 外部标准

| # | 内容 | 状态 | 说明 |
|---|---|---|---|
| F1 | W3C DTCG Design Tokens 格式 | `DERIVED` | 社区组规范，用于 tokens.json |
| F2 | DESIGN.md（Google Labs / Stitch） | `DERIVED` | 开放规范，**不是正式标准**；需跟踪上游 |
| F3 | WCAG 2.x 对比度阈值（4.5:1 / 3:1） | `OFFICIAL`（W3C） | — |

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-10-10 | 初版。C1/C2 由产品负责人实测标记为 OBSERVED；E1–E5 来自开放平台前端文案 |
