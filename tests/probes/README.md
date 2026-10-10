# Probe Skills（第一轮运行时验证）

在 DesignBuddy 本体开发之前，用 5 个最小测试 Skill，在真实的 WorkBuddy 环境中取得证据。

- **测试人员**：直接阅读 [`PROBE_TEST_GUIDE.md`](PROBE_TEST_GUIDE.md)，安装 `dist/` 中的 ZIP 即可。
- **开发者**：修改源码后，执行下面两条命令重新生成：

```bash
python3 tests/probes/tools/build_brand_probes.py   # 重新生成 brand-alpha / brand-beta
python3 tests/probes/tools/pack_probes.py          # lint 检查 + 打包 dist/*.zip + SHA256SUMS
```

| 目录 | 说明 |
|---|---|
| `environment-probe/` | 运行环境探测（Python / Node / Shell / 工作目录 / 读写 / 读取自身资源） |
| `protection-probe/` | 付费或加密形态下各项能力的可用性 |
| `installation-probe/` | 确定性生成 → 原生安装交接 → 用 build-manifest 比对 |
| `brand-alpha/`、`brand-beta/` | 虚构品牌 Skill（由 `tools/build_brand_probes.py` 生成，不要手改） |
| `tools/` | 生成器、打包器、对比度校验器（只用标准库） |
| `dist/` | 可直接安装的 ZIP |
