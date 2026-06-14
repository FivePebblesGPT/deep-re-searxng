---
name: research-deep
description: Run SearXNG-backed deep research from outline.yaml and fields.yaml. Use when the user asks to run deep research, fill result JSON files, resume research batches, or research each item in an outline.
---

# Research Deep

## Workflow

1. Locate matching `outline.yaml` and `fields.yaml`; if multiple topics exist, ask which one to run.
2. Read `execution.batch_size`, `execution.items_per_agent`, and `execution.output_dir`.
3. Resume safely:
   - create the output directory if missing
   - skip items whose slugged JSON file already validates
   - retry invalid or missing files
4. For each batch, spawn `searxng_researcher` agents. Each agent receives:
   - topic
   - one or more item YAML blocks according to `items_per_agent`
   - full field schema
   - instruction to return JSON objects in the response only
5. The parent agent writes each returned JSON file to `{output_dir}/{item_slug}.json`.
6. Validate every written file with:

```bash
python scripts/research/validate_json.py -f <fields.yaml> -j <result.json>
```

## Researcher Output Contract

Each JSON object must:

- cover all fields from `fields.yaml`
- use English values
- mark uncertain field values with `[uncertain]`
- include a top-level `uncertain` array of field names
- include source URLs in fields where source tracking is part of the schema

The delegated researcher must not write files. The parent owns filesystem writes and validation.

## Completion

Report completed, skipped, failed, and uncertain-heavy items plus the result directory.
