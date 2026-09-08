from dataclasses import dataclass
from .models import Tender

@dataclass(frozen=True)
class RiskResult:
    score: int
    flags: list[str]


def reduction_pct(budget_kzt: float, award_kzt: float) -> float:
    if budget_kzt <= 0:
        return 0.0
    return round((budget_kzt - award_kzt) / budget_kzt * 100, 4)


def evaluate(tender: Tender) -> RiskResult:
    score = 0
    flags: list[str] = []
    reduction = reduction_pct(tender.budget_kzt, tender.award_kzt)

    if tender.bids_count == 1:
        score += 25
        flags.append("single_bid")
    if reduction > 15:
        score += 20
        flags.append("large_price_reduction")
    if 0 <= reduction < 0.5:
        score += 10
        flags.append("award_close_to_budget")
    if tender.license_count == 0:
        score += 30
        flags.append("no_recorded_licenses")
    if tender.budget_kzt >= 1_000_000_000:
        score += 15
        flags.append("high_value")

    return RiskResult(score=min(score, 100), flags=flags)
