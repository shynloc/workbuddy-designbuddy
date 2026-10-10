# WorkBuddy QA 测试提示词（v0.1.4）

用于回归测试 QA 候选版，不需要填写任何内容。商业版上架后的实测请改用 `dist/v1.0.0/POST_LAUNCH_TEST.md`。历史提示词见 `history/`。

```
DesignBuddy QA：运行全量本地验收测试，并输出测试报告。

测试背景（记录到 ENV-008）：designbuddy-qa v0.1.4，本地安装（客户端技能导入），未付费，未加密，开发者本人账号。
系统和 WorkBuddy 版本请你自己检测（方法见 qa-protocol 的 ENV-007），不要让我填写。

执行要求：
1. 严格按照 designbuddy-qa 的 references/qa-protocol.md 执行。脚本用例以 run-all 的输出为准，不要改写。
2. 测试报告保存到当前项目文件夹下的 DesignBuddy-QA-Reports。如果不可写，只问我一次。
3. 回填 ENV-007、ENV-008、ENV-009。每个 PASS 都要带 --evidence。
4. 核对 environment.json 中的 package.manifest_sha256 是否等于 b94f37a1e0da8890c99cd0de60e74bc3fce67ec9368210538e85e4159c878811。
5. 安装链路：
   - H1、H2、H3a 按协议中的已知平台事实直接记录；
   - 征得我同意后，执行 deliver --run，把 Alpha / Beta 复制到下载文件夹，然后引导我通过客户端技能导入完成 H4；
   - 装上后运行 Brand Skill 的 selfcheck，回填 INS-004、INS-005；
   - 回填 INS-006、INS-007；
   - 禁止你自己把文件写入 WorkBuddy 的 skills 目录（H5）。
6. 多品牌测试（MB-003 ~ MB-005）只告诉我 next-session-prompts.md 的位置，不要在本会话中模拟。
7. 你自己的临时文件放到报告目录下的 agent-notes/。全部回填完成后，最后执行 finalize。
8. 不要安装 Python、Node 或任何依赖。
9. 结束时告诉我：TEST_REPORT.md 和 results.json 的完整路径、汇总表、各状态的结论、还需要我手工完成的事项。
```
