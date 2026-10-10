---
name: dbprobe-installation
display_name: DesignBuddy 安装链路探测
display_name_en: DesignBuddy Installation Probe
description: DesignBuddy 开发测试专用。仅当用户明确说“运行 DesignBuddy 安装探测”或“run dbprobe installation”时使用。用确定性生成器生成一个测试 Skill，再在用户明确确认后，尝试交给 WorkBuddy 原生机制安装，并记录实际走通的安装路径。不要在其他任何场景使用。
description_zh: DesignBuddy 开发测试专用：生成测试 Skill，并验证原生安装交接路径。
description_en: DesignBuddy test-only probe that generates a sample skill and tests native install handoff.
version: 1.0.0
author: DesignBuddy Dev
user-invocable: true
disable-model-invocation: false
---

# DesignBuddy 安装链路探测（测试专用）

## 目标

验证下面这条链路，并**如实**记录每一步的实际情况：

```
生成 Skill → 交接原生安装 → 用户确认 → 安装 → 核对
```

## 纪律（必须遵守）

- **禁止**直接把文件写进或复制进 WorkBuddy 自己的 Skill 安装目录（H5，V1 不批准）。
- 不安装任何软件或依赖。
- 只在当前工作目录下的 `dbprobe-results/` 中写文件。
- 在用户**明确回复"确认安装"**之前，不执行任何安装动作。
- 不修改、不覆盖用户已有的其他 Skill。如果发现已存在同名的 `dbprobe-generated-hello`，先告诉用户，再等待指示。
- 某一步失败时，原样记录错误，不要擅自绕路。

## 参数

如果用户说了"版本 1.1.0"（升级测试），生成时加上 `--version 1.1.0`；否则默认为 1.0.0。

## 步骤

### B1. 生成

依次尝试 `python3`、`python`、`py -3`，用第一个可用的解释器运行：

```
<python命令> "<Skill目录>/scripts/gen_skill.py" [--version 1.1.0]
```

- 原样贴出脚本报告，记下 `skill_dir`、`zip` 和 `build_id`。
- 如果没有可用的 Python：
  1. 把 B1 记为 BLOCKED（脚本路径不可用）；
  2. 改为按 @references/agent-write-spec.md 手写一个 Skill（V-IN-01 回退路径）；
  3. 标注 UNVALIDATED。

### B2. 安装能力盘点（只盘点，不调用）

1. **H1**：检查你当前可用的工具列表，找出名称或说明中涉及安装、导入、创建 Skill 的工具。列出工具名和参数名。如果没有，写"无"。
2. **H2**：检查当前是否有内置的 Skill Creator（或同类）技能可以调用。写明名称，或写"无"。
3. **H5 检查**：确认你**没有**、也**不会**直接写入 WorkBuddy 的 Skill 目录。

### B3. 请求用户确认

向用户展示以下内容：

- Skill 名称、版本、`build_id`；
- 文件位置；
- 可选的安装路径（只列出 B2 中确实存在的）：
  - **H1** 原生安装工具：<工具名>
  - **H2** 交给 Skill Creator，要求"原样安装、不得修改任何文件"
  - **H3** 由用户自己发一句安装指令（给出可直接复制的句子：`请把位于 <skill_dir> 的 Skill 原样安装到 WorkBuddy，不要修改任何文件内容。`）
  - **H4** 手动导入 ZIP：<zip 路径>

然后询问：

> 请回复"确认安装 H1 / H2 / H3 / H4"中的一项。

**停在这里等待用户回复。**

### B4. 执行（仅针对用户选择的那一项）

| 选项 | 做法 |
|---|---|
| H1 | 调用该工具，传入 `skill_dir`（或工具要求的 ZIP 路径）。原样记录工具的返回内容 |
| H2 | 调用 Skill Creator，明确要求原样安装 `skill_dir` 中的 Skill，不重新生成、不改写任何文件。记录它实际做了什么（有没有改写内容、有没有重新生成） |
| H3 | 只把那句指令交给用户，由用户发送；你不执行安装 |
| H4 | 只告诉用户 ZIP 路径，以及"请通过 WorkBuddy 的 Skill 导入入口手动导入"；你不执行安装 |

### B5. 输出报告

```
## DBPROBE INSTALLATION REPORT v1.0.0
B1 生成: Result=<...> | 方式=<脚本/手写> | version=<...> | build_id=<...>
    skill_dir=<...> | zip=<...>
B2 盘点: H1=<工具名或无> | H2=<技能名或无> | H5=未使用
B3 用户选择: <H1/H2/H3/H4/未确认>
B4 执行: Result=<PASS/FAIL/PARTIAL/BLOCKED> | 平台返回=<原文> | 是否改写内容=<是/否/未知>
下一步: 请在【新对话】中输入"运行 DesignBuddy 安装验证"做安装后核对
```
