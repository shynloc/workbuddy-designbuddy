# 上架后实测（付费加密环境）

目的：在付费加密的真实环境中，确认 DesignBuddy 能正常工作。

建议在审核通过、装机人数还少的时候实测 1~2 次，有问题立即下架整改。

## 前提

- 用**普通购买者账号**（不是开发者本人账号）从市场购买并安装。
- 如果条件允许，开发者账号也测一次，对比两者的结果。

## 测试步骤：新开一个会话，粘贴下面这段

```
请帮我测试 DesignBuddy 在当前安装环境中是否可用，按顺序执行并如实报告每一步的结果（不要跳过，不要模拟）：
1. 运行 DesignBuddy 自检（selftest），贴出返回的 JSON。
2. 运行 env，贴出 package 字段。
3. 读取 DesignBuddy 的 references/design-workflow.md，复述其中"## 1. 判断路径"一节的标题。
4. 用下面的信息走一遍完整流程，每个 Gate 都选 KEEP，最后执行 build --deliver：
   品牌名：Test Cafe；英文名：Test Cafe；slug：test-cafe；行业：咖啡店；受众：附近上班族；
   定位：安静可靠的社区咖啡；性格：温暖、简洁、可靠；路径：new。
5. 告诉我下载文件夹中 DesignBuddy/test-cafe/ 里有哪些文件。
```

## 判定

| 步骤 | 通过 | 不通过时说明什么 |
|---|---|---|
| 1 selftest | `"ok": true` | 脚本无法执行，或者文件被平台改动 |
| 2 env | 有 `manifest_sha256`（与 `PACKAGE_FINGERPRINT.txt` 中的值一致） | 安装的不是这个包 |
| 3 读取 references | 能复述出标题 | Agent 读不到加密后的规范文件 |
| 4 完整流程 | build 返回 `ok: true`，`delivery.ok` 为 true | 生成器或模板在加密后不可用 |
| 5 交付 | 有 6 个文件（Skill ZIP、Portable ZIP、2 个预览、来源报告、安装说明） | 写不到下载文件夹 |

任何一步不通过：

1. 立即下架；
2. 把整段对话截图，或复制回复内容发给我。

我会按以下顺序定位：

1. 脚本能执行、但读不到资源 → 把模板内嵌进生成器（仍然是本地的确定性构建）；
2. 脚本不能执行 → 另外评估方案。服务端编译需要你批准。

全部通过后，把结果告诉我，我会把状态更新为 PAID_ENCRYPTED_RUNTIME_VERIFIED。
