"""Regression checks for non-vacuous research field coverage and CLI failures."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/validate_json.py"
VALIDATOR = runpy.run_path(str(SCRIPT))


class ResearchValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fields = self.root / "fields.yaml"
        self.result = self.root / "result.json"
        self.result.write_text(json.dumps({"name": "Example"}), encoding="utf-8")

    def schema(self, fields: list[dict]) -> dict:
        self.fields.write_text(yaml.safe_dump({"field_categories": [
            {"category": "Custom Category", "fields": fields}
        ]}), encoding="utf-8")
        return VALIDATOR["load_fields_yaml"](self.fields)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), "-f", str(self.fields), *args],
                              cwd=self.root, capture_output=True, text=True, check=False)

    def test_unmarked_fields_are_required_and_missing_values_fail(self) -> None:
        schema = self.schema([{"name": "name"}, {"name": "source"}])
        result = VALIDATOR["validate_json"](self.result, schema)
        self.assertFalse(result["valid"])
        self.assertEqual(result["missing_required"], ["source"])

    def test_explicit_optional_fields_and_custom_category_nesting(self) -> None:
        schema = self.schema([{"name": "name", "required": True},
                              {"name": "source", "required": False}])
        self.result.write_text('{"Custom Category": {"name": "Example"}}', encoding="utf-8")
        result = VALIDATOR["validate_json"](self.result, schema)
        self.assertTrue(result["valid"])
        self.assertEqual(result["missing_optional"], ["source"])

    def test_unsupported_empty_and_malformed_schemas_fail(self) -> None:
        for data in ({}, {"fields": {"Basic": [{"name": "name"}]}},
                     {"field_categories": []}, {"field_categories": ["invalid"]},
                     {"field_categories": [{"category": "Basic", "fields": []}]}):
            with self.subTest(data=data):
                self.fields.write_text(yaml.safe_dump(data), encoding="utf-8")
                result = self.run_cli("-j", str(self.result))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("[ERROR]", result.stdout)

    def test_duplicate_reserved_and_non_boolean_fields_fail(self) -> None:
        for fields in ([{"name": "name"}, {"name": "name"}], [{"name": "uncertain"}],
                       [{"name": "name", "required": "false"}]):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                self.schema(fields)

    def test_missing_invalid_or_non_object_results_do_not_pass(self) -> None:
        self.schema([{"name": "name"}])
        for content in ("not JSON", "[]", '"name"'):
            with self.subTest(content=content):
                self.result.write_text(content, encoding="utf-8")
                self.assertNotEqual(self.run_cli("-j", str(self.result)).returncode, 0)
        self.assertNotEqual(self.run_cli("-j", str(self.root / "missing.json")).returncode, 0)
        self.assertNotEqual(self.run_cli("--dir", str(self.root / "absent")).returncode, 0)


if __name__ == "__main__":
    unittest.main()
