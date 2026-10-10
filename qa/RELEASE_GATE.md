# 发布门槛与剩余验证计划

> **2026-10-11 更新**：产品负责人确认 H4（客户端技能导入）可用，要求把交付文件放到下载文件夹，并决定"其他没问题，可以发布"。
>
> - G-2（macOS）、G-4（多品牌）、G-5（真实品牌）由产品负责人**豁免为发布后观察项**，记录在 `dist/v1.0.0/KNOWN_LIMITATIONS.md`。
> - G-3 由 H4 满足（产品负责人实测）。
> - 已生成 `dist/v1.0.0/designbuddy-v1.0.0.zip`。

## 1. 商业版 `designbuddy-v1.0.0.zip` 的生成门槛（原始定义）

商业版只在下列条件**全部满足**后才生成。生成后由你亲自上传，我不会发布。

| # | 门槛 | 当前状态（v0.1.1） |
|---|---|---|
| G-1 | 最新 QA 包在 **Windows** 真机上：SCRIPT 用例全部 PASS，P0/P1 = 0，没有证据不足的 PASS | ⏳ v0.1.1：SCRIPT 57/57、证据完整；剩余 1 个 P1 FAIL（INS-003，平台限制）和 1 个隐私遗漏（已在 v0.1.2 修复）。**v0.1.2 待复测** |
| G-2 | 最新 QA 包在 **macOS** 真机上同样满足 G-1 | ❌ 未测 |
| G-3 | 至少一条安装路径（H2/H3/H4）能**原样安装**，附工具调用证据，selfcheck = MATCH | ❌ H1/H2/H3a 已证实不可行；H3b/H4 待测；需要你在 `DECISION_REQUEST_INSTALL.md` 中决策 |
| G-4 | 多品牌：MB-003 / MB-004 / MB-005 在独立新会话中 PASS | ❌ 未测（这是核心产品承诺） |
| G-5 | 用一个真实（非夹具）品牌走完全程，Gate 交互可用，问题数量合理 | ❌ 未测（D-03：夹具会自动通过 Gate） |
| G-6 | 产品决策已确认：正式名 `designbuddy`、展示名与简介、价格（整数，TBD）、服务类目、Brand Skill 的 `author` 默认值、商业版是否保留诊断入口 | ❌ 需要你决定 |
| G-7 | 付费加密验证（PP-002/003） | 不阻塞**上传**，但在 PAID_ENCRYPTED_RUNTIME_VERIFIED 之前，对外不宣称有加密或源码保护 |

**结论**：门槛尚未满足，本轮**不生成** `designbuddy-v1.0.0.zip`，以免给出一个看起来可以上架、实际未经验证的包。

一旦 G-1 到 G-6 满足，我会生成以下内容：

- 干净的商业版：不含夹具品牌、不含 QA Runner 入口，保留运行时自检；
- `RELEASE_CHECKLIST.md`、`MARKETPLACE_LISTING.md`、`RELEASE_NOTES.md`、`KNOWN_LIMITATIONS.md`；
- 权限与隐私说明，安装与售后指南。

## 2. 剩余验证计划（按顺序）

| 步骤 | 内容 | 谁做 | 预计耗时 | 产出 |
|---|---|---|---|---|
| 1 | Windows：卸载 v0.1.0 → 安装 v0.1.1 → 粘贴 `qa/WORKBUDDY_QA_PROMPT.md` | 你 + WorkBuddy Agent | 10~15 分钟 | 报告 #2（Windows） |
| 2 | 同一台 Windows：按 Agent 的提示用 H3 再装一次 Beta，确认对话式安装是否原样安装 | 你 | 5 分钟 | INS-003 证据 |
| 3 | 三个独立新会话：执行 `next-session-prompts.md` 中的 MB-003 / 004 / 005，截图 | 你 | 10 分钟 | MB 证据 |
| 4 | macOS：重复步骤 1 和 3 | 你 | 15 分钟 | 报告 #3（macOS） |
| 5 | 我根据报告 #2、#3 修复问题（如有）→ v0.1.2；全部通过则进入步骤 6 | 我 | — | — |
| 6 | 你确认 G-6 中的产品决策 | 你 | — | — |
| 7 | 用你自己的一个真实品牌，或一个不含敏感信息的样例，走一遍完整的 Gate 流程（G-5） | 你 + 我 | 20~30 分钟 | 体验反馈 |
| 8 | 我生成 `designbuddy-v1.0.0.zip` 和全部提交材料 | 我 | — | 商业包 |
| 9 | 你上传开放平台 → 平台解析（PLATFORM_PARSE_PASSED）→ 审核（REVIEW_APPROVED） | 你 | 平台时间 | 平台状态 |
| 10 | 经你批准后：付费加密环境下的开发者 / 购买者验证（PP-002/003）→ PAID_ENCRYPTED_RUNTIME_VERIFIED | 你 | — | 加密证据 |

上述 5 个状态（LOCAL_QA_PASSED → … → PAID_ENCRYPTED_RUNTIME_VERIFIED）互不替代。每个状态只在取得对应证据后才标记。
