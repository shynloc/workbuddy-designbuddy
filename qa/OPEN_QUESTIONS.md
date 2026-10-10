# OPEN_QUESTIONS — DesignBuddy QA v0.1.0

下表是这一轮真机测试需要回答的问题。"对应用例"一列指向会产生证据的测试。

| ID | 问题 | 影响 | 对应用例 |
|---|---|---|---|
| Q-01 | WorkBuddy 的 Skill 执行环境（macOS / Windows）中，`python3` / `python` / `py -3` 哪个可用？ | 决定是否需要无 Python 的降级方案 | ENV-001、ENV-009 |
| Q-02 | Windows 上 Agent 读取命令输出时用什么编码？CLI 输出 UTF-8 JSON，中文是否会乱码？ | 报告可读性 | ENV-009（请在报告中注明是否乱码） |
| Q-03 | Agent 的工具列表中是否有原生安装 Skill 的工具（H1）？第三方 Skill 能否调用？ | 安装主路径 | INS-001 |
| Q-04 | 内置 Skill Creator 能否"原样"安装指定的 ZIP 或目录，还是会重新生成内容？ | H2 是否可用 | INS-002、INS-005 |
| Q-05 | 用户在对话中发 ZIP 并要求原样安装，是否走原生安装、是否保持内容不变？ | H3 体验 | INS-003、INS-005 |
| Q-06 | `templates/` 下的多级子目录（data/、fixtures/、brand-skill/…）能否被平台正常解析和保留？ | 包结构 | PKG-004（package-manifest 能检出缺失或改动） |
| Q-07 | Skill 运行时能否写入用户的项目文件夹？默认工作目录在哪里？ | 报告与 Workspace 的位置 | ENV-003、ENV-004 |
| Q-08 | 多个 Brand Skill 共存时，模型实际怎样调度？无品牌请求是否会被误套？ | 多品牌设计是否成立 | MB-003..005 |
| Q-09 | frontmatter 中的全角尖括号（用于让 `<` `>` 失效）在 WorkBuddy UI 中显示是否正常？ | 极端品牌名的显示 | 人工观察 |
| Q-10 | 付费加密后，脚本能否执行、模板能否读取、产物能否输出？开发者与购买者是否一致？ | D-03 / Compiler 架构 | PP-002、PP-003（需要你批准付费测试） |
| Q-11 | 一次 QA RUN ALL 在真机上的耗时和 Token 消耗 | 体验与成本 | 请在报告中注明 |
| Q-12 | Brand Skill 的 `author` 默认用品牌名是否合适？ | frontmatter | 产品决定 |
