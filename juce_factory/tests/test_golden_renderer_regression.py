from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from juce_factory.factory.contract import load_contract
from juce_factory.factory.generator import generate_project


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "golden_gain.contract.json"
BASELINE = ROOT / "fixtures" / "golden_gain_source_baseline.json"


class GoldenRendererRegressionTests(unittest.TestCase):
    def test_generated_source_matches_pre_extraction_ci_baseline(self):
        contract = load_contract(EXAMPLE)
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(
            baseline["contract_sha256"],
            "709f4580ac860f3c38e8ab8e016a468e9f0512eae0c40840434d8c048e55ed28",
        )
        with tempfile.TemporaryDirectory() as td:
            out = generate_project(contract, Path(td) / "GoldenGain")
            manifest = json.loads(
                (out / "factory_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                manifest["generated_source_sha256"],
                baseline["generated_source_sha256"],
            )
            self.assertEqual(manifest["juce_version"], baseline["juce_version"])


if __name__ == "__main__":
    unittest.main()
