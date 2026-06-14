---
name: delegated-research
description: Delegate a focused web research task to a specialized SearXNG researcher and synthesize the findings. Use when the user asks to delegate research, use another agent for research, or wants sourced one-shot research without creating a full outline.
---

# Delegated Research

## Workflow

1. Restate the research question, success criteria, time sensitivity, and expected output shape.
2. Spawn exactly one `searxng_researcher` agent unless the user explicitly asks for multiple delegated researchers.
3. Give the researcher:
   - the exact research question
   - current date requirements
   - any source preferences or exclusions
   - required output format
   - instruction to use SearXNG MCP tools and return findings only
4. Wait for the delegated result.
5. Synthesize the final answer in the parent thread:
   - lead with the answer
   - separate verified facts from inference
   - include source links
   - call out gaps, uncertainty, and conflicting evidence

## Boundaries

Do not create `outline.yaml`, `fields.yaml`, or result JSON files. Use `research` and `research-deep` for the full multi-item workflow.
