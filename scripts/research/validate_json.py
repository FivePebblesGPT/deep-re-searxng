#!/usr/bin/env python3
"""Validate Deep Research JSON files against a fields.yaml schema."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, TypedDict

import yaml


SKIP_KEYS = {"_source_file", "uncertain"}

CATEGORY_MAPPING: dict[str, list[str]] = {
    "basic_info": ["basic_info", "Basic Info"],
    "technical_features": ["technical_features", "technical_characteristics", "Technical Features"],
    "performance_metrics": ["performance_metrics", "performance", "Performance Metrics"],
    "milestone_significance": ["milestone_significance", "milestones", "Milestone Significance"],
    "business_info": ["business_info", "commercial_info", "Business Info"],
    "competition_ecosystem": ["competition_ecosystem", "competition", "Competition Ecosystem"],
    "history": ["history", "History"],
    "market_positioning": ["market_positioning", "market", "Market Positioning"],
}


class FieldSchema(TypedDict):
    all_fields: set[str]
    required_fields: set[str]
    field_categories: dict[str, str]
    category_mapping: dict[str, list[str]]


class ValidationResult(TypedDict):
    file: str
    total_defined: int
    covered: int
    missing: int
    extra: int
    coverage_rate: float
    missing_required: list[str]
    missing_optional: list[str]
    missing_by_category: dict[str, list[str]]
    extra_fields: list[str]
    valid: bool


def load_fields_yaml(fields_path: Path) -> FieldSchema:
    """Load fields.yaml and return normalized field sets."""
    with fields_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("field_categories"), list):
        raise ValueError("expected a field_categories list in fields.yaml")
    if not data["field_categories"]:
        raise ValueError("fields.yaml must define at least one field category")

    all_fields: set[str] = set()
    required_fields: set[str] = set()
    field_categories: dict[str, str] = {}
    category_mapping = {key: list(value) for key, value in CATEGORY_MAPPING.items()}
    has_required_markers = False

    for category in data["field_categories"]:
        if not isinstance(category, dict):
            raise ValueError("each field category must be an object")
        category_name = category.get("category")
        fields = category.get("fields")
        if not isinstance(category_name, str) or not category_name.strip():
            raise ValueError("each field category needs a nonempty category name")
        if not isinstance(fields, list) or not fields:
            raise ValueError(f"category {category_name!r} needs a nonempty fields list")
        category_slug = slugify_category(category_name)
        category_mapping.setdefault(category_slug, [])
        for alias in (category_slug, category_name):
            if alias not in category_mapping[category_slug]:
                category_mapping[category_slug].append(alias)
        for field in fields:
            if not isinstance(field, dict):
                raise ValueError("each field must be an object with a name")
            name = field.get("name")
            if not isinstance(name, str) or not name.strip() or name in SKIP_KEYS:
                raise ValueError(f"invalid or reserved field name: {name!r}")
            if name in all_fields:
                raise ValueError(f"duplicate field name: {name}")
            all_fields.add(name)
            field_categories[name] = category_name
            if "required" in field:
                has_required_markers = True
                if not isinstance(field["required"], bool):
                    raise ValueError(f"required must be a Boolean for field {name!r}")
            if field.get("required", False):
                required_fields.add(name)

    if not has_required_markers:
        required_fields = set(all_fields)

    return {
        "all_fields": all_fields,
        "required_fields": required_fields,
        "field_categories": field_categories,
        "category_mapping": category_mapping,
    }


def slugify_category(category_name: str) -> str:
    """Convert a category label into a common JSON object key."""
    slug_chars: list[str] = []
    previous_was_separator = False
    for char in category_name.strip().lower():
        if char.isalnum():
            slug_chars.append(char)
            previous_was_separator = False
        elif not previous_was_separator:
            slug_chars.append("_")
            previous_was_separator = True
    return "".join(slug_chars).strip("_") or "unknown"


def extract_json_fields(data: Any, category_mapping: dict[str, list[str]] | None = None) -> set[str]:
    """Extract field names from flat or category-nested result JSON."""
    mapping = CATEGORY_MAPPING if category_mapping is None else category_mapping
    nested_keys = {key for keys in mapping.values() for key in keys}
    fields: set[str] = set()
    stack: list[tuple[Any, bool]] = [(data, True)]

    while stack:
        value, is_category_level = stack.pop()
        if isinstance(value, dict):
            for key, child in value.items():
                if key in SKIP_KEYS:
                    continue
                if is_category_level and key in nested_keys and isinstance(child, dict):
                    stack.append((child, True))
                    continue
                fields.add(str(key))
        elif isinstance(value, list):
            stack.extend((item, is_category_level) for item in value if isinstance(item, dict))

    return fields


def validate_json(json_path: Path, schema: FieldSchema) -> ValidationResult:
    """Validate one JSON result file."""
    with json_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("a research result must be a JSON object")

    all_fields = schema["all_fields"]
    required_fields = schema["required_fields"]
    field_categories = schema["field_categories"]
    json_fields = extract_json_fields(data, schema["category_mapping"])
    covered = all_fields & json_fields
    missing = all_fields - json_fields
    extra = json_fields - all_fields
    missing_required = missing & required_fields
    missing_by_category: defaultdict[str, list[str]] = defaultdict(list)

    for field in missing:
        missing_by_category[field_categories.get(field, "Unknown")].append(field)

    return {
        "file": json_path.name,
        "total_defined": len(all_fields),
        "covered": len(covered),
        "missing": len(missing),
        "extra": len(extra),
        "coverage_rate": len(covered) / len(all_fields) * 100 if all_fields else 100.0,
        "missing_required": sorted(missing_required),
        "missing_optional": sorted(missing - required_fields),
        "missing_by_category": {key: sorted(value) for key, value in missing_by_category.items()},
        "extra_fields": sorted(extra),
        "valid": len(missing_required) == 0,
    }


def print_result(result: ValidationResult, verbose: bool = True) -> None:
    """Print a human-readable validation result."""
    status = "PASS" if result["valid"] else "FAIL"
    line = "=" * 60
    print(f"\n{line}")
    print(f"[{status}] {result['file']}")
    print(line)
    print(f"Coverage: {result['coverage_rate']:.1f}% ({result['covered']}/{result['total_defined']})")

    if result["missing_required"]:
        print(f"\n[ERROR] Missing required fields ({len(result['missing_required'])}):")
        print("\n".join(f"  - {field}" for field in result["missing_required"]))

    if verbose and result["missing_optional"]:
        missing_required = set(result["missing_required"])
        print(f"\n[WARN] Missing optional fields ({len(result['missing_optional'])}):")
        for category in sorted(result["missing_by_category"]):
            optional = [
                field
                for field in result["missing_by_category"][category]
                if field not in missing_required
            ]
            if optional:
                print(f"  [{category}]: {', '.join(optional)}")

    if verbose and result["extra_fields"]:
        extra = result["extra_fields"]
        print(f"\n[INFO] Extra fields ({len(extra)}):")
        print(f"  {', '.join(extra[:10])}")
        if len(extra) > 10:
            print(f"  ... and {len(extra) - 10} more")


def resolve_fields_path(raw_path: str) -> Path:
    """Resolve fields.yaml with common current-directory fallbacks."""
    fields_path = Path(raw_path)
    if fields_path.exists():
        return fields_path

    for candidate in (Path.cwd() / "fields.yaml", Path.cwd().parent / "fields.yaml"):
        if candidate.exists():
            return candidate

    raise FileNotFoundError(f"fields.yaml not found: {fields_path}")


def collect_json_files(args: argparse.Namespace) -> list[Path]:
    """Collect JSON paths from --json or --dir arguments."""
    if args.json:
        return [Path(path) for path in args.json]

    result_dir = Path(args.dir)
    if result_dir.exists():
        return sorted(result_dir.glob("*.json"))

    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Deep Research JSON field coverage")
    parser.add_argument("--fields", "-f", type=str, default="fields.yaml", help="Path to fields.yaml")
    parser.add_argument("--json", "-j", type=str, nargs="*", help="JSON file paths to validate")
    parser.add_argument("--dir", "-d", type=str, default="results", help="Directory containing JSON files")
    parser.add_argument("--quiet", "-q", action="store_true", help="Show summary only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        fields_path = resolve_fields_path(args.fields)
        schema = load_fields_yaml(fields_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    print(f"Field definition file: {fields_path}")
    total_fields = len(schema["all_fields"])
    total_required = len(schema["required_fields"])
    print(f"Total fields: {total_fields} (required: {total_required}, optional: {total_fields - total_required})")

    json_files = collect_json_files(args)
    if not json_files:
        print("[ERROR] No JSON files found")
        return 1

    results: list[ValidationResult] = []
    for json_path in json_files:
        try:
            result = validate_json(json_path, schema)
        except (OSError, ValueError) as exc:
            print(f"[ERROR] {json_path}: {exc}")
            continue
        results.append(result)
        print_result(result, verbose=not args.quiet)

    line = "=" * 60
    print(f"\n{line}")
    print("Summary")
    print(line)
    passed = sum(1 for result in results if result["valid"])
    avg_coverage = sum(result["coverage_rate"] for result in results) / len(results) if results else 0.0
    print(f"Validation passed: {passed}/{len(json_files)}")
    print(f"Average coverage: {avg_coverage:.1f}%")

    return 0 if passed == len(json_files) else 1


if __name__ == "__main__":
    sys.exit(main())
