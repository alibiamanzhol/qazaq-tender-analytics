import csv
import io
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .models import Tender, TenderView
from .risk import evaluate, reduction_pct
from .store import all_tenders, get_tender, upsert_many

app = FastAPI(title="Qazaq Tender Analytics", version="1.0.0")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def view(t: Tender) -> TenderView:
    risk = evaluate(t)
    return TenderView(**t.model_dump(), reduction_pct=reduction_pct(t.budget_kzt, t.award_kzt), risk_score=risk.score, risk_flags=risk.flags)

@app.on_event("startup")
def seed() -> None:
    if all_tenders():
        return
    sample = Path(__file__).parent.parent / "data" / "sample_tenders.csv"
    if sample.exists():
        with sample.open(encoding="utf-8") as f:
            upsert_many([Tender(**row) for row in csv.DictReader(f)])

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")

@app.get("/api/tenders", response_model=list[TenderView])
def tenders():
    return [view(t) for t in all_tenders()]

@app.get("/api/tenders/{tender_id}", response_model=TenderView)
def tender(tender_id: str):
    item = get_tender(tender_id)
    if not item:
        raise HTTPException(404, "Tender not found")
    return view(item)

@app.get("/api/summary")
def summary():
    items = [view(t) for t in all_tenders()]
    total_budget = sum(x.budget_kzt for x in items)
    total_award = sum(x.award_kzt for x in items)
    return {
        "tenders": len(items),
        "total_budget_kzt": total_budget,
        "total_award_kzt": total_award,
        "savings_kzt": total_budget - total_award,
        "high_risk": sum(1 for x in items if x.risk_score >= 50),
    }

@app.get("/api/suppliers")
def suppliers():
    groups = {}
    for x in [view(t) for t in all_tenders()]:
        g = groups.setdefault(x.supplier, {"supplier": x.supplier, "awards": 0, "award_value_kzt": 0.0, "avg_risk": 0.0, "_risk": 0})
        g["awards"] += 1
        g["award_value_kzt"] += x.award_kzt
        g["_risk"] += x.risk_score
    out = []
    for g in groups.values():
        g["avg_risk"] = round(g.pop("_risk") / g["awards"], 1)
        out.append(g)
    return sorted(out, key=lambda x: x["award_value_kzt"], reverse=True)

@app.post("/api/import")
async def import_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "CSV file required")
    raw = (await file.read()).decode("utf-8-sig")
    try:
        items = [Tender(**row) for row in csv.DictReader(io.StringIO(raw))]
    except Exception as exc:
        raise HTTPException(400, f"Invalid CSV: {exc}") from exc
    return {"imported": upsert_many(items)}
