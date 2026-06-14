# Security Policy

## Supported Versions

This repo is currently a local combined distribution. Security fixes should land on the active development branch and be released with the next tagged version.

## Reporting a Vulnerability

Do not open a public issue for security-sensitive findings. Report privately through the repository owner or GitHub Security Advisories once this repo has a public advisory channel.

Include:

- affected version or commit
- configuration and runtime mode
- reproduction steps
- impact and suggested mitigation

## Threat Model

`deep-re-searxng` runs a Node.js MCP server between an AI assistant and a SearXNG instance. It can also fetch and convert arbitrary URLs through `web_url_read`.

Primary risks:

- SSRF through `web_url_read`
- unintended exposure of the MCP HTTP endpoint
- credentials in environment variables
- prompt injection or misleading content from web pages
- data leakage through search queries sent to the configured SearXNG instance and its enabled engines

## Built-In Controls

- `web_url_read` blocks private/internal URLs by default.
- Redirects are checked before they are followed.
- HTTP mode defaults to localhost binding unless overridden.
- Hardened HTTP mode supports bearer auth, CORS allowlists, and host allowlists.
- The bundled Compose file binds SearXNG and MCP ports to `127.0.0.1`.
- The `searxng_researcher` Codex agent is configured read-only and generic web search is disabled.

## Deployment Recommendations

For local use, prefer the bundled Compose stack:

```bash
docker compose up -d --build
```

Do not expose `MCP_HTTP_PORT` directly to the internet. If remote access is required:

```bash
MCP_HTTP_HARDEN=true
MCP_HTTP_AUTH_TOKEN=<strong-random-token>
MCP_HTTP_ALLOWED_ORIGINS=https://your-app.example.com
MCP_HTTP_ALLOWED_HOSTS=your-app.example.com
MCP_HTTP_ALLOW_PRIVATE_URLS=false
```

Put the service behind a TLS-terminating reverse proxy and keep `web_url_read` private URL access disabled unless internal fetching is intentional.

## Dependency Auditing

```bash
npm run audit:deps
npm run security
```

Python helper dependencies are listed in `requirements.txt`.
