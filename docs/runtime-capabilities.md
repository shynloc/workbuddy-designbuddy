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
| `UNVERIFIED` | 无证据，待验证。下表中的"TO TEST"表示已经安排了验证用例，证据等级仍然是 UNVERIFIED |
| `STALE` | 上游已变化，待复核 |

> **代表性规则**：单次实验结果写成 `OBSERVED（条件：系统 / 来源 / 是否加密 / 账号类型）`，不得上升为通用平台保证。未加密形态的结果不能代表加密形态。测试结果原文见 [`runtime-validation-results.md`](runtime-validation-results.md)。

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
| A8 | `category` 字段的可选值是否包含 `design` | `UNVERIFIED` | 开放平台前端文案中，专家类目里出现过 design（"设计"）选项；Skill 的 category 是否相同未确认。Probe 中暂不填写 category | V-PK-03 |
| A9 | `@references/x.md` 后紧跟中文标点时，WorkBuddy 能否正确解析路径 | `UNVERIFIED` | WB-OPDK 校验器会误判（`OBSERVED`，2026-10-10 本地预检）。编译器规定引用后必须紧跟空白字符（DERIVED） | — |

## B. 运行环境

| # | 能力 | 状态 | 证据 | 验证用例 |
|---|---|---|---|---|
| B1 | WorkBuddy 同时提供 macOS 和 Windows 客户端 | `OBSERVED` | 产品负责人提供 | — |
| B2 | Windows 上执行命令所用的 shell（bash / Git Bash / PowerShell / cmd） | `UNVERIFIED` | — | V-EN-02 |
| B3 | 用户机器上是否有可用的 `python3` / `python` / `py` / `node` | `UNVERIFIED`（因机器而异） | 必须在运行时探测 | V-EN-01, V-EN-03 |
| B4 | Skill 运行时的当前工作目录，以及能否在其中写入文件 | `UNVERIFIED` | — | V-EN-05 |
| B5 | Skill 能否读取自身包内的 references/scripts/templates（Agent 读取，或脚本按相对路径读取） | `UNVERIFIED`（本地未加密 → T-ENV / T-PRO-L；加密 → T-PRO-M1/M2） | — | V-PP-03/04, V-EN-04 |
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
| C8 | H5：直接写入 WorkBuddy 本地 Skill 目录 | **不测试、不采用**（NOT APPROVED FOR V1，D-08） | 将来采用需产品负责人单独批准 | — |
| C9 | 同名 Skill 的升级、覆盖行为 | `TO TEST` | — | V-IN-07（T-INS-UP） |
| C11 | 安装后的产物与构建包逐字节一致（没有被 Skill Creator 等改写） | `TO TEST` | build-manifest + selfcheck | T-INS-H1..H4 |
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

三个概念分开记录：

- **Paid Skill**：销售机制；
- **Encrypted Skill**：平台的加密选项；
- **Source Protection**：实际保护效果。

| # | 能力 | 状态 | 证据 | 验证用例 |
|---|---|---|---|---|
| E1 | 技能和专家可以设置付费：一次性买断或按月订阅 | `OBSERVED`（开放平台前端文案） | open.workbuddy.cn 页面 i18n 文案（2026-10-10 抓取）："发布付费技能 · 支持一次性买断或按月订阅" | — |
| E2 | 价格为 1–9999 的整数；付费方式上架后不可更改；改价次数每年有限 | `OBSERVED`（前端文案） | 同上 | 提交时复核 |
| E3 | 开通收款的条件：已认证、无违规、已有 ≥1 个审核通过的技能或专家 | `OBSERVED`（前端文案） | 同上；产品负责人满足这些条件 | — |
| E4 | 费用：内测期间平台服务费 1%，微信支付手续费 0.6% | `OBSERVED`（前端文案，可能变化） | 同上 | 提交时复核 |
| E5 | UI 显示"付费能力必须加密，不可关闭"，以及"一定技术防护但无法完全避免泄漏，且用户不可使用自定义模式调用" | `OBSERVED`（仅 UI 文案） | 同上 | — |
| E6 | **Source Protection**：用户或其他 Agent 能否读取、复制、提取原始实现；保护在哪一层实现 | `UNVERIFIED` | — | V-PP-01/02/06 |
| E8 | 加密形态下：Agent 读取 references / 脚本执行 / 脚本读取资源 / 资源输出到工作区 / 生成器生成新文件 | `UNVERIFIED` | 决定 D-03 | V-PP-03/04/07/08（T-PRO-M1） |
| E9 | 开发者账号与普通购买者账号的行为是否一致 | `UNVERIFIED` | — | V-PP-09（T-PRO-M1 vs M2） |
| E7 | "自定义模式"的含义，以及它对 DesignBuddy 交互的影响 | `UNVERIFIED` | — | V-PP-05 |

## F. 外部标准

| # | 内容 | 状态 | 说明 |
|---|---|---|---|
| F1 | W3C DTCG Design Tokens 格式 | `DERIVED` | 社区组规范，用于 tokens.json |
| F2 | DESIGN.md（Google Labs / Stitch） | `DERIVED` | 开放规范，**不是正式标准**；需跟踪上游 |
| F3 | WCAG 2.x 对比度阈值（4.5:1 / 3:1） | `OFFICIAL`（W3C） | — |

## G. WorkBuddy 真机观察（QA 报告 qa-20261011-015550-2691，designbuddy-qa 0.1.0）

条件：Windows 11（10.0.26200）· WorkBuddy 5.7.7.0 · 本地安装 · 未付费 · 未加密 · 开发者账号 · 单次运行。

| # | 能力 | 状态 | 证据 |
|---|---|---|---|
| G1 | Skill 执行环境有可用的 `python3`（3.13.14），也有 `python` / `py` / `node` | `OBSERVED（Windows/5.7.7.0）` | environment.json、ENV-001/009 |
| G2 | Agent 的命令执行工具是 Bash（Git Bash，MSYSTEM 存在）；另有独立的 win32 命令工具 | `OBSERVED（Windows/5.7.7.0）` | ENV-009 |
| G3 | 用户级 Skill 安装目录：`<HOME>/.workbuddy/skills/<skill-name>/` | `OBSERVED` | environment.json 的 skill_root（已脱敏） |
| G4 | 安装时平台在 Skill 根目录写入 `_user_meta.json` | `OBSERVED` | PKG-005 证据 |
| G5 | 平台工具 `search_and_install_skills` 只能按名称安装技能市场中的 Skill，不接受本地 ZIP 或目录 → H1 对本地包不适用 | `OBSERVED` | INS-001 |
| G6 | 第三方 Skill 可以读取自身的 templates、执行自身脚本、向用户项目目录写文件（未加密形态） | `OBSERVED（未加密）` | PKG-007、PP-001、ENV-003/004 |
| G7 | ~~从本地 ZIP 安装的 Brand Skill 内容逐字节保持不变~~ | **作废**：第 2 轮证明 skill-creator 没有安装器，所以 v0.1.0 的 H2 安装很可能是 Agent 自己写入的（H5），不能作为平台能力的证据 | qa/history/FIX_REPORT-v0.1.1.md 与 qa/FIX_REPORT.md 第 4 节 |
| G8 | DesignBuddy 编译器在 Windows 和 Linux 上的产物逐文件一致 | `OBSERVED` | FIX_REPORT §1 |
| G11 | 内置 `skill-creator` 只提供创建和打包引导（init_skill.py / package_skill.py），没有安装执行器 | `OBSERVED（5.7.7/Win）` | INS-002（qa-20261011-025430-7c19） |
| G12 | 用户在对话中发送带路径的安装句，会被转给 `marketplace-skill-installer` → `search_and_install_skills`（只支持市场），无法安装本地 ZIP | `OBSERVED（5.7.7/Win）` | INS-003 |
| G13 | 平台能把本地 ZIP 装为 Skill（designbuddy-qa 本身被装上，平台写入了 `_user_meta.json`）；具体入口（附件 / UI 导入）待记录 | `OBSERVED`（结果）/ `UNVERIFIED`（入口） | PKG-008、INS-007（待测） |
| G14 | WorkBuddy 版本可以从安装目录下的 `resources/install-manifest.json`（appVersion）读取 | `OBSERVED（Win）` | ENV-007 |
| G15 | 客户端有专门的技能导入入口，可以从本地上传 Skill ZIP 并安装（H4） | `OBSERVED`（产品负责人实测，2026-10-11） | 产品负责人反馈 |
| G9 | 付费加密形态 | `UNVERIFIED` | PP-002/003 BLOCKED |
| G10 | macOS | `UNVERIFIED` | 未测 |

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-10-10 | 初版。C1/C2 由产品负责人实测标记为 OBSERVED；E1–E5 来自开放平台前端文案 |
| 2026-10-11 | 第 2 轮真机：新增 G11~G14；G7 作废（v0.1.0 的 H2 很可能是 H5） |
| 2026-10-11 | 新增 G 节：v0.1.0 QA 在 Windows / WorkBuddy 5.7.7.0 上的真机观察 |
| 2026-10-10 | R2：拆分 Paid / Encrypted / Source Protection 三个概念；新增 A9、C11、E8、E9；C8（H5）改为不测试、不采用；去掉独立的"TO TEST"等级（并入 UNVERIFIED） |
