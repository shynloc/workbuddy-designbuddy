# IMPLEMENTATION_STATUS — DesignBuddy QA v0.1.3 / 商业版 v1.0.0

状态取值：**DONE**（已实现，有自动化测试覆盖）· **PARTIAL**（部分实现）· **NOT_DONE**（未实现）· **PLATFORM**（需要 WorkBuddy 真机验证）

## A1 核心链路

| # | 要求 | 状态 | 实现位置 | 测试 |
|---|---|---|---|---|
| 1 | Existing / Partial / New 三条路径的最小验证 | DONE | `dbcore/engine.py` intake、directions；夹具 brand-alpha（Existing）、brand-beta（Partial）、brand-gamma-new（New） | CORE-001/002/003 |
| 2 | Brand IR（JSON 唯一事实来源），带字段和版本校验 | DONE | `dbcore/ir.py`（schema_version 1.0.0；Fact / Provenance / Confidence / Review；规则矛盾检测） | CORE-004/005、SEC-006、QA-008 |
| 3 | 从同一份 IR 生成规则、颜色和排版 Token | DONE | `dbcore/exporters.py`：tokens.json（DTCG）、tokens.css、17 个 references | CORE-010 |
| 4 | WorkBuddy Brand Skill + Portable Design System（含 DESIGN.md 和 Tokens） | DONE | `export_skill`、`export_portable`、`package.pack` | CORE-007/008/012 |
| 5 | 可预览的品牌应用样例 | DONE | `templates/preview/`：poster.html、onepager.html（离线） | CORE-009 |
| 6 | Brand QA、对比度、资产来源与许可、内容完整性与安全 | DONE | `dbcore/qa.py`、`package.lint_skill`、`util.safe_*` | QA-*、SEC-* |
| 7 | 用户确认后的安装交接 | DONE（H4） | `references/installation-handoff.md`：协议 + Brand Skill 自带 selfcheck。实际交接由 Agent 在 WorkBuddy 中执行 | INS-000（SCRIPT）；INS-001..006（PLATFORM） |
| 8 | QA RUN ALL，结构化结果 + Markdown 报告 | DONE | `dbcore/qarunner.py`、`designbuddy.py run-all / record`（--commands、证据不足检测、包指纹、结构化脱敏、平台元数据分级、finalize） | 全部（74 个） |

## 架构要求的落实情况

| 要求 | 状态 | 说明 |
|---|---|---|
| 确定性 Compiler（不在运行时现场生成模板） | DONE | 模板在 `templates/`，生成器在 `dbcore/`。同一输入构建两次，除 generated_at 外逐字节一致（CORE-011）；发布 ZIP 也可复现 |
| Design Gates G1–G6（KEEP/CHANGE/REJECT，按顺序，按 Gate 限制可改字段，3 轮收敛提示） | DONE | `engine.apply_gate`（CORE-006） |
| Provenance：冲突检测与裁决、优先审核 INFERRED/GENERATED | DONE | `status.review_first`、`conflicts` |
| 多品牌消歧（写入 Brand Skill） | DONE（规则）/ PLATFORM（实际触发行为） | MB-001/002；MB-003..005 需要新会话 |
| Progressive Disclosure（SKILL.md 路由表） | DONE | Brand Skill 的 SKILL.md 约 5KB，按任务类型路由 references |
| Local-first / 不联网 | DONE | SEC-010 |
| 付费保护验证 | PLATFORM | PP-002/003 = BLOCKED（需要真实的市场付费加密环境） |
| 无障碍放行关卡 + USER_OVERRIDE | DONE | QA-003 |
| 字体和素材许可治理 | DONE | QA-006/007/009；font-manifest、asset-manifest |
| Workspace 断点续做 | DONE | `.designbuddy/state.json`、`brand-ir/history/`（UX-004） |
| Office 模板（.potx/.dotx/.xltx） | NOT_DONE | 列为 Advanced Export，不在 v0.1 范围。Brand Skill 中的 ppt/word/excel 规则已经可以独立使用 |
| 从 PDF / PPT / 图片中自动抽取设计特征 | NOT_DONE | v0.1 由 Agent 把用户材料整理成 brief（标注来源）。见 SPEC_DEVIATIONS D-02 |
| 无 Python 时的 Node 降级 | NOT_DONE | 输出 BLOCKED 报告（qa-protocol 第 6 节） |

## 代码结构

```
designbuddy-qa/                 ← 打包进 ZIP 的 Skill 本体
  SKILL.md
  references/  design-workflow · compiler-contract · installation-handoff · qa-protocol · safety
  scripts/designbuddy.py        ← CLI 入口（JSON 输出，稳定的退出码）
  scripts/dbcore/               util · color · ir · engine · exporters · package · qa · workspace · deliver · runtime · qarunner（仅 QA 版）
  templates/brand-skill/        Brand Skill 的 SKILL.md 模板 + 3 个脚本模板
  templates/preview/ portable/  HTML / DESIGN.md / README 模板
  templates/data/               directions.json（6 个视觉方向）· fonts.json（10 款字体的许可摘要）
  templates/fixtures/           brand-alpha / brand-beta / brand-gamma-new + 12 个畸形输入
tools/build_release.py          ← 单元测试 → 暂存 + package-manifest → lint → 打包 → 夹具品牌包 → 解压后全量测试 → 校验和
tests/unit/                     ← 21 个 unittest（含各轮修复的回归测试）
tools/build_commercial.py       ← 商业版：剔除 QA 内容 → 打包 → 从解压包端到端验证
```

## v0.1.3 / v1.0.0 新增

| 要求 | 状态 | 说明 |
|---|---|---|
| 交付到下载文件夹 | DONE | `deliver` / `build --deliver` → `<下载>/DesignBuddy/<品牌>/`，不覆盖已有文件（CORE-014、SEC-014） |
| 安装方式 | DONE | 客户端技能导入（H4，产品负责人实测可用）；H5 禁止 |
| 商业版构建 | DONE | `dist/v1.0.0/designbuddy-v1.0.0.zip`（author: ShyNloc），见 `dist/v1.0.0/BUILD_VERIFICATION.md` |
