# QA 协议（QA RUN ALL）

目标：在用户的真实 WorkBuddy 中，跑完全部本地验收测试，并输出可以保存的报告。

**原则**：

- 能用脚本判断的，一律由脚本判断。
- 需要平台或人工的，由 Agent 按本协议执行，并用 `record` 回填证据。
- 不在当前会话里"模拟"新会话的结果。

## 1. 选择输出目录（最多问一次）

- 如果当前有用户可见、可写的项目文件夹，就直接使用 `<项目文件夹>/DesignBuddy-QA-Reports/`。
- 如果不确定，**只问一次**：

  > 测试报告要保存到哪个文件夹？（建议选一个你能在访达或资源管理器里打开的文件夹）

- 不要把报告写到隐藏目录，也不要写到 Skill 安装目录。

## 2. 运行脚本测试

```
<PY> "<SKILL>/scripts/designbuddy.py" run-all --out "<输出目录>"
```

- 返回的 JSON 中有 `report_dir`，下文记作 `<RUN>`。
- 报告目录的结构：

```
<RUN>/TEST_REPORT.md        主报告
<RUN>/results.json          逐项结果
<RUN>/environment.json
<RUN>/artifacts-manifest.json
<RUN>/issues.md
<RUN>/next-session-prompts.md
<RUN>/artifacts/            Alpha/Beta/Gamma 的 Brand Skill ZIP、Portable ZIP、Preview
```

## 3. Agent 用例：回填格式

用下面的命令回填 Agent 和人工用例：

```
<PY> "<SKILL>/scripts/designbuddy.py" record --run "<RUN>" --id <ID> --result <PASS|FAIL|PARTIAL|BLOCKED|NOT_TESTED> --actual "<实际情况>" --evidence "<证据：命令输出摘要/截图名>" --context "<系统 / WorkBuddy 版本 / 安装形态>" [--reason "<阻塞原因>"] [--commands "<实际执行的工具调用或命令>" ...]
```

- Agent 自己产生的临时文件（例如安全审计时解压的包），一律放到 `<RUN>/agent-notes/`。
- 不要写进 `artifacts/`，也不要写进 `.qa-work/`。

`record` 的约束：

- 脚本用例（SCRIPT）不能回填，会被拒绝。
- PASS 必须同时提供 `--actual` 和 `--evidence`。
- INS-001 ~ INS-005 的 PASS，还必须用 `--commands` 写清楚**由谁执行、调用了什么**。例如：`Skill Creator 工具调用：<工具名>(<参数>)`，或 `用户在客户端 UI 中导入 <文件>`。
- BLOCKED 必须提供原因。

### ENV-007 WorkBuddy 版本

- 如果能从环境或用户提示词中得知版本，就记为 PASS，并写明来源。
- 否则记为 NOT_TESTED，reason 写"Agent 无法读取客户端版本"。

### ENV-008 安装形态

按用户提示词中的说明（例如"本地 ZIP 安装、未付费、未加密、开发者账号"）记录。如果用户没有说明，记为 NOT_TESTED。

### ENV-009 shell 与命令执行方式

记录实际执行命令的方式，例如"bash / zsh / PowerShell / 未知"，以及 `<PY>` 的实际值。

## 4. 安装链路（INS-001 ~ INS-006）

1. 在 `<RUN>/artifacts/` 中找到以下两个文件：
   - `alpha-demo-brand-system-1.0.0.zip`
   - `beta-demo-brand-system-1.0.0.zip`
2. 按 @references/installation-handoff.md 的格式展示摘要，询问：

   > 是否允许安装这两个测试品牌 Skill？

   **等用户明确回复后再继续。** 用户拒绝时：INS-001 ~ 005 记为 BLOCKED，reason 写"用户未授权安装"；INS-006 记为 PASS（确认流程已执行）。
3. 依次尝试 H1 → H2 → H3 → H4，每种方式的实际结果分别回填 INS-001 ~ INS-004。

   **关于 H5 的界定**：如果安装动作是你（Agent）自己用 Bash 或文件工具把 ZIP 解压、复制到 WorkBuddy 的 Skill 目录（例如 `~/.workbuddy/skills/`），那就是被禁止的 H5，不算 H2。

   - H2 必须是 WorkBuddy 内置的 Skill Creator 或平台机制**自己**完成安装。
   - 如果你不能确定是谁写入的，就记为 PARTIAL，并在 `--actual` 中说明。

   已知平台事实（OBSERVED，WorkBuddy 5.7.7.0 / Windows 11）：`search_and_install_skills` 只能安装技能市场中的 Skill，不接受本地 ZIP 或目录。如果你的环境里也是这样，INS-001 记为 BLOCKED 并引用这一点。

   各种结果的记法：
   - 方式不存在或没有权限 → BLOCKED，写明原因；
   - 尝试后失败 → FAIL，写明错误原文；
   - 成功 → PASS，必须附 `--commands`。
   - 已有一种方式成功后，H3、H4 可以不执行，记为 NOT_TESTED，reason 写"已有 <Hn> PASS，按协议作为备选未执行"。
4. INS-005：安装成功后，在已安装的 Brand Skill 目录中运行 `scripts/selfcheck.py`。
   - `overall: MATCH` → PASS；
   - 否则 → FAIL，附上 MISMATCH 列表。
5. INS-006：记录你在安装前是否展示了摘要并取得确认，附上用户回复的原文。

## 5. 多品牌（MB-003 ~ MB-005）

- 这三项**必须在独立的新会话中执行**。在当前会话里不能执行，也不能模拟。
- 把 `<RUN>/next-session-prompts.md` 的位置告诉用户，三项保持 NOT_TESTED（PENDING_MANUAL）。
- 用户在新会话中测完后，可以回到这里，用 `record` 回填结果。

## 6. 没有可用 Python 时（BLOCKED 报告）

1. 不要安装 Python，也不要让用户配置环境。
2. 在输出目录中新建 `DesignBuddy-QA-Reports/blocked-<日期>/TEST_REPORT.md`，内容如下：

```
# DesignBuddy QA 测试报告（BLOCKED）
- 原因：当前 WorkBuddy Skill 执行环境中没有可用的 Python（尝试了 python3 / python / py -3）
- 各命令的原始输出：<粘贴>
- 系统 / shell：<...>
- 结果：所有 SCRIPT 用例 = BLOCKED；ENV-001 = FAIL（P0）
- 建议：下一轮评估"无 Python"环境的降级方案（例如 Node 版最小 Runner 或 WorkBuddy 内置运行时）
```

3. 告诉用户报告的位置。

## 7. 结束时给用户的汇报

汇报内容只包括以下几项：

- `TEST_REPORT.md` 和 `results.json` 的路径；
- 汇总表：通过率、P0~P3 数量、未验证项；
- 各状态的结论；
- 需要用户在新会话中完成的事项。

不要额外添加主观评价。
