# Finding Marimo

Use this decision tree when the user wants to start or pair with a marimo notebook.

## Discover First

Run the bundled discovery script before starting a new server:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/discover-servers.sh
```

If one matching server is already running, use it. If multiple servers are running, choose the one whose notebook path matches the user's request, or target the user's requested port with `--port`.

## Start A Server

For `infrastructure/marimo` (the shared marimo tool environment), prefer the local venv:

```bash
cd ~/Documents/Q-agent/infrastructure/marimo
source venv/bin/activate
marimo edit examples/signal_research.py --no-token
```

Use `--no-token` for local pairing so the server appears in marimo's local registry and the execute script can discover it. Do not use `--headless` unless the user asks for a headless session.

## Execute Code

Use the bundled execute script:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/execute-code.sh --port 2718 -c "print('connected')"
```

For multiline snippets, use a single-quoted heredoc so shell interpolation cannot alter the code.
