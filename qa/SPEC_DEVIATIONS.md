# SPEC_DEVIATIONS — DesignBuddy（v0.1.0 起，截至 v1.0.0）

本文记录与 PRD、架构文档或本轮需求不一致的地方，并说明理由。凡是影响产品定义的条目，都标注了"需确认"。

| ID | 规格要求 | v0.1.0 的实际做法 | 理由 | 后续 |
|---|---|---|---|---|
| D-01 | Existing 路径应从 PDF、PPT、Figma、网站中"抽取" | 编译器的输入是结构化的 `brief.json`。由 Agent 阅读用户材料后填写 brief，并在每个值上标注 `source`（记为 DOCUMENTED） | 只用标准库无法可靠解析 PPTX/PDF 的视觉信息；而 Agent 读取图片和文档的能力需要真机验证（runtime-capabilities B7） | v0.2 评估：读取 PPTX/SVG/CSS 中的颜色和字体（标准库 zipfile/xml），产出 EXTRACTED 来源 |
| D-02 | 脚本不产出 `EXTRACTED` 来源类型 | 枚举中有，但 v0.1 的脚本不会产生它 | 同 D-01 | 同 D-01 |
| D-03 | QA 中的 Gate 体现"人机审核" | QA Runner 使用夹具中预设的决策（`fixture_decisions`）自动走完 G1–G6 | 自动化测试需要可重复执行。真实用户的 Gate 交互由 Agent 按 design-workflow 执行 | 真机中由用户实际走一遍 Gate（建议在 v0.2 中增加 UX 人工用例） |
| D-04 | 用户只提供了 Alpha / Beta 两个夹具 | 增加了 `brand-gamma-new`（New 路径）和 12 个畸形输入 | 要覆盖三条路径和各类安全用例 | — |
| D-05 | 架构中的 Portable 包包含 `brand-ir.yaml` | 不输出 YAML | 已决定 JSON 是唯一事实来源，YAML 是可选格式。v0.1 不做，以减少表面积 | 需要时再加（只写，不读） |
| D-06 | 架构中有 IR diff 和 Schema 迁移 | 只校验 `schema_version`，版本不一致时拒绝（E_SCHEMA_VERSION）。没有 diff 和迁移 | v0.1 只有 schema 1.0.0 | 引入 1.1.0 时再实现 |
| D-07 | Office 二进制模板 | 未实现 | 已列为 Advanced Export；规则本身已经可用 | v0.3+ |
| D-08 | 无 Python 时的降级 | 输出 BLOCKED 报告，不提供 Node 版 Runner | 先确认真机的 Python 可用性（ENV-001），再决定是否投入 | 取决于真机报告 |
| D-09 | 多品牌真实触发测试 | QA Runner 只做静态检查（MB-001/002）；MB-003..005 需要在独立新会话中人工执行 | 本会话内模拟没有意义；平台调度只能观察 | — |
| D-10 | Skill frontmatter `category` | 不填写 | 可选值未经验证（runtime-capabilities A8）；它不是必填字段 | 平台确认后补上 |
| D-11 | QA 包包含一个含 `<script>` 的 SVG 样本 | 以 `malicious-svg.txt` 形式存放（扩展名不是 .svg，属于惰性文本），init 时按内容识别为 SVG 并拒绝纳入 | 安全测试需要恶意样本；改成 .txt 是为了避免被包 lint 拦截，也避免被当作图片渲染 | 商业版不包含任何测试夹具 |
| D-12 | Brand Skill 的 `author` | 默认填品牌名 | 在 brief 中未提供作者时的合理默认值 | 由用户在 G6 确认（需确认） |
| D-13 | 报告目录"用户明确选择" | 优先使用当前项目文件夹下的 `DesignBuddy-QA-Reports/`，不确定时问一次 | 减少提问次数 | — |
| D-14 | `references/` 文件名 | Brand Skill 中 PDF 规则合并在 `word.md`；共 17 个 references | 减少文件数量；PDF 与 Word 的文档规则高度重合 | 用户反馈后可拆分 |
| D-15 | 架构要求以对话内安装为主路径（原生安装交接） | V1 的安装方式是：交付到下载文件夹 → 用户在客户端技能导入（H4） | 两轮真机测试证明 Agent 侧没有本地安装通道；H5 被禁止；产品负责人确认 H4 可用，并要求把交付文件放到下载文件夹 | 平台开放本地安装 API 后再评估 |
| D-16 | 发布门槛 G-2 / G-4 / G-5（macOS、多品牌、真实品牌） | 由产品负责人豁免为发布后观察项 | 产品负责人决定 | 见 `dist/v1.0.0/KNOWN_LIMITATIONS.md` |
