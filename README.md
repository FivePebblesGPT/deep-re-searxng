# Deep Re SearXNG

Deep Re SearXNG combines a SearXNG-backed MCP server with repo-scoped Codex Deep Research skills. The MCP server provides private web search and URL reading; the skills orchestrate outline creation, delegated research, batch result JSON, and final reports.

This project is based on:

- `ihor-sokoliuk/mcp-searxng` for the TypeScript MCP server
- `Weizhena/Deep-Research-skills` for the Deep Research workflow shape

See `NOTICE.md` for pinned source commits.

## What It Provides

- A bundled local Compose stack: SearXNG, Valkey, and the MCP HTTP server.
- The original MCP tool names:
  - `searxng_web_search`
  - `searxng_search_suggestions`
  - `searxng_instance_info`
  - `web_url_read`
- Repo-scoped Codex skills under `.agents/skills`:
  - `$research`
  - `$research-add-items`
  - `$research-add-fields`
  - `$research-deep`
  - `$research-report`
  - `$delegated-research`
- A custom read-only Codex agent, `searxng_researcher`, configured to use SearXNG MCP tools instead of generic web search.

## Quick Start

Build and start the local stack:

```bash
docker compose up -d --build
```

Check the services:

```bash
curl http://127.0.0.1:3000/health
curl 'http://127.0.0.1:8080/search?q=searxng&format=json'
```

In Codex, trust this project so `.codex/config.toml` is loaded. The MCP endpoint is:

```text
http://127.0.0.1:3000/mcp
```

Use the one-shot delegated workflow:

```text
$delegated-research Research current SearXNG JSON API setup requirements and summarize sources.
```

Use the multi-item workflow:

```text
$research Compare open-source metasearch engines
$research-deep
$research-report
```

## Local Development

Install Node dependencies:

```bash
npm ci
```

Install Python dependencies for research validation:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Run checks:

```bash
npm run lint
npm run build
npm test
python scripts/research/validate_json.py --help
docker compose config
```

## Runtime Configuration

The MCP server needs `SEARXNG_URL`. In the bundled Compose stack this is set to `http://searxng:8080`.

Useful optional environment variables:

- `SEARXNG_DEFAULT_LANGUAGE`
- `SEARXNG_DEFAULT_SAFESEARCH`
- `SEARXNG_MAX_RESULTS`
- `SEARXNG_MAX_RESULT_CHARS`
- `URL_READ_MAX_CHARS`
- `URL_READ_MAX_CONTENT_LENGTH_BYTES`
- `FETCH_TIMEOUT_MS`
- `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`
- `MCP_HTTP_PORT`, `MCP_HTTP_HOST`
- `MCP_HTTP_HARDEN`, `MCP_HTTP_AUTH_TOKEN`

SearXNG JSON output is enabled in `searxng/settings.yml`:

```yaml
search:
  formats:
    - html
    - json
```

## Research Workflow Notes

`$research` creates a topic directory with:

```text
outline.yaml
fields.yaml
```

`$research-deep` reads those files, delegates item research to `searxng_researcher`, writes one JSON file per item, and validates results with:

```bash
python scripts/research/validate_json.py -f <fields.yaml> -j <result.json>
```

Delegated researchers are read-only and must return structured findings to the parent agent. The parent owns all file writes.
