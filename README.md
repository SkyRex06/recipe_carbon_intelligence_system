# Recipe Carbon Intelligence Platform

A hackathon-ready enterprise web app for carbon accounting and optimization of recipes and menus.

## What this MVP includes

- **Recipe carbon calculator** with ingredient + cooking method emissions.
- **Substitution explorer** that uses flavor-profile similarity + carbon reduction scoring.
- **Recipe optimizer** generating 3 variants (20%, 40%, 60% target reduction).
- **Menu dashboard API** for hotspot analysis and optimization potential.
- **Compliance report payload** endpoint suitable for export pipelines.
- **Simple web UI** for demo workflows.

## Stack

- FastAPI + Pydantic
- Lightweight static HTML/JS frontend
- Pytest for service-level tests

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## API endpoints

- `POST /api/calculate` – recipe carbon breakdown
- `GET /api/substitutions/{ingredient}?target_reduction=0.4` – substitution candidates
- `POST /api/optimize` – 20/40/60% optimization variants
- `POST /api/menu` – menu-level dashboard summary
- `POST /api/reports/compliance` – compliance-ready summary payload

## Notes

- Includes a built-in carbon coefficient database for **70+ ingredient keys** and cooking methods.
- Ingredient aliases and fuzzy matching handle common naming differences.
- Unknown ingredients default to a conservative fallback coefficient.
