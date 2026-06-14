---
name: research-add-items
description: Add research items to an existing Deep Research outline. Use when the user asks to add items, expand coverage, or supplement research objects.
---

# Research Add Items

## Workflow

1. Locate the active `outline.yaml`; if more than one exists, ask which topic to update.
2. Read the existing `items` list and normalize names for duplicate detection.
3. Collect additions from the user. If the user asks for discovery or coverage, delegate to `searxng_researcher` for sourced suggestions.
4. Merge confirmed items into `outline.yaml` with `name`, optional `category`, and `description`.
5. Preserve existing execution settings and item order, appending new items at the end.

## Completion

Report the updated path, new item count, and skipped duplicates.
