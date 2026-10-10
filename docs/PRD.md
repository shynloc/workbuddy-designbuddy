---
title: DesignBuddy PRD
version: 0.2 (R1 修订)
status: DRAFT — 待产品负责人确认
owner: 产品负责人（个人开发者主体）
last_updated: 2026-10-10
related: DESIGNBUDDY_ARCHITECTURE_REVISION.md · architecture.md · validation-plan.md
---

# DesignBuddy 产品需求文档

## 1. 一句话定义

DesignBuddy 是一个运行在 WorkBuddy 中的专业 **AI Brand System Builder 与 Compiler**。它的工作流程是：

1. 通过对话理解用户的品牌、现有资产和视觉偏好；
2. 建立一个结构化、可验证、可持续升级的 **Brand IR**；
3. 把 Brand IR 编译成以下产出：
   - WorkBuddy 可执行的 Brand Skill；
   - Portable Design System；
   - Design Tokens；
   - 跨媒介设计规范；
   - 模板；
   - Brand QA；
   - Preview 样例；
4. 通过 WorkBuddy 原生能力，把生成的 Brand Skill 安装给用户。

用户最终得到的不是"一份设计说明"，而是**一个以后每次都能真正执行品牌设计规范的 AI 品牌系统**。

## 2. 目标用户

| 用户 | 典型情况 | 主要路径 |
|---|---|---|
| OPC（一人公司） | 有名字，可能有 Logo，没有系统 | Partial / New |
| 小企业主 | 有 Logo、旧 PPT、网站，规范零散不一致 | Partial / Existing |
| 职场人士 | 个人品牌或团队对外材料，需要统一的 PPT 和文档风格 | New / Partial |
| 自媒体 IP | 需要统一封面、海报、社交媒体视觉 | New / Partial |
| 品牌 / UI 设计师 | 已有完整 VI 或 Design System，想让 AI 能执行 | Existing |

## 3. 要解决的问题

1. 每次让 AI 做 PPT、海报、网页，都要重新交代颜色、字体、风格，而且结果仍不一致。
2. 小团队没有能力建立完整的品牌系统；已有的规范又是 PDF，AI 不能直接执行。
3. 品牌规则散落在多个文件里，互相冲突，没有一个唯一的事实来源。
4. AI 生成的设计经常忽略对比度、字体许可、素材版权等问题。

## 4. 产品原则

1. **System-first**：先建系统，再出产物。
2. **Brand IR 是唯一事实来源**：所有产出都从 IR 编译得到。
3. **Provenance**：区分"品牌事实"和"AI 推断"。
4. **Gate 驱动决策**：帮用户快速做决定，不搞无限修改。
5. **Brand Skill 自包含**：运行时不依赖 DesignBuddy，不制造锁定。
6. **原生安装 + 明确确认**：不静默修改用户环境。
7. **Contextual Brand Runtime**：按语境调用；多品牌时必须消歧；不做全局默认。
8. **Capability-first**：先探测运行能力，不假设操作系统或解释器；QA 不能被静默跳过。
9. **隐私与许可优先**：原始资料不进入 Skill；字体和素材默认不打包。
10. **Token 成本是设计目标**：采用 Progressive Disclosure。

## 5. 与 WorkBuddy Skill Creator 的差异（商业定位）

| | WorkBuddy Skill Creator | DesignBuddy |
|---|---|---|
| 定位 | Generic Skill Builder | Professional Brand System Compiler |
| 输入 | 用户描述的任意需求 | 品牌资料 + 资产 + 偏好 + 设计决策 |
| 方法论 | 无领域方法 | Brand Discovery、视觉方向、色彩、字体、版式体系 |
| 中间层 | 无 | Brand IR + Provenance + 版本 |
| 质量保障 | 无领域 QA | 无障碍放行关卡、Brand QA、包 lint、Runtime 自测 |
| 治理 | 无 | 资产、字体、来源 manifest，许可治理 |
| 产出 | 一个 Skill | Brand Skill + Portable Design System + Tokens + 模板 + Preview + Source Report |
| 多品牌 | 不涉及 | 消歧规则 + 测试 |

**竞争壁垒**来自以下方面，而不是 prompt 本身，也不依赖加密：

- 专业设计方法论、Brand IR、多源品牌抽取、人机审核流程；
- 跨媒介系统、Design Tokens、Brand QA、无障碍检查；
- 资产与许可治理、Skill 编译器、Portable 导出、Runtime 验证；
- 未来的模板库和行业设计包。

## 6. 用户旅程

### 6.1 New Brand（从零开始）

1. 用户说"帮我做一套品牌系统"。DesignBuddy 探测运行环境，在本地建立 Workspace，并说明大约需要多少轮对话、每轮做什么。
2. **Discovery**（不直接问"你的主色是什么"），依次了解：
   - 做什么；
   - 面向谁；
   - 想给人什么感觉；
   - 与竞品有什么不同；
   - 不想要什么感觉；
   - 喜欢哪些参考。
3. **G1 Foundation**：确认定位、性格、语气。
4. **G2 Visual Direction**：给出 2–3 个方向，例如 Quiet Professional / Editorial Modern / Bold Technical。每个方向包含情绪关键词、色板、字体组合，以及一个小样例。用户选一个。
5. **G3 Core System**：确认颜色、字体、间距、栅格、Logo 规则，同时附上无障碍检测结果。
6. **G4 Applications**：确认 Word、PPT、Excel、PDF、Web、海报、社交媒体的规则。
7. **G5 Preview**：审核海报、落地页、One-pager 三个样例。
8. **G6 Export**：查看最终摘要，确认是否安装。
9. **安装与自测**：执行原生安装，运行 Smoke Test，然后告诉用户以后怎样触发这个 Skill。
10. **交付**：Brand Skill 已安装；同时提供 Portable 包、Preview 和 Source Report。

### 6.2 Partial Brand

1. 用户上传 Logo、主色和历史 PPT。
2. DesignBuddy 抽取信息，进行 Gap Analysis，向用户展示哪些部分是已有的、哪些需要补全。
3. G1 时确认保留已知规则；G2 只针对缺失部分给出方向。
4. 后续流程与 New 相同。

### 6.3 Existing Brand

1. 用户上传品牌手册、VI、PPT、网站、代码等资料。
2. DesignBuddy 执行：抽取 → 归一化 → 冲突检测（例如"主色出现了 #0057FF 和 #0A5CFF 两种，请裁决"）。
3. 用户确认后进入 G3、G4，跳过 G2，或把 G2 简化为"现状确认"。
4. 原则是**保留现有品牌，不重新设计**。

### 6.4 续做与升级

- **续做**：用户说"继续做 ACKS 的品牌系统"，DesignBuddy 读取 Workspace 状态，从中断处继续。
- **升级**：用户说"ACKS 换主色了"，DesignBuddy 修改 IR，执行 IR diff，给出版本号建议，然后重新编译，并在用户确认后升级安装。

### 6.5 日常使用（Brand Skill 运行时）

- 用户说"帮 ACKS 做一份融资 PPT"，ACKS Brand Skill 被触发，按以下顺序工作：
  1. 按路由加载 brand-core、color、typography、ppt 这几份规范；
  2. 生成初稿（Draft）；
  3. 执行 Brand QA；
  4. 修正问题（Fix）；
  5. 输出终稿（Final）。
- 用户说"帮我做个 PPT"，且没有任何品牌线索：Brand Skill 不应被擅自套用，或在被调用后先询问用户要用哪个品牌。

## 7. 功能需求

### 7.1 Intake 与 Discovery

| ID | 需求 | 优先级 |
|---|---|---|
| FR-01 | 运行环境探测（Capability-first），结果写入 Workspace | P0 |
| FR-02 | 创建 Workspace 并支持断点续做；支持多品牌项目 | P0 |
| FR-03 | 根据上传材料建议入口路径（Existing / Partial / New），由用户确认 | P0 |
| FR-04 | 接收并登记原始资料（source-manifest），标记是否包含敏感信息 | P0 |
| FR-05 | 从 Logo、PPT、PDF、截图、网站、代码中抽取颜色、字体、版式特征（具体可抽取的范围以运行时能力为准） | P0 |
| FR-06 | 无品牌用户的 Discovery 问题集（分轮提问，每轮不超过 3–4 个问题） | P0 |
| FR-07 | 参考品牌只提炼原则，不复制资产 | P0 |

### 7.2 Brand IR

| ID | 需求 | 优先级 |
|---|---|---|
| FR-10 | Brand IR 的 Schema、校验和版本管理 | P0 |
| FR-11 | 每条事实带 Provenance（来源类型、证据、置信度、审核状态） | P0 |
| FR-12 | 检测冲突，并提交用户裁决 | P0 |
| FR-13 | 对缺失或不完整的部分做 Gap Analysis | P0 |
| FR-14 | 规则按 MUST / SHOULD / AVOID / NEVER 分级，并带 id | P0 |
| FR-15 | IR diff 与版本号建议 | P1 |

### 7.3 Gates

| ID | 需求 | 优先级 |
|---|---|---|
| FR-20 | G1–G6 各个 Gate，只接受 KEEP / CHANGE / REJECT 三种反馈 | P0 |
| FR-21 | 把模糊反馈引导成具体修改 | P0 |
| FR-22 | 同一 Gate 连续 3 轮 CHANGE 后给出 A/B 方案收敛 | P1 |
| FR-23 | 审核时优先展示 INFERRED、GENERATED、低置信度和有冲突的项 | P0 |

### 7.4 设计系统

| ID | 需求 | 优先级 |
|---|---|---|
| FR-30 | 色彩系统：主色、辅色、强调色、中性色、语义色、色阶、使用比例 | P0 |
| FR-31 | 字体系统：中英文配对、字号阶梯、行高、字重、fallback、中英混排规则 | P0 |
| FR-32 | 间距、圆角、边框、阴影、栅格（Web、印刷、幻灯片） | P0 |
| FR-33 | Logo 使用规则（安全区、最小尺寸、允许的背景、禁止用法） | P0 |
| FR-34 | 图片、插画、图标、动效风格 | P0 |
| FR-35 | 语气（Voice） | P0 |
| FR-36 | 应用规范：Word、PPT、Excel、PDF、Web、海报、社交媒体 | P0 |

### 7.5 QA

| ID | 需求 | 优先级 |
|---|---|---|
| FR-40 | 无障碍对比度检测，结果为 PASS/WARNING/FAIL；核心组合 FAIL 时阻止放行；支持 USER_OVERRIDE | P0 |
| FR-41 | Brand QA 清单（通用项 + 各媒介专项） | P0 |
| FR-42 | 脚本不可用时由 Agent 兜底，结果标注 UNVALIDATED，不允许静默跳过 | P0 |

### 7.6 编译与导出

| ID | 需求 | 优先级 |
|---|---|---|
| FR-50 | 编译 WorkBuddy Brand Skill（官方结构、高质量 frontmatter、路由、多品牌消歧、QA 循环） | P0 |
| FR-51 | 包 lint：结构、frontmatter、引用、路径、密钥、预算 | P0 |
| FR-52 | Portable 导出：DESIGN.md、tokens.json（DTCG）、tokens.css、brand-ir.json/yaml、README | P0 |
| FR-53 | 资产、字体、来源三类 manifest；字体默认不打包 | P0 |
| FR-54 | Source Report | P0 |
| FR-55 | 3 个 HTML Preview 样例，作为 G5 的审核对象 | P0 |
| FR-56 | Office 模板 .potx / .dotx / .xltx（Advanced Export，失败时降级） | P1 |

### 7.7 安装与验证

| ID | 需求 | 优先级 |
|---|---|---|
| FR-60 | 安装前展示摘要，并取得用户的明确确认 | P0 |
| FR-61 | 原生安装交接：H1 → H4 逐级降级；ZIP 作为 fallback。**不实现 H5**（直接写入 Skill 目录） | P0 |
| FR-62 | 安装后的一致性校验：用 build-manifest 比对文件列表、内容哈希、版本、关键规则、引用；然后做 Runtime Smoke Test | P0 |
| FR-63 | 同名 Skill 升级时说明版本变化，并重新确认 | P0 |
| FR-64 | 备份导出（ZIP + Portable） | P0 |

## 8. 非功能需求

| ID | 需求 |
|---|---|
| NFR-01 | 跨平台：Windows 和 macOS 的 WorkBuddy 客户端都能用；不假设 shell 和解释器 |
| NFR-02 | 零外部依赖：只用 Python 标准库；禁止默认执行 pip 或 npm 安装 |
| NFR-03 | Token 预算（目标值，待实测）：Brand Skill 的 SKILL.md ≤ 2k，单个 reference ≤ 1.5k，单次任务 ≤ 8k |
| NFR-04 | 隐私：原始资料默认不进入 Skill；不向外部服务发送资料；产物中不含绝对路径或密钥 |
| NFR-05 | 确定性：相同 IR 编译出相同产物。基础模板、组件和生成器都是预先构建好的，运行时**不**由 Agent 现场编写 |
| NFR-08 | 本地优先：不经产品负责人批准，不引入服务端编译或云端依赖 |
| NFR-06 | 可恢复：每次 Gate 通过后都保存 IR 快照，可以回滚 |
| NFR-07 | 证据纪律：平台相关的判断标注 OFFICIAL / OBSERVED / DERIVED / UNVERIFIED |

## 9. 商业化

| 项 | 内容 |
|---|---|
| 形态 | WorkBuddy 技能市场的 **Paid Skill**（买断制） |
| 价格 | **TBD**。待产品完成度、开发成本、用户体验、Runtime 验证和市场策略明确后再定。平台 UI 文案显示价格须为 1–9999 的整数（OBSERVED，来自前端文案，以提交时实际为准），因此不能定 19.9 |
| 不可更改项 | 付费方式上架后不可更改（UI 文案 OBSERVED）；改价次数每年有限 |
| 对外表述 | 只说 "Paid Skill"。区分三个概念：Paid Skill（销售机制）、Encrypted Skill（平台加密选项）、Source Protection（实际保护效果）。实际保护能力未经测试前，不使用后两种说法（见 PAID_SKILL_PROTECTION_VALIDATION.md） |
| 免费版 | 不做。产品负责人已有其他免费 Skill |
| 服务类目（个人主体） | 主类目"工具 → 办公"，辅类目"工具 → 图片处理"；市场分类选"设计"。提交当天需复核官方类目页 |
| 发布主体 | 已认证的个人开发者，已有审核通过的 Skill 和专家，满足开通收款的前置条件 |

## 10. V1 范围

**V1 必须跑通的链路**：

```
Brand Discovery → Brand IR → Design System → Preview → Brand Skill → Install → Runtime Test
```

- **包含**：FR 中所有 P0 项；FR-56（Office 模板）尽力而为。
- **不包含**：模板市场、行业设计包、品牌审计、Drift 检测、团队与多组织协作、Figma Connector、云端资产库、Buddy App 的 Mode-level Harness、完整 Node 版脚本。

## 11. 成功指标（发布后观察）

| 指标 | 目标（初始值，待校准） |
|---|---|
| 完成率：从 Intake 到安装成功 | ≥ 60% |
| 平均 Gate CHANGE 轮次 | ≤ 2 |
| 安装成功率（任意一种 H 方式） | ≥ 95% |
| 品牌明确的请求触发命中率 | ≥ 90% |
| 无品牌线索请求的误套用率 | ≤ 5% |
| 单次品牌任务的 token 消耗 | 低于预算 |
| 用户评分与复购 | 以平台数据为准 |

## 12. 发布标准（Release Criteria）

1. validation-plan 中所有 **Blocker** 级用例都有结论，结论为 PASS 或"已有可接受的降级方案"。
2. 用 Alpha / Beta 两个虚构品牌，分别在 Windows 和 macOS 上走完端到端链路。
3. 多品牌消歧测试通过。
4. 包通过 lint 和 WB-OPDK 的 `validate_skill.py`。
5. Paid Skill 保护验证完成，对外文案与验证结论一致。
6. 提交当天复核官方 Skill 文档、服务类目和付费规则。

## 13. 依赖与开放问题

- 平台能力的证据等级：[`runtime-capabilities.md`](runtime-capabilities.md)
- 开放问题：[`open-questions.md`](open-questions.md)
- 验证计划：[`validation-plan.md`](validation-plan.md)
