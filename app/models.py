from pydantic import BaseModel, Field

class Tender(BaseModel):
    id: str
    title: str
    customer: str
    supplier: str
    budget_kzt: float = Field(ge=0)
    award_kzt: float = Field(ge=0)
    bids_count: int = Field(ge=0)
    license_count: int = Field(ge=0)
    status: str

class TenderView(Tender):
    reduction_pct: float
    risk_score: int
    risk_flags: list[str]
