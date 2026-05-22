# Credentials Reference

All credentials and API keys used across the workspace, where they're consumed, and how to set them.

For the simplest setup, copy `.env.example` to `.env` at the repo root and fill in the values you need. Most pipelines also accept their own pipeline-local `.env` or profile files (documented below).

## Quick start

```bash
cp .env.example .env
# Edit .env with the credentials you actually need — none are required up front.
```

Then activate the shared venv:

```bash
cd infrastructure && source .venv/bin/activate
```

The `.env` file is gitignored. Do **not** commit it.

---

## Required vs optional

| Credential | Required for | Optional for |
|---|---|---|
| `SEC_EDGAR_IDENTITY` | `infrastructure/pipelines/edgar/` | Everything else |
| `WRDS_USERNAME` / `WRDS_PASSWORD` | `infrastructure/pipelines/wrds/` | Everything else (WRDS is paid; access from your institution) |
| Exchange API keys (BINANCE/COINBASE/KRAKEN) | Authenticated/rate-elevated access only | Public OHLCV endpoints work without keys |
| `POLYMARKET_API_KEY` | Authenticated CLOB endpoints, trading | Read-only price history & Gamma metadata work without keys |
| `NEO4J_PASSWORD` | `agent_graph_system/` with Neo4j backend | Local in-memory graph backend |
| `GITHUB_TOKEN` | `agent_graph_system/ingestion/github/` | Other pipelines |
| `MARIMO_TOKEN` | Marimo kernel started with `--token` | Public marimo notebooks |
| `QC_USER_ID` / `QC_API_TOKEN` | Non-interactive `lean login` | Interactive `lean login` (preferred) |

---

## Per-pipeline references

### SEC EDGAR

- **Env**: `SEC_EDGAR_IDENTITY` — e.g. `"Your Name your.email@example.com"`
- **Why**: SEC requires a real user-agent identifying the operator. Pipelines hitting EDGAR with the placeholder pattern will be rate-limited or blocked.
- **Code**: `infrastructure/pipelines/edgar/pipeline.py`

### WRDS (Wharton Research Data Services)

- **Profile file**: `infrastructure/pipelines/wrds/.wrds_profiles.json` (gitignored — copy from `wrds_profiles.example.json`)
- **Password**: `~/.pgpass` (recommended) or `WRDS_PASSWORD` env var
- **Profile selection**: `WRDS_PROFILE` env var or `--profile <name>` flag on any pipeline script
- **Note**: WRDS access requires an institutional subscription. Schemas you can query depend on what your institution entitles.

### Crypto exchanges

- **Env**: `BINANCE_API_KEY/SECRET`, `COINBASE_API_KEY/SECRET`, `KRAKEN_API_KEY/SECRET`
- **Pipeline-local example**: `infrastructure/pipelines/crypto/.env.example`
- **Note**: Public OHLCV via `ccxt` works without authentication. Only set keys if you need higher rate limits or authenticated endpoints.

### Polymarket

- **Env**: `POLYMARKET_API_KEY`, `POLYMARKET_API_SECRET`
- **Code**: `infrastructure/pipelines/polymarket/`
- **Note**: Read-only Gamma + CLOB endpoints work without authentication.

### agent_graph_system — Neo4j

- **Env**: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- **Default backend**: local in-memory (no Neo4j required). Set `GRAPH_BACKEND=neo4j` to switch.
- **Compose**: see `agent_graph_system/docker-compose.yml`

### agent_graph_system — GitHub

- **Env**: `GITHUB_TOKEN` (PAT with `repo` or `public_repo`), `GITHUB_WEBHOOK_SECRET`, `GITHUB_REPOS` (comma-separated `owner/repo` list)
- **Code**: `agent_graph_system/ingestion/github/`

### Marimo notebooks

- **Env**: `MARIMO_TOKEN`
- **Use**: only when you've started marimo with `--token`, typically to authenticate the `marimo-pair` skill kernel client. Local notebooks usually run without auth.

### QuantConnect (lean CLI)

- **Preferred**: run `lean login` interactively — credentials are stored at `~/.lean/credentials`.
- **Non-interactive**: `QC_USER_ID` + `QC_API_TOKEN` env vars (useful for CI).

---

## Security

- Never commit `.env`, `wrds_profiles.json` (without `.example`), `~/.pgpass`, or any file matching `*credentials*` / `*secret*`.
- The repo ships with a Gitleaks-based scanner in `.github/workflows/secret-scan.yml`; it will block PRs that introduce committed secrets.
- Rotate any credential that has been pasted into chat, a notebook, or a Slack message — assume it's compromised.
