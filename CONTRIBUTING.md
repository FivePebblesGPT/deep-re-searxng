# Contributing

Deep Re SearXNG is a local combined distribution of:

- a TypeScript SearXNG MCP server
- repo-scoped Codex Deep Research skills
- a bundled local Docker Compose runtime

## Development

```bash
npm ci
npm run lint
npm run build
npm test
docker compose config
```

For Python research helpers:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/research/validate_json.py --help
```

Keep the four MCP tool names stable unless a breaking change is intentional:

- `searxng_web_search`
- `searxng_search_suggestions`
- `searxng_instance_info`
- `web_url_read`

When changing skills, keep `SKILL.md` descriptions short and include clear `Use when` trigger language.
