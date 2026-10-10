# WorkBuddy QA 测试提示词（v0.1.1，第 2 轮）

使用前，先把 `【】` 里的内容换成你的实际情况。上一轮的提示词见 `history/WORKBUDDY_QA_PROMPT-v0.1.0.md`。

```
DesignBuddy QA：运行全量本地验收测试，并输出测试报告。

测试背景（请原样记录到 ENV-007 / ENV-008）：
- designbuddy-qa v0.1.1，本地安装，未付费，未加密，开发者本人账号
- 操作系统：【macOS 15 / Windows 11】
- WorkBuddy 版本：【例如 5.7.7.0】
- 本轮是 v0.1.0 之后的修复回归测试（见 FIX_REPORT：FIX-01 ~ FIX-06）

执行要求：
1. 严格按照 designbuddy-qa 的 references/qa-protocol.md 执行。所有脚本用例以 run-all 的输出为准，不要自行判断 PASS，也不要改写脚本用例的结果。
2. 测试报告保存到【我的项目文件夹路径】/DesignBuddy-QA-Reports。如果该位置不可写，只问我一次。
3. 回填 ENV-007、ENV-008、ENV-009。每个 PASS 都要带 --evidence。
4. 核对 environment.json 中的 package.manifest_sha256，是否等于 45a2f988cd37ae49c7498672ad8cbd343489cdf9cd8e80b9a0fd2ff74b870f22，并在汇报中说明。
5. 安装链路：安装 Alpha / Beta 之前，先展示摘要并征求我的确认。
   - INS 的 PASS 必须用 --commands 写清楚由谁执行、调用了哪个工具、参数是什么。
   - 如果是你自己用 Bash 或文件工具把 ZIP 解压、复制到 WorkBuddy 的 skills 目录，那是被禁止的 H5，不要这样做；如果已经发生，要如实记录。
   - 如果 H2 成功，请再请我按 H3 试一次（我在对话中发一句安装指令），用于确认对话式安装是否同样原样安装。
6. 你自己的临时文件（例如审计时的解压副本）放到报告目录下的 agent-notes/。
7. 多品牌测试（MB-003 ~ MB-005）不要在本会话中模拟，只告诉我 next-session-prompts.md 的位置。
8. 不要安装 Python、Node 或任何依赖。
9. 结束时告诉我：TEST_REPORT.md 和 results.json 的完整路径、汇总表（含"证据不足的 PASS"）、各状态的结论、还需要我手工完成的事项。
```
