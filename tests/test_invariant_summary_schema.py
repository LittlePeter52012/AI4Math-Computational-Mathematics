from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "skills"
    / "invariant-computation"
    / "schema"
    / "invariant_summary.schema.json"
)
EXAMPLE_PATH = (
    ROOT
    / "skills"
    / "invariant-computation"
    / "examples"
    / "invariant_summary.example.json"
)


class InvariantSummarySchemaTests(unittest.TestCase):
    def load_json(self, path: Path) -> object:
        self.assertTrue(path.is_file(), f"Missing JSON contract artifact: {path}")
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)

    def test_schema_is_valid_draft_2020_12(self) -> None:
        Draft202012Validator.check_schema(self.load_json(SCHEMA_PATH))

    def test_public_example_conforms_to_schema(self) -> None:
        schema = self.load_json(SCHEMA_PATH)
        example = self.load_json(EXAMPLE_PATH)

        Draft202012Validator(schema).validate(example)

    def test_remaining_uncertainty_cannot_be_omitted(self) -> None:
        schema = self.load_json(SCHEMA_PATH)
        example = copy.deepcopy(self.load_json(EXAMPLE_PATH))
        del example["remaining_uncertainty"]

        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(example)

    def test_theorem_backed_classification_may_omit_caveat(self) -> None:
        schema = self.load_json(SCHEMA_PATH)
        example = copy.deepcopy(self.load_json(EXAMPLE_PATH))
        del example["classification_caveat"]

        Draft202012Validator(schema).validate(example)

    def test_invalid_contract_variants_are_rejected(self) -> None:
        schema = self.load_json(SCHEMA_PATH)
        example = self.load_json(EXAMPLE_PATH)

        missing_version = copy.deepcopy(example)
        del missing_version["backend"]["version_evidence"]
        invalid_quality = copy.deepcopy(example)
        invalid_quality["invariant"]["result_quality"] = "proved"
        empty_checks = copy.deepcopy(example)
        empty_checks["validation_checks"] = []

        for label, invalid in (
            ("missing backend version evidence", missing_version),
            ("unsupported result quality", invalid_quality),
            ("empty validation checks", empty_checks),
        ):
            with self.subTest(label=label):
                with self.assertRaises(ValidationError):
                    Draft202012Validator(schema).validate(invalid)

    def test_extension_fields_remain_forward_compatible(self) -> None:
        schema = self.load_json(SCHEMA_PATH)
        example = copy.deepcopy(self.load_json(EXAMPLE_PATH))
        example["producer_extension"] = {"name": "downstream-agent"}

        Draft202012Validator(schema).validate(example)


if __name__ == "__main__":
    unittest.main()
