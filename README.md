## Release Sentinel

Release Sentinel is a Python-based deployment gatekeeper. It evaluates proposed
release plans against policy, checks change windows, and aggregates service
readiness signals before allowing or rejecting a rollout.

- Partial implementation of SLO and error-budget evaluation
- Release policies that mix numeric and textual risk levels
- Docs that reference a future `azure_boards` integration not fully wired up

### Features
- Python 3.10+ and modern `pyproject.toml` packaging
- `typer` CLI with subcommands to:
  - evaluate a release plan
  - show policy summaries
  - inspect readiness signals for a service
- YAML-based policy and release definitions validated via Pydantic
- Pluggable readiness backends (mock SLO provider, incident feed, deploy freeze)
- Unit tests for the core evaluation and parsing logic

### Layout

```
release-sentinel/
├── configs/
│   ├── policies.yaml
│   └── release_plan.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   └── OPERATIONS.md
├── src/
│   └── release_sentinel/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── evaluator.py
│       ├── signals.py
│       └── integrations/
│           ├── azure_boards.py
│           └── slo_provider.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_evaluator.py
│   └── test_signals.py
├── pyproject.toml
├── LICENSE
└── README.md
```

### Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

release-sentinel evaluate configs/release_plan.yaml --policies configs/policies.yaml
```

### Running Tests

```bash
pytest
```

### Ambiguity Hooks

This codebase intentionally includes realistic ambiguities:

- Risk levels are sometimes numeric (1–5) and sometimes textual
  (`low`/`medium`/`high`/`critical`) in both policy and plan files.
- Docs describe different expectations for how "canary" vs "blue-green" modes
  should be evaluated compared to what the code currently enforces.
- The operations guide references Azure Boards auto-ticket creation, while the
  implementation only includes a stubbed integration.

These make it a good target for tasks that require clarification instead of
blind implementation.
