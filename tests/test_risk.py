from app.models import Tender
from app.risk import evaluate, reduction_pct

def test_reduction():
    assert reduction_pct(100, 93) == 7.0

def test_risk_flags_are_explicit():
    t = Tender(id="x", title="x", customer="x", supplier="x", budget_kzt=2_000_000_000, award_kzt=1_999_000_000, bids_count=1, license_count=0, status="awarded")
    result = evaluate(t)
    assert result.score == 80
    assert set(result.flags) == {"single_bid", "award_close_to_budget", "no_recorded_licenses", "high_value"}
