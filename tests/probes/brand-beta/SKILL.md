---
name: beta-demo-brand-system
display_name: Beta Demo 品牌设计系统（测试）
display_name_en: Beta Demo Brand System (Test)
description: 当用户为 Beta Demo（贝塔示例；别名：Beta、Beta Demo、贝塔示例、贝塔）创建、修改或审核 PPT、Word、Excel、PDF、网页、海报、社交媒体视觉或其他品牌物料时，使用本品牌设计系统。用户未提及该品牌且语境不明确时不要使用。Beta Demo 是 DesignBuddy 测试用的虚构品牌。
description_zh: Beta Demo（贝塔示例）虚构测试品牌的设计系统：颜色、字体、版式、图片风格与品牌 QA。
description_en: Design system for the fictional test brand Beta Demo — colors, type, layout, imagery and brand QA.
version: 1.0.0
author: DesignBuddy Dev
user-invocable: true
disable-model-invocation: false
---

# Beta Demo 品牌设计系统（DesignBuddy 测试品牌）

> 由 DesignBuddy Probe 生成器生成 · Skill 1.0.0 · Design System 1.0.0 · 虚构品牌，仅用于测试

## 0. 测试仪器（仅测试版有）

只要本 Skill 被使用，回复的**第一行**必须是：

`【品牌系统】Beta Demo v1.0.0（beta-demo-brand-system）`

这一行用来让测试者看到实际触发的是哪个品牌 Skill。

## 1. 品牌识别与消歧

1. 用户明确提到 Beta Demo 或别名（Beta、Beta Demo、贝塔示例、贝塔）→ 使用本系统。
2. 当前对话已经明确在为 Beta Demo 工作 → 可以继续使用，并在第一行声明。
3. 用户没有提到任何品牌，且语境不明确（例如只说"做一份 PPT"）→ **不要擅自套用**。先问用户："要使用哪个品牌的设计系统？还是不使用品牌规范？"
4. 本系统不是默认品牌，也不会全局生效。
5. 品牌转换：例如"把 Alpha Demo 的文档改成 Beta Demo 风格"，此时 source = Alpha Demo，target = Beta Demo。输出只遵循 Beta Demo 的规则；Alpha Demo 的规则只用来识别需要替换的元素，不得混用。如果用户要求的是相反方向（把 Beta Demo 改成 Alpha Demo 风格），则本系统是 source，不得把本系统的规则应用到输出上。

## 2. 职责边界

- 默认只**应用设计**：信息层级、版式、字体、颜色、图表、视觉、品牌一致性。
- 不改写用户的业务内容。用户明确要求时，才按 @references/brand-core.md 中的语气规则调整文字。

## 3. 任务路由（只读需要的文件）

| 任务 | 读取 |
|---|---|
| PPT / 演示 | @references/brand-core.md · @references/color.md · @references/typography.md · @references/ppt.md |
| 海报 / 社交媒体视觉 | @references/brand-core.md · @references/color.md · @references/poster.md |
| 其他物料（Word、网页等） | @references/brand-core.md · @references/color.md · @references/typography.md |
| 出稿前 | @references/qa-checklist.md |

每个 reference 文件都有一个"加载标记"。在 QA 报告中列出本次实际读取过的加载标记。

## 4. 关键规则

- `MUST-TYPE-01` **MUST** 所有一级标题使用 Source Han Serif SC（思源宋体），字重 600
- `MUST-COLOR-01` **MUST** 主色固定为 #9A3412（Beta Rust）
- `NEVER-LOGO-01` **NEVER** 不得拉伸、旋转 Logo，不得为 Logo 添加阴影或描边
- `NEVER-COLOR-01` **NEVER** 不得使用色板以外的颜色（图片内容除外）
- `NEVER-TYPE-01` **NEVER** 标题不得使用无衬线字体

## 5. 工作流

Draft → Brand QA（@references/qa-checklist.md ）→ Fix → Final。

QA 报告格式：

```
Brand QA: PASS/FAIL | 违反规则: <id 列表或 无> | 已读取: <加载标记列表> | 校验: VALIDATED/UNVALIDATED
```

## 6. 脚本

如果有可用的 Python，用 `scripts/validate_contrast.py --tokens templates/tokens/tokens.json` 校验配色组合，结果标注 VALIDATED。

如果没有可用的 Python，手工核对 @references/color.md 中列出的组合，结果标注 UNVALIDATED。
