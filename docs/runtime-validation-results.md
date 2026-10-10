---
title: Runtime Validation Results
status: LIVING DOCUMENT — 第一轮尚未执行
last_updated: 2026-10-10
---

# Runtime Validation Results

本文记录真实 WorkBuddy 环境中的测试结果。测试方法见 [`tests/probes/PROBE_TEST_GUIDE.md`](../tests/probes/PROBE_TEST_GUIDE.md)，用例总表见 [`validation-plan.md`](validation-plan.md)。

## 记录规则

1. **Result** 只能取以下值：`PASS` · `FAIL` · `PARTIAL` · `BLOCKED` · `NOT_TESTED`。
2. **Environment** 必须写明以下信息，不同形态的结果不能互相代替：
   - 操作系统；
   - Skill 来源（本地 / 市场）；
   - 是否付费；
   - 是否加密；
   - 账号类型（开发者 / 购买者）。
3. 某项测试只能在正式发布后完成时，记为 `BLOCKED`，**不得**用未加密版的结果代替。
4. **Confidence**（high / medium / low）表示本次结果的可信度。只测过一次、或结果不稳定时，最高记为 medium。
5. 单次实验结果只能把 runtime-capabilities.md 中对应条目更新为 `OBSERVED（条件：…）`，**不得上升为通用平台保证**。

## 真机运行记录

| Run ID | 包 | 环境 | SCRIPT | 结论 | 后续 |
|---|---|---|---|---|---|
| qa-20261011-015550-2691 | designbuddy-qa 0.1.0（未直接记录 ZIP 哈希；PKG-004 校验 46 个文件一致） | Windows 11 · WorkBuddy 5.7.7.0 · 本地 · 未加密 · 开发者 | 55/56（PKG-005 FAIL） | 1 个 P0、1 个被误判的 P1（脱敏）、INS-002 证据不足 | v0.1.1 修复，见 `qa/FIX_REPORT.md` |

> 下文的 T-* 条目来自第一轮 Probe 计划（已被 QA 候选版取代），保留以作历史记录。

## 预检（非 WorkBuddy 环境，不作为证据）

2026-10-10，在开发容器（Linux、Python 3.13、Node 22）中做了以下检查。这只说明测试包本身可以运行，**不代表 WorkBuddy 中的行为**：

| 检查 | 结果 |
|---|---|
| 5 个 Probe 通过 WB-OPDK 的 `validate_skill.py` | 通过 |
| 5 个 Probe 通过 `pack_probes.py` 的 lint 检查 | 通过 |
| env_probe.py 与 env_probe_node.js | 运行正常 |
| protect_probe.py | 全部检查项为 PASS（未加密的本地文件） |
| gen_skill.py → selfcheck.py | 原样解压后显示 MATCH；篡改任意一个文件后显示 MISMATCH |
| Alpha / Beta 的 tokens 对比度 | 全部 PASS |

**发现**：WB-OPDK 的校验器会把紧跟在 `@references/x.md` 后面的中文标点误识别为路径的一部分。

- 处理：所有引用路径后面统一加一个空格。
- 后续要求：DesignBuddy 编译器必须遵守这一规则。
- 状态：WorkBuddy 自身的解析器是否有同样的问题尚未验证（UNVERIFIED）。

---

### T-ENV-1

```
Test ID: T-ENV-1
Environment: macOS
WorkBuddy Version: —
Capability: 运行环境：解释器 / Shell / 工作目录 / 文件读写 / Skill 自身资源读取
Expected: dbprobe-environment 报告：A2 能复述标记；A4 至少一个解释器可用；ENV-WRITE、ENV-SELFREAD 为 PASS
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 决定 Capability-first 的分级在 macOS 上的实际分布
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-ENV-2

```
Test ID: T-ENV-2
Environment: Windows（无 Python）
WorkBuddy Version: —
Capability: 同 T-ENV-1
Expected: A4 中 Python 全部不可用属于事实，不算失败；记录 Agent 的兜底行为
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 决定 AGENT 兜底分级的必要性和 QA 中 UNVALIDATED 的比例
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-ENV-3

```
Test ID: T-ENV-3
Environment: Windows（有 Python）
WorkBuddy Version: —
Capability: 同 T-ENV-1
Expected: 同 T-ENV-1；确认 python / py / python3 哪个可用，以及 Shell 类型
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 决定 Windows 上的解释器探测顺序
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-PRO-L

```
Test ID: T-PRO-L
Environment: macOS · 本地安装 · 未付费 · 未加密 · 开发者
WorkBuddy Version: —
Capability: 保护基线：references 读取 / 脚本执行 / 资源读取 / 资源输出 / 生成器 / 源码可见性
Expected: P-EXEC、P-RES-READ、P-RES-EXPORT、P-GEN-EMBED、P-GEN-RENDER 均为 PASS（未加密基线）
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 只作为对照基线；不能代替加密形态的结论
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-PRO-M1

```
Test ID: T-PRO-M1
Environment: 市场安装 · 付费 · 加密 · 开发者本人
WorkBuddy Version: —
Capability: 同 T-PRO-L（加密形态）
Expected: 待测
Actual: —
Evidence: —
Result: BLOCKED
Confidence: —
Impact: 决定 D-03：P-EXEC 与 P-GEN-RENDER 为 PASS → 保留完整 Compiler 架构
Recommended Action: BLOCKED — 需要产品负责人批准发布付费测试包
```

### T-PRO-M2

```
Test ID: T-PRO-M2
Environment: 市场安装 · 付费 · 加密 · 普通购买者
WorkBuddy Version: —
Capability: 同 T-PRO-L（加密形态，购买者视角）
Expected: 待测
Actual: —
Evidence: —
Result: BLOCKED
Confidence: —
Impact: 确认开发者账号与购买者账号的行为是否一致
Recommended Action: BLOCKED — 需要产品负责人批准购买测试
```

### T-INS-H1

```
Test ID: T-INS-H1
Environment: macOS / Windows
WorkBuddy Version: —
Capability: H1 原生安装工具交接
Expected: Agent 能列出并调用原生安装工具；安装验证显示 overall MATCH、build_id 一致
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 决定主安装路径
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-INS-H2

```
Test ID: T-INS-H2
Environment: macOS / Windows
WorkBuddy Version: —
Capability: H2 交给内置 Skill Creator 原样安装
Expected: 安装成功，且没有重新生成或改写文件（overall MATCH）
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 如果出现改写 → H2 只能配合一致性校验使用，或被降级
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-INS-H3

```
Test ID: T-INS-H3
Environment: macOS / Windows
WorkBuddy Version: —
Capability: H3 用户发一句指令触发原生安装
Expected: 平台接管安装；验证 MATCH
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 作为不依赖 Agent 工具权限的备选主路径
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-INS-H4

```
Test ID: T-INS-H4
Environment: macOS / Windows
WorkBuddy Version: —
Capability: H4 ZIP 手动导入
Expected: 能找到导入入口；验证 MATCH
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 兜底路径的操作指引
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-INS-UP

```
Test ID: T-INS-UP
Environment: 任一
WorkBuddy Version: —
Capability: 同名 Skill 从 1.0.0 升级到 1.1.0
Expected: 记录是覆盖、并存还是报错；验证显示 1.1.0 和 #0F7B5F
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 决定升级流程和确认话术
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-MB-1

```
Test ID: T-MB-1
Environment: 只安装 Alpha
WorkBuddy Version: —
Capability: 品牌明确（正式名）时触发
Expected: 第一行为 Alpha 声明
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 自动调用命中率
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-MB-2

```
Test ID: T-MB-2
Environment: 只安装 Alpha
WorkBuddy Version: —
Capability: 品牌明确（中文别名）时触发
Expected: 第一行为 Alpha 声明
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 别名写入 description 是否有效
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-MB-3

```
Test ID: T-MB-3
Environment: 只安装 Alpha
WorkBuddy Version: —
Capability: 无品牌线索时不误套
Expected: 不触发 Alpha；如果触发了，先询问
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 误套用率
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-MB-4

```
Test ID: T-MB-4
Environment: 同时安装 Alpha 和 Beta
WorkBuddy Version: —
Capability: 无品牌线索时不随机选择
Expected: 先询问，或不套用任何品牌
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 多品牌消歧的核心用例
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-MB-5

```
Test ID: T-MB-5
Environment: 同时安装 Alpha 和 Beta
WorkBuddy Version: —
Capability: 明确指定 Alpha
Expected: 只触发 Alpha
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: —
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-MB-6

```
Test ID: T-MB-6
Environment: 同时安装 Alpha 和 Beta
WorkBuddy Version: —
Capability: 明确指定 Beta（中文别名）
Expected: 只触发 Beta
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: —
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-MB-7

```
Test ID: T-MB-7
Environment: 同时安装 Alpha 和 Beta
WorkBuddy Version: —
Capability: 品牌转换 Beta → Alpha
Expected: 识别出 source=Beta、target=Alpha；输出只使用 Alpha 的规则
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 品牌转换规则是否有效
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```

### T-MB-8

```
Test ID: T-MB-8
Environment: 同时安装 Alpha 和 Beta
WorkBuddy Version: —
Capability: 会话内品牌延续
Expected: 沿用 Alpha，并声明
Actual: —
Evidence: —
Result: NOT_TESTED
Confidence: —
Impact: 语境延续规则
Recommended Action: 按 PROBE_TEST_GUIDE 执行
```
