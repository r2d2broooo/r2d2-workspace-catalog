# R2D2 Trading System

A research and paper-trading workspace for US equities. It combines an operator dashboard, shared market-data services, quantitative context, independent model-assisted research and a Strategy Lab. The aim is to make inputs, decisions and measured outcomes inspectable in one place.

This is a source release of an integrated application. The dashboard imports the shared bot runtime, so both are kept in this repository. It does not include a funded brokerage connection, private account history or a ready-to-run market-data snapshot.

## Main capabilities

- **Market research:** watchlists, screening, momentum and relative-strength rankings, breadth, sector/industry/theme context, earnings, news and filing tools.
- **Charts and measurements:** daily chart rendering, moving-average and volatility facts, factors and key levels computed by code.
- **Uncertainty ranges:** a lightweight statistical range engine with horizon-specific calibration and historical evaluation. Live ranges describe uncertainty; they are not point-price or direction predictions.
- **Independent paper books:** provider-specific sessions and ledgers keep model research separate. Saved risk controls and order execution stay in code.
- **Strategy Lab:** validated expressions describe entries, ranking, sizing, stops and exits. The historical engine models finite cash, next-open fills and trading costs. Existing validation checks and forward paper trials separate research from promotion.
- **Deterministic policy research:** a fixed-state learned-entry experiment trains on in-sample data, freezes ordinary Lab rules, then evaluates them. It uses no LLM calls and does not bypass the trial/promotion process.
- **Operations:** input-freshness checks, resumable review records, usage accounting and observable run status.

## Layout and workflow

| Directory | Responsibility |
|---|---|
| `dashboard/` | FastAPI application, Alpine interface and operator-facing routes |
| `telegram-bots/` | Shared runtime, data producers, agents, execution and tests |
| `trading-wiki/` | Wiki schema and bookkeeping code; private ticker notes are omitted |
| `research-archive/` | Historical source for reference; not the active trading policy |
| `installed-systemd-examples/` | Configuration examples requiring local review |

The normal workflow is: configure sources → produce/check data → inspect research → evaluate a strategy or paper decision → inspect outcomes. Cloning does not start a provider, refresh data, enable a timer or place an order.

## Getting started

Read [SETUP.md](SETUP.md) before configuring a deployment. Use separate virtual environments for the two applications and install their respective requirements. Review workspace paths and service definitions, create local environment files from the examples, populate a watchlist and build the required data caches. Provider CLIs, Ollama and Telegram are optional integrations with their own setup.

For a source-only check:

```bash
python3 check.py
```

The watchlist is deliberately empty in this release. No credentials, browser profiles, private research notes, paper books or market caches are supplied. A fresh clone therefore needs configuration and data before the dashboard's research and trading flows are useful.

## Validation and limits

The exported system has focused tests using temporary state and stubbed providers. Historical results remain affected by data quality, universe selection and execution assumptions. Passing a historical check does not establish future profitability. The first deterministic policy experiment failed its validation; this repository preserves the experiment infrastructure, not a claim of an effective trading strategy.

Agent, browser and knowledge helpers also have standalone repositories. This integration keeps compatible copies so restoring it does not depend on assembling unrelated repositories manually. See the workspace catalogue for ownership and update guidance.

## Privacy, provenance and updates

This repository is a sanitized source export. No provider credentials, personal contact information, configured IP addresses, private conversations or runtime databases are included. Example hostnames and local environment variables are intentional. Keep newly generated account data and captures outside version control.

A source manifest records exported files. Local adaptations and third-party material retain their own provenance/notices; public visibility does not apply a new blanket license to every file. Related repositories and the manual update process are listed in the [workspace catalogue](https://github.com/r2d2broooo/r2d2-workspace-catalog).

Updates are made only on explicit request. Cloning does not enable an automatic sync, scheduled publication or Git push.
