# 编译器约定（Compiler Contract）

## brief.json（输入，brief_version 1.0.0）

```json
{
  "brief_version": "1.0.0",
  "path": "existing | partial | new",
  "brand": {
    "name": "品牌名（单行，≤60 字）", "name_zh": "可选", "name_en": "可选",
    "slug": "kebab-case，仅小写字母/数字/连字符，≤48",
    "aliases": ["别名"], "industry": "...", "audience": "...", "positioning": "...",
    "personality": ["..."], "values": ["..."], "anti_personality": ["..."]
  },
  "voice": {"tone": "...", "preferred": ["..."], "avoid": ["..."]},
  "known": {
    "colors": {"primary": "#RRGGBB 或 {\"value\":\"#RRGGBB\",\"source\":\"来源\"} 或 [多个来源观测]",
               "ink": "...", "paper": "...", "accent": "...", "surface": "..."},
    "fonts": {"heading": "字体名", "body": "字体名"},
    "heading_weight": 700, "radius": "8px",
    "rules": [{"id": "NEVER-PHOTO-01", "level": "NEVER", "text": "...", "subject": "可选", "action": "可选"}]
  },
  "discovery": {"keywords": ["..."], "liked_references": ["只提炼原则"]},
  "assets": [{"id": "logo-main", "file": "相对路径", "type": "logo", "owner": "...",
              "license": "user-owned | 许可名 | unknown", "redistribution_allowed": true}],
  "sources": [{"id": "...", "type": "pdf", "name": "...", "contains_sensitive_data": true, "extracted_items": ["colors"]}]
}
```

### 输入规则

- 同一个字段如果有多个不同的观测值，会生成冲突（`conflict-<字段>`），必须在 G3 裁决。
- 资产路径必须是相对路径，不能包含 `..`，也不能是绝对路径。
- 含有脚本的 SVG 会被拒绝纳入。
- `license` 为 unknown，或不允许再分发的资产，不会打包。

## 命令

| 命令 | 作用 |
|---|---|
| `init --brief F --workspace D [--force]` | 录入数据并生成 Brand IR 草稿 |
| `status --workspace D` | 返回 Gate 状态、候选方向、冲突、待重点审核项、下一步 |
| `gate --workspace D --gate Gn --decision KEEP\|CHANGE\|REJECT [--set k=v ...]` | 执行 Gate 决策 |
| `validate --workspace D [--release]` | 校验 IR |
| `preview --workspace D` | 生成离线 Preview，并做 QA |
| `build --workspace D [--force]` | 编译全部产物。已存在不同版本时拒绝覆盖，除非加 `--force`（需用户同意） |
| `run-all --out D` | QA RUN ALL |
| `record ...` | 回填 Agent 或人工用例 |
| `selftest` | 核对本 Skill 是否与发布构建一致 |

### 各 Gate 允许的 `--set` 字段

| Gate | 允许的字段 |
|---|---|
| G1 | `brand.industry`、`brand.audience`、`brand.positioning` |
| G2 | `direction` |
| G3 | `color.<角色>`、`font.heading`、`font.body`、`heading_weight`、`radius`、`resolve.<冲突id>`、`override.<组合名>` |

## Brand IR（schema_version 1.0.0）

### 顶层结构

`schema_version`、`metadata`、`brand`、`design_system`、`applications`、`rules`、`conflicts`、`candidates`、`assets`、`fonts`、`sources`、`gates`、`version`。

### 每个事实（Fact）的格式

```
{value, source_type, confidence, review, evidence}
```

- `source_type`：USER_CONFIRMED / DOCUMENTED / EXTRACTED / INFERRED / GENERATED
- `review`：pending / approved / changed / rejected / user_override

### 规则格式

`{id: LEVEL-领域-两位数, level: MUST|SHOULD|AVOID|NEVER, text_zh, subject, action}`

如果同一个 `subject + action` 同时出现 MUST 和 NEVER/AVOID，会被判定为矛盾并拒绝。

### 校验范围

校验由标准库实现，包括必填字段、类型、枚举、交叉引用和业务规则。**不是**完整的 JSON Schema 校验器。

## 输出（`<WS>/exports/`）

```
workbuddy-skill/<slug>-brand-system/
  SKILL.md, references/（17 个）, scripts/（validate_contrast / validate_brand / selfcheck）,
  templates/tokens/, templates/assets/, templates/build-manifest.json
<slug>-brand-system-<ver>.zip                        ← 安装用，单一根目录
portable-design-system/  DESIGN.md · brand-ir.json · tokens.json(DTCG) · tokens.css · manifests · assets/ · examples/
<slug>-portable-design-system-<ver>.zip
preview/  poster.html · onepager.html（离线）
source-report/  source-report.md · provenance.json
```

### 可复现

- `build_id` = SHA-256（规范化 IR + 编译器版本）。
- 同一输入两次构建，除 `generated_at` 外逐字节相同。

## Agent 禁止事项

- 手改 `exports/` 中的派生文件。要修改，就改 IR 后重新 build。
- 在运行时自己编写模板、生成器或 tokens 来代替编译器。
- 跳过 QA，或把脚本没有执行的检查写成 PASS。
