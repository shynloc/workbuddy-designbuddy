# FIX_REPORT — DesignBuddy QA v0.1.1 → v0.1.2

上一轮的修复报告见 `history/FIX_REPORT-v0.1.1.md`。

## 1. 输入证据核对（报告 qa-20261011-025430-7c19）

| 项 | 结果 |
|---|---|
| 被测包 | designbuddy-qa **0.1.1**。`environment.json` 中的 `package.manifest_sha256` = `45a2f988…b870f22`，**与发布值完全一致**，确认测的就是交付的 v0.1.1 ZIP |
| 环境 | Windows 11（10.0.26200）· WorkBuddy 5.7.7（来源：`resources/install-manifest.json` 的 appVersion）· python3 3.13.14 · Git Bash |
| 跨平台可复现 | Windows 上生成的 alpha / beta build_id（`69c08dd42588` / `b948d8b0e13f`）与 Linux 上 v0.1.1 的构建一致 |
| SCRIPT | **57/57 PASS** |
| 报告完整性 | 6 个报告文件和 artifacts 齐全；Agent 自己写的文件放在了 `agent-notes/`（符合 FIX-06） |

## 2. v0.1.1 修复的真机验证结果

| 修复 | 真机证据 | 结论 |
|---|---|---|
| FIX-01 平台元数据 | PKG-005 PASS（`_user_meta.json` 被识别为平台文件）；PKG-008 PASS（没有未知文件） | ✅ 已在真机验证 |
| FIX-02 Windows 脱敏 | SEC-012 PASS；Runner 生成的 6 个报告文件中，用户名出现 **0** 次 | ✅ 已在真机验证（但 agent-notes 有遗漏，见 FIX-07） |
| FIX-03 安装证据 | INS-001/002/003/006 都附了 `commands_or_actions`；"证据不足的 PASS" = 无 | ✅ 已在真机验证 |
| FIX-05 包指纹 | 报告头部和 environment.json 都显示了指纹，与发布值一致 | ✅ 已在真机验证 |
| FIX-06 目录分离 | Runner 没有残留临时目录；Agent 文件在 `agent-notes/` | ✅ 已在真机验证 |
| FIX-04 selfcheck 分级 | 本轮没有安装成功，未能执行 | ⏳ 未覆盖 |

## 3. 结果分类

| 类别 | 用例 | 说明 |
|---|---|---|
| FAIL | **INS-003**（P1） | 用户发送带路径的安装句后，被转给 `marketplace-skill-installer`，最终是只支持市场的 `search_and_install_skills`。**这是平台能力限制，不是包缺陷**，按协议如实记为 FAIL，不修改测试去掩盖 |
| BLOCKED | INS-001 | 平台工具只支持市场 Skill |
| BLOCKED | INS-002 | `skill-creator` 只提供创建和打包引导，没有安装执行器；唯一的替代做法是 H5，已按要求拒绝 |
| BLOCKED | PP-002/003 | 需要付费加密环境 |
| NOT_TESTED | INS-004 | 用户选择跳过 |
| NOT_TESTED | INS-005 | 没有安装成功 |
| NOT_TESTED | MB-003~005 | 前提是已安装 Brand Skill，安装链路没有走通 |
| 遗漏 | macOS | 整轮未测 |

## 4. 重要的追溯更正：v0.1.0 的 INS-002 很可能是 H5

本轮实测证明，`skill-creator` **没有任何安装执行器**。因此 v0.1.0 报告中"H2 经 Skill Creator……原样解包到用户级 skills 目录"的 PASS，不可能是 Skill Creator 完成的。**最合理的解释是 Agent 自己把 ZIP 解压进了 `~/.workbuddy/skills/`，也就是 H5。**

- 该结果已在 `docs/runtime-validation-results.md` 中标记为**无效**。
- 这件事也说明，FIX-03（安装类 PASS 必须附命令）是必要的。
- 本轮 Agent 明确声明没有执行任何写入，并在事后核查 skills 目录确认没有 alpha / beta 条目。

## 5. 本轮修复（v0.1.2）

### FIX-07 · P1（隐私）· `agent-notes` 中仍有用户名路径

- **复现**：`agent-notes/session-notes.md` 中出现 `C:/Users/<用户名>/.workbuddy/skills/`。
- **根因**：脱敏只覆盖 Runner 自己生成的文件，Agent 自由书写的笔记没有经过脱敏；SEC-012 也没有扫描这个目录。
- **修复**：
  - 新增 `finalize --run <RUN>`：对 `agent-notes/` 中的文本文件就地脱敏，重新生成报告，再重新执行 SEC-012；
  - SEC-012 的扫描范围扩大到 `agent-notes/`；
  - 协议把 finalize 列为必须执行的最后一步。
- **影响文件**：`qarunner.py`、`designbuddy.py`、`SKILL.md`、`references/qa-protocol.md`
- **回归测试**：`test_fix07_finalize_redacts_agent_notes`

### FIX-08 · P2 · 提示词里的 `【】` 占位符被照抄进结果

- **现象**：ENV-007 / ENV-008 的 actual 中出现了"【macOS 15 / Windows 11】"等未填写的占位符。
- **修复**：
  - 新提示词不再有占位符，系统和 WorkBuddy 版本由 Agent 自己检测；
  - 协议写明了已知的版本读取位置，并要求不要照抄占位符。

### FIX-09 · P1（测试设计）· 安装链路覆盖不足

- **问题**：H3 只测了"发送路径文字"，没测"把 ZIP 作为附件拖进对话"；H4 被跳过。可是 designbuddy-qa 自己就是被平台装上的（有 `_user_meta.json` 为证），说明**确实存在一条能装本地 ZIP 的平台路径，只是测试没覆盖到**。
- **修复**：
  - 协议把 H3 拆成 H3a（路径文字）和 H3b（ZIP 附件）；
  - H1~H3 都失败时，H4 必须请用户执行；
  - 新增 **INS-007**：记录 designbuddy-qa 本身是怎样安装的；
  - 协议中写入两轮测试得到的平台事实。
- **回归测试**：`test_fix09_ins007_present_and_manual`

## 6. 回归结论（开发机）

| 项 | 结果 |
|---|---|
| 单元测试 | 19/19（新增 2 个） |
| 包 lint | 0 错误 |
| 解压副本中的 SCRIPT 用例 | 57/57 |
| 可复现构建 | 是（ZIP 的 SHA-256 一致） |

没有删除或放宽任何测试。INS-003 的 FAIL 原样保留，因为它反映的是真实的平台能力。

## 7. 需要你决策的事项（不在本次自动修复范围内）

见 `DECISION_REQUEST_INSTALL.md`。如果平台路径（H3b/H4）对最终用户也不可用，"对话内一键安装"就只能用 H5 一类的方式实现，而这需要你单独批准。
