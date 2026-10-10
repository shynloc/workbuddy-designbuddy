---
name: dbprobe-environment
display_name: DesignBuddy 环境探测
display_name_en: DesignBuddy Environment Probe
description: DesignBuddy 开发测试专用。仅当用户明确说“运行 DesignBuddy 环境探测”或“run dbprobe environment”时使用；探测当前 WorkBuddy Skill 执行环境中的 Python/Node/Shell、工作目录、文件读写与 Skill 自身资源读取能力，并输出测试报告。不要在其他任何场景使用。
description_zh: DesignBuddy 开发测试专用：探测 WorkBuddy Skill 执行环境能力并输出报告。
description_en: DesignBuddy test-only probe that reports the WorkBuddy skill runtime capabilities.
category: productivity
version: 1.0.0
author: DesignBuddy Dev
user-invocable: true
disable-model-invocation: false
---

# DesignBuddy 环境探测（测试专用）

你正在执行一个**只读诊断**。目标是如实记录当前 WorkBuddy Skill 执行环境的真实能力，不是把任务"做成功"。

## 纪律（必须遵守）

- 不安装任何东西：禁止 `pip install`、`npm install`、`brew`、`winget` 等。
- 只在当前工作目录下的 `dbprobe-results/` 中写文件，不修改其他任何文件。
- 不读取、不输出用户的私人文件、账号或凭据。
- 某一步失败时，**原样记录错误信息并继续**下一步，不要尝试修复环境。
- 不要美化结果：做不到就写 FAIL 或 BLOCKED。

## 步骤

### A1. Skill 位置

说明本 Skill 目录（本 SKILL.md 所在目录）的绝对路径，以及你是怎么知道这个路径的（平台直接提供 / 从上下文推断 / 无法确定）。

### A2. 读取 references

读取 @references/env-reference.md ，原样复述其中的读取标记。

### A3. Shell 识别

依次执行下面两条命令，各自原样记录输出或报错：

1. `echo "shell-check:$0"`
2. `$PSVersionTable.PSVersion`

### A4. 解释器探测

依次执行下面四条命令，各自原样记录输出或报错：

1. `python3 -c "import sys;print(sys.version)"`
2. `python -c "import sys;print(sys.version)"`
3. `py -3 -c "import sys;print(sys.version)"`
4. `node -e "console.log(process.version)"`

### A5. 运行探测脚本

用 A4 中**第一个成功**的 Python 命令运行脚本（路径两侧加双引号）：

```
<python命令> "<Skill目录>/scripts/env_probe.py" --font "Source Han Sans" --font "Noto Sans SC"
```

- 如果没有任何 Python 可用、但 Node 可用，运行：`node "<Skill目录>/scripts/env_probe_node.js"`。
- 如果都不可用，把 A5 记为 BLOCKED，并说明原因。
- 把脚本输出中 `=== DBPROBE REPORT BEGIN ===` 到 `=== DBPROBE REPORT END ===` 之间的内容**原样**贴出。

### A6. 输出最终报告

严格使用下面的格式输出。Result 只能是 PASS / FAIL / PARTIAL / BLOCKED / NOT_TESTED。

```
## DBPROBE ENVIRONMENT REPORT v1.0.0
A1 Skill位置: <路径> | 获取方式: <...> | Result: <...>
A2 references读取: <复述的标记或错误> | Result: <...>
A3 Shell: <两条命令的原样输出> | 判断: <bash/zsh/PowerShell/cmd/未知>
A4 解释器: python3=<...> | python=<...> | py=<...> | node=<...>
A5 脚本运行: 使用命令=<...> | Result: <...>
<脚本报告原文>
结果文件: <dbprobe-results 中的文件路径>
异常与备注: <...>
```
