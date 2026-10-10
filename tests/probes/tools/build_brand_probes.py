#!/usr/bin/env python3
"""Generate the fictional brand probe skills (brand-alpha, brand-beta).

A miniature of the DesignBuddy compiler: one data dict per brand -> a full
WorkBuddy Brand Skill following the R1 runtime spec (brand resolution,
routing, MUST/NEVER rules, QA loop). Both brands are fictional and contain
no real assets. Re-run after editing BRANDS; outputs are committed.

    python3 tests/probes/tools/build_brand_probes.py
"""
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBES = HERE.parent

BRANDS = {
    "brand-alpha": {
        "slug": "alpha-demo",
        "name": "Alpha Demo",
        "name_zh": "阿尔法示例",
        "aliases": ["Alpha", "Alpha Demo", "阿尔法示例", "阿尔法"],
        "other": "Beta Demo",
        "personality": "冷静、精确、科技感",
        "voice": "简洁、陈述句、少用感叹号",
        "colors": {
            "primary": ("#1F4FD8", "Alpha Blue", "标题强调、按钮、图表主序列"),
            "ink": ("#111827", "Ink", "正文文字"),
            "paper": ("#FFFFFF", "Paper", "页面背景"),
            "mist": ("#EEF2FF", "Mist", "卡片与分区背景"),
            "accent": ("#B45309", "Signal Amber", "少量高亮、数据标注点；禁止用作文字色"),
        },
        "heading_font": "Source Han Sans SC（思源黑体）",
        "body_font": "Source Han Sans SC（思源黑体）",
        "fallback": "PingFang SC, Microsoft YaHei, sans-serif",
        "heading_weight": "700",
        "radius": "8px",
        "ppt": "16:9；左对齐网格，左右边距 64px；标题页使用 Alpha Blue 满版背景 + 白色标题；内容页白底；每页最多 1 个强调色元素",
        "poster": "大面积留白（≥40%）；标题左上对齐；Alpha Blue 色块不超过画面 30%；几何线条作为辅助图形",
        "imagery": "冷色调、干净的产品或抽象几何画面；不使用卡通插画",
        "never": [
            ("NEVER-LOGO-01", "不得拉伸、旋转 Logo，不得为 Logo 添加阴影或描边"),
            ("NEVER-COLOR-01", "不得使用色板以外的颜色（图片内容除外）"),
            ("NEVER-COLOR-02", "Signal Amber 不得用作正文或标题文字颜色"),
        ],
    },
    "brand-beta": {
        "slug": "beta-demo",
        "name": "Beta Demo",
        "name_zh": "贝塔示例",
        "aliases": ["Beta", "Beta Demo", "贝塔示例", "贝塔"],
        "other": "Alpha Demo",
        "personality": "温暖、人文、杂志感",
        "voice": "亲切、叙述感、允许适度修辞",
        "colors": {
            "primary": ("#9A3412", "Beta Rust", "标题、引言线、按钮"),
            "ink": ("#1C1917", "Charcoal", "正文文字"),
            "paper": ("#FFF7ED", "Cream", "页面背景"),
            "sand": ("#FED7AA", "Sand", "装饰色块、分区背景"),
            "accent": ("#0F766E", "Teal Note", "链接与少量点缀"),
        },
        "heading_font": "Source Han Serif SC（思源宋体）",
        "body_font": "Source Han Sans SC（思源黑体）",
        "fallback": "Songti SC, SimSun, serif / PingFang SC, Microsoft YaHei, sans-serif",
        "heading_weight": "600",
        "radius": "2px",
        "ppt": "16:9；杂志式不对称网格；标题页 Cream 背景 + Beta Rust 衬线大标题；引言使用左侧 4px Beta Rust 竖线",
        "poster": "衬线大标题居中或底部对齐；Cream 底色；允许大幅人物或生活方式摄影；文字压图时必须加 Charcoal 60% 遮罩",
        "imagery": "暖色调、自然光、生活方式摄影；可使用手绘质感插画",
        "never": [
            ("NEVER-LOGO-01", "不得拉伸、旋转 Logo，不得为 Logo 添加阴影或描边"),
            ("NEVER-COLOR-01", "不得使用色板以外的颜色（图片内容除外）"),
            ("NEVER-TYPE-01", "标题不得使用无衬线字体"),
        ],
    },
}

FRONT = """---
name: {slug}-brand-system
display_name: {name} 品牌设计系统（测试）
display_name_en: {name} Brand System (Test)
description: 当用户为 {name}（{name_zh}；别名：{aliases}）创建、修改或审核 PPT、Word、Excel、PDF、网页、海报、社交媒体视觉或其他品牌物料时，使用本品牌设计系统。用户未提及该品牌且语境不明确时不要使用。{name} 是 DesignBuddy 测试用的虚构品牌。
description_zh: {name}（{name_zh}）虚构测试品牌的设计系统：颜色、字体、版式、图片风格与品牌 QA。
description_en: Design system for the fictional test brand {name} — colors, type, layout, imagery and brand QA.
version: 1.0.0
author: DesignBuddy Dev
user-invocable: true
disable-model-invocation: false
---
"""

BODY = """
# {name} 品牌设计系统（DesignBuddy 测试品牌）

> 由 DesignBuddy Probe 生成器生成 · Skill 1.0.0 · Design System 1.0.0 · 虚构品牌，仅用于测试

## 0. 测试仪器（仅测试版有）

只要本 Skill 被使用，回复的**第一行**必须是：

`【品牌系统】{name} v1.0.0（{slug}-brand-system）`

这一行用来让测试者看到实际触发的是哪个品牌 Skill。

## 1. 品牌识别与消歧

1. 用户明确提到 {name} 或别名（{aliases}）→ 使用本系统。
2. 当前对话已经明确在为 {name} 工作 → 可以继续使用，并在第一行声明。
3. 用户没有提到任何品牌，且语境不明确（例如只说"做一份 PPT"）→ **不要擅自套用**。先问用户："要使用哪个品牌的设计系统？还是不使用品牌规范？"
4. 本系统不是默认品牌，也不会全局生效。
5. 品牌转换：例如"把 {other} 的文档改成 {name} 风格"，此时 source = {other}，target = {name}。输出只遵循 {name} 的规则；{other} 的规则只用来识别需要替换的元素，不得混用。如果用户要求的是相反方向（把 {name} 改成 {other} 风格），则本系统是 source，不得把本系统的规则应用到输出上。

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

{rules}

## 5. 工作流

Draft → Brand QA（@references/qa-checklist.md ）→ Fix → Final。

QA 报告格式：

```
Brand QA: PASS/FAIL | 违反规则: <id 列表或 无> | 已读取: <加载标记列表> | 校验: VALIDATED/UNVALIDATED
```

## 6. 脚本

如果有可用的 Python，用 `scripts/validate_contrast.py --tokens templates/tokens/tokens.json` 校验配色组合，结果标注 VALIDATED。

如果没有可用的 Python，手工核对 @references/color.md 中列出的组合，结果标注 UNVALIDATED。
"""


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))


def tokens_json(b):
    colors = {k: {"$value": v[0], "$type": "color", "$description": "%s — %s" % (v[1], v[2])}
              for k, v in b["colors"].items()}
    pairs = [
        {"name": "body text / page", "fg": "color.ink", "bg": "color.paper"},
        {"name": "primary text / page", "fg": "color.primary", "bg": "color.paper"},
        {"name": "page text / primary fill", "fg": "color.paper", "bg": "color.primary"},
        {"name": "body text / tint surface", "fg": "color.ink", "bg": "color.%s" % list(b["colors"])[3]},
        {"name": "accent / page (UI only)", "fg": "color.accent", "bg": "color.paper", "large": True},
    ]
    return {
        "$description": "%s design tokens (W3C DTCG format). Fictional test brand." % b["name"],
        "color": colors,
        "font": {
            "heading": {"$value": b["heading_font"], "$type": "fontFamily"},
            "body": {"$value": b["body_font"], "$type": "fontFamily"},
        },
        "radius": {"base": {"$value": b["radius"], "$type": "dimension"}},
        "$extensions": {"dbprobe.contrastPairs": pairs},
    }


def build(folder, b):
    root = PROBES / folder
    if root.exists():
        shutil.rmtree(root)
    aliases = "、".join(b["aliases"])
    rules = [("MUST-TYPE-01", "MUST", "所有一级标题使用 %s，字重 %s" % (b["heading_font"], b["heading_weight"])),
             ("MUST-COLOR-01", "MUST", "主色固定为 %s（%s）" % (b["colors"]["primary"][0], b["colors"]["primary"][1]))]
    rules += [(rid, "NEVER", text) for rid, text in b["never"]]
    rules_md = "\n".join("- `%s` **%s** %s" % r for r in rules)
    ctx = dict(b, aliases=aliases, rules=rules_md)
    write(root / "SKILL.md", FRONT.format(**ctx) + BODY.format(**ctx))

    tag = b["slug"].split("-")[0].upper()
    color_rows = "\n".join("| `color.%s` | %s | `%s` | %s |" % (k, v[1], v[0], v[2]) for k, v in b["colors"].items())
    refs = {
        "brand-core.md": "# 品牌核心\n\n加载标记：`%s-REF-CORE`\n\n- 品牌：%s（%s），虚构测试品牌\n- 性格：%s\n- 语气：%s\n- 图片风格：%s\n"
                         % (tag, b["name"], b["name_zh"], b["personality"], b["voice"], b["imagery"]),
        "color.md": "# 颜色\n\n加载标记：`%s-REF-COLOR`\n\n| token | 名称 | 值 | 用途 |\n|---|---|---|---|\n%s\n\n"
                    "必须达标的组合：正文 / 页面背景 ≥ 4.5:1；页面背景色文字 / 主色填充 ≥ 4.5:1；强调色仅限非文字 UI（≥ 3:1）。\n"
                    % (tag, color_rows),
        "typography.md": "# 字体\n\n加载标记：`%s-REF-TYPE`\n\n| 角色 | 字体 | 字重 |\n|---|---|---|\n| 标题 | %s | %s |\n| 正文 | %s | 400 |\n\n"
                         "回退字体：%s\n\n字号阶梯（PPT）：标题 40 / 小标题 28 / 正文 18 / 注释 12。\n\n"
                         "字体文件不随本 Skill 分发；请使用本机已安装的字体或回退字体。\n"
                         % (tag, b["heading_font"], b["heading_weight"], b["body_font"], b["fallback"]),
        "ppt.md": "# PPT 规范\n\n加载标记：`%s-REF-PPT`\n\n- %s\n- 图表：主序列使用主色，其余序列使用中性色。\n- 每页只表达一个核心观点。\n" % (tag, b["ppt"]),
        "poster.md": "# 海报 / 社交媒体视觉\n\n加载标记：`%s-REF-POSTER`\n\n- %s\n- 尺寸：小红书 1242×1660；公众号封面 900×383；竖版 1080×1920。\n" % (tag, b["poster"]),
        "qa-checklist.md": "# Brand QA\n\n加载标记：`%s-REF-QA`\n\n- [ ] Logo：没有违反 NEVER-LOGO-01\n- [ ] 颜色：只使用色板中的颜色；主色用法正确\n"
                           "- [ ] 字体：标题和正文字体正确\n- [ ] 对比度：达到 color.md 中的阈值\n- [ ] 版式：遵守对应媒介的规范\n"
                           "- [ ] 内容：没有擅自改写用户的业务内容\n" % tag,
    }
    for name, text in refs.items():
        write(root / "references" / name, text)
    write(root / "templates" / "tokens" / "tokens.json", json.dumps(tokens_json(b), ensure_ascii=False, indent=2) + "\n")
    write(root / "scripts" / "validate_contrast.py", (HERE / "validate_contrast.py").read_text(encoding="utf-8"))
    print("built", root)


if __name__ == "__main__":
    for folder, data in BRANDS.items():
        build(folder, data)
