---
name: research
description: Create a Deep Research outline and field schema for later SearXNG-backed research. Use when the user asks to start research, create a research outline, compare many items, or prepare deep research.
---

# Research

## Workflow

1. Build an initial framework from model knowledge:
   - topic
   - candidate research items
   - field categories and fields worth collecting
   - known uncertainty or likely missing areas
2. Ask the user to confirm material choices that cannot be inferred:
   - add/remove items
   - add/remove field categories
   - time range for web supplementation
   - batch size and items per agent
3. Delegate web supplementation to `searxng_researcher`:
   - ask it to find missing important items and fields
   - require source URLs
   - do not ask it to write files
4. Merge model and delegated findings, deduplicate items, and create:
   - `{topic_slug}/outline.yaml`
   - `{topic_slug}/fields.yaml`

## File Contracts

`outline.yaml`:

```yaml
topic: "Research topic"
items:
  - name: "Item name"
    category: "Optional category"
    description: "Why this item is in scope"
execution:
  batch_size: 3
  items_per_agent: 1
  output_dir: "./results"
```

`fields.yaml`:

```yaml
field_categories:
  - category: "Basic Info"
    fields:
      - name: "name"
        description: "Canonical item name"
        detail_level: "brief"
        required: true
```

Use detail levels `brief`, `moderate`, or `detailed`. Include an `uncertain` field category only when the research target needs domain-specific uncertainty tracking beyond the reserved JSON `uncertain` array.

## Completion

After writing both YAML files, show the paths, item count, field count, execution settings, and any assumptions that still matter.
