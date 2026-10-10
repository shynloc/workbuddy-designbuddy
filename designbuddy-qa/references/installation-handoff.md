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

## 2. 交接方式

已经确认（OBSERVED，WorkBuddy 5.7.7，产品负责人实测）：**客户端有专门的"技能导入"入口，可以从本地上传 Skill ZIP 并安装。** 这是 V1 的主路径（H4）。Agent 侧的安装通道（H1/H2/H3a）实测都不可行，所以不必尝试。

### 主路径：交付到下载文件夹 → 用户在客户端导入（H4）

1. 用户确认后，执行：

   ```
   <PY> "<SKILL>/scripts/designbuddy.py" deliver --workspace "<WS>"
   ```

   - 也可以在构建时直接加参数：`build --deliver`。
   - 交付包会复制到 `<下载>/DesignBuddy/<品牌>/`，里面包括：Brand Skill ZIP、Portable ZIP、preview/、source-report.md、安装说明.txt。
   - 不会覆盖已有文件：同名的不同文件会加序号，相同的文件会跳过。
   - 找不到下载文件夹时，问用户一次希望放在哪里，然后用 `--to "<文件夹>"`。
2. 告诉用户：

   > 交付包已放在 <folder>。请打开 WorkBuddy 的技能管理，使用"导入 / 上传本地技能"，选择 <skill_zip>。

3. 用户导入后，按第 3 节做安装后核对。

### 其他方式

| 方式 | 结论 |
|---|---|
| H1 `search_and_install_skills` | 只支持技能市场，不适用于本地包 |
| H2 `skill-creator` | 没有安装器 |
| H3a 发送路径文字 | 会被转给市场安装器，不可行 |
| H3b 把 ZIP 作为附件发进对话 | 未验证，可以作为备选告诉用户 |
| ~~H5~~ | **禁止**：Agent 不得自己把文件写入、复制或解压到 WorkBuddy 的 Skill 目录 |

## 3. 安装后核对（不能只看"安装成功"的提示）

1. 在已安装的 Brand Skill 中运行 `scripts/selfcheck.py`，按结果处理：

   | 结果 | 含义 | 处理 |
   |---|---|---|
   | `MATCH` | 所有文件的 SHA-256 与 `templates/build-manifest.json` 一致 | 通过 |
   | `PLATFORM-META` | 平台添加的元数据（例如 `_user_meta.json`） | 正常，不读取其内容 |
   | `MATCH_WITH_EXTRA`（退出码 3） | 存在未知的额外文件 | 必须向用户说明 |
   | `MISMATCH` | 文件被改写 | 安装失败 |
2. 核对 frontmatter 中的版本，以及 `build_id`。
3. 抽查 `references/color.md` 中主色的值，与构建时一致。
4. 告诉用户以后怎样触发：

   > 以后说"给 <品牌名> 做一份……"即可。

   并说明：多个品牌同时安装时，没有指明品牌的请求不会被自动套用。
