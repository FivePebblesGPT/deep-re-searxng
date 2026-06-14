---
name: research-add-fields
description: Add field definitions to an existing Deep Research fields schema. Use when the user asks to add fields, refine dimensions, or expand the data captured by deep research.
---

# Research Add Fields

## Workflow

1. Locate the active `fields.yaml`; if more than one exists, ask which topic to update.
2. Read existing `field_categories` and field names.
3. Collect additions from the user. If the user asks for discovery, delegate to `searxng_researcher` for common fields in the domain.
4. For each accepted field, choose:
   - category
   - `name`
   - `description`
   - `detail_level`: `brief`, `moderate`, or `detailed`
   - `required`: `true` only when missing it should fail validation
5. Append fields without renaming existing fields unless the user explicitly requests a schema migration.

## Completion

Report the updated path, added fields, skipped duplicates, and any validation-impacting required fields.
