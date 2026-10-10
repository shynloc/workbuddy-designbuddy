---
title: DesignBuddy Technical Architecture
status: DRAFT (R2) — D-01/D-02 已接受；D-03 待验证；平台相关部分待 Probe 结果后冻结
last_updated: 2026-10-10
related: DESIGNBUDDY_ARCHITECTURE_REVISION.md · PRD.md · runtime-capabilities.md
---

# DesignBuddy 技术架构

本文是 DesignBuddy 的**实现规格**。设计理由与边界见 [`DESIGNBUDDY_ARCHITECTURE_REVISION.md`](DESIGNBUDDY_ARCHITECTURE_REVISION.md)（下称 *Revision*）。

凡依赖 `UNVERIFIED` / `TO TEST` 平台能力的部分，都会标注对应的验证用例编号。在验证完成之前，**不得在代码里把猜测写成确定逻辑**。

---

## 1. 系统总览

```
                         ┌─────────────────────────── DesignBuddy (Paid Skill, Builder/Compiler) ───────────────────────────┐
 用户资料 / 偏好 / 决策 ──▶│ Intake ─▶ Extract ─▶ Normalize ─▶ Brand IR ─▶ Validate ─▶ Gates(G1–G6) ─▶ Compiler/Exporters │
                         │    ▲                                  │  ▲                                        │                │
                         │    └──────────── Workspace (用户本地, 断点续做) ─────────────────────────────────────┘                │
                         └──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                                             │
                     ┌───────────────────────────────┬───────────────────────────────┬────────┴───────────────┐
                     ▼                               ▼                               ▼                        ▼
           exports/workbuddy-skill/       exports/portable-design-system/     exports/preview/       exports/source-report/
                     │
          Native Install Handoff (H1→H4, 需用户确认)
                     ▼
         {brand}-brand-system  (Contextual Brand Runtime, 自包含, 运行时不依赖 DesignBuddy)
```

DesignBuddy 由三层组成：

| 层 | 内容 | 载体 |
|---|---|---|
| Method | 设计方法论、Gate 协议、话术、规则库 | `SKILL.md` + `references/` |
| Engine | 能力探测、IR 校验、色彩与对比度计算、编译、打包 lint | `scripts/`（只用 Python 标准库） |
| Knowledge | 字体许可库、平台尺寸、行业配色参考、模板骨架 | `references/` + 内嵌在生成器中的数据 |

## 2. DesignBuddy 包结构（付费 Skill 本体）

> **2026-10-11 实现说明**：开放平台只接受两级目录（A10）。实际包结构为 `scripts/db_*.py` 与平铺的 `templates/<类别>.<文件>`，下面的树仅表示逻辑分组。

```
designbuddy/
├── SKILL.md                         # 触发、阶段路由、Gate 协议摘要、关键纪律（≤ 2.5k tokens）
├── references/
│   ├── workflow-gates.md            # G1–G6 定义、KEEP/CHANGE/REJECT、收敛机制、反馈引导话术
│   ├── intake-paths.md              # Existing / Partial / New 判定与流程
│   ├── discovery-guide.md           # 无品牌用户的 Discovery 问题集
│   ├── extraction-guide.md          # 从 Logo/PPT/PDF/网站/截图/代码 抽取设计特征的方法
│   ├── visual-directions.md         # 方向生成方法：原型库、差异化维度、参考提炼规则
│   ├── color-system.md              # 色阶生成、语义色、比例、深色模式
│   ├── typography-system.md         # 中英文字体配对、字号阶梯、行高、fallback
│   ├── layout-system.md             # 间距、栅格、圆角、阴影、构图
│   ├── imagery-system.md            # 摄影、插画、图标、动效
│   ├── voice-system.md              # 语气与措辞
│   ├── application-specs.md         # Word/PPT/Excel/PDF/Web/Poster/Social 规范框架与平台尺寸
│   ├── accessibility.md             # WCAG 组合清单、阈值、USER_OVERRIDE 流程
│   ├── font-licenses.md             # 可商用字体知识库（每条都有来源 URL 和 verified_at）
│   ├── brand-ir-spec.md             # 给 Agent 看的 IR 字段说明（Schema 的人类可读版）
│   ├── compiler-spec.md             # Brand Skill 与 Portable 的输出规范
│   ├── install-handoff.md           # H1–H4 探测与交接、确认话术、安装后比对（H5 不实现）
│   └── capability-fallback.md       # 脚本不可用时 Agent 的手工步骤与 UNVALIDATED 标注
├── scripts/
│   ├── db.py                        # 统一入口：python db.py <command> [...]
│   └── designbuddy/                 # 标准库实现的模块（见 §7）
└── templates/                       # 预置模板体系与标准组件（Web/海报/社交/Office 主题骨架、tokens 模板），由生成器渲染
```

> **默认架构：预置的确定性 Compiler。**
>
> 生成器、规则、数据模型、校验器、模板体系、标准组件、导出逻辑，全部在开发阶段完成并打包进 DesignBuddy。用户使用时，由生成器根据 Brand IR **确定性地**产出品牌专属文件。
>
> 产出的方式是"渲染"：读取模板，再用 IR 中的值填充，然后写出新文件。这与"把模板原样复制给用户"是两回事。
>
> **D-03（CONDITIONAL FALLBACK / PENDING VALIDATION）**：
> - 只有在 T-PRO 证明加密形态下脚本不能执行、或资源不可用时，才逐级降级（降级顺序见 *Revision* §29）。
> - 由 Agent 现场编写模板或生成器，是最后一级降级，**不是默认路径**。
> - 服务端编译需要产品负责人另行批准。

## 3. Brand IR 规范

### 3.1 文件与格式

- 规范格式：`brand-ir/brand-ir.json`，UTF-8 编码（D-01，ACCEPTED）。
- 根级别必须有 `schema_version`（SemVer），与 Brand Design System 的版本（`metadata.system_version`）相互独立。
- 历史快照：每次 Gate 通过后写入 `brand-ir/history/brand-ir.{system_version}.{timestamp}.json`。
- YAML：仅作为导出视图（`brand-ir.yaml`），不作为输入。

### 3.2 Fact 包装

所有可能被审核的值都使用 Fact 包装。纯结构性的字段（如 id）不需要。

```json
{
  "value": <any>,
  "source_type": "USER_CONFIRMED|DOCUMENTED|EXTRACTED|INFERRED|GENERATED",
  "evidence": ["<source-id>#<locator>", "reference:<name>", "decision:<review-id>"],
  "confidence": "high|medium|low",
  "review": "pending|approved|changed|rejected|user_override",
  "note": "<可选>"
}
```

### 3.3 Rule 结构

规则是 Brand Skill 运行时执行的最小单位。

```json
{
  "id": "NEVER-LOGO-01",
  "level": "MUST|SHOULD|AVOID|NEVER",
  "scope": ["identity", "all-media"],
  "text_zh": "不得拉伸、旋转 Logo，不得为 Logo 添加阴影或描边",
  "text_en": "Never stretch, rotate, shadow or outline the logo",
  "check": "manual|script:<name>",
  "provenance": { "source_type": "GENERATED", "confidence": "high", "review": "approved", "evidence": [] }
}
```

### 3.4 顶层结构（V1）

数据模型只描述品牌本身，不包含任何导出格式的细节。

```jsonc
{
  "schema_version": "1.0.0",              // IR 数据模型的版本（必须有）
  "metadata": {
    "system_version": "1.0.0",           // Brand Design System Version
    "generated_by": "DesignBuddy 1.0.0",
    "created_at": "...", "updated_at": "...",
    "path": "existing|partial|new",
    "locale": ["zh-CN", "en"]
  },
  "brand": {
    "name": Fact, "name_en": Fact, "aliases": Fact<string[]>, "slug": "acks",
    "industry": Fact, "audience": Fact, "positioning": Fact,
    "personality": Fact<string[]>, "values": Fact<string[]>, "anti_personality": Fact<string[]>,
    "voice": { "tone": Fact, "preferred_language": Fact<string[]>, "avoid_language": Fact<string[]>, "examples": Fact },
    "identity": {
      "logo": { "primary": AssetRef, "variants": [AssetRef], "clear_space": Fact, "minimum_size": Fact,
                "backgrounds_allowed": Fact, "misuse": [RuleRef] }
    }
  },
  "design_system": {
  "colors": {
    "primary": [ColorToken], "secondary": [ColorToken], "accent": [ColorToken],
    "neutral": [ColorToken], "semantic": { "success": ColorToken, "warning": ..., "error": ..., "info": ... },
    "usage_ratio": Fact,                  // 例如 60/30/10
    "dark_mode": Fact                     // 可选
  },
  "typography": {
    "families": [ { "role": "heading|body|mono|display", "family": Fact, "fallbacks": Fact<string[]>, "font_ref": "font-manifest#id" } ],
    "weights": Fact, "scale": [ { "token": "h1", "size": Fact, "line_height": Fact, "weight": Fact, "tracking": Fact } ],
    "cjk_rules": Fact                     // 中英混排、标点挤压、字距
  },
  "spacing": { "base": Fact, "scale": Fact<number[]> },
  "radius": Fact, "borders": Fact, "shadows": Fact,
  "grid": { "web": Fact, "print": Fact, "slide": Fact },
  "layout": Fact,
  "imagery": Fact, "photography": Fact, "illustration": Fact, "iconography": Fact, "motion": Fact,
  "accessibility": { "target": "WCAG 2.x AA", "pairs": [ContrastResult], "overrides": [Override] }
  },                                      // end design_system
  "applications": { "document": Fact, "presentation": Fact, "spreadsheet": Fact, "web": Fact, "poster": Fact, "social": Fact },
  "rules": [Rule],
  "assets": "→ asset-manifest.json",
  "licenses": "→ font-manifest.json + asset-manifest.json",
  "provenance": { "counts": {...}, "pending": [<json-pointer>] },
  "version": { "system": "1.0.0", "skill": "1.0.0", "changelog": [...] }
}
```

### 3.5 ColorToken

```json
{
  "token": "brand.primary.500",
  "name": "ACKS Blue",
  "hex": Fact,
  "rgb": [0, 87, 255],
  "cmyk": Fact,
  "usage": ["CTA", "标题强调"],
  "avoid": ["大面积背景"]
}
```

- RGB 由 hex 派生，不单独存储为 Fact。
- CMYK 用于印刷，属于可选项，未经印刷校准时标注 `INFERRED`。

### 3.6 校验（`db.py ir validate`）

| 层级 | 检查内容 |
|---|---|
| 结构 | 必填字段、类型、枚举值 |
| 引用 | AssetRef、font_ref、RuleRef 都能解析 |
| 一致性 | 不同位置出现同一个 token 名时数值冲突；字号阶梯单调；间距是基数的倍数（WARNING） |
| 放行 | 存在 `review = pending` 的 MUST/NEVER 规则 → 不能导出；核心对比度组合 FAIL 且没有 override → 不能导出 |

- 输出 JSON 报告，包含 `errors[]`、`warnings[]`、`pending[]`。
- **实现边界**：
  - V1 用标准库自己实现上表中的检查：必填字段、类型、枚举值、交叉引用、业务规则。
  - Python 标准库**不原生支持** JSON Schema 校验，我们也**不宣称**实现了完整的 JSON Schema 规范。
  - 另外附带 `schemas/brand-ir.schema.json`，供有 `jsonschema` 等外部工具的开发者使用。它不是运行时依赖。
- `schema_version` 与当前 DesignBuddy 支持的版本不一致时，先执行迁移（`ws migrate`），再校验。

## 4. Workspace 与状态机

### 4.1 目录

见 *Revision* §7。

- 默认根目录：当前 WorkBuddy 工作目录下的 `designbuddy-workspace/`。可写性由 V-EN-05 确认；不可写时询问用户换一个目录。

### 4.2 `project.json`

```json
{
  "slug": "acks",
  "display_name": "ACKS",
  "path": "partial",
  "created_at": "...",
  "designbuddy_version": "1.0.0",
  "skill_name": "acks-brand-system",
  "versions": { "system": "1.0.0", "skill": "1.0.0" }
}
```

### 4.3 `.designbuddy/state.json`

```json
{
  "phase": "G3_CORE_SYSTEM",
  "gate_status": { "G1": "KEEP", "G2": "KEEP", "G3": "IN_REVIEW" },
  "change_rounds": { "G3": 1 },
  "capabilities": "→ capabilities.json",
  "install": { "method": null, "verified": false },
  "next_action_zh": "确认字号阶梯（H1 40 → 36？）",
  "updated_at": "..."
}
```

### 4.4 阶段状态机

```
INIT → INTAKE → (DISCOVERY | IMPORT_EXTRACT) → G1_FOUNDATION → G2_DIRECTION* → G3_CORE_SYSTEM
     → G4_APPLICATIONS → QA → G5_PREVIEW → G6_EXPORT → INSTALL → RUNTIME_TEST → DONE
* Path A 中 G2 退化为"现状确认"
任一 Gate：KEEP → 下一阶段 · CHANGE → 本阶段重做 · REJECT → 回退一个阶段
```

## 5. Compiler（Exporters）

```
brand-ir.json ──validate──▶ ┬─ skill exporter    ─▶ exports/workbuddy-skill/{slug}-brand-system/
                             ├─ portable exporter ─▶ exports/portable-design-system/
                             ├─ preview exporter  ─▶ exports/preview/
                             └─ report exporter   ─▶ exports/source-report/
```

| Exporter | 产出 | 说明 |
|---|---|---|
| `skill` | SKILL.md, references/*.md, scripts/*.py, templates/**, templates/build-manifest.json | 见 §8；每个文件头写入生成元数据；manifest 记录每个文件的 SHA-256 和 build_id，供安装后比对 |
| `tokens` | tokens.json (W3C DTCG), tokens.css | DTCG：`$value` / `$type` / `$description`；CSS：`--brand-*` 变量 |
| `designmd` | DESIGN.md | YAML frontmatter（tokens）+ Markdown 说明；只用于 Portable |
| `office` | office-theme.xml；.potx / .dotx / .xltx（Advanced） | 用 zipfile 写 OOXML；失败不阻塞 |
| `preview` | poster.html, landing.html, onepager.html | 内联 tokens.css；不依赖外部 CDN |
| `report` | source-report.md + .json | 来源分布、推断清单、override、许可、置信度 |
| `manifests` | asset-manifest.json, font-manifest.json, source-manifest.json | 见 §10 |

### 编译要求

- **确定性**：同一份 IR 加同一个 DesignBuddy 版本，输出应逐字节一致（时间戳和 build_id 除外）。写文件时统一使用 UTF-8 和 LF 换行符。
- **引用写法**：`@references/x.md` 后面必须紧跟空白字符或行尾。WB-OPDK 的校验器会把紧跟其后的中文标点误判为路径的一部分；WorkBuddy 自身的解析器是否有同样问题尚未验证。
- **lint**：编译完成后跑 `db.py package lint`，检查以下内容：
  - 结构（只允许官方的三个子目录）；
  - frontmatter 必填字段；
  - `@references` 路径能找到对应文件；
  - 不含绝对路径和疑似密钥；
  - 包体与 token 预算；
  - ZIP 顶层只有一个目录。

## 6. Capability-first Runtime

### 6.1 探测（`capabilities.json`）

Agent 先用跨 shell 通用的方式依次尝试：`python3 -c ...`、`python -c ...`、`py -3 -c ...`、`node -e ...`。

- 每一项都要真正执行一小段代码，看能否运行成功。只检查版本号不够，因为 Windows 上的 `python` 可能只是 Microsoft Store 的占位程序。
- 选出可用的解释器后，再执行 `db.py env probe` 写出完整报告。

```json
{
  "os": "windows|darwin|linux|unknown",
  "shell_hint": "bash|zsh|powershell|cmd|unknown",
  "python": { "cmd": "py -3", "version": "3.12.4", "ok": true },
  "node": { "cmd": "node", "version": "20.11", "ok": true },
  "fs_writable": { "workspace": true },
  "zip": true,
  "tier": "PY|NODE_MIN|AGENT",
  "probed_at": "..."
}
```

### 6.2 执行分级

| Tier | 条件 | 行为 |
|---|---|---|
| `PY` | 有可用的 Python ≥ 3.8 | 全部能力，结果标注 `VALIDATED` |
| `NODE_MIN` | 无 Python，有 Node | 只提供 Node 版的**对比度计算**和 **IR 校验**（V1 最小集）；其余由 Agent 完成，标注 `UNVALIDATED` |
| `AGENT` | 两者都没有 | Agent 按 `capability-fallback.md` 手工完成；所有 QA 结果标注 `UNVALIDATED`；Office 二进制模板跳过 |

### 6.3 禁止项

- 默认禁止 `pip install` 和 `npm install`。
- 不写死路径分隔符和用户目录，一律用 `pathlib`。
- 不假设固定使用 bash 或 PowerShell 的语法。所有调用都是"解释器 + 脚本 + 参数"的形式。

## 7. 脚本清单（DesignBuddy）

统一入口为 `python <skill>/scripts/db.py <group> <command>`。所有命令都输出 JSON 到 stdout，退出码约定：`0` 成功，`1` 校验失败，`2` 使用错误，`3` 环境不支持。

| 命令 | 作用 |
|---|---|
| `env probe` | 能力探测，写 capabilities.json |
| `ws init/status/snapshot/migrate` | Workspace 初始化、状态、快照、迁移 |
| `ir validate` | IR 校验（§3.6） |
| `ir diff <a> <b>` | 两个 IR 版本的差异，用于升级说明和版本号建议 |
| `color scale <hex>` | 生成色阶（OKLCH 近似） |
| `color contrast --ir` | 对 IR 中所有规定组合做对比度检测，输出 PASS/WARNING/FAIL |
| `font check <family>` | 只检查用户点名的字体是否已安装（V-EN-06） |
| `compile skill/portable/preview/report/office` | 各个 Exporter |
| `package lint/zip` | 包校验与打 ZIP |
| `install verify` | 生成 Smoke Test 用例，并比对安装结果 |

## 8. 生成的 Brand Skill 规格

### 8.1 目录

见 *Revision* §12。

### 8.2 SKILL.md 模板（结构）

```markdown
---
name: acks-brand-system
display_name: ACKS 品牌设计系统
display_name_en: ACKS Brand System
description: 当用户为 ACKS（ACKS Studio；别名：…）创建、修改或审核 PPT、Word、Excel、PDF、网页、海报、社交媒体视觉或其他品牌物料时使用本品牌设计系统。未提及该品牌且语境不明确时不要使用。
description_zh: ACKS 官方品牌设计系统：颜色、字体、版式、图片风格与各类物料规范，含品牌 QA。
description_en: Official ACKS brand design system — colors, type, layout, imagery and media rules with brand QA.
category: design            # 以开放平台当前可选值为准（V-PK-03）
version: 1.0.0              # Brand Skill Version
author: <用户/组织>
user-invocable: true
disable-model-invocation: false
---
# ACKS Brand System
<!-- generated by DesignBuddy 1.0.0 from brand-ir 1.0.0 at … — do not edit; update via DesignBuddy -->

## 1. 品牌识别与消歧        （§10 规则，4–6 行）
## 2. 职责边界              （应用设计，不擅改内容）
## 3. 任务路由              （任务类型 → @references 列表）
## 4. 关键规则              （≤15 条 MUST/NEVER，带 id）
## 5. 工作流                Draft → Brand QA（@references/qa-checklist.md）→ Fix → Final
## 6. 脚本                  （可用时执行 validate_*；不可用 → 手工检查并标注 UNVALIDATED）
## 7. 版本                  Skill 1.0.0 · Design System 1.0.0
```

### 8.3 Brand Skill 自带的脚本（只用标准库，无外部依赖）

- `validate_contrast.py <fg> <bg> [--large]`：计算单个颜色组合的对比度。
- `validate_brand.py <file>`：对 HTML/CSS/SVG 文本产物做静态检查，例如是否使用了未批准的颜色、是否使用了允许的字体。

> 对 Office 二进制产物的检查属于 Future 范围。

## 9. Portable Export 规格

见 *Revision* §13。补充两点：

- **DESIGN.md** 的 frontmatter 包含 `name`、`version` 和精简的 tokens（colors、typography、spacing、radius）。正文按以下顺序编排：Overview → Colors → Typography → Layout → Components → Imagery → Voice → Do / Don't。
  - 格式跟随 Stitch DESIGN.md 的约定（`DERIVED`，见 open-questions Q-11）。
- **README.md** 给出在 Claude Code、Cursor、Codex、Web 项目中的引用方式，例如：引入 tokens.css，或把 DESIGN.md 放在项目根目录。

## 10. Manifests

| Manifest | 位置 | 关键字段 |
|---|---|---|
| source-manifest.json | workspace/sources/ | source, type, sha256, extracted_items, contains_sensitive_data, included_in_final(默认 false), reason |
| asset-manifest.json | templates/assets/ 及 portable/assets/ | filename, type, source, owner, license, redistribution_allowed, included, sha256, notes |
| font-manifest.json | templates/assets/ 及 portable/ | family, style, weights, source, license, license_url, redistribution_allowed, bundled(默认 false), fallbacks, verified_at |

打包时，lint 拒绝以下文件：

- `included = true` 但 `redistribution_allowed = false` 的资产；
- `bundled = true` 但许可证不允许再分发的字体。

## 11. QA 引擎

| QA | 时机 | 实现 |
|---|---|---|
| IR 校验 | 每次 Gate 前后 | `ir validate` |
| 对比度 | G3、G5、导出前 | `color contrast --ir`；FAIL 阻止放行，除非有 override |
| Brand QA（构建期） | G5 样例 | Agent 按清单检查，加上对 HTML 的 `validate_brand` 静态检查 |
| 包 lint | 导出与安装前 | `package lint` |
| Runtime Smoke Test | 安装后 | `install verify` 生成用例，Agent 执行并比对 |

所有 QA 结果都写入 `reviews/qa-*.json`，并标注 `VALIDATED` 或 `UNVALIDATED`。

## 12. Install Handoff

见 *Revision* §14–16。实现上分两部分：

- `install-handoff.md` 规定探测顺序和话术；
- `install verify` 负责一致性比对，包括：Skill 名、版本、一条 MUST 规则的数值、触发句、反例句。

- H1–H4 的可行性全部依赖 T-INS 的验证结果。在验证完成前，**代码中不写死任何一种安装方式**，只按探测结果选择。
- **H5 不实现**（NOT APPROVED FOR V1）。
- 安装后的一致性比对使用 `templates/build-manifest.json` 和 Brand Skill 自带的 `selfcheck`。原型见 `tests/probes/installation-probe`。

## 13. 决策日志

| ID | 决策 | 理由 | 状态 |
|---|---|---|---|
| D-01 | Brand IR 用 JSON 作为唯一事实来源；必须有 `schema_version`；自己实现校验；YAML 只作可选导出 | 标准库支持；跨平台；可校验 | **ACCEPTED** 2026-10-10 |
| D-02 | Project Metadata 用 `project.json` | 同 D-01 | **ACCEPTED** 2026-10-10 |
| D-03 | 由 Agent 现场生成全部文件 | 加密状态下可能不可用的应对措施 | **CONDITIONAL FALLBACK / PENDING VALIDATION**；默认是预置的确定性 Compiler |
| D-04 | V1 的脚本只做 Python 版；Node 只做对比度和 IR 校验两个最小功能 | 控制开发量，同时保证 QA 不被跳过 | 提议 |
| D-05 | Brand Skill 根目录只保留官方结构；CHANGELOG 放进 references/ | 保守遵循官方规范（V-PK-02） | 提议 |
| D-06 | Preview 统一用 HTML，不内嵌外部 CDN | 跨平台、离线可用、风险最低 | 提议 |
| D-07 | Brand Skill 不维护"已安装品牌清单"，消歧只依据品牌线索 | 跨 Skill 可见性未知 | 提议 |
| D-08 | H5（直接写入 WorkBuddy Skill 目录）不进入 V1 | 授权、兼容、注册、升级、覆盖风险 | **DECIDED** 2026-10-10；将来采用需单独批准 |
| D-09 | 安装后必须用 build-manifest 比对文件列表、内容、版本、关键规则、引用 | "安装成功"提示不代表内容一致 | **DECIDED** 2026-10-10 |
| D-10 | 不经批准不引入服务端编译 | 本地优先，保护用户品牌资料 | **DECIDED** 2026-10-10 |
