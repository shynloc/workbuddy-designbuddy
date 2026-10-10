# DesignBuddy QA 测试指南（最短路径，当前版本 v0.1.3）

不需要安装 Python、Node 或配置任何环境。

## 你需要做的 5 步

1. **下载**：仓库中的 `dist/v0.1.3/designbuddy-qa-v0.1.3.zip`。校验值见 `dist/v0.1.3/SHA256SUMS.txt` 和 `PACKAGE_FINGERPRINT.txt`。
   - 如果装过旧版本，请先在 WorkBuddy 中删除旧的 `designbuddy-qa`，以及测试品牌 `alpha-demo-brand-system`、`beta-demo-brand-system`。
2. **安装**：在 WorkBuddy 中安装这个 ZIP。可以把 ZIP 发到对话里，并说"请把这个 ZIP 原样安装为 Skill，不要修改任何文件内容"；也可以用客户端的 Skill 导入入口。请记下你用的是哪种方式。
3. **新开一个会话**，粘贴 [`WORKBUDDY_QA_PROMPT.md`](WORKBUDDY_QA_PROMPT.md) 中的提示词（先替换 `【】` 里的内容）。
4. **只在以下节点回复**：
   - 选择报告保存目录（最多问一次）；
   - 是否允许安装 Alpha / Beta 测试品牌 Skill；
   - 如果走 H3 或 H4，按提示亲自发送安装指令或导入 ZIP。
5. **取走报告**：把 `TEST_REPORT.md` 和 `results.json` 交回给开发 Agent。如果有截图，一起附上。

单次运行大约 1~3 分钟（脚本部分在开发机上不到 1 秒）。安装链路的耗时取决于平台。

## 可选：多品牌新会话测试（MB-003 ~ MB-005）

1. 打开报告目录中的 `next-session-prompts.md`。
2. 每一条测试都**新开一个会话**，粘贴对应的提示词，截图保存回复。
3. 回到 QA 会话，告诉 Agent 每条的结果，让它用 `record` 命令回填；也可以直接把截图交给开发 Agent。

## macOS 和 Windows 都要测

两个平台的结果不能互相代替。建议各跑一次，并分别保存报告。

## 测试结束后的清理

1. 在 WorkBuddy 中删除以下测试 Skill：
   - `designbuddy-qa`（如果不再测试）
   - `alpha-demo-brand-system`
   - `beta-demo-brand-system`
2. 报告目录中的 `artifacts/` 可以删除。报告文件（TEST_REPORT.md、results.json）请保留到下一轮修复完成。
3. 本测试不会修改你已有的正式 Skill 和专家，不会联网，也不会发布任何东西。
