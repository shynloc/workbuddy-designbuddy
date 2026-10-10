# TEST_MATRIX — DesignBuddy QA v0.1.2

由 `tools/build_release.py` 从 QA Runner 的用例定义自动生成。Test ID 稳定，后续版本只新增、不重排。

执行类型：**SCRIPT** = QA Runner 自动判定；**AGENT** = WorkBuddy 中的 Agent 按协议执行并用 `record` 回填；**MANUAL** = 需要用户操作或独立新会话。

## ENV · 运行环境（8）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| ENV-001 | SCRIPT | P0 | Skill 脚本能在当前环境用 Python 运行 | Python ≥ 3.8 正常执行 | PASS |
| ENV-002 | SCRIPT | P2 | 记录操作系统与 shell 线索 | 得到 OS 与 shell 信息 | PASS |
| ENV-003 | SCRIPT | P0 | 报告目录可写（含中文/空格路径） | 写入、读取、删除成功 | PASS |
| ENV-004 | SCRIPT | P2 | 当前工作目录可写性 | 可写；不可写时需改用用户指定目录 | PASS |
| ENV-005 | SCRIPT | P3 | Node 可用性探测（仅记录） | 完成探测 | PASS |
| ENV-007 | AGENT | P2 | 记录 WorkBuddy 客户端版本 | Agent 如实记录 | NOT_TESTED |
| ENV-008 | AGENT | P1 | 记录 Skill 安装形态：本地/市场、是否付费、是否加密、开发者/购买者 | Agent 如实记录 | NOT_TESTED |
| ENV-009 | AGENT | P2 | 记录 Agent 实际使用的 shell 与命令执行方式 | Agent 如实记录 | NOT_TESTED |

## PKG · 包装与资源（8）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| PKG-001 | SCRIPT | P0 | SKILL.md frontmatter 合法且必填字段齐全 | 无 frontmatter 错误 | PASS |
| PKG-002 | SCRIPT | P0 | 所有 @references 引用都能解析 | 无缺失引用 | PASS |
| PKG-003 | SCRIPT | P0 | 必需脚本、模板、夹具存在 | 全部存在 | PASS |
| PKG-004 | SCRIPT | P1 | 安装后的包与发布构建一致（package-manifest） | 全部 SHA-256 一致 | PASS |
| PKG-005 | SCRIPT | P0 | 包内无绝对路径、密钥、字体、垃圾文件、非标准根目录项 | lint 无错误 | PASS |
| PKG-006 | SCRIPT | P0 | 入口脚本可作为独立子进程执行 | 退出码 0，版本号正确 | PASS |
| PKG-008 | SCRIPT | P1 | 安装副本中的额外文件：平台元数据与未知文件分开判定 | 没有未知的额外文件 | PASS |
| PKG-007 | SCRIPT | P0 | 运行时可读取内置模板 | 模板可读且非空 | PASS |

## CORE · 核心功能（13）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| CORE-001 | SCRIPT | P0 | Existing 路径：导入→冲突检测→裁决→Brand IR | 冲突被检测并经 Gate 裁决，IR 通过 release 校验 | PASS |
| CORE-002 | SCRIPT | P0 | Partial 路径：保留已知规则，补全缺口 | 已知主色保留；缺失项标记 GENERATED | PASS |
| CORE-003 | SCRIPT | P0 | New 路径：Discovery→2–3 个方向→选择→完整系统 | 生成 3 个候选，选择后得到完整系统 | PASS |
| CORE-004 | SCRIPT | P1 | schema_version 校验 | 错误版本被拒绝 | PASS |
| CORE-005 | SCRIPT | P1 | Provenance / Confidence 覆盖 | 每个事实都有合法来源与置信度 | PASS |
| CORE-006 | SCRIPT | P0 | Design Gates 顺序与放行 | 跳级、未确认构建、越权修改都被拒绝 | PASS |
| CORE-007 | SCRIPT | P0 | 编译 WorkBuddy Brand Skill（lint + 单根 ZIP） | lint 无错误，ZIP 只有一个根目录 | PASS |
| CORE-008 | SCRIPT | P0 | Portable Design System（DESIGN.md + DTCG tokens + CSS） | 全部文件生成且格式正确 | PASS |
| CORE-009 | SCRIPT | P1 | 生成可离线打开的 Preview | poster.html 与 onepager.html，无外部资源 | PASS |
| CORE-010 | SCRIPT | P0 | 单一事实来源：主色在 tokens.json / tokens.css / references / DESIGN.md / Preview 一致 | 5 处一致 | PASS |
| CORE-011 | SCRIPT | P1 | 同一输入两次构建结果可复现 | 规范化后逐文件一致 | PASS |
| CORE-012 | SCRIPT | P1 | Brand Skill 自检：原样 MATCH，篡改后 MISMATCH | 两种情况都被正确识别 | PASS |
| CORE-013 | SCRIPT | P1 | Alpha / Beta / Gamma 的 Brand Skill ZIP、Portable ZIP、Preview 已输出 | 产物齐全 | PASS |

## QA · 设计质量（10）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| QA-001 | SCRIPT | P0 | WCAG 对比度计算与已知基准一致 | 21:1、4.48:1、6.63:1、2.15:1 及分级正确 | PASS |
| QA-002 | SCRIPT | P0 | Alpha / Beta / Gamma 核心配色组合达到 AA | 无核心 FAIL | PASS |
| QA-003 | SCRIPT | P0 | 低对比度核心组合阻止放行，USER_OVERRIDE 留痕 | G3 被拦截；用户坚持后记录 USER_OVERRIDE | PASS |
| QA-004 | SCRIPT | P1 | 检测未批准颜色（预览与 Brand Skill 校验脚本） | 原始无违规；注入的颜色被检出 | PASS |
| QA-005 | SCRIPT | P2 | 禁止规则：强调色不得用作文字 | 原始通过；违规被检出 | PASS |
| QA-006 | SCRIPT | P1 | 字体缺失或未知时有回退栈且不打包 | 回退栈以通用字族结尾；许可标为未知；不打包 | PASS |
| QA-007 | SCRIPT | P0 | 未授权资产不打包，manifest 记录排除原因 | 只打包 user-owned Logo | PASS |
| QA-008 | SCRIPT | P1 | 检测互相矛盾的规则（MUST vs NEVER） | 被拒绝并指出冲突规则 | PASS |
| QA-009 | SCRIPT | P0 | 所有输出中不含字体文件 | 无 .ttf/.otf/.woff 等 | PASS |
| QA-010 | SCRIPT | P1 | Brand Skill 内容完整（17 个 references） | 全部存在 | PASS |

## SEC · 安全与隐私（13）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| SEC-001 | SCRIPT | P0 | 恶意 HTML 字符串被转义 | 输出中没有可执行的 <script>/<img onerror> | PASS |
| SEC-002 | SCRIPT | P0 | 资产路径穿越（../）被拒绝 | 返回 E_PATH，不产生输出 | PASS |
| SEC-003 | SCRIPT | P0 | 资产绝对路径被拒绝 | 返回 E_PATH，不产生输出 | PASS |
| SEC-004 | SCRIPT | P0 | 非法 slug（../evil）被拒绝 | 返回 E_SLUG，不产生输出 | PASS |
| SEC-006 | SCRIPT | P1 | 重复规则 ID 被拒绝 | 返回 E_IR_INVALID，不产生输出 | PASS |
| SEC-007 | SCRIPT | P0 | 品牌名中的换行（frontmatter 注入）被拒绝 | 返回 E_FIELD，不产生输出 | PASS |
| SEC-013 | SCRIPT | P0 | 字体名中的 CSS/HTML 注入被拒绝 | 返回 E_FONT_NAME，不产生输出 | PASS |
| SEC-005 | SCRIPT | P1 | 无效 JSON 优雅失败 | 退出码 2、结构化错误、无 Traceback | PASS |
| SEC-008 | SCRIPT | P0 | 含脚本的 SVG 不被纳入 | include=false 并说明原因 | PASS |
| SEC-009 | SCRIPT | P0 | 不覆盖已存在的不同版本 Skill | 返回 E_EXISTS，原文件不变 | PASS |
| SEC-010 | SCRIPT | P0 | 不联网（静态检查网络模块） | 没有任何网络模块导入 | PASS |
| SEC-011 | SCRIPT | P1 | 输出限定在报告目录，Skill 自身不被修改 | 全部产物在 <run-dir>/artifacts | PASS |
| SEC-012 | SCRIPT | P1 | 报告脱敏：不出现用户主目录绝对路径 | 报告中只有 <HOME>/<RUN_DIR> 占位 | PASS |

## INS · 安装链路（8）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| INS-000 | SCRIPT | P0 | 代码中没有 H5（直接写入 WorkBuddy 内部 Skill 目录） | 无相关路径 | PASS |
| INS-001 | AGENT | P1 | H1：原生安装工具（检查 Agent 工具列表中是否存在） | 安装成功，selfcheck=MATCH；或如实记录 BLOCKED | NOT_TESTED |
| INS-002 | AGENT | P1 | H2：交给内置 Skill Creator 原样安装（检查是否改写） | 安装成功，selfcheck=MATCH；或如实记录 BLOCKED | NOT_TESTED |
| INS-003 | MANUAL | P1 | H3：用户发一句话触发原生安装 | 安装成功，selfcheck=MATCH；或如实记录 BLOCKED | NOT_TESTED |
| INS-004 | MANUAL | P1 | H4：通过 UI 导入 ZIP | 安装成功，selfcheck=MATCH；或如实记录 BLOCKED | NOT_TESTED |
| INS-005 | AGENT | P0 | 安装后 Brand Skill selfcheck=MATCH、版本与关键规则一致 | MATCH | NOT_TESTED |
| INS-006 | AGENT | P0 | 安装前已向用户展示摘要并取得明确确认 | 有确认记录 | NOT_TESTED |
| INS-007 | MANUAL | P1 | 记录 designbuddy-qa 本身是用哪种方式安装的（对话中附 ZIP 文件 / 客户端 UI 导入 / 其他），以及是否由平台完成 | 如实记录；这是已知能装上本地 ZIP 的路径 | NOT_TESTED |

## MB · 多品牌（5）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| MB-001 | SCRIPT | P1 | Alpha / Beta 的 description 含名称、别名，SKILL.md 含消歧规则 | 全部包含 | PASS |
| MB-002 | SCRIPT | P1 | Alpha / Beta 别名不重叠 | 交集为空 | PASS |
| MB-003 | MANUAL | P1 | 独立新会话：「给 Alpha Demo 做一份 PPT 封面」只触发 Alpha | 见 next-session-prompts.md | NOT_TESTED |
| MB-004 | MANUAL | P1 | 独立新会话：「做一份 PPT」不擅自套用任何品牌（应先询问） | 见 next-session-prompts.md | NOT_TESTED |
| MB-005 | MANUAL | P1 | 独立新会话：「把 Beta Demo 的这段文档改成 Alpha Demo 风格」source=Beta、target=Alpha | 见 next-session-prompts.md | NOT_TESTED |

## PP · 付费加密（3）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| PP-001 | SCRIPT | P1 | 当前安装形态下：读取模板、执行脚本、生成文件 | 全部可用 | PASS |
| PP-002 | MANUAL | P1 | 市场付费加密形态（开发者账号）：资源、脚本、生成器可用性 | 需要真实付费加密环境 | BLOCKED |
| PP-003 | MANUAL | P1 | 市场付费加密形态（普通购买者账号）：资源、脚本、生成器可用性 | 需要真实付费加密环境 | BLOCKED |

## UX · 用户体验（4）

| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |
|---|---|---|---|---|---|
| UX-001 | SCRIPT | P2 | 最短路径的用户决策次数 | ≤ 10 次 | PASS |
| UX-002 | SCRIPT | P1 | 用户无需编写代码或临时设计通用模板 | 三条路径只用数据决策完成 | PASS |
| UX-003 | SCRIPT | P3 | 构建耗时 | 每个品牌 < 30 秒 | PASS |
| UX-004 | SCRIPT | P1 | 错误后可恢复，不破坏工作区 | 失败后可修正并继续 | PASS |

合计 72 个用例：AGENT 7、MANUAL 8、SCRIPT 57。
