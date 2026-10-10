# Agent 手写回退规格（仅在没有可用 Python 时使用）

用途：测试"Agent 能否不借助脚本，直接把一个 Skill 写到磁盘"（V-IN-01 的回退路径）。
这样产出的结果**一律标注 UNVALIDATED**，因为没有哈希清单可以比对。

在 `dbprobe-results/generated/manual/dbprobe-generated-hello/` 下写入两个文件，内容逐字照抄，不要增删任何字符。

## 文件 1：SKILL.md

```
---
name: dbprobe-generated-hello
display_name: DesignBuddy 安装验证样品（手写）
display_name_en: DesignBuddy Install Verification Sample (manual)
description: DesignBuddy 开发测试专用。仅当用户明确说“运行 DesignBuddy 安装验证”时使用；复述构建标记。不要在其他任何场景使用。
description_zh: DesignBuddy 开发测试专用安装验证样品（手写版）。
description_en: DesignBuddy test-only install verification sample (manual build).
version: 1.0.0
author: DesignBuddy Dev
---

# DesignBuddy 安装验证样品（手写版）

构建标记：`DBP-GEN-MANUAL-Z9`

被调用时，复述构建标记，并读取 @references/rules.md ，复述 MUST-COLOR-01 的值。
```

## 文件 2：references/rules.md

```
# Rules

| id | level | rule |
|---|---|---|
| MUST-COLOR-01 | MUST | 主色固定为 `#2F6FEB` |
```
