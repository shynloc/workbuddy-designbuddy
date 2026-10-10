"""Unit tests for DesignBuddy QA core (stdlib unittest).

Run: python3 -m unittest discover -s tests/unit -v
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "designbuddy-qa" / "scripts"))
sys.dont_write_bytecode = True

from dbcore import color as C, engine, ir as IR, qarunner, util, workspace as W  # noqa: E402
from dbcore.util import DBError  # noqa: E402

FIX = ROOT / "designbuddy-qa" / "templates" / "fixtures"


class ColorTests(unittest.TestCase):
    def test_contrast_reference_values(self):
        self.assertAlmostEqual(C.contrast("#000000", "#FFFFFF"), 21.0, places=2)
        self.assertAlmostEqual(C.contrast("#777777", "#FFFFFF"), 4.48, places=2)
        self.assertEqual(C.grade(4.48, "text"), "WARNING")
        self.assertEqual(C.grade(4.48, "large"), "PASS")
        self.assertEqual(C.grade(2.9, "ui"), "FAIL")

    def test_darken_until_reaches_target(self):
        out = C.darken_until("#F59E0B", "#FFFFFF", 4.5)
        self.assertGreaterEqual(C.contrast(out, "#FFFFFF"), 4.5)

    def test_norm_hex_rejects_bad_values(self):
        for bad in ("red", "#FFF", "#GGGGGG", None, "#1234567"):
            with self.assertRaises(DBError):
                C.norm_hex(bad)


class SafetyTests(unittest.TestCase):
    def test_relpath(self):
        for bad in ("../x", "/etc/passwd", "C:\\x", "a/../b", "a\\b", ""):
            with self.assertRaises(DBError):
                util.safe_relpath(bad)
        self.assertEqual(util.safe_relpath("assets/logo.svg"), "assets/logo.svg")

    def test_font_name_and_radius(self):
        with self.assertRaises(DBError):
            util.safe_font_name("x';}</style>")
        self.assertEqual(util.safe_font_name("Source Han Sans SC"), "Source Han Sans SC")
        self.assertEqual(util.safe_font_name("思源黑体"), "思源黑体")
        with self.assertRaises(DBError):
            util.safe_radius("8px;}")
        self.assertEqual(util.safe_weight("700"), 700)

    def test_yaml_and_html_are_inert(self):
        self.assertNotIn("<", util.yaml_str("<script>"))
        self.assertEqual(util.esc_html("<b>&"), "&lt;b&gt;&amp;")


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_existing_conflict_detected(self):
        ir = engine.intake(json.loads((FIX / "brand-alpha.json").read_text(encoding="utf-8")))
        self.assertEqual([c["field"] for c in ir["conflicts"]], ["colors.primary"])
        self.assertEqual(ir["conflicts"][0]["suggested"], "#1F4FD8")

    def test_new_path_has_three_candidates_and_no_system(self):
        ir = engine.intake(json.loads((FIX / "brand-gamma-new.json").read_text(encoding="utf-8")))
        self.assertIsNone(ir["design_system"])
        self.assertEqual(len(ir["candidates"]), 3)
        self.assertEqual(ir["candidates"][0]["id"], "bold-technical")

    def test_full_fixture_build_is_reproducible(self):
        a = qarunner.run_fixture("brand-beta", self.tmp / "a")
        b = qarunner.run_fixture("brand-beta", self.tmp / "b")
        self.assertTrue(a["ok"])
        self.assertEqual(a["build"]["build_id"], b["build"]["build_id"])
        self.assertEqual(qarunner._normalized_tree(a["build"]), qarunner._normalized_tree(b["build"]))

    def test_gate_order_enforced(self):
        W.init(FIX / "brand-beta.json", self.tmp / "ws")
        with self.assertRaises(DBError) as cm:
            W.gate(self.tmp / "ws", "G2", "KEEP")
        self.assertEqual(cm.exception.code, "E_GATE_ORDER")

    def test_duplicate_rule_ids_invalid(self):
        brief = json.loads((FIX / "malformed-inputs" / "duplicate-rule-ids.json").read_text(encoding="utf-8"))
        ir = engine.intake(brief)
        codes = [e["code"] for e in IR.validate(ir)["errors"]]
        self.assertIn("E_DUPLICATE_RULE", codes)


class RecordTests(unittest.TestCase):
    def test_record_refuses_script_cases_and_unbacked_pass(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            res = qarunner.run_all(str(tmp / "run"))
            run = res["report_dir"]
            with self.assertRaises(DBError):
                qarunner.record(run, "QA-001", "FAIL", "tamper")
            with self.assertRaises(DBError):
                qarunner.record(run, "INS-001", "PASS", "")
            with self.assertRaises(DBError):
                qarunner.record(run, "PP-002", "BLOCKED", "x")
            out = qarunner.record(run, "ENV-009", "PASS", "bash", context="unit test")
            self.assertTrue(out["ok"])
            data = json.loads((Path(run) / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(next(c for c in data["cases"] if c["id"] == "ENV-009")["result"], "PASS")
            self.assertEqual(res["summary"]["counts"]["FAIL"], 0)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
