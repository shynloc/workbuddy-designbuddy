# FIX_REPORT — DesignBuddy QA v0.1.0 → v0.1.1

## 1. 输入证据核对

| 项 | 结果 |
|---|---|
| 报告 | `qa-20261011-015550-2691`：TEST_REPORT.md、results.json、environment.json、issues.md、artifacts-manifest.json、next-session-prompts.md、artifacts/（72 个文件，SHA-256 与 manifest 逐一一致） |
| 版本 | designbuddy-qa 0.1.0，Brand IR schema 1.0.0 |
| 环境 | Windows 11（10.0.26200）· WorkBuddy 5.7.7.0（ENV-007 证据：WorkBuddy.exe 的 ProductVersion）· Python 3.13.14 · Agent 通过 WorkBuddy 的 Bash 工具（Git Bash）执行，`<PY>`=python3 |
| 安装形态 | 本地安装到用户级 skills 目录，未付费，未加密，开发者账号（ENV-008） |
| 测试包哈希 | 报告中**没有直接记录 ZIP 哈希**（这本身是一个缺陷，见 FIX-05）。间接核对：PKG-004 用 46 个文件比对了 package-manifest，结果全部一致；文件数与 `dist/designbuddy-qa-v0.1.0.zip`（`39f31d91…`）相同。v0.1.0 只发布过这一个构建，可以认定被测包就是它 |
| 跨平台可复现 | 报告中 Windows 生成的 `alpha-demo-brand-system-1.0.0.zip`，与 Linux 上用 v0.1.0 构建的结果逐文件一致（28/28，已排除 generated_at），build_id 相同（`00198c2fe97f`） |
| 报告之外的文件 | `artifacts/_work/audit/`：Agent 安全审计时解压的副本，不是 Runner 的产物（Runner 在结束时已删除自己的 _work）；`artifacts/security-audit-alpha-beta.md`：Agent 写的审计报告（结论 P2 安全） |

## 2. 结果分类

| 类别 | 用例 |
|---|---|
| **FAIL** | PKG-005（P0） |
| **证据不足的 PASS**（不能算通过） | INS-002（没有记录工具调用或命令，安装机制描述模糊，见 FIX-03）；INS-005 依赖 INS-002 的安装，**selfcheck 证据本身有效**，但安装方式待澄清 |
| **被 SCRIPT 误判的 PASS** | SEC-012（报告脱敏）：v0.1.0 判 PASS，实际报告**泄漏**了 Windows 用户名路径（FIX-02） |
| BLOCKED | INS-001（平台事实：`search_and_install_skills` 只能装市场 Skill）；PP-002、PP-003（需要付费加密市场环境） |
| NOT_TESTED | INS-003、INS-004（H2 成功后作为备选未执行）；MB-003 ~ MB-005（需要独立新会话） |
| 未覆盖 | macOS 整轮未测 |

## 3. 缺陷与修复

### FIX-01 · P0 · PKG-005 把平台写入的元数据当成包缺陷

- **复现**：WorkBuddy 5.7.7.0 安装 Skill 时，会在根目录写入 `_user_meta.json`；随后 PKG-005 报"根目录存在非标准项"。
- **根因**：构建期的严格 lint（检查我们自己的包）被原样用在了已安装副本上，而安装副本里有平台文件。
- **修复**：
  - `package.lint_skill(root, platform_files=...)`：平台元数据只按文件名识别，**不读取内容**（可能含用户信息），也不计入包错误。
  - 新增 **PKG-008**：把安装副本中的额外文件分成"平台元数据"和"未知文件"；**出现未知文件就判 FAIL**。
  - 发布构建的 lint 不传 `platform_files`，所以我们自己的 ZIP 永远不能包含 `_user_meta.json`。**安全标准没有放宽。**
- **影响文件**：`scripts/dbcore/package.py`、`scripts/dbcore/qarunner.py`
- **回归测试**：
  - `test_fix01_platform_meta_is_not_a_package_error`：发布 lint 仍然报错；安装 lint 通过；再加入一个未知文件后报错。
  - 构建工具在解压副本中写入模拟的 `_user_meta.json` 后，PKG-005 和 PKG-008 都通过。
- **风险**：其他版本或系统可能写入不同名称的元数据。如果写了，PKG-008 会判 FAIL 并列出文件名，届时按真机证据补充白名单。

### FIX-02 · P1 · 报告脱敏在 Windows 上失效，而 SEC-012 误报 PASS

- **复现**：v0.1.0 的 `environment.json` 中，`skill_root` 为 `C:\\Users\\<用户名>\\.workbuddy\\…`，`cwd` 为 `d:\\<用户名>\\…`；`results.json` 中 Agent 回填的证据也包含用户名路径。
- **根因**：
  - 脱敏是对**已序列化的 JSON 字符串**做字面替换，而 Windows 路径在 JSON 中是双反斜杠，所以匹配不上；
  - 没有处理盘符大小写（`d:` 和 `D:`）和正斜杠写法；
  - SEC-012 用同样有缺陷的方法检查，于是误报 PASS。
- **修复**：
  - `util.redact` 覆盖原样、正斜杠、反斜杠、JSON 转义四种写法，忽略大小写，再兜底匹配通用用户目录模式和"用户名作为路径段"；
  - `redact_obj` 改为在结构化数据上逐个字符串脱敏；
  - `util.leaks` 作为独立的泄漏检测器；SEC-012 改为检查 5 个报告文件；
  - `record` 回填的内容同样经过脱敏。
- **影响文件**：`scripts/dbcore/util.py`、`scripts/dbcore/qarunner.py`
- **回归测试**：
  - `test_fix02_windows_paths_are_redacted_in_all_forms`：覆盖 Windows 的 5 种写法，并确认旧检查确实会漏掉 JSON 转义写法；
  - 用真机报告原文验证：泄漏片段 environment.json 4 → 0，results.json 3 → 0。
- **风险**：通用模式会把形如 `/home/xxx` 的普通文本也替换掉。这在报告场景中可以接受。

### FIX-03 · P1 · 安装类 PASS 缺少可核查的执行证据

- **问题**：INS-002 的 commands_or_actions 为空，描述是"经 Skill Creator 的用户级 Skill 目录机制……解包到用户级 skills 目录"。从证据**无法区分**是 Skill Creator 或平台安装的，还是 Agent 自己解包写入的。后者就是被禁止的 H5。
- **修复**：
  - `record` 新增 `--commands`。INS-001 ~ 005 的 PASS 必须写明"由谁执行、调用了什么"，所有 AGENT/MANUAL 的 PASS 都必须提供 `--evidence`。
  - 汇总中新增"证据不足的 PASS"，只要存在，`LOCAL_QA_PASSED` 就不能为 YES。
  - qa-protocol 和 installation-handoff 写明：**Agent 自己把文件解压或复制进 `~/.workbuddy/skills/` 就是 H5**，不能记作 H2。
- **影响文件**：`qarunner.py`、`designbuddy.py`、`references/qa-protocol.md`、`references/installation-handoff.md`
- **回归测试**：
  - `test_fix03_install_pass_requires_commands_and_evidence`
  - `test_fix05_weak_evidence_blocks_local_qa_passed`
- **对 v0.1.0 结果的处理**：INS-002 视为**待澄清**。v0.1.1 真机复测时必须附上实际的工具调用。

### FIX-04 · P2 · Brand Skill 的 selfcheck 对额外文件不分级

- **修复**：
  - `_user_meta.json` 记为 `PLATFORM-META`（结果仍为 MATCH，退出码 0）；
  - 未知额外文件 → `MATCH_WITH_EXTRA`（退出码 3）；
  - 内容被改动 → `MISMATCH`（退出码 1）。
- **影响文件**：`templates/brand-skill/scripts/selfcheck.py.tmpl`
- **回归测试**：`test_fix04_selfcheck_classifies_extra_files`

### FIX-05 · P2 · 报告无法对应到具体安装包

- **修复**：
  - `environment.json` 新增 `package.version` 和 `package.manifest_sha256`，报告头部也显示这两项；
  - 每个版本都发布 `PACKAGE_FINGERPRINT.txt`，内容是 ZIP 和 package-manifest 的 SHA-256。
- **影响文件**：`qarunner.py`、`tools/build_release.py`

### FIX-06 · P3 · Agent 文件与 Runner 临时目录混在一起

- **修复**：
  - Runner 的临时目录改为 `<RUN>/.qa-work/`，运行结束时删除，不再放在 `artifacts/` 下；
  - 协议要求 Agent 把自己的文件放到 `<RUN>/agent-notes/`。
- **回归测试**：`test_fix03…` 中断言 `.qa-work` 和 `artifacts/_work` 在运行后都不存在。
- 本次改动顺带引入一个回归：`artifacts/` 目录不再被创建，导致 CORE-013 失败。已修复，并由 run-all 覆盖。

## 4. 回归结论（开发机，Linux）

| 项 | v0.1.0 | v0.1.1 |
|---|---|---|
| 单元测试 | 12/12 | **17/17**（新增 5 个修复回归测试） |
| 包 lint | 0 错误 | 0 错误 |
| 解压副本中的 SCRIPT 用例（含模拟的 `_user_meta.json`） | 56/56（未模拟平台文件） | **57/57**（新增 PKG-008） |
| 可复现构建 | 是 | 是（两次构建，ZIP 的 SHA-256 一致） |

**没有删除任何测试；没有放宽任何安全检查。** 唯一被修改的旧测试是 `test_record_…`：它按旧规则只提供上下文就允许 PASS，新规则要求必须有证据，规则是收紧的。

## 5. 架构与兼容性

- Brand IR schema 仍为 1.0.0，与 v0.1.0 的 Workspace 和 IR 完全兼容。
- 编译器逻辑没有变化。同一个 IR 在 v0.1.1 下的 build_id 会变，这是因为 build_id 包含编译器版本，属于设计如此。
- 没有改动 Local-first、安装需确认、不联网、保护用户数据等核心约束。
- 从 v0.1.0 升级的方式：在 WorkBuddy 中删除旧的 `designbuddy-qa`，再安装 v0.1.1。Skill 名称没有变。

## 6. WorkBuddy 平台新事实（已写入 docs/runtime-capabilities.md）

| 事实 | 等级 |
|---|---|
| WorkBuddy 5.7.7.0 / Windows 11：Skill 执行环境有 python3 3.13.14；Agent 的 Bash 工具基于 Git Bash | OBSERVED（单机单次） |
| 用户级 Skill 目录位于用户主目录下的 `.workbuddy/skills/<name>/` | OBSERVED |
| 安装时会在 Skill 根目录写入 `_user_meta.json` | OBSERVED |
| `search_and_install_skills` 只能安装技能市场中的 Skill，不接受本地 ZIP 或目录 | OBSERVED |
| 由平台或 Skill Creator 安装的 Brand Skill，文件逐字节保持不变（selfcheck MATCH） | OBSERVED（安装机制待澄清，见 FIX-03） |
| 编译器在 Windows 与 Linux 上的产物逐文件一致 | OBSERVED |
