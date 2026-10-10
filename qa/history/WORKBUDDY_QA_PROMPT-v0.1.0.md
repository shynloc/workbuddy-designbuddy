# WorkBuddy QA 测试提示词（直接复制下方代码块）

使用前，先把 `【】` 里的内容换成你的实际情况。不知道的项可以删掉。

```
DesignBuddy QA：运行全量本地验收测试，并输出测试报告。

测试背景（请原样记录到 ENV-007 / ENV-008）：
- designbuddy-qa v0.1.0，本地 ZIP 安装，未付费，未加密，开发者本人账号
- 操作系统：【macOS 15 / Windows 11】
- WorkBuddy 版本：【例如 1.x.x，不知道就删掉这一行】

执行要求：
1. 严格按照 designbuddy-qa 的 references/qa-protocol.md 执行。所有脚本用例以 run-all 的输出为准，不要自行判断 PASS，也不要改写脚本用例的结果。
2. 测试报告保存到【我的项目文件夹路径】/DesignBuddy-QA-Reports。如果该位置不可写，只问我一次。
3. 回填 ENV-007、ENV-008、ENV-009（实际使用的 shell 和 Python 命令）。
4. 安装链路：安装 Alpha / Beta 测试品牌 Skill 之前，先展示摘要并征求我的确认。依次尝试 H1、H2、H3、H4，把每种方式的真实结果回填到 INS-001 ~ INS-006。禁止写入 WorkBuddy 内部的 Skill 目录。
5. 多品牌测试（MB-003 ~ MB-005）不要在本会话中模拟，只告诉我 next-session-prompts.md 的位置。
6. 不要安装 Python、Node 或任何依赖。如果没有可用的 Python，按协议第 6 节输出 BLOCKED 报告。
7. 结束时告诉我：TEST_REPORT.md 和 results.json 的完整路径、汇总表、各状态的结论、还需要我手工完成的事项。
```
