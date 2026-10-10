# CHANGELOG

## designbuddy-qa 0.1.2 — 2026-10-11（修复 WorkBuddy 真机报告 qa-20261011-025430-7c19）

详见 `qa/FIX_REPORT.md`。

- **FIX-07（P1，隐私）**：新增 `finalize` 命令，对 agent-notes 就地脱敏并重新检查；SEC-012 的扫描范围扩大到 agent-notes。
- **FIX-08（P2）**：提示词去掉占位符；ENV-007 改为由 Agent 自行读取版本。
- **FIX-09（P1，测试设计）**：H3 拆为 H3a（路径文字）和 H3b（ZIP 附件）；H1~H3 都失败时必须执行 H4；新增 INS-007（记录 designbuddy-qa 自身的安装方式）；协议写入两轮真机测试得到的平台事实。
- **追溯更正**：v0.1.0 的 INS-002（H2 PASS）实际很可能是 H5，已标记为无效。
- 单元测试 19 个；72 个用例（57 SCRIPT）。

## designbuddy-qa 0.1.1 — 2026-10-11（修复 WorkBuddy 真机报告 qa-20261011-015550-2691）

详见 `qa/FIX_REPORT.md`。

### 修复

- **FIX-01（P0）**：WorkBuddy 安装时写入的 `_user_meta.json` 导致 PKG-005 误报 FAIL。改为按文件名识别平台元数据（不读取内容）；新增 PKG-008，未知的额外文件仍判 FAIL。发布构建的 lint 仍然严格。
- **FIX-02（P1，隐私）**：Windows 路径脱敏失效（JSON 转义、盘符大小写、斜杠方向），而 SEC-012 误报 PASS。改为结构化脱敏，并配独立的泄漏检测器。
- **FIX-03（P1）**：INS 类 PASS 必须用 `record --commands` 记录实际执行者和工具调用；所有 Agent/人工 PASS 必须附 `--evidence`；新增"证据不足的 PASS"汇总，存在时 LOCAL_QA_PASSED 不能为 YES；明确 Agent 自行解包到 skills 目录属于 H5。
- **FIX-04（P2）**：Brand Skill 的 selfcheck 把额外文件分成 PLATFORM-META、MATCH_WITH_EXTRA（退出码 3）、MISMATCH 三级。
- **FIX-05（P2）**：environment.json 和报告头部显示包指纹；每个版本发布 PACKAGE_FINGERPRINT.txt。
- **FIX-06（P3）**：Runner 临时目录改为 `<RUN>/.qa-work/`；Agent 文件放到 `<RUN>/agent-notes/`。

### 发布方式

- 输出到 `dist/v0.1.1/`。v0.1.0 的包保持原样，不会被覆盖。
- 单元测试 17 个；SCRIPT 用例 57 个。

## designbuddy-qa 0.1.0 — 2026-10-10（QA 候选版，首个可安装版本）

### 新增

- **Brand System Compiler**：brief.json → Brand IR（schema 1.0.0，JSON）→ WorkBuddy Brand Skill（17 个 references + 3 个自检脚本 + tokens + manifest）+ Portable Design System（DESIGN.md、DTCG tokens.json、tokens.css、manifests、assets、examples）+ 离线 Preview（海报、单页）+ Source Report。
- **三条路径**：Existing（含冲突检测与裁决）、Partial（缺口生成）、New（6 个视觉方向中排名前 3 → 用户选择）。
- **Design Gates G1–G6**：KEEP / CHANGE / REJECT；按顺序执行；按 Gate 限制可修改的字段；3 轮修改后提示收敛。
- **QA**：WCAG 对比度放行关卡 + USER_OVERRIDE；未批准颜色检测；禁止规则检测；字体回退栈；许可治理（不打包字体、不打包未授权资产）；规则矛盾检测；单一事实来源一致性检查；可复现构建。
- **安全**：路径穿越、绝对路径、非法 slug、frontmatter 注入、CSS/HTML 注入、恶意 SVG、无效 JSON、覆盖保护、不联网、报告脱敏。
- **QA RUN ALL**：70 个用例（56 SCRIPT + 14 AGENT/MANUAL），输出 TEST_REPORT.md、results.json、environment.json、artifacts-manifest.json、issues.md、next-session-prompts.md、artifacts/。
- **`record` 命令**：Agent 和人工用例的回填有约束——不能改写 SCRIPT 用例；PASS 必须有证据；BLOCKED 必须有原因。
- **构建工具** `tools/build_release.py`：可复现的 ZIP、package-manifest、解压后全量自测、SHA256SUMS。

### 已知限制

见 `qa/SPEC_DEVIATIONS.md` 和 `qa/OPEN_QUESTIONS.md`。
