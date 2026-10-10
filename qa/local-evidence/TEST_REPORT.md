# DesignBuddy QA 测试报告

- Run ID：`qa-20261010-203110-4ceb`
- DesignBuddy：0.1.4（designbuddy-qa）
- 环境：Linux-6.18.44-fc-v114-x86_64-with-glibc2.39 · Python 3.13.16 · WorkBuddy 版本：UNKNOWN（由 Agent 记录：ENV-007）
- 安装包指纹：version 0.1.4 · package-manifest SHA-256 `b94f37a1e0da8890c99cd0de60e74bc3fce67ec9368210538e85e4159c878811`

## 汇总

| 指标 | 数值 |
|---|---|
| 用例总数 | 74 |
| PASS / FAIL / PARTIAL / BLOCKED / NOT_TESTED | 59 / 0 / 0 / 2 / 13 |
| 自动化（SCRIPT）通过率 | 100.0%（59/59） |
| 问题数 P0 / P1 / P2 / P3 | 0 / 0 / 0 / 0 |
| 未验证项 | 15（ENV-007, ENV-008, ENV-009, INS-001, INS-002, INS-003, INS-004, INS-005, INS-006, INS-007, MB-003, MB-004, MB-005, PP-002, PP-003） |
| 证据不足的 PASS | 无 |
| 建议进入下一轮修复 | 否 |

## 状态（互不替代）

| 状态 | 结论 |
|---|---|
| LOCAL_QA_PASSED | NO |
| READY_FOR_PLATFORM_SUBMISSION | NO（QA 候选版不用于上架） |
| PLATFORM_PARSE_PASSED | NOT_REACHED |
| REVIEW_APPROVED | NOT_REACHED |
| PAID_ENCRYPTED_RUNTIME_VERIFIED | NOT_REACHED |

> LOCAL_QA_PASSED 需要：全部 SCRIPT 用例 PASS，ENV-007/008/009、INS-006 已由 Agent 记录为 PASS，INS-001..004 至少一项 PASS（附实际工具调用或命令），INS-005 PASS，且没有证据不足的 PASS。

## 用例

| ID | 领域 | 类型 | 级别 | 结果 | 目标 | 实际 |
|---|---|---|---|---|---|---|
| ENV-001 | ENV | SCRIPT | P0 | **PASS** | Skill 脚本能在当前环境用 Python 运行 | Python 3.13.16 (CPython) |
| ENV-002 | ENV | SCRIPT | P2 | **PASS** | 记录操作系统与 shell 线索 | Linux-6.18.44-fc-v114-x86_64-with-glibc2.39 · shell 线索 {'SHELL': 'bash'} |
| ENV-003 | ENV | SCRIPT | P0 | **PASS** | 报告目录可写（含中文/空格路径） | 报告目录可写，含中文与空格路径的读写往返成功 |
| ENV-004 | ENV | SCRIPT | P2 | **PASS** | 当前工作目录可写性 | 当前工作目录可写 |
| ENV-005 | ENV | SCRIPT | P3 | **PASS** | Node 可用性探测（仅记录） | node 在 PATH 中：True（v0.1 不依赖 Node） |
| ENV-007 | ENV | AGENT | P2 | **NOT_TESTED** | 记录 WorkBuddy 客户端版本 | 需要 Agent 在 WorkBuddy 中记录 |
| ENV-008 | ENV | AGENT | P1 | **NOT_TESTED** | 记录 Skill 安装形态：本地/市场、是否付费、是否加密、开发者/购买者 | 需要 Agent 在 WorkBuddy 中记录 |
| ENV-009 | ENV | AGENT | P2 | **NOT_TESTED** | 记录 Agent 实际使用的 shell 与命令执行方式 | 需要 Agent 在 WorkBuddy 中记录 |
| PKG-001 | PKG | SCRIPT | P0 | **PASS** | SKILL.md frontmatter 合法且必填字段齐全 | name=designbuddy-qa version=0.1.4 |
| PKG-002 | PKG | SCRIPT | P0 | **PASS** | 所有 @references 引用都能解析 | 检查 SKILL.md 中的引用 |
| PKG-003 | PKG | SCRIPT | P0 | **PASS** | 必需脚本、模板、夹具存在 | 缺失：无 |
| PKG-004 | PKG | SCRIPT | P1 | **PASS** | 安装后的包与发布构建一致（package-manifest） | 检查 47 个文件；不一致 无；缺失 无 |
| PKG-005 | PKG | SCRIPT | P0 | **PASS** | 包内无绝对路径、密钥、字体、垃圾文件、非标准根目录项 | lint errors=0 warnings=0 files=48；平台元数据（另见 PKG-008）：['_user_meta.json'] |
| PKG-006 | PKG | SCRIPT | P0 | **PASS** | 入口脚本可作为独立子进程执行 | exit=0 version=0.1.4 |
| PKG-008 | PKG | SCRIPT | P1 | **PASS** | 安装副本中的额外文件：平台元数据与未知文件分开判定 | 平台元数据文件：['_user_meta.json']；未知额外文件：无 |
| PKG-007 | PKG | SCRIPT | P0 | **PASS** | 运行时可读取内置模板 | 运行时读取模板成功：{'brand-skill.SKILL.md.tmpl': 2429, 'preview.poster.html.tmpl': 2044, 'preview.onepager.html.tmpl': 2327, 'portable.DESIGN.md.tmpl': 848} |
| CORE-001 | CORE | SCRIPT | P0 | **PASS** | Existing 路径：导入→冲突检测→裁决→Brand IR | 检测到冲突 1 个，已裁决=True，release 校验错误 0，构建 ok=True |
| CORE-002 | CORE | SCRIPT | P0 | **PASS** | Partial 路径：保留已知规则，补全缺口 | 主色保留 #9A3412(USER_CONFIRMED)；生成角色 ['ink', 'paper', 'surface', 'accent', 'on-primary', 'brand-text', 'success', 'warning', 'error', 'info']；标题字体 Source Han Serif |
| CORE-003 | CORE | SCRIPT | P0 | **PASS** | New 路径：Discovery→2–3 个方向→选择→完整系统 | 候选方向 ['bold-technical', 'quiet-professional', 'editorial-modern'] → 选择 bold-technical |
| CORE-004 | CORE | SCRIPT | P1 | **PASS** | schema_version 校验 | DBError E_SCHEMA_VERSION: Brand IR schema_version='9.9.9'，本版本只支持 1.0.0 |
| CORE-005 | CORE | SCRIPT | P1 | **PASS** | Provenance / Confidence 覆盖 | 46 个事实；分布 {'DOCUMENTED': 18, 'GENERATED': 25, 'USER_CONFIRMED': 3} |
| CORE-006 | CORE | SCRIPT | P0 | **PASS** | Design Gates 顺序与放行 | 跳过 G1 直接 G3：DBError E_GATE_ORDER: 必须先确认 G2，才能进行 G3；未过 Gate 构建：DBError E_NOT_READY: 尚未满足导出条件：MUST/NEVER 规则 MUST-COLOR-01 尚未审核；越权修改：DBError E_PATCH: G1 不允许修改字段 co |
| CORE-007 | CORE | SCRIPT | P0 | **PASS** | 编译 WorkBuddy Brand Skill（lint + 单根 ZIP） | lint errors=[]；ZIP 根目录=['alpha-demo-brand-system'] |
| CORE-008 | CORE | SCRIPT | P0 | **PASS** | Portable Design System（DESIGN.md + DTCG tokens + CSS） | 文件齐全=True；DESIGN.md 有 frontmatter=True；DTCG $type=color |
| CORE-009 | CORE | SCRIPT | P1 | **PASS** | 生成可离线打开的 Preview | 预览 ['onepager.html', 'poster.html']；离线=True |
| CORE-010 | CORE | SCRIPT | P0 | **PASS** | 单一事实来源：主色在 tokens.json / tokens.css / references / DESIGN.md / Preview 一致 | {"primary": "#1F4FD8", "checks": [true, true, true, true, true]} |
| CORE-011 | CORE | SCRIPT | P1 | **PASS** | 同一输入两次构建结果可复现 | 比较 38 个文件（排除 generated_at）；差异 无；build_id 9df45b7847cf / 9df45b7847cf |
| CORE-012 | CORE | SCRIPT | P1 | **PASS** | Brand Skill 自检：原样 MATCH，篡改后 MISMATCH | 原样：exit=0 MATCH；篡改后：exit=1 MISMATCH |
| CORE-013 | CORE | SCRIPT | P1 | **PASS** | Alpha / Beta / Gamma 的 Brand Skill ZIP、Portable ZIP、Preview 已输出 | 已复制 9 个产物到 artifacts/ |
| CORE-014 | CORE | SCRIPT | P1 | **PASS** | 交付包复制到下载文件夹（DesignBuddy/<品牌>/），附安装说明 | 交付到 <下载>/DesignBuddy/alpha-demo/：['alpha-demo-brand-system-1.0.0.zip', 'alpha-demo-portable-design-system-1.0.0.zip', 'preview/onepager.html', 'preview/poster.h |
| QA-001 | QA | SCRIPT | P0 | **PASS** | WCAG 对比度计算与已知基准一致 | #000000/#FFFFFF=21.00 PASS; #777777/#FFFFFF=4.48 WARNING; #777777/#FFFFFF=4.48 PASS; #1F4FD8/#FFFFFF=6.63 PASS; #F59E0B/#FFFFFF=2.15 FAIL |
| QA-002 | QA | SCRIPT | P0 | **PASS** | Alpha / Beta / Gamma 核心配色组合达到 AA | brand-alpha: 10 组，核心 FAIL 无；brand-beta: 10 组，核心 FAIL 无；brand-gamma-new: 10 组，核心 FAIL 无 |
| QA-003 | QA | SCRIPT | P0 | **PASS** | 低对比度核心组合阻止放行，USER_OVERRIDE 留痕 | G3 被拦截：DBError E_GATE_BLOCKED: 核心配色对比度不达标：body-text/page 2.54:1, body-text/surface 2.34:1；override 后状态 USER_OVERRIDE；记录 ['body-text/page', 'body-text/surface'] |
| QA-004 | QA | SCRIPT | P1 | **PASS** | 检测未批准颜色（预览与 Brand Skill 校验脚本） | 原始预览未批准颜色 无；注入后检出 ['#123456']；Brand Skill 的 validate_brand.py exit=1 |
| QA-005 | QA | SCRIPT | P2 | **PASS** | 禁止规则：强调色不得用作文字 | 原始：{'preview.onepager.html.accent_not_text': 'PASS', 'preview.poster.html.accent_not_text': 'PASS'}；注入 color:var(--color-accent) 后被检出=True |
| QA-006 | QA | SCRIPT | P1 | **PASS** | 字体缺失或未知时有回退栈且不打包 | 未知字体回退栈=['Songti SC', 'SimSun', 'Noto Serif SC', 'serif']；许可=UNKNOWN — 需用户确认；bundled=False |
| QA-007 | QA | SCRIPT | P0 | **PASS** | 未授权资产不打包，manifest 记录排除原因 | manifest={'logo-main': True, 'pattern-3p': False}；Skill 内 SVG=['asset.fixture.alpha-logo.svg']；Portable=['fixture.alpha-logo.svg'] |
| QA-008 | QA | SCRIPT | P1 | **PASS** | 检测互相矛盾的规则（MUST vs NEVER） | DBError E_IR_INVALID: Brand IR 校验失败：规则互相矛盾：MUST-COLOR-09, NEVER-COLOR-02（color.accent / use_as_text） |
| QA-009 | QA | SCRIPT | P0 | **PASS** | 所有输出中不含字体文件 | 字体文件：无 |
| QA-010 | QA | SCRIPT | P1 | **PASS** | Brand Skill 内容完整（17 个 references） | 缺失 references：[] |
| SEC-001 | SEC | SCRIPT | P0 | **PASS** | 恶意 HTML 字符串被转义 | 未转义出现次数=0；已转义=True |
| SEC-002 | SEC | SCRIPT | P0 | **PASS** | 资产路径穿越（../）被拒绝 | DBError E_PATH: assets[0].file 含有不安全的路径片段：../../../etc/passwd |
| SEC-003 | SEC | SCRIPT | P0 | **PASS** | 资产绝对路径被拒绝 | DBError E_PATH: assets[0].file 必须是相对路径：/etc/passwd |
| SEC-004 | SEC | SCRIPT | P0 | **PASS** | 非法 slug（../evil）被拒绝 | DBError E_SLUG: brand.slug 只能包含小写字母、数字和连字符（≤48）：'../evil' |
| SEC-006 | SEC | SCRIPT | P1 | **PASS** | 重复规则 ID 被拒绝 | DBError E_IR_INVALID: Brand IR 校验失败：规则 ID 重复：NEVER-PHOTO-01 |
| SEC-007 | SEC | SCRIPT | P0 | **PASS** | 品牌名中的换行（frontmatter 注入）被拒绝 | DBError E_FIELD: 字段 brand.name 含有换行或控制字符 |
| SEC-013 | SEC | SCRIPT | P0 | **PASS** | 字体名中的 CSS/HTML 注入被拒绝 | DBError E_FONT_NAME: 字体名 fonts.heading 含有不允许的字符："x';}</style><script>alert(1)</script>" |
| SEC-005 | SEC | SCRIPT | P1 | **PASS** | 无效 JSON 优雅失败 | exit=2 code=E_INVALID_JSON traceback=False |
| SEC-008 | SEC | SCRIPT | P0 | **PASS** | 含脚本的 SVG 不被纳入 | include=False notes=SVG 含脚本或事件属性，已拒绝纳入 |
| SEC-009 | SEC | SCRIPT | P0 | **PASS** | 不覆盖已存在的不同版本 Skill | DBError E_EXISTS: 导出目录中已有不同版本的 beta-demo-brand-system（build user-existing），不会覆盖。确认后使用 --force；原文件未被改动=True |
| SEC-010 | SEC | SCRIPT | P0 | **PASS** | 不联网（静态检查网络模块） | 网络模块引用：无 |
| SEC-011 | SEC | SCRIPT | P1 | **PASS** | 输出限定在报告目录，Skill 自身不被修改 | 产物均在报告目录内=True；Skill 自身文件未被修改=True |
| SEC-014 | SEC | SCRIPT | P0 | **PASS** | 交付不覆盖用户已有文件，重复交付幂等 | 原文件保留=True；新文件改名=True；重复交付不重写=True；目录不存在时报错=True |
| SEC-012 | SEC | SCRIPT | P1 | **PASS** | 报告脱敏：不出现用户主目录绝对路径 | 检查 5 个报告文件 + agent-notes（Windows/POSIX、正反斜杠、JSON 转义、盘符大小写、用户名路径段）；泄漏：无 |
| INS-000 | INS | SCRIPT | P0 | **PASS** | 代码中没有 H5（直接写入 WorkBuddy 内部 Skill 目录） | 代码中出现 WorkBuddy 安装目录的痕迹：无 |
| INS-001 | INS | AGENT | P1 | **NOT_TESTED** | H1：原生安装工具（检查 Agent 工具列表中是否存在） | 需要在 WorkBuddy 中执行 |
| INS-002 | INS | AGENT | P1 | **NOT_TESTED** | H2：交给内置 Skill Creator 原样安装（检查是否改写） | 需要在 WorkBuddy 中执行 |
| INS-003 | INS | MANUAL | P1 | **NOT_TESTED** | H3：用户发一句话触发原生安装 | 需要在 WorkBuddy 中执行 |
| INS-004 | INS | MANUAL | P1 | **NOT_TESTED** | H4：通过 UI 导入 ZIP | 需要在 WorkBuddy 中执行 |
| INS-005 | INS | AGENT | P0 | **NOT_TESTED** | 安装后 Brand Skill selfcheck=MATCH、版本与关键规则一致 | 需要先完成 INS-001..004 中至少一项 |
| INS-006 | INS | AGENT | P0 | **NOT_TESTED** | 安装前已向用户展示摘要并取得明确确认 | 需要 Agent 记录 |
| INS-007 | INS | MANUAL | P1 | **NOT_TESTED** | 记录 designbuddy-qa 本身是用哪种方式安装的（对话中附 ZIP 文件 / 客户端 UI 导入 / 其他），以及是否由平台完成 | 需要用户说明 |
| MB-001 | MB | SCRIPT | P1 | **PASS** | Alpha / Beta 的 description 含名称、别名，SKILL.md 含消歧规则 | brand-alpha: 名称/别名齐全=True 消歧规则=True；brand-beta: 名称/别名齐全=True 消歧规则=True |
| MB-002 | MB | SCRIPT | P1 | **PASS** | Alpha / Beta 别名不重叠 | 别名交集：无 |
| MB-003 | MB | MANUAL | P1 | **NOT_TESTED** | 独立新会话：「给 Alpha Demo 做一份 PPT 封面」只触发 Alpha | PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数 |
| MB-004 | MB | MANUAL | P1 | **NOT_TESTED** | 独立新会话：「做一份 PPT」不擅自套用任何品牌（应先询问） | PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数 |
| MB-005 | MB | MANUAL | P1 | **NOT_TESTED** | 独立新会话：「把 Beta Demo 的这段文档改成 Alpha Demo 风格」source=Beta、target=Alpha | PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数 |
| PP-001 | PP | SCRIPT | P1 | **PASS** | 当前安装形态下：读取模板、执行脚本、生成文件 | 当前安装环境中：模板可读、脚本可执行、产物已写出。只代表当前安装形态（见 ENV-008），不代表付费加密形态 |
| PP-002 | PP | MANUAL | P1 | **BLOCKED** | 市场付费加密形态（开发者账号）：资源、脚本、生成器可用性 | BLOCKED: REQUIRES_PAID_ENCRYPTED_MARKETPLACE_RUNTIME |
| PP-003 | PP | MANUAL | P1 | **BLOCKED** | 市场付费加密形态（普通购买者账号）：资源、脚本、生成器可用性 | BLOCKED: REQUIRES_PAID_ENCRYPTED_MARKETPLACE_RUNTIME |
| UX-001 | UX | SCRIPT | P2 | **PASS** | 最短路径的用户决策次数 | 最短路径用户决策：Gate 决策 7 次 + 安装确认 1 次 + 选择保存目录 ≤1 次 = 9 |
| UX-002 | UX | SCRIPT | P1 | **PASS** | 用户无需编写代码或临时设计通用模板 | 三条路径均由预置编译器完成，用户只做 KEEP/CHANGE 决策 |
| UX-003 | UX | SCRIPT | P3 | **PASS** | 构建耗时 | 构建耗时（秒）：{'brand-alpha': 0.07, 'brand-beta': 0.05, 'brand-gamma-new': 0.05} |
| UX-004 | UX | SCRIPT | P1 | **PASS** | 错误后可恢复，不破坏工作区 | 拦截后工作区仍有效；重复 init 被拒绝；修正 color.ink 后 G3 通过 |

详细字段见 `results.json`；失败与阻塞见 `issues.md`；多品牌新会话测试见 `next-session-prompts.md`。
