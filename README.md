# Qazaq Tender Analytics

A compact procurement analytics service for exploring tender data from Kazakhstan. It focuses on price movement, supplier concentration and transparent, rule-based risk indicators that can be inspected and explained.

## What it does

- imports tender records from CSV;
- calculates bid reduction percentages;
- highlights single-bid and unusually low-price cases;
- summarizes suppliers and contracting authorities;
- exposes a REST API through FastAPI;
- includes a small browser dashboard for quick review;
- keeps risk rules explicit instead of hiding them behind a black box.

## Risk model

The current score is intentionally simple and auditable. Points are added for:

| Signal | Points |
| --- | ---: |
| Only one submitted bid | 25 |
| Award price is more than 15% below budget | 20 |
| Award price is within 0.5% of budget | 10 |
| Supplier has no recorded license flags in the imported dataset | 30 |
| Tender value is at least KZT 1 billion | 15 |

The score is a screening signal, not a finding of wrongdoing.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the dashboard or `http://127.0.0.1:8000/docs` for the API.

## Import format

```csv
id,title,customer,supplier,budget_kzt,award_kzt,bids_count,license_count,status
T-001,Road reconstruction,Akimat of Region,Example LLP,1200000000,1116000000,3,2,awarded
```

Import a file:

```bash
curl -X POST http://127.0.0.1:8000/api/import \
  -F "file=@data/sample_tenders.csv"
```

## API

- `GET /api/tenders` — tender list with calculated risk data
- `GET /api/tenders/{id}` — one tender
- `GET /api/summary` — portfolio-level statistics
- `GET /api/suppliers` — supplier aggregation
- `POST /api/import` — CSV import

## Project structure

```text
app/
  main.py          FastAPI application
  models.py        Pydantic models
  risk.py          transparent scoring rules
  store.py         SQLite data access
  static/          lightweight dashboard
data/
  sample_tenders.csv
tests/
  test_risk.py
```

## Notes

This repository is designed for public-data analysis and due-diligence workflows. Data quality should always be checked against the original procurement platform and official registers before drawing conclusions.

## License

MIT
