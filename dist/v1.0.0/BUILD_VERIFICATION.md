# BUILD_VERIFICATION — designbuddy v1.0.0

由 `tools/build_commercial.py` 自动生成，是开发机上的本地验证证据，**不代表平台解析、审核或付费加密环境中的结果**。

- ZIP：`designbuddy-v1.0.0.zip`
- ZIP SHA-256：`e3bea5a57617095ad95f109b3a905bb1ae1a33a6ee0c77652fb50f78464c557f`
- package-manifest SHA-256：`23b27cdb4eec617ca0ca33b386f2e34cea90f651c01b12a562c76af62394cdd9`
- 根目录：`designbuddy/`；28 个文件；150667 bytes；lint 0 错误
- 已剔除 QA 专用内容：templates/fixtures, scripts/dbcore/qarunner.py, references/qa-protocol.md；对 9 个禁用词的扫描结果：无命中

| 检查 | 结果 |
|---|---|
| version | PASS |
| selftest | PASS |
| env_fingerprint | PASS |
| qa_commands_unavailable | PASS |
| e2e_existing | PASS |
| e2e_new | PASS |

## 端到端（从解压后的商业包运行 CLI，交付到临时的下载文件夹）

- **existing**：步骤 init(0) → G1 KEEP(0) → G2 KEEP(0) → G3 CHANGE resolve.conflict-colors-primary=#1F4FD8(0) → G3 KEEP(0) → G4 KEEP(0) → preview(0) → G5 KEEP(0) → G6 KEEP(0) → build --deliver(0)；Brand QA {'passed': True, 'fail': 0, 'warning': 0, 'total': 18}；交付文件 6 个；交付的 Brand Skill 通过 lint=True，selfcheck=MATCH；build_id `cf0854646745`
- **new**：步骤 init(0) → G1 KEEP(0) → G2 KEEP direction=bold-technical(0) → G3 KEEP(0) → G4 KEEP(0) → preview(0) → G5 KEEP(0) → G6 KEEP(0) → build --deliver(0)；Brand QA {'passed': True, 'fail': 0, 'warning': 0, 'total': 18}；交付文件 6 个；交付的 Brand Skill 通过 lint=True，selfcheck=MATCH；build_id `540fbb1eaced`
