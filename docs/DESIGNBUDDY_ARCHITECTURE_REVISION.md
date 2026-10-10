---
title: DesignBuddy Architecture Revision
doc_type: decision-record
revision: R2
status: DRAFT — R2 决策已由产品负责人确认；平台相关部分待 Probe 验证
last_updated: 2026-10-10
supersedes: 对话中的早期构想（"生成 ZIP 让用户手动安装"、"安装后全局继承"、"付费 Skill 必须加密"等表述）
---

# DesignBuddy 架构修订（R2）

本文是 DesignBuddy 的**架构决策记录**。它把产品负责人 2026-10-10 的补充要求整理为正式约束，并替代此前对话中的初步构想。

- 本文回答"为什么这样设计、边界在哪里"。
- [`architecture.md`](architecture.md) 回答"具体怎么实现"（文件结构、Schema、脚本接口）。
- [`PRD.md`](PRD.md) 回答"做什么、给谁、怎样算完成"。
- 平台事实的证据等级见 [`runtime-capabilities.md`](runtime-capabilities.md)，待验证项见 [`validation-plan.md`](validation-plan.md) 与 [`open-questions.md`](open-questions.md)。

## R2 决策记录（2026-10-10，产品负责人确认）

| 事项 | 决定 | 影响章节 |
|---|---|---|
| 付费保护的认知修正 | **ACCEPTED**。严格区分 Paid Skill（销售机制）、Encrypted Skill（平台加密选项）、Source Protection（实际防读取、防复制的效果）三个概念。对外统一称 Paid Skill | §0、§26 |
| D-01 / D-02：用 JSON 作为唯一事实来源 | **ACCEPTED**，附加三项要求：必须有 `schema_version`；必须实现数据校验（不宣称标准库支持完整的 JSON Schema 校验）；数据模型与导出格式分离 | §3、architecture.md §3 |
| D-03：完全现场生成 | **NOT APPROVED AS DEFAULT**，改为 **CONDITIONAL FALLBACK / PENDING VALIDATION**。默认架构保持"预置的确定性 Compiler + Brand IR → 构建" | §29、architecture.md §2 |
| H1–H4 | **APPROVED FOR TESTING** | §16 |
| H5（直接写入 Skill 目录） | **NOT APPROVED FOR V1**。以后如要采用，必须由产品负责人单独批准 | §14、§16 |
| 第一轮 Probe Skills | **APPROVED FOR PREPARATION**，见 `tests/probes/` | validation-plan.md |
| 服务端编译 | 未经批准不得引入。本地优先架构不得改为依赖云服务 | §29 |

## 0. 知识分级约定

所有关于 WorkBuddy 平台和技术能力的判断，都标注证据等级。这套分级延续 WB-OPDK 的知识纪律：

| 等级 | 含义 |
|---|---|
| `OFFICIAL` | WorkBuddy 当前官方文档明确规定 |
| `OBSERVED` | 在真实 WorkBuddy 环境中实测观察到 |
| `DERIVED` | 基于官方规则或实测推导出的工程设计 |
| `EXPERIMENTAL` | 已设计但未充分验证的方案 |
| `UNVERIFIED` | 尚无证据，只是假设，不得写进代码当作事实 |
| `STALE` | 上游已变化，等待重新验证 |

### 与早期构想相比的关键修正

| # | 早期表述 | 修正后 |
|---|---|---|
| 1 | 生成 ZIP，用户自己找目录安装 | 主路径改为**交给 WorkBuddy 原生机制安装**，ZIP 仅作 fallback（§14–16） |
| 2 | 安装后所有设计任务自动继承品牌 | 改为 **Contextual Brand Runtime**：按语境调用，多品牌时必须消歧（§9–10） |
| 3 | 付费 Skill 必须加密 | 区分三个概念：**Paid Skill**（销售机制，`OBSERVED`）≠ **Encrypted Skill**（平台 UI 中的加密选项，`OBSERVED` 仅限文案）≠ **Source Protection**（实际保护效果，`UNVERIFIED`）。对外只说 Paid Skill（§26） |
| 4 | 价格 19.9 元 / 19 或 20 元 | 价格 **TBD**，不阻塞架构。平台 UI 文案显示只允许 1–9999 元的整数（`OBSERVED`，来自前端文案） |
| 5 | 按操作系统分 bash / PowerShell | 改为 **Capability-first** 能力探测（§14、architecture.md §6） |
| 6 | 各规范文件分别写颜色、字号等数值 | 统一以 **Brand IR** 为唯一事实来源，所有文件都从它派生（§3） |

---

## 1. Product Definition

**DesignBuddy = AI Brand System Builder + Brand System Compiler + WorkBuddy Brand Skill Generator**

DesignBuddy 是运行在 WorkBuddy 中的专业品牌系统构建器和编译器。它把五类输入编译成一个 AI 可以长期执行的品牌设计系统：

- 品牌资料；
- 现有视觉资产；
- 用户的设计偏好；
- 用户确认过的设计决策；
- DesignBuddy 内置的专业设计方法论。

它**不是**：

- 帮用户写品牌规范文档的 Skill；
- 套壳版的 Claude Design；
- 通用的 Skill 生成器（WorkBuddy 已经内置 Skill Creator）。

### 三类核心产出

1. **WorkBuddy Brand Skill**：可在 WorkBuddy 中执行的品牌 Skill。
2. **Portable Design System**：可移植的设计系统，包括 DESIGN.md、tokens、Brand IR。
3. **Preview / Sample Applications**：用于用户验收的样例应用。

另有附属产出 **Source Report**：记录来源、推断依据、许可和置信度。

### 产品闭环

```
Brand Discovery → Brand Analysis → Brand IR → Visual Direction → User Approval
→ Design System → Validation → Generate Brand Skill → Install in WorkBuddy
→ Runtime Test → Export / Backup
```

### 借鉴 Claude Design 的边界

我们只借鉴 Claude Design 的四个方法：

- System-first：先建系统，再出产物；
- Review Gates：分阶段审核；
- Examples：用样例验收；
- Reusable Design Rules：可复用的设计规则。

不复制 Claude Design 的界面和产品结构。DesignBuddy 的核心是利用 WorkBuddy 自己的特点：Skill 可以被生成、被安装、被模型调用，并成为长期能力。所以产品逻辑是：

```
Design System → Compiler → Executable Skill
```

## 2. DesignBuddy vs Brand Skill

| | DesignBuddy | Brand Skill（如 `acks-brand-system`） |
|---|---|---|
| 角色 | Builder / Compiler（构建期） | Runtime Product（运行期） |
| 何时使用 | 新建品牌、改版、新增应用、更新资产、升级设计系统 | 日常做 PPT、文档、网页、海报等任何品牌物料 |
| 分发方式 | 在 WorkBuddy 技能市场付费上架 | 由 DesignBuddy 生成，在用户本人的 WorkBuddy 中安装 |
| 依赖关系 | 依赖用户的 Workspace | **完全自包含，运行时不依赖 DesignBuddy** |
| 保护 | 付费 Skill（保护机制待验证） | 属于用户本人，不加密、可编辑、可导出 |

**原则：不制造运行时锁定。** 用户卸载 DesignBuddy 后，已安装的 Brand Skill 必须照常工作（验证项 V-RT-07）。

### 为什么不直接用 WorkBuddy 的 Skill Creator（商业差异）

Skill Creator 是通用的 Skill 生成器，"能生成 Skill"不构成差异。DesignBuddy 的价值在于 Skill 里**装的是什么**，以及**这些内容怎样被可靠地生产出来**：

- 专业的 Brand Discovery 方法；
- Design System 方法论和 Brand IR；
- 视觉方向的生成与评选；
- Design Tokens、中英文字体体系、版式与栅格体系；
- 无障碍 QA（作为放行关卡），以及 Asset 治理和 License 治理；
- 跨媒介规则：Word、PPT、Excel、PDF、Web、海报、社交媒体；
- Office、Web、海报模板；
- Preview 验收；
- 多品牌运行规则；
- Portable Export；
- Runtime 自测。

一句话：**Skill Creator 是 Generic Skill Builder；DesignBuddy 是 Professional Brand System Compiler。**

## 3. Brand IR

Brand IR（Brand Intermediate Representation，品牌中间表示）是**唯一事实来源（Single Source of Truth）**。

```
Sources → Extraction → Normalization → Brand IR → Validation → Human Approval → Exporters
```

### 规则

1. 任何最终文件都不允许"自带"颜色、字体、尺寸等数值。它们一律由 Exporter 从 Brand IR 渲染出来，包括：SKILL.md、references/*.md、tokens.json、tokens.css、DESIGN.md、Office 主题、Preview。
2. 修改品牌只改 Brand IR，然后重新编译。**不手改派生文件**。派生文件的头部写明 `generated from brand-ir vX.Y.Z — do not edit`。
3. Brand IR 必须满足三点：
   - 机器可读；
   - 有版本号；
   - 能校验：有 Schema 和校验脚本。

### 存储格式（决策 D-01 / D-02，ACCEPTED）

- **Brand IR 和 Project Metadata 统一用 JSON 作为机器可读的唯一事实来源**（`brand-ir.json`、`project.json`）。
- 理由：
  - Python 标准库直接支持；
  - 跨平台稳定，容易解析；
  - 适合结构化校验和版本管理，方便扩展。
- **必须包含 `schema_version`**（SemVer），位于根级别。它与 Brand Design System 的版本是两个独立的版本号。
- **必须实现数据校验**：
  - V1 用标准库自己实现必要的检查：必填字段、类型、枚举值、交叉引用、业务规则（详见 architecture.md §3.6）。
  - **Python 标准库并不原生支持完整的 JSON Schema 校验**，我们也不对外宣称"完整 JSON Schema 校验"。
  - 同时附带 `brand-ir.schema.json`，供有 `jsonschema` 等外部工具的开发者使用。它不是运行时依赖。
- **数据模型与导出格式分离**：IR 只描述品牌和设计系统本身，不包含任何导出格式的细节。导出格式由 Exporter 负责：

  ```
  Brand IR (JSON) → Exporters ├── WorkBuddy Brand Skill
                               ├── DESIGN.md
                               ├── Design Tokens (DTCG JSON)
                               ├── CSS
                               ├── Office Themes
                               └── Portable Bundle
  ```

- YAML（`brand-ir.yaml`）只作为**可选的导出格式**，不作为输入，也不是运行时的必需依赖。

### 顶层结构

```
schema_version
metadata
brand           ─ name · aliases · industry · audience · positioning · personality · values · voice · identity(logo…)
design_system   ─ colors · typography · spacing · radius · borders · shadows · grid · layout · imagery
                  · photography · illustration · iconography · motion · accessibility
applications    ─ document · presentation · spreadsheet · web · poster · social
rules           ─ MUST / SHOULD / AVOID / NEVER
assets · licenses  ─ 指向 manifest
provenance      ─ 统计与待审核索引
version         ─ system / skill / changelog
```

完整的字段定义和示例见 [`architecture.md` §3](architecture.md#3-brand-ir-规范)。

## 4. Provenance / Confidence

风险：AI 推断出来的东西，最后被写成"品牌事实"。

### 应对：给事实加来源字段

所有关键事实都用统一的 **Fact 包装**：

```json
{
  "value": "#0057FF",
  "source_type": "EXTRACTED",
  "evidence": ["sources/logo.svg#fill"],
  "confidence": "high",
  "review": "approved",
  "note": ""
}
```

| 字段 | 取值 |
|---|---|
| `source_type` | `USER_CONFIRMED` · `DOCUMENTED`（用户提供的品牌规范中明确写明）· `EXTRACTED`（从资产中测量得到）· `INFERRED`（AI 推断）· `GENERATED`（DesignBuddy 新设计） |
| `confidence` | `high` · `medium` · `low` |
| `review` | `pending` · `approved` · `changed` · `rejected` · `user_override` |

### Review 规则

- Gate 审核时**优先展示**：`INFERRED`、`GENERATED`、`confidence = low`、以及存在冲突的 Fact。
- `USER_CONFIRMED` 和高置信度的 `DOCUMENTED` 默认折叠，不要求用户逐条重新确认。
- 最终导出前，不允许任何 `review = pending` 的 MUST/NEVER 规则存在（Release Gate）。
- Source Report 汇总所有 Fact 的来源分布，这本身就是交付物。

## 5. Existing / Partial / New Brand Flows

三条入口最终汇入**同一个 Brand IR**，不做三套互不兼容的系统。

| 路径 | 典型输入 | 原则 | 流程 |
|---|---|---|---|
| **A. Existing** | Logo、品牌手册、VI、PPT、PDF、Figma 导出、网站、代码仓库 | **Preserve Existing Brand**：保留现有品牌，不重新设计 | Import → Extract → Normalize → Detect Conflicts → Review → IR → Export |
| **B. Partial** | Logo、主色、品牌名、几份历史 PPT | 保留已知规则，补全缺失部分 | Import → Extract → **Gap Analysis** → Generate Missing → Review → IR |
| **C. New** | 什么都没有 | 先做 Discovery，不直接问"主色是什么" | Discovery → Foundation → 2–3 Visual Directions → Select → Full System |

### 路径判定

Intake 阶段由 DesignBuddy 根据用户上传的材料**建议**一条路径，用户确认后执行。用户也可以中途切换路径，例如在 Partial 流程中发现资料其实很完整，就转到 Existing。

### Gap Analysis

逐一检查 IR 的每个顶层模块，标记为 `present` / `partial` / `missing`。只对 `missing` 和 `partial` 部分生成内容，生成的内容标记为 `GENERATED`。

### 冲突检测（Path A/B）

同一个属性出现多个不同的值时（比如 PPT 用 #0057FF，网站用 #0A5CFF），DesignBuddy 不会自动挑一个，而是：

1. 列出所有冲突值和各自的证据；
2. 给出建议（例如"按出现频次和最新程度，建议统一为 #0057FF"）；
3. 由用户在 Gate 中裁决。

裁决结果记为 `USER_CONFIRMED`。

### 参考品牌（Path C，以及 A/B 的补充）

用户可能说"我喜欢 Apple / 参考 Linear"。DesignBuddy 只**提炼原则**：

- 留白；
- 信息密度；
- 色彩使用比例；
- 字体层级；
- 节奏；
- 图片风格。

提炼结果写入 IR，标记为 `INFERRED`，证据写成 `reference:<name>`。**禁止**复制以下内容：

- Logo；
- 特有插画、图片、图标；
- 字体文件；
- 明显的 Trade Dress（可识别的整体外观）。

## 6. Design Gates

目标是帮用户**快速做决策**，避免无限次的 vibe 式修改。

| Gate | 审核对象 | 进入条件 |
|---|---|---|
| G1 Brand Foundation | 定位、受众、性格、价值观、语气、禁忌 | Discovery / Import 完成 |
| G2 Visual Direction | 2–3 个方向（Path A 可跳过或简化为"现状确认"） | G1 KEEP |
| G3 Core Design System | 颜色、字体、间距、圆角、阴影、栅格、Logo 规则、无障碍结果 | G2 KEEP |
| G4 Application System | Word、PPT、Excel、PDF、Web、海报、社交媒体的规则 | G3 KEEP |
| G5 Preview / Sample | 3 个样例（见 §22） | G4 KEEP，且 QA 无未处理的 FAIL |
| G6 Final Export | 最终摘要、版本、包含的内容、安装确认 | G5 KEEP |

### 反馈格式

每个 Gate 只接受三种反馈：

- **KEEP**：保留；
- **CHANGE + 具体修改**；
- **REJECT + 原因**。

用户给出模糊反馈时（如"看着怪怪的"），DesignBuddy 引导成**可执行的修改**：

- 先提供 2–3 个具体的候选解释，例如"是主标题太重？配色太冷？还是间距太挤？"；
- 落实为具体指令，例如"主标题字重 700 → 600"或"Accent Green 仅用于按钮和状态，禁止大面积用作背景"。

### 收敛机制

- 同一个 Gate 连续 3 轮 CHANGE 后，DesignBuddy 主动给出 A/B 两个具体方案，让用户二选一。
- 每次 Gate 决策写入 `reviews/`，用于审计和断点续做。

## 7. DesignBuddy Workspace

不能靠单次会话保存一个完整的品牌项目。Workspace **属于用户**，存放在用户本地的工作目录，可以断点续做。

```
designbuddy-workspace/{brand-slug}/
├── project.json            # 项目元数据（决策 D-02：用 JSON 代替 YAML，原因同 D-01）
├── sources/                # 用户原始资料（不进入最终 Skill）
│   └── source-manifest.json
├── extracted/              # 抽取的中间结果
├── brand-ir/
│   ├── brand-ir.json
│   └── history/            # 历次 IR 快照
├── reviews/                # 每个 Gate 的决策记录
├── previews/
├── exports/
│   ├── workbuddy-skill/
│   ├── portable-design-system/
│   ├── preview/
│   └── source-report/
└── .designbuddy/
    ├── state.json          # 当前阶段 / Gate / 下一步
    ├── version.json        # 生成这个 Workspace 的 DesignBuddy 版本、Schema 版本
    └── migrations/
```

### 续做体验

用户说"继续做 ACKS 的品牌系统"时：

1. DesignBuddy 读取 `state.json`；
2. 用一段话告诉用户上次进行到哪里；
3. 从中断的 Gate 继续，不重复 Discovery。

### 多品牌

一个 Workspace 根目录下可以有多个 `{brand-slug}/` 项目。

## 8. WorkBuddy Brand Skill Runtime

已安装的 Brand Skill 是 **Contextual Brand Runtime**：在相关语境下由模型按语义调用。它**不是** Global Always-on System Prompt。

### SKILL.md 的职责（只做五件事）

1. Trigger：触发描述，主要由 frontmatter 承担；
2. Brand Resolution：品牌消歧（§10）；
3. Routing：根据任务类型决定加载哪些 references（§11）；
4. Critical Rules：只放 MUST/NEVER 中最关键的 10–15 条；
5. QA Gate：每次出稿走 Draft → Brand QA → Fix → Final（§20）。

### 内容与设计分离（默认职责）

- Brand Skill 默认只负责**应用设计系统**：信息层级、版式、字体、颜色、图表、视觉、品牌一致性。
- 不擅自改写用户的业务内容和语义。
- 只有用户明确要求"也帮我改内容"时，才扩展到内容层面，并沿用 `voice` 规则。

### 两个概念的严格区分

| 概念 | 机制 | 状态 |
|---|---|---|
| Contextual Brand Runtime | 普通 Skill + 高质量 description + 品牌消歧 | V1 |
| Mode-level Brand Harness | 由 Buddy App 的 Work Mode 绑定品牌 Skill，在该模式下全程生效 | Future，V1 不承诺 |

## 9. Auto Invocation

frontmatter 是 Runtime 的一部分。DesignBuddy 自动生成高质量的 `description`、`description_zh`、`description_en`，必须包含：

- 品牌正式名称、英文名、别名；
- 任务类型：创建、修改、审核；
- 支持的物料：PPT、Word、Excel、PDF、网页、海报、社交媒体视觉等；
- 使用语境。

### 模板（中文）

> 当用户为 {正式名}（{英文名}；别名：{别名列表}）创建、修改或审核 PPT、Word、Excel、PDF、网页、海报、社交媒体视觉或其他品牌物料时，使用本品牌设计系统。用户未提及该品牌且语境不明确时，不要使用本技能。

### 默认 frontmatter 策略

| 字段 | 默认值 | 说明 |
|---|---|---|
| `disable-model-invocation` | `false` | — |
| `user-invocable` | `true` | — |
| `allowed-tools` | 不设置 | 只有明确需要时才设置 |
| `version` | Brand Skill 版本 | 见 §23 |
| `author` | 用户本人或其组织 | Brand Skill 属于用户，不写 DesignBuddy |

自动调用的命中率和误触发率是 `TO TEST` 项（V-RT-03/04）。

## 10. Multi-brand Conflict Handling

### 规则（写入每个 Brand Skill 的 SKILL.md）

1. 用户**明确提到**品牌名或别名 → 使用对应的 Brand Skill。
2. 当前上下文**明显**属于某个品牌（例如正在编辑该品牌的文件，或本次对话已经确定了品牌）→ 可以使用。
3. 可能同时适用多个品牌，或请求里没有任何品牌线索（如"帮我做个 PPT"）→ **先问用户**，不擅自套用。
4. 任何 Brand Skill 都**不得**自称默认品牌，也不得声称全局生效。
5. 品牌转换（"把 Beta 的文档改成 Alpha 风格"）：
   - 明确识别 source brand = Beta、target brand = Alpha；
   - 输出只遵循 target brand 的规则；
   - source brand 只用来识别"哪些元素需要替换"，两套规则不混用。

### 为什么不维护"已安装品牌清单"

单个 Brand Skill 无法可靠地知道还装了哪些其他 Brand Skill（`UNVERIFIED`）。所以消歧逻辑不依赖清单，而依赖"有没有明确的品牌线索"。

### 测试

使用虚构品牌 Alpha / Beta，见 validation-plan V-MB-*。

## 11. Progressive Disclosure

Token 成本是 WorkBuddy 产品体验的重要指标，按设计目标对待。

### SKILL.md 中的路由表（示例）

| 任务 | 加载的 references |
|---|---|
| PPT / 演示 | brand-core · color · typography · ppt |
| Word / PDF 文档 | brand-core · color · typography · word |
| Excel | brand-core · color · typography · excel |
| Web | brand-core · color · typography · spacing-layout · web |
| 海报 | brand-core · poster · imagery（按需加 color、typography） |
| 社交媒体 | brand-core · social · imagery |
| 涉及 Logo | + identity |
| 写文案或改内容 | + voice |
| 出稿前 QA | qa-checklist（+ accessibility） |

### Token 预算（DERIVED 目标值，待实测校准）

| 对象 | 预算 |
|---|---|
| SKILL.md | ≤ 2k tokens |
| 单个 reference | ≤ 1.5k tokens |
| 单次任务总加载 | ≤ 8k tokens |

### 写法约束

- references 以**规则表、token 表**为主，少写散文。
- 颜色、尺寸直接写数值和 token 名，不重复解释原理。
- DesignBuddy 自身也遵循同样的原则：方法论按阶段懒加载，不一次性读完。

## 12. WorkBuddy Skill Export

保守遵循当前官方结构（`OFFICIAL`：SKILL.md + references/ + scripts/ + templates/）。

```
{brand-slug}-brand-system/
├── SKILL.md
├── references/  brand-core · identity · voice · color · typography · spacing-layout · imagery
│                · iconography · accessibility · word · ppt · excel · web · poster · social
│                · qa-checklist · licensing · changelog
├── scripts/     validate_brand.py · validate_contrast.py · （可选）check_tokens.py
└── templates/   tokens/ · office/ · web/ · poster/ · social/ · assets/
```

- **根目录不加** DESIGN.md、assets/、tokens/、examples/ 等自定义项。这些只放在 Portable 包里，直到 V-PK-02 验证完成。
- CHANGELOG 放在 `references/changelog.md`，而不是根目录。WB-OPDK 实测的发布包也去掉了根目录的 README/CHANGELOG。
- Brand Skill 自带的脚本**只用 Python 标准库**。脚本不可用时，SKILL.md 给出 Agent 自查清单，并要求在结果中标注 `UNVALIDATED`。

## 13. Portable Export

DesignBuddy 不把用户锁死在 WorkBuddy。"做一次品牌系统，不只 WorkBuddy 能用"是重要卖点。

```
portable-design-system/
├── README.md          # 如何在 Claude Code / Cursor / Stitch / Codex / Web 项目中使用
├── DESIGN.md          # 可移植标准（YAML tokens + Markdown 说明）
├── brand-ir.json      # 规范格式
├── brand-ir.yaml      # 只读视图
├── tokens.json        # W3C DTCG 格式
├── tokens.css         # CSS 变量
├── assets/            # 只含允许再分发的资产（以 manifest 为准）
└── examples/          # Preview 样例的副本（用户同意后才放入）
```

### DESIGN.md 的定位

- DESIGN.md 是 **Portable Standard**，**不是** WorkBuddy 的运行时入口。WorkBuddy 版通过 Progressive Disclosure 读取 references，不读取大而全的 DESIGN.md。
- DESIGN.md 格式参照 Google Labs / Stitch 提出的开放规范（YAML tokens + Markdown）。该规范**不是正式标准**，证据等级 `DERIVED`，需要跟踪上游变化。

## 14. Installation Flow

原则：**DesignBuddy 负责生成正确的 Skill；WorkBuddy 原生机制负责安装。**

```
Generate → Validate package → Preview → Explain（最终摘要）→ Explicit User Confirmation
→ Native Install Handoff → Verify（Runtime Smoke Test）→ Backup（ZIP + Portable）
```

### 确认话术（示例）

> 你的品牌 Skill 已经准备完成。
>
> - 名称：ACKS Brand System（`acks-brand-system`）
> - 版本：Skill 1.0.0 / Design System 1.0.0
> - 包含：品牌定位 · 颜色 · 字体 · 版式 · 图片风格 · Word · PPT · Excel · Web · Poster · Social · QA Rules
> - 无障碍：核心配色组合全部 PASS（1 项 WARNING 已记录）
> - 不包含：你的原始资料（已留在 Workspace 中）
>
> 是否现在安装到 WorkBuddy？

### 安装纪律

- 必须得到明确确认（"是 / 安装"）才执行，**不得静默安装**。
- 不在后台修改用户的 Skill 环境。
- **V1 不采用 H5**（直接写入 WorkBuddy 内部的 Skill 目录）。即使技术上可行，也涉及用户授权、路径兼容、Skill 注册机制、升级机制、软件版本变化、意外覆盖现有 Skill 等问题。除非 H1–H4 全部无法满足需求，且能证明 H5 安全、可逆、可维护，否则不实现。**即便将来采用，也必须经产品负责人单独批准。**
- 同名 Skill 已存在时，先说明"这是升级：1.0.0 → 1.1.0，变更如下……"，再确认。

### 安装后

立即运行 Smoke Test（§16），并告诉用户以后怎样触发：

> 以后你说"给 ACKS 做一份……"即可。

## 15. Conversation Install — OBSERVED Capability

| 能力 | 等级 | 证据 |
|---|---|---|
| WorkBuddy 能在对话中创建并安装 Skill | `OBSERVED` | 产品负责人实测（2026-10）：使用 WorkBuddy 内置的 Skill Creator，经过对话讨论 → 生成 → 直接安装 |
| WorkBuddy 内置 Skill Creator 这个 Skill | `OBSERVED` | 同上 |

需要验证的问题已经从"WorkBuddy 能不能安装"变为：

> **DesignBuddy 作为第三方 Skill，应该怎样把已经生成好的 Brand Skill 交给 WorkBuddy 原生机制完成安全安装？**

## 16. Third-party Install Handoff — Validation Plan

### 候选交接方式（按优先级排列；H1–H4 已批准测试，H5 不进入 V1）

| 方式 | 描述 | 优点 | 风险 |
|---|---|---|---|
| H1 原生安装工具 | 运行时 Agent 的工具列表中如果存在安装或创建 Skill 的工具，就直接把 Brand Skill 目录或 ZIP 交给它 | 最稳定、最原生 | 工具不一定存在，也不一定对第三方 Skill 开放 |
| H2 Skill 串联 | DesignBuddy 指示 Agent 调用内置 Skill Creator，并传入"从路径 X 安装已生成的 Skill"的指令 | 复用已经 OBSERVED 的路径 | Skill Creator 可能会"重写"而不是"原样安装" → 必须做内容一致性校验 |
| H3 用户一句话触发 | DesignBuddy 给出一句可以直接复制的指令（例如"请安装位于 X 的 Skill"），由用户发出，触发原生安装 | 安装动作由用户发起，天然满足确认要求 | 多一步操作 |
| H4 ZIP 手动导入 | 生成符合规范的 ZIP，按指引通过 WorkBuddy UI 导入 | 一定可用 | 体验最差，**仅作 fallback** |
| H5 直接写目录 | 写入 WorkBuddy 本地的 Skill 目录 | — | **NOT APPROVED FOR V1**，不实现，也不作为测试步骤执行；将来如要采用，需单独批准 |

### 运行时选择逻辑

按 H1 → H2 → H3 → H4 依次探测并降级。不存在 H5 分支。实际使用了哪种方式，记录到 `state.json` 和 Source Report。

### 安装后的一致性校验（无论用哪种方式）

只看"安装成功"的提示是不够的。必须核对实际安装的产物与原始构建包是否一致：

1. **文件列表与内容**：
   - 构建时生成 `build-manifest`，记录每个文件的 SHA-256 和 `build_id`；
   - 安装后由 Brand Skill 自带的自检脚本逐一比对；
   - 结果区分 MATCH / MISMATCH / 只有换行符不同 / 缺失 / 多出。
2. **版本**：frontmatter 中的版本、manifest 中的版本、`build_id` 三者一致。
3. **关键规则**：抽查 MUST/NEVER 规则的具体数值（例如主色 HEX），确认没有被 Skill Creator 改写或重新生成。
4. **引用**：所有 `@references/` 路径都能读取。
5. **触发**：发出品牌明确的触发句，确认命中；发出无品牌的泛化请求，确认不会误套品牌（或至少会先询问）。

如果没有可用的 Python，由 Agent 核对第 2–5 项，结果标注 UNVALIDATED。这套机制已在 `tests/probes/installation-probe` 中实现了最小原型。

详细用例见 validation-plan V-IN-*、V-RT-*。

## 17. Asset Management

每个品牌包都生成 `templates/assets/asset-manifest.json`，Portable 包中也有一份。字段：

```
filename · type · source · owner · license · redistribution_allowed · included · sha256 · notes
```

- **Logo**：优先使用用户提供的矢量文件。DesignBuddy 可以生成派生版本（反白、单色、小尺寸），派生关系写进 `source`。
- **第三方参考网站**：只用于视觉分析、提炼规律、确定风格方向。**不得**自动复制其中的 Logo、图片、Icon、字体。
- 用户原始资料由 `source-manifest.json` 管理（§24），与最终 Skill 包分开。
- `included = true` 的前提：`redistribution_allowed` 是 `true` 或 `user_owned`，并且用户已确认。

## 18. Font / License System

**不扫描整个电脑的字体目录，不自动复制字体文件，不默认打包字体。**

### 字体来源优先级

1. 用户明确提供的字体；
2. 品牌规范中明确指定的字体；
3. 用户确认本机可用的字体：只检查用户点名的字体是否已安装，不全盘扫描；
4. DesignBuddy 推荐的可商用替代字体（来自内置的 `font-licenses` 知识库，每条带核验日期）；
5. 建立 fallback stack。

### font-manifest 字段

```
family · style · weights · source · license · license_url · redistribution_allowed · bundled · fallbacks · verified_at
```

- 默认 `bundled: false`。
- 只有在许可**明确允许再分发**并且用户确认的情况下，才打包字体文件。
- 在报告中提示常见风险：某些系统自带字体的商用授权有限制。具体字体的结论以知识库条目和它的来源为准，不在本文写死。

## 19. Accessibility QA

无障碍检查是 **Release Gate**，不只是写在品牌指南里的文字。

### 至少检测以下颜色组合

| 组合 | 阈值（WCAG 2.x） |
|---|---|
| 正文 / 背景（含浅色、深色背景） | 4.5:1 |
| 大字号标题 / 背景 | 3:1 |
| 按钮文字 / 按钮底色，按钮 / 页面背景 | 4.5:1 / 3:1（非文本 UI） |
| 链接 / 背景，以及链接 / 正文的区分 | 4.5:1 |
| 状态色（成功、警告、错误、信息）上的文字 | 4.5:1 |
| 图片或色块上叠加的文字（Text Overlay） | 4.5:1，并给出遮罩 / 描边规则 |

### 输出

每对组合输出 `PASS` / `WARNING` / `FAIL`：

- `WARNING`：仅达到大字号阈值，或接近临界值。

### 放行规则

- 核心 UI 组合出现 FAIL，**不能进入 G5**。
- 用户坚持不改时，记录 `USER_OVERRIDE`，内容包括：组合、比值、用户的理由、时间。这条记录写入 IR 和 Source Report，同时生成一条 Brand Skill 规则（例如"该组合禁止用于正文"）。
- **不偷偷修改，也不偷偷放行。**
- 脚本无法运行时，由 Agent 手动计算，并标记 `UNVALIDATED`。不允许静默跳过检查。

## 20. Brand QA

DesignBuddy（构建期）和 Brand Skill（运行期）都有 QA 循环。

### 运行期循环（写入每个 Brand Skill）

```
Draft → Brand QA → Fix → Final
```

### 通用检查项

Logo · Color · Typography · Spacing · Alignment · Composition · Accessibility · Image Style · Voice · Forbidden Patterns

### 媒介专项

按需额外加载：PPT QA · Web QA · Poster QA · Document QA（Word/PDF）· Spreadsheet QA

### 规则分级

所有关键规则尽量写成 `MUST` / `SHOULD` / `AVOID` / `NEVER`，每条规则带 id，便于 QA 引用，例如：

```
NEVER-LOGO-01  不得拉伸、旋转 Logo，不得给 Logo 加阴影或描边
MUST-TYPE-01   所有一级标题使用 Brand Heading Font
AVOID-COLOR-03 Accent 色大面积用作背景
NEVER-COLOR-01 使用未经批准的品牌颜色
```

### QA 输出

QA 输出一份简短报告，列出违反的规则 id 和修复动作。脚本可用时附上校验结果；不可用时标注 `UNVALIDATED`。

## 21. Office Templates

`.potx`、`.dotx`、`.xltx` 属于 **Advanced Export**，**不是核心依赖**。

- 核心产出先成立：规则、tokens、references、Brand Skill。没有二进制模板时，Brand Skill 依然能根据规则生成符合品牌的 Office 文档。
- 模板用 Python 标准库（zipfile + OOXML）生成。

### 需要逐项验证

| 验证内容 | 用例 |
|---|---|
| Skill ZIP 能否稳定携带二进制文件 | V-OF-01 |
| Mac Office 兼容性 | V-OF-02 |
| Windows Office 兼容性 | V-OF-03 |
| WPS 兼容性 | V-OF-04 |
| Agent 能否在运行时正确取用模板 | V-OF-05 |

验证通过之前，模板以"附加产物"的身份提供，失败不影响整体交付。

## 22. Preview / Acceptance

Preview 是正式的 Release Gate（G5）。打包前至少生成以下三个样例：

1. **Poster / Social Visual**：一张海报或社交媒体主视觉；
2. **Landing Page**：一个落地页；
3. **Presentation / One-pager**：演示页或单页文档。

### 规则

- 三个样例都用 HTML 生成，最通用、最可靠。
- 样例内容用中性的示意文案，或用户提供的真实文案。
- 每个样例都要通过 Brand QA，并附上无障碍结果。
- 样例存放在 `exports/preview/`，**默认不进入 Runtime Skill**。用户同意后，可复制到 Portable 包的 `examples/`。
- 用户在 G5 给出 KEEP 后，才能进入 Final Export。
- 如果用户发现问题，需要判断问题出在哪一层：
  - **IR 问题**（规则本身不对）→ 回到 G3 或 G4 修改；
  - **样例实现问题** → 只修改样例。

## 23. Versioning

三层版本（均使用 SemVer）：

| 版本 | 含义 | 示例 |
|---|---|---|
| DesignBuddy Version | 编译器本身的版本 | 1.2.0 |
| Brand Skill Version | 生成的 WorkBuddy Skill 包版本（即 frontmatter 中的 `version`） | 1.0.1 |
| Brand Design System Version | Brand IR 的语义版本 | 2.0.0 |

### 规则

- Runtime bug 修复：Skill 版本 +patch，System 版本不变（例如 Skill 1.0.1 / System 1.0.0）。
- 品牌主色更换（破坏性变化）：System 版本 +major，Skill 版本 +minor（例如 Skill 1.1.0 / System 2.0.0）。
- 新增应用模块（如增加 Excel）：System 版本 +minor，Skill 版本 +minor。

### 所有导出物都写入的元数据

```
generated_by: DesignBuddy x.y.z · generated_at · build_id · system_version · schema_version
```

### 变更记录与迁移

- `references/changelog.md`（Skill 内）和 Portable README 记录变更。
- `.designbuddy/migrations/` 记录 IR Schema 的迁移。DesignBuddy 升级后打开旧 Workspace 时，会先迁移再续做。

## 24. Privacy

用户可能提供内部 PPT、商业计划、客户文件、未发布资料等敏感内容。

### source-manifest.json

```
source · type · extracted_items · contains_sensitive_data · included_in_final · reason
```

### 规则

- 默认 `included_in_final = false`。最终 Skill 只保留**运行所需的品牌规则**和**用户允许使用的资产**。
- 抽取时只提取设计相关的特征：颜色、字体、版式、构图。业务文本不写入 IR。确有必要引用业务文本时（例如 voice 示例），需要用户同意，并做脱敏处理。
- Workspace 保存在用户本地。DesignBuddy 不把资料发送到任何外部服务（WorkBuddy 本身的模型调用除外）。
- 生成的 Skill 不包含本地绝对路径、账号、密钥等信息。打包前用 lint 检查。
- 这样做同时降低了隐私风险、包体大小和上下文成本。

## 25. Runtime Validation Ledger

完整表格维护在 [`runtime-capabilities.md`](runtime-capabilities.md)，验证用例见 [`validation-plan.md`](validation-plan.md)。摘要：

| Capability | Status |
|---|---|
| Skill 包结构（SKILL.md / references / scripts / templates） | OFFICIAL |
| Skill ZIP 被开放平台解析接受 | OBSERVED（WB-OPDK 实测） |
| 对话内 Skill 生成与安装（内置 Skill Creator） | OBSERVED |
| 第三方 Skill 生成另一个 Skill 的文件 | TO TEST |
| 第三方 Skill → 原生安装交接 | TO TEST |
| 多个 Brand Skill 共存与消歧 | TO TEST |
| 基于 description 的自动调用 | TO TEST |
| 二进制 Office 模板随 Skill 携带与使用 | TO TEST |
| 指定字体是否已安装的检测 | TO TEST |
| scripts 在 Win/Mac 上的可用解释器 | TO TEST |
| Paid Skill（付费销售机制） | OBSERVED（UI 文案） |
| Encrypted Skill（平台加密选项） | OBSERVED（仅 UI 文案） |
| Source Protection（实际保护效果） | UNVERIFIED → T-PRO-M1/M2 |
| 加密后：references 可读 / 脚本可执行 / 资源可读 / 资源可输出 / 生成器可用 | TO TEST（T-PRO，关键，见 §29） |
| 开发者账号与购买者账号的行为是否一致 | TO TEST（T-PRO-M1 vs M2） |
| Portable DESIGN.md | DERIVED |

## 26. Paid Skill Protection Validation

三个概念必须严格区分，不能混为一谈：

| 概念 | 含义 | 当前证据 |
|---|---|---|
| **Paid Skill** | 付费销售机制（买断 / 订阅、定价、收款） | `OBSERVED`（开放平台 UI 文案） |
| **Encrypted Skill** | 平台提供的"加密"选项。UI 文案显示付费时强制开启 | `OBSERVED`（仅 UI 文案） |
| **Source Protection** | 实际能否阻止用户或其他 Agent 读取、复制、提取原始实现 | `UNVERIFIED` |

详细验证见 [`PAID_SKILL_PROTECTION_VALIDATION.md`](PAID_SKILL_PROTECTION_VALIDATION.md)。

- 已观察到：开放平台前端文案包含"已开启（付费能力必须加密，不可关闭）"，以及"会对资产内容进行一定技术防护，但无法完全避免泄漏，且用户不可使用自定义模式调用"。这只能证明 UI 存在这个开关，**不能证明**保护在哪一层实现、效果如何。
- 在验证完成之前：对外只说 **Paid Skill**，不写 Encrypted Skill。
- 架构上**不把商业壁垒寄托在加密上**。壁垒来自方法论、Brand IR、编译器、QA、模板库，以及持续更新。

## 27. V1 Scope

V1 只做一件事：把下面这条链跑通。

```
Brand Discovery → Brand IR → Design System → Preview → Brand Skill → Install → Runtime Test
```

### V1 包含

- 三条入口：Existing / Partial / New，统一汇入 IR；
- G1–G6 的 Gate 机制，带 KEEP/CHANGE/REJECT 和收敛机制；
- Brand IR：Schema、校验、Provenance；
- 核心设计系统：颜色、字体、间距、圆角、阴影、栅格、Logo 规则、图片和图标风格、语气；
- 应用规范：Word、PPT、Excel、PDF、Web、海报、社交媒体，以 references 规则为主；
- 无障碍对比度 QA（放行关卡）和 Brand QA 清单；
- 资产、字体、来源的 manifest；
- WorkBuddy Brand Skill 编译与包校验；
- Portable 导出：DESIGN.md、tokens.json、tokens.css、brand-ir.json/yaml；
- 3 个 HTML 样例；
- 原生安装交接（H1–H4 降级）和 Smoke Test；
- Workspace 断点续做；
- Capability-first 能力探测与 `UNVALIDATED` 标注。

### V1 尽力而为

Office 二进制模板（.potx/.dotx/.xltx）。验证不通过时降级，不阻塞发布。

## 28. Future Scope

以下内容 V1 预留扩展点，但不实现：

- 模板市场、行业设计包；
- Design System 增量更新、品牌审计、Design Drift 检测（检查产物是否偏离规范）；
- 团队品牌系统、多品牌组织；
- Figma Connector、云端资产库；
- Buddy App 的 Mode-level Brand Harness；
- Node 版完整脚本。

## 29. Known Unknowns

完整列表与处理方式见 [`open-questions.md`](open-questions.md)。最关键的几项：

1. **第三方 Skill 交接原生安装的具体机制**：H1–H5 中哪些可用。
2. **加密状态下，DesignBuddy 自带的编译能力还能不能用**。

   **D-03 的状态是 CONDITIONAL FALLBACK / PENDING VALIDATION，不是默认架构。**

   **默认架构（不变）**：

   ```
   DesignBuddy 内置的编译能力（预先写好的生成器、规则、数据模型、校验器、模板体系、标准组件、导出逻辑）
     + Brand IR
     → Deterministic Build
     → Brand Skill Package
   ```

   需要区分两件事：

   | | 性质 | 结论 |
   |---|---|---|
   | 运行时**生成成品文件**（品牌专属的 SKILL.md、Tokens、规范、CSS、DESIGN.md、配置） | DesignBuddy 的正常职责，由确定性生成器根据 IR 产出 | 默认如此 |
   | 运行时让 Agent **重新编写我们的基础模板、组件、生成器** | 慢、耗 Token、结果不可复现，会把产品变成 vibe coding | **不作为默认架构** |

   **加密状态下需要验证的能力**（tests/probes/protection-probe）：
   1. Agent 能否读取 references；
   2. 能否执行自带脚本；
   3. 脚本能否读取所需的模板和资源；
   4. 能否把模板内容输出到用户工作目录；
   5. 能否用生成器直接生成新文件，而不复制模板原文件；
   6. 以上行为在开发者账号和普通购买者账号中是否一致。

   **关键判断**：读不到原始源码，不等于不能执行受保护的生成器。只要生成器能执行，并能向指定目录输出产物，完整的 Compiler 架构就可以保留。

   **按验证结果决定调整方式**：

   | 验证结果 | 架构调整 |
   |---|---|
   | 脚本能执行，且能读取自身资源 | 保持默认架构 |
   | 脚本能执行，但不能读取自身资源 | 把模板和数据内嵌进生成器代码（仍是预置的确定性生成器，不是现场编写） |
   | 脚本不能执行 | 评估其他方案。服务端编译**必须经产品负责人批准**；未经批准，不得把本地优先架构改为依赖云服务 |
   | 以上都不可行 | 才考虑 Agent 现场生成，并作为降级方案标注 UNVALIDATED |
3. **"用户不可使用自定义模式调用"的确切含义**，以及它对 DesignBuddy 交互的影响。
4. WorkBuddy 在 Windows / macOS 上执行命令所用的 shell 和可用解释器。
5. 第三方 Skill 是否有权限读写用户的工作目录、默认工作目录在哪里。
6. Skill 包的大小上限、文件数上限，以及能否包含二进制文件。
7. 多个 Brand Skill 同时安装时，模型调用的实际行为。
8. 改价次数、付费方式不可更改等规则的最新状态（来自 UI 文案，可能变化）。

## 30. Risks

| 风险 | 影响 | 缓解 |
|---|---|---|
| 原生安装交接不可用 | 主路径体验降级 | H1→H4 逐级降级；ZIP + 图文指引兜底 |
| 加密导致自带的生成器或资源不可用 | 编译能力受损 | 先测试（T-PRO）；按 §29 的结果逐级调整；Agent 现场生成只作为最后的降级方案（D-03 CONDITIONAL） |
| 自动调用误触发或漏触发 | 品牌被乱套，或该用时没用 | 高质量 description、消歧规则、多品牌测试 |
| Skill Creator 在安装时改写内容 | 规则失真 | 安装后做一致性校验和 Smoke Test |
| AI 推断被当成事实 | 品牌错误 | Provenance 机制、Gate 优先审核 INFERRED/GENERATED 项 |
| 无限修改 | 成本高、用户疲劳 | 6 个 Gate、3 轮后 A/B 收敛 |
| 字体或素材侵权 | 法律风险 | 默认不打包；manifest 和许可知识库；参考只提炼原则 |
| 隐私泄露 | 信任风险 | source-manifest；默认不纳入原始资料；路径和密钥 lint |
| Token 成本过高 | 体验差、费用高 | Progressive Disclosure、预算指标、实测校准 |
| 解释器不可用（尤其 Windows） | QA 不能自动执行 | Capability-first；Agent 兜底并标注 UNVALIDATED |
| Office 模板兼容性 | 模板打不开或样式错乱 | 列为 Advanced Export，降级不阻塞 |
| 被 Skill Creator 或其他免费 Skill 替代 | 商业风险 | 差异化（§2），持续积累方法论和模板 |
| 平台规则变化（付费、审核、结构） | 返工 | 证据分级；Ledger 跟踪 STALE；提交当天复核官方文档 |
| 买断制下后续更新的成本 | 收入与维护不匹配 | V1 范围收敛；未来通过行业设计包等独立产品变现（待定） |
