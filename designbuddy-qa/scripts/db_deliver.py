"""Deliver finished outputs to a place the user can find easily (default: the Downloads folder).

Never overwrites: an existing file with identical content is skipped; a different
file of the same name gets a numbered suffix. Writes only under
<base>/DesignBuddy/<slug>/.
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

from db_util import DBError, sha256_bytes, write_text

WIN_DOWNLOADS_GUID = "{374DE290-123F-4565-9164-39C4925E467B}"


def downloads_dir():
    """Return (path, how_found). DESIGNBUDDY_DOWNLOADS overrides everything."""
    override = os.environ.get("DESIGNBUDDY_DOWNLOADS")
    if override:
        return Path(override), "env:DESIGNBUDDY_DOWNLOADS"
    home = Path.home()
    if sys.platform.startswith("win"):
        try:
            import winreg  # stdlib, Windows only
            key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
                val, _ = winreg.QueryValueEx(k, WIN_DOWNLOADS_GUID)
            return Path(os.path.expandvars(val)), "windows-registry"
        except Exception:  # noqa: BLE001 - fall back to the conventional folder
            return home / "Downloads", "default"
    if sys.platform.startswith("linux"):
        cfg = home / ".config" / "user-dirs.dirs"
        try:
            m = re.search(r'^XDG_DOWNLOAD_DIR="([^"]+)"', cfg.read_text(encoding="utf-8"), re.M)
            if m:
                return Path(m.group(1).replace("$HOME", str(home))), "xdg-user-dirs"
        except OSError:
            pass
    return home / "Downloads", "default"


def _place(src_bytes, dst):
    """Copy bytes to dst without overwriting. Returns (final_path, action)."""
    if dst.exists():
        if dst.is_file() and sha256_bytes(dst.read_bytes()) == sha256_bytes(src_bytes):
            return dst, "unchanged"
        stem, suf = dst.stem, dst.suffix
        n = 2
        while True:
            cand = dst.with_name("%s-%d%s" % (stem, n, suf))
            if not cand.exists():
                dst = cand
                break
            if cand.is_file() and sha256_bytes(cand.read_bytes()) == sha256_bytes(src_bytes):
                return cand, "unchanged"
            n += 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src_bytes)
    return dst, "written"


GUIDE = """{brand} · DesignBuddy 交付包
================================

本文件夹由 DesignBuddy 生成，所有内容只保存在你的电脑上。

1. 安装品牌 Skill（让 WorkBuddy 以后自动按品牌规范做设计）
   - 打开 WorkBuddy 客户端的技能管理，找到"导入 / 上传本地技能"入口（名称以客户端为准）
   - 选择本文件夹中的：{skill_zip}
   - 安装完成后，新开一个会话说："给 {brand} 做一份……"即可

2. 其他文件
   - {portable_zip}：可移植设计系统（DESIGN.md、Design Tokens、CSS），可用于 Claude Code、Cursor、网页项目等
   - preview/：离线样例，双击即可在浏览器中打开
   - source-report.md：品牌规则的来源、AI 推断项与许可说明

版本：Skill {skill_version} · Design System {system_version} · build {build_id}
"""


def deliver(ws, to=None):
    ws = Path(ws)
    report_path = ws / "reviews" / "build-report.json"
    if not report_path.is_file():
        raise DBError("E_NOT_BUILT", "还没有构建产物，请先运行 build")
    rep = json.loads(report_path.read_text(encoding="utf-8"))
    if to:
        base, how = Path(to), "user-specified"
    else:
        base, how = downloads_dir()
    if not base.is_dir():
        raise DBError("E_DELIVER_TARGET", "找不到交付目录：%s。请用 --to 指定一个你能找到的文件夹" % base, {"how": how})
    slug = rep["skill"][: -len("-brand-system")] if rep["skill"].endswith("-brand-system") else rep["skill"]
    target = base / "DesignBuddy" / slug
    items = [(Path(rep["skill_zip"]), Path(rep["skill_zip"]).name), (Path(rep["portable_zip"]), Path(rep["portable_zip"]).name)]
    for f in sorted(Path(rep["preview_dir"]).glob("*.html")):
        items.append((f, "preview/" + f.name))
    src_report = ws / "exports" / "source-report" / "source-report.md"
    if src_report.is_file():
        items.append((src_report, "source-report.md"))
    delivered = []
    try:
        for src, rel in items:
            final, action = _place(src.read_bytes(), target / rel)
            delivered.append({"file": str(final), "action": action})
        skill_final = next(d["file"] for d in delivered if d["file"].endswith(".zip") and "portable" not in Path(d["file"]).name)
        portable_final = next(d["file"] for d in delivered if "portable" in Path(d["file"]).name)
        guide = GUIDE.format(brand=slug, skill_zip=Path(skill_final).name, portable_zip=Path(portable_final).name,
                             skill_version=rep["skill_version"], system_version=rep["system_version"], build_id=rep["build_id"])
        tmp = target / ".guide.tmp"
        write_text(tmp, guide)
        final, action = _place(tmp.read_bytes(), target / "安装说明.txt")
        tmp.unlink()
        delivered.append({"file": str(final), "action": action})
    except OSError as e:
        raise DBError("E_DELIVER_WRITE", "无法写入 %s：%s。请用 --to 指定其他文件夹" % (target, type(e).__name__))
    return {"ok": True, "folder": str(target), "found_by": how, "skill_zip": skill_final, "files": delivered,
            "next_zh": "打开 WorkBuddy 技能管理 → 导入本地技能 → 选择 %s" % skill_final}


def deliver_run(run_dir, to=None):
    """QA helper: copy the Brand Skill ZIPs of a QA run to <base>/DesignBuddy/QA-<run_id>/."""
    run_dir = Path(run_dir)
    zips = sorted((run_dir / "artifacts").glob("*-brand-system-*.zip"))
    if not zips:
        raise DBError("E_NOT_BUILT", "报告目录中没有 Brand Skill ZIP：%s" % run_dir)
    base, how = (Path(to), "user-specified") if to else downloads_dir()
    if not base.is_dir():
        raise DBError("E_DELIVER_TARGET", "找不到交付目录：%s。请用 --to 指定一个你能找到的文件夹" % base, {"how": how})
    target = base / "DesignBuddy" / ("QA-" + run_dir.name)
    files = []
    try:
        for z in zips:
            final, action = _place(z.read_bytes(), target / z.name)
            files.append({"file": str(final), "action": action})
    except OSError as e:
        raise DBError("E_DELIVER_WRITE", "无法写入 %s：%s。请用 --to 指定其他文件夹" % (target, type(e).__name__))
    return {"ok": True, "folder": str(target), "found_by": how, "files": files,
            "next_zh": "打开 WorkBuddy 技能管理 → 导入本地技能 → 依次选择 %s 中的 ZIP" % target}
