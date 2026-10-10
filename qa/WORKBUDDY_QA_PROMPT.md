# WorkBuddy QA 测试提示词（v0.1.2，第 3 轮）

这一版不需要填写任何内容，直接复制下面的代码块。上一轮的提示词见 `history/`。

```
DesignBuddy QA：运行全量本地验收测试，并输出测试报告。

测试背景（记录到 ENV-008）：designbuddy-qa v0.1.2，本地安装，未付费，未加密，开发者本人账号。本轮是 v0.1.1 之后的修复回归（FIX-07 ~ FIX-09）。
系统和 WorkBuddy 版本请你自己检测（方法见 qa-protocol 的 ENV-007），不要让我填写。

执行要求：
1. 严格按照 designbuddy-qa 的 references/qa-protocol.md 执行。脚本用例以 run-all 的输出为准，不要改写。
2. 测试报告保存到当前项目文件夹下的 DesignBuddy-QA-Reports。如果不可写，只问我一次。
3. 回填 ENV-007、ENV-008、ENV-009。每个 PASS 都要带 --evidence。
4. 核对 environment.json 中的 package.manifest_sha256 是否等于 c8e97bc5f9f100ff201c8f9ac5397849aea9bc49f7b3f0a6bbf25d938d249919。
5. 安装链路（这是本轮重点）：
   - 安装前先展示摘要并征求我的确认；
   - H1、H2 可以直接引用协议中的已知平台事实，快速记录；
   - H3 两种做法都要试：H3a 我发一句带路径的安装指令；H3b 我把 Alpha 的 ZIP 作为附件拖进对话。请明确告诉我每一步该怎么做；
   - 如果 H1~H3 都不成功，请引导我用客户端的 Skill 导入入口完成 H4，并记录入口位置；
   - 任何一种方式装上之后，运行 Brand Skill 的 selfcheck，回填 INS-005；
   - 问我 designbuddy-qa 本身是怎样装上的，回填 INS-007；
   - 禁止你自己把文件解压或复制到 WorkBuddy 的 skills 目录（H5）。
6. 如果 Alpha / Beta 装上了，告诉我 next-session-prompts.md 的位置，我会在新会话中做 MB-003 ~ MB-005。不要在本会话中模拟。
7. 你自己的临时文件放到报告目录下的 agent-notes/。全部回填完成后，最后执行 finalize。
8. 不要安装 Python、Node 或任何依赖。
9. 结束时告诉我：TEST_REPORT.md 和 results.json 的完整路径、汇总表、各状态的结论、还需要我手工完成的事项。
```
