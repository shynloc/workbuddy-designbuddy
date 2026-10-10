# DesignBuddy

DesignBuddy 是一个运行在 WorkBuddy 中的专业 **AI Brand System Builder & Compiler**。

它把品牌资料、现有资产、设计偏好和用户确认的决策编译成一个结构化的 **Brand IR**，再从 Brand IR 生成以下产出：

- 可在 WorkBuddy 中执行的 **Brand Skill**；
- 一套 **Portable Design System**（DESIGN.md、Design Tokens、Brand IR）；
- 用于验收的 **Preview 样例**；
- 记录来源、推断和许可的 **Source Report**。

生成的 Brand Skill 通过 WorkBuddy 原生能力安装，安装前需要用户确认。

> 当前阶段：**QA 候选版 v0.1.1**（第 2 轮）。v0.1.0 已在 Windows / WorkBuddy 5.7.7.0 完成首轮真机测试，问题已修复，见 [`qa/FIX_REPORT.md`](qa/FIX_REPORT.md)。发布门槛见 [`qa/RELEASE_GATE.md`](qa/RELEASE_GATE.md)。

## 快速开始（测试人员）

1. 下载 `dist/v0.1.1/designbuddy-qa-v0.1.1.zip`，在 WorkBuddy 中安装（先删除旧版本）；
2. 新开会话，粘贴 [`qa/WORKBUDDY_QA_PROMPT.md`](qa/WORKBUDDY_QA_PROMPT.md)；
3. 取回 `TEST_REPORT.md` 和 `results.json`。

详见 [`qa/QA_TEST_GUIDE.md`](qa/QA_TEST_GUIDE.md)。

## 开发者

```bash
python3 -m unittest discover -s tests/unit          # 单元测试
python3 designbuddy-qa/scripts/designbuddy.py run-all --out /tmp/qa   # 源码直接跑 QA
python3 tools/build_release.py                       # 构建 dist/（可复现）+ 本地证据
```

| 目录 | 内容 |
|---|---|
| `designbuddy-qa/` | Skill 本体（打包进 ZIP 的全部内容） |
| `tools/` | 构建与发布工具 |
| `tests/unit/` | 单元测试 |
| `qa/` | 测试指南、提示词、测试矩阵、实现状态、偏离说明、开放问题、变更记录、本地测试证据 |
| `dist/` | 各版本的安装包（`dist/v<版本>/`；v0.1.0 位于 dist 根目录）、夹具品牌包、校验和、发布说明 |
| `tests/probes/` | 第一轮平台探针（已被 QA 候选版取代，保留作参考） |

## 文档

| 文档 | 内容 |
|---|---|
| [docs/DESIGNBUDDY_ARCHITECTURE_REVISION.md](docs/DESIGNBUDDY_ARCHITECTURE_REVISION.md) | 架构决策记录（R2），共 30 个主题 |
| [docs/PRD.md](docs/PRD.md) | 产品需求 |
| [docs/architecture.md](docs/architecture.md) | 技术架构与实现规格 |
| [docs/runtime-capabilities.md](docs/runtime-capabilities.md) | 平台能力台账（OFFICIAL / OBSERVED / UNVERIFIED） |
| [docs/open-questions.md](docs/open-questions.md) | 开放问题与待确认的产品决策 |
| [docs/validation-plan.md](docs/validation-plan.md) | 开发前验证用例 |
| [docs/PAID_SKILL_PROTECTION_VALIDATION.md](docs/PAID_SKILL_PROTECTION_VALIDATION.md) | 付费 Skill 保护验证 |
| [docs/runtime-validation-results.md](docs/runtime-validation-results.md) | 真机测试结果 |
| [tests/probes/PROBE_TEST_GUIDE.md](tests/probes/PROBE_TEST_GUIDE.md) | 第一轮 Probe 测试指南（含 ZIP） |

本项目沿用 [WB-OPDK](https://github.com/shynloc/workbuddy-open-platform-devkit) 的知识分级纪律。
