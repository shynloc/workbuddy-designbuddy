# 安装交接

原则：DesignBuddy 负责生成正确的 Skill；安装交给 WorkBuddy 的原生机制完成。

## 1. 安装前必须确认（不得静默安装）

先向用户展示下面的摘要（数值从 `build` 返回的 JSON 中读取）：

> 你的品牌 Skill 已准备完成。
>
> - 名称：<skill>（版本 <skill_version>，Design System <system_version>，build <build_id>）
> - 包含：品牌核心、Logo、语气、颜色、字体、间距版式、图片、图标、无障碍、PPT、Word、Excel、网页、海报、社交媒体、QA 清单、许可说明
> - 不包含：你的原始资料、字体文件、未授权素材
> - 安装包：<skill_zip>
>
> 是否现在安装到 WorkBuddy？

- 只有用户**明确回复同意**后才能继续。
- 如果已存在同名 Skill，要先说明这是升级（旧版本 → 新版本），再次确认。

## 2. 交接方式（依次尝试，记录每一种的实际结果）

| 方式 | 做法 | 失败时 |
|---|---|---|
| H1 原生工具 | 检查你可用的工具中，是否有安装、导入或创建 Skill 的工具。有就传入 ZIP 或目录 | 没有 → 记录"无此工具"（BLOCKED） |
| H2 Skill Creator | 调用 WorkBuddy 内置的 Skill Creator，要求它**原样安装**指定的 ZIP 或目录，**不得重新生成或修改任何文件** | 它改写了文件 → 记为 FAIL，并告知用户 |
| H3 用户一句话 | 给用户一句可以直接复制的话：`请把这个 ZIP 原样安装为 Skill，不要修改任何文件内容：<skill_zip>` | — |
| H4 ZIP 导入 | 告诉用户 ZIP 的路径，请用户通过 WorkBuddy 的 Skill 导入入口手动安装 | — |
| ~~H5~~ | **禁止**：不得把文件写入或复制到 WorkBuddy 内部的 Skill 目录 | — |

## 3. 安装后核对（不能只看"安装成功"的提示）

1. 在已安装的 Brand Skill 中运行 `scripts/selfcheck.py`。必须得到 `overall: MATCH`：所有文件的 SHA-256 与 `templates/build-manifest.json` 一致，并且没有多余文件。
2. 核对 frontmatter 中的版本，以及 `build_id`。
3. 抽查 `references/color.md` 中主色的值，与构建时一致。
4. 告诉用户以后怎样触发：

   > 以后说"给 <品牌名> 做一份……"即可。

   并说明：多个品牌同时安装时，没有指明品牌的请求不会被自动套用。
