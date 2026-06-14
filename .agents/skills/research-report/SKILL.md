---
name: research-report
description: Generate a Markdown report from Deep Research JSON results. Use when the user asks to summarize research results, create report.md, or turn result JSON files into a readable report.
---

# Research Report

## Workflow

1. Locate the active `outline.yaml`, `fields.yaml`, and result directory.
2. Read every result JSON file and validate it with `scripts/research/validate_json.py`.
3. Ask the user only for high-impact presentation choices, such as which short fields to show in the table of contents.
4. Generate `{topic_slug}/generate_report.py` when a reusable conversion script is useful; otherwise write the report directly.
5. Create `{topic_slug}/report.md`.

## Report Rules

- Include every item from the outline.
- Use a table of contents with anchor links.
- Organize detail sections by field category.
- Skip values containing `[uncertain]`, values listed in the top-level `uncertain` array, and empty values.
- Put JSON fields not defined in `fields.yaml` under `Other Info`, excluding `_source_file` and `uncertain`.
- Preserve source URLs where present.

## Completion

Report the output path, number of result files included, skipped invalid files, and omitted uncertain fields.
