# CHANGELOG

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
