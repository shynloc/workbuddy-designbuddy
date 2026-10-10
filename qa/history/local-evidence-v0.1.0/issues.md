# Issues

## FAIL / PARTIAL（需要修复）

无。

## BLOCKED / NOT_TESTED（需要外部条件，不算通过）

- **ENV-007** NOT_TESTED — 记录 WorkBuddy 客户端版本（需要 Agent 在 WorkBuddy 中记录）
- **ENV-008** NOT_TESTED — 记录 Skill 安装形态：本地/市场、是否付费、是否加密、开发者/购买者（需要 Agent 在 WorkBuddy 中记录）
- **ENV-009** NOT_TESTED — 记录 Agent 实际使用的 shell 与命令执行方式（需要 Agent 在 WorkBuddy 中记录）
- **INS-001** NOT_TESTED — H1：原生安装工具（检查 Agent 工具列表中是否存在）（需要在 WorkBuddy 中执行）
- **INS-002** NOT_TESTED — H2：交给内置 Skill Creator 原样安装（检查是否改写）（需要在 WorkBuddy 中执行）
- **INS-003** NOT_TESTED — H3：用户发一句话触发原生安装（需要在 WorkBuddy 中执行）
- **INS-004** NOT_TESTED — H4：通过 UI 导入 ZIP（需要在 WorkBuddy 中执行）
- **INS-005** NOT_TESTED — 安装后 Brand Skill selfcheck=MATCH、版本与关键规则一致（需要先完成 INS-001..004 中至少一项）
- **INS-006** NOT_TESTED — 安装前已向用户展示摘要并取得明确确认（需要 Agent 记录）
- **MB-003** NOT_TESTED — 独立新会话：「给 Alpha Demo 做一份 PPT 封面」只触发 Alpha（PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数）
- **MB-004** NOT_TESTED — 独立新会话：「做一份 PPT」不擅自套用任何品牌（应先询问）（PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数）
- **MB-005** NOT_TESTED — 独立新会话：「把 Beta Demo 的这段文档改成 Alpha Demo 风格」source=Beta、target=Alpha（PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数）
- **PP-002** BLOCKED — 市场付费加密形态（开发者账号）：资源、脚本、生成器可用性（BLOCKED: REQUIRES_PAID_ENCRYPTED_MARKETPLACE_RUNTIME）
- **PP-003** BLOCKED — 市场付费加密形态（普通购买者账号）：资源、脚本、生成器可用性（BLOCKED: REQUIRES_PAID_ENCRYPTED_MARKETPLACE_RUNTIME）
