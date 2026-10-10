#!/usr/bin/env node
// DesignBuddy environment probe — Node fallback (used only when no Python works).
// Built-in modules only. No npm install. Writes only under <cwd>/dbprobe-results/.
"use strict";
const fs = require("fs");
const os = require("os");
const path = require("path");

const PROBE = "dbprobe-environment";
const PROBE_VERSION = "1.0.0";
const SKILL_DIR = path.resolve(__dirname, "..");
const checks = [];
const add = (id, capability, result, detail) => checks.push({ id, capability, result, detail });

add("ENV-NODE", "Node interpreter runs this script", "PASS", { version: process.version, execPath: process.execPath });
add("ENV-OS", "Operating system", "PASS", { platform: process.platform, release: os.release(), arch: process.arch });
const shell = {};
for (const k of ["SHELL", "COMSPEC", "PSModulePath", "MSYSTEM", "TERM_PROGRAM"]) {
  const v = process.env[k];
  shell[k] = v === undefined ? null : (k === "SHELL" || k === "COMSPEC" ? path.basename(v) : "present");
}
add("ENV-SHELL", "Shell hints visible to child process", "PASS", shell);
add("ENV-PATHS", "Working directory and skill location", "PASS", { cwd: process.cwd(), script_path: __filename, skill_dir: SKILL_DIR });

const markers = { "references/env-reference.md": "DBP-ENV-REF-5K2P", "templates/env-template.txt": "DBP-ENV-TPL-8V3N" };
const self = {};
let ok = 0;
for (const [rel, m] of Object.entries(markers)) {
  try {
    const t = fs.readFileSync(path.join(SKILL_DIR, rel), "utf8");
    self[rel] = t.includes(m) ? "marker found" : "readable, marker missing";
    if (t.includes(m)) ok++;
  } catch (e) { self[rel] = "unreadable: " + e.message; }
}
add("ENV-SELFREAD", "Script reads files inside its own skill package", ok === 2 ? "PASS" : ok ? "PARTIAL" : "FAIL", self);

const outDir = path.join(process.cwd(), "dbprobe-results");
try {
  const d = path.join(outDir, "中文 目录 test");
  fs.mkdirSync(d, { recursive: true });
  const f = path.join(d, "品牌 文件.txt");
  fs.writeFileSync(f, "DesignBuddy 写入测试 ✓", "utf8");
  const back = fs.readFileSync(f, "utf8");
  fs.unlinkSync(f); fs.rmdirSync(d);
  add("ENV-WRITE", "Write/read/delete UTF-8 file with Chinese path", back === "DesignBuddy 写入测试 ✓" ? "PASS" : "FAIL", { out_dir: outDir });
} catch (e) { add("ENV-WRITE", "Write/read/delete UTF-8 file with Chinese path", "FAIL", { error: e.message }); }

const runId = "env-node-" + new Date().toISOString().replace(/[-:T]/g, "").slice(0, 14);
const payload = { probe: PROBE, probe_version: PROBE_VERSION, run_id: runId, runner: "node", finished_at: new Date().toISOString(), checks };
try {
  fs.mkdirSync(outDir, { recursive: true });
  const jp = path.join(outDir, runId + ".json");
  fs.writeFileSync(jp, JSON.stringify(payload, null, 2), "utf8");
  payload.result_file = jp;
} catch (e) { payload.result_file = "NOT SAVED: " + e.message; }

console.log("=== DBPROBE REPORT BEGIN ===");
console.log(`probe: ${PROBE} ${PROBE_VERSION}`);
console.log(`run_id: ${runId}`);
console.log(`result_file: ${payload.result_file}`);
for (const c of checks) {
  console.log(`- [${c.result}] ${c.id} — ${c.capability}`);
  console.log("    " + JSON.stringify(c.detail));
}
console.log("=== DBPROBE REPORT END ===");
