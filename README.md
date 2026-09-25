# BREX — Brand Radar API → Excel Pipeline

Pulls AI visibility data (mentions, citations, impressions, share of voice) for a brand and its
competitors from the Ahrefs Brand Radar API and accumulates it in an Excel file with the same
structure as the Brand Radar "AI visibility / Platforms" export.

For scope, endpoint mapping, constraints and roadmap, see [plan.md](plan.md).

## Setup

Requires Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and fill it in:

```
AHREFS_API_KEY=<Ahrefs API key>
BREX_REPORT_ID=<report id>
```

- `.env` is never committed (`.gitignore`). Do not put the key in code or in `.env.example`.
- `BREX_REPORT_ID` comes from the report URL: `app.ahrefs.com/brand-radar/reports/<report_id>/...`
  If you don't know it, the connection test lists the reports in the account.

## Connection test

Run from the repo folder:

```powershell
.\.venv\Scripts\python -m scripts.auth_test
```

Calls the `management/brand-radar-reports` endpoint (does not consume units) and prints the
account's Brand Radar reports as JSON.

## Structure

```
brex/
  config.py      .env loading, constants (prompts="custom")
  client.py      Ahrefs API client: Bearer auth, exponential backoff on 429
scripts/
  auth_test.py   connection test
plan.md          project plan (Turkish)
```

## Notes

- Most Brand Radar endpoints support both GET and POST. For the Overview endpoints used in this
  project we prefer POST: the brand definition is a nested object (`url_groups`) that doesn't fit
  in a query string, and `citations-overview` only supports POST.
- The client enforces `prompts="custom"` on every Brand Radar request; any other value raises an
  error before the request is sent. Only requests that return custom prompt data are free of unit
  cost.
- No direct changes on `main`; each step runs on its own branch.
- Output files (`*.xlsx`, `*.csv`, `outputs/`) contain brand data and are never committed.
