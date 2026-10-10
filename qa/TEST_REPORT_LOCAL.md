# TEST_REPORT_LOCAL — DesignBuddy QA v0.1.2

开发机本地测试证据。由 `tools/build_release.py` 自动生成，**不代表 WorkBuddy 真机结果**。

## 测试环境

- 平台：Linux-6.18.44-fc-v114-x86_64-with-glibc2.39（x86_64）
- Python：3.13.16；PATH 中的 node：True
- 运行方式：把 `dist/v0.1.2/designbuddy-qa-v0.1.2.zip` 解压到含空格和中文的路径，并写入模拟的平台元数据 `_user_meta.json`（复现 WorkBuddy 5.7.7.0 的安装行为），然后从解压后的副本执行
- 安装包：zip sha256 `49c218b16a8568c16820323996c6d2bcf1923c0f15cfce7a5369a8043ac1b94b`；package-manifest sha256 `c8e97bc5f9f100ff201c8f9ac5397849aea9bc49f7b3f0a6bbf25d938d249919`
- WorkBuddy：**未参与**（开发容器中没有 WorkBuddy 客户端）

## 结果

| 项 | 结果 |
|---|---|
| 单元测试（tests/unit） | 通过 |
| Skill lint（结构 / frontmatter / 引用 / 路径 / 密钥 / 字体） | errors=0 warnings=0，47 个文件，217720 bytes |
| `version` | designbuddy-qa 0.1.2 |
| `selftest`（package-manifest 完整性） | ok=True，46 个文件 |
| QA RUN ALL 用例 | 72 个 |
| PASS / FAIL / PARTIAL / BLOCKED / NOT_TESTED | 57 / 0 / 0 / 2 / 13 |
| SCRIPT 通过率 | 100.0%（57/57） |
| 问题 P0/P1/P2/P3 | 0 / 0 / 0 / 0 |

## 未验证项（需要 WorkBuddy 真机或人工）

- `ENV-007` NOT_TESTED · 记录 WorkBuddy 客户端版本 — 需要 Agent 在 WorkBuddy 中记录
- `ENV-008` NOT_TESTED · 记录 Skill 安装形态：本地/市场、是否付费、是否加密、开发者/购买者 — 需要 Agent 在 WorkBuddy 中记录
- `ENV-009` NOT_TESTED · 记录 Agent 实际使用的 shell 与命令执行方式 — 需要 Agent 在 WorkBuddy 中记录
- `INS-001` NOT_TESTED · H1：原生安装工具（检查 Agent 工具列表中是否存在） — 需要在 WorkBuddy 中执行
- `INS-002` NOT_TESTED · H2：交给内置 Skill Creator 原样安装（检查是否改写） — 需要在 WorkBuddy 中执行
- `INS-003` NOT_TESTED · H3：用户发一句话触发原生安装 — 需要在 WorkBuddy 中执行
- `INS-004` NOT_TESTED · H4：通过 UI 导入 ZIP — 需要在 WorkBuddy 中执行
- `INS-005` NOT_TESTED · 安装后 Brand Skill selfcheck=MATCH、版本与关键规则一致 — 需要先完成 INS-001..004 中至少一项
- `INS-006` NOT_TESTED · 安装前已向用户展示摘要并取得明确确认 — 需要 Agent 记录
- `INS-007` NOT_TESTED · 记录 designbuddy-qa 本身是用哪种方式安装的（对话中附 ZIP 文件 / 客户端 UI 导入 / 其他），以及是否由平台完成 — 需要用户说明
- `MB-003` NOT_TESTED · 独立新会话：「给 Alpha Demo 做一份 PPT 封面」只触发 Alpha — PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数
- `MB-004` NOT_TESTED · 独立新会话：「做一份 PPT」不擅自套用任何品牌（应先询问） — PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数
- `MB-005` NOT_TESTED · 独立新会话：「把 Beta Demo 的这段文档改成 Alpha Demo 风格」source=Beta、target=Alpha — PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数
- `PP-002` BLOCKED · 市场付费加密形态（开发者账号）：资源、脚本、生成器可用性 — BLOCKED: REQUIRES_PAID_ENCRYPTED_MARKETPLACE_RUNTIME
- `PP-003` BLOCKED · 市场付费加密形态（普通购买者账号）：资源、脚本、生成器可用性 — BLOCKED: REQUIRES_PAID_ENCRYPTED_MARKETPLACE_RUNTIME

## 状态

- LOCAL_QA_PASSED：NO
- READY_FOR_PLATFORM_SUBMISSION：NO（QA 候选版不用于上架）
- PLATFORM_PARSE_PASSED：NOT_REACHED
- REVIEW_APPROVED：NOT_REACHED
- PAID_ENCRYPTED_RUNTIME_VERIFIED：NOT_REACHED

> LOCAL_QA_PASSED 为 NO 是预期结果：ENV-007/008/009、INS-*、MB-003..005 必须在 WorkBuddy 中执行并回填。

完整原始输出见 `qa/local-evidence/`（TEST_REPORT.md、results.json 等）。上一版本的证据见 `qa/history/`。
