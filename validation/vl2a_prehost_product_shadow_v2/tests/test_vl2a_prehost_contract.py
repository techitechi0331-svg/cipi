from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "automation" / "vl2a_prehost" / "apply_candidate.py"
spec = importlib.util.spec_from_file_location("apply_candidate", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PERSIST_PATH = Path(__file__).resolve().parents[1] / "automation" / "vl2a_prehost" / "persist_staging.py"
persist_spec = importlib.util.spec_from_file_location("persist_staging", PERSIST_PATH)
persist = importlib.util.module_from_spec(persist_spec)
assert persist_spec.loader is not None
persist_spec.loader.exec_module(persist)

GOOD = {
    "candidate_id": "HA100X-R4-012-591362e2",
    "primary_dcr_ohm": 64.42056271688182,
    "secondary_dcr_ohm": 3031.5360890531933,
    "magnetizing_h": 23.787562773717497,
    "leakage_h": 0.00016910013055046575,
    "secondary_cap_f": 1.8971658271371616e-11,
    "core_loss_ohm": 266576.9148779566,
    "turns_ratio": 10.0,
}

class PreHostContractTests(unittest.TestCase):
    def test_candidate_validation(self):
        parsed = mod.require_candidate(json.dumps(GOOD))
        self.assertEqual(parsed["candidate_id"], GOOD["candidate_id"])
        bad = dict(GOOD)
        bad["magnetizing_h"] = -1
        with self.assertRaises(ValueError):
            mod.require_candidate(json.dumps(bad))

    def test_patch_is_input_transformer_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "vl2a_lineamp_v01" / "Source"
            source.mkdir(parents=True)
            (source / "LA2AEngine.h").write_text(
                '#pragma once\n#include "LineAmplifierDSP.h"\n'
                'namespace vl2a {\nclass X {\n    TransformerModel inputTransformer[2];\n};\n}\n',
                encoding="utf-8",
            )
            (source / "LA2AEngine.cpp").write_text(
                "    for (auto& t : inputTransformer)       t.prepare(sr, 12.0f, 0.12f);\n"
                "        transformed[ch] = inputTransformer[ch].process(in[ch]);\n"
                "    for (auto& t : legacyOutputTransformer)t.prepare(sr, 9.0f, 0.16f);\n",
                encoding="utf-8",
            )
            mod.patch_engine(root, GOOD)
            h = (source / "LA2AEngine.h").read_text(encoding="utf-8")
            c = (source / "LA2AEngine.cpp").read_text(encoding="utf-8")
            model = (source / "HA100XPreHostModel.h").read_text(encoding="utf-8")
            self.assertIn("HA100XPreHostModel inputTransformer[2]", h)
            self.assertIn("t4.resistanceOhms()", c)
            self.assertIn("legacyOutputTransformer", c)
            self.assertIn(GOOD["candidate_id"], model)
            self.assertIn("kSourceOhm = 150.0", model)
            self.assertIn("kDarkLoadOhm = 48590.0", model)
            self.assertIn("kBrightLoadOhm = 34900.0", model)

    def test_probe_is_research_only(self):
        text = mod.probe_cpp()
        self.assertIn("PREHOST_CANDIDATE", text)
        self.assertIn("vl2a_prehost_baseline", mod.probe_cmake())
        self.assertIn("vl2a_prehost_candidate", mod.probe_cmake())

    def test_staging_branch_is_bounded(self):
        branch = persist.safe_branch(GOOD["candidate_id"], "123456")
        self.assertEqual(branch, "research/prehost/ha100x-r4-012-591362e2-123456")
        with self.assertRaises(ValueError):
            persist.safe_branch("../unsafe", "123")

if __name__ == "__main__":
    unittest.main()
