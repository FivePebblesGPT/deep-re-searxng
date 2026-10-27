# Deep research setup

Deep Re SearXNG combines the upstream MCP server with a local search stack and
six research skills. The source repository is
<https://github.com/FivePebblesGPT/deep-re-searxng>; see [NOTICE.md](../NOTICE.md)
for the integrated upstream revisions. Node.js 22+ is required for Node development.

## Local stack

From this repository, start SearXNG, Valkey and the fork's HTTP MCP server:

```bash
docker compose -f compose.yaml up -d --build
docker compose -f compose.yaml ps
curl --fail http://127.0.0.1:3000/health
curl --fail 'http://127.0.0.1:8080/search?q=searxng&format=json'
```

SearXNG JSON search is enabled in `searxng/settings.yml`. Replace its example
`server.secret_key` for your deployment. Compose sets the internal
`SEARXNG_URL=http://searxng:8080`; clients connect to
`http://127.0.0.1:3000/mcp`. `SEARXNG_PORT` and `MCP_HTTP_PORT` change host ports.
Inspect `docker compose -f compose.yaml logs` when diagnosing startup failures.

Use `-f compose.yaml` explicitly: the repository also retains the upstream
`docker-compose.yml`/overlays as MCP-only examples. They do not start this bundled
search stack. Docker support and access to image/build dependencies are required.

## Python and local development

The parent research agent runs the validator, so install its Python dependency:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python scripts/research/validate_json.py --help
```

Activate that environment when invoking skill commands that use `python`.
For local Node development, run `npm ci`, `npm run lint`, `npm run build` and
`npm test`. The research asset tests also use Python/PyYAML, so run tests with
the virtual environment activated. Building the Node package does not package
the repo-scoped skills or Python scripts into the npm CLI artifact.

## Agent setup

Codex loads the repo-scoped `.codex/config.toml` and
`.codex/agents/searxng-researcher.toml` after you trust/open this project. Skills
live under `.agents/skills/`; `searxng_researcher` returns findings without writing
files. The parent owns outline/result/report writes and validation.

Other agent hosts must register the HTTP MCP endpoint and adapt the agent and
skill discovery paths. Preserve the parent/worker boundary and resolve
`scripts/research/validate_json.py` relative to this repository, not an unrelated
research workspace. The server tools remain:

- `searxng_web_search`
- `searxng_search_suggestions`
- `searxng_instance_info`
- `web_url_read`

See [client configuration recipes](client-configurations.md) for MCP-only
OpenCode and other client examples. MCP registration alone does not install a
delegated researcher or the research skills.

## Workflow

For a focused question, invoke `delegated-research`. For a multi-item investigation:

1. `research`: define a topic and create `outline.yaml` and `fields.yaml`.
2. Optionally use `research-add-items` or `research-add-fields` to refine scope.
3. `research-deep`: delegate source-backed findings, write result JSON and validate it.
4. `research-report`: synthesize valid results and report uncertainty/omissions.

In Codex, the invocation sequence is `$research`, `$research-deep`, and
`$research-report`. Other hosts can load the skills by name. Keep source URLs,
versions/access dates and actual reading stages; a report is not proof that papers
were screened in full text.

The canonical field schema remains:

```yaml
field_categories:
  - category: Basic Info
    fields:
      - name: name
        description: Canonical item name
        required: true
```

Validate an item with:

```bash
.venv/bin/python scripts/research/validate_json.py \
  -f /path/to/topic/fields.yaml -j /path/to/topic/results/item.json
```

Unsupported or empty field schemas fail rather than silently checking zero
fields. If no field has an explicit `required` marker, all fields are required;
otherwise those markers determine requiredness. Use explicit `required: false`
for optional fields. Field coverage is not factual/source verification.
