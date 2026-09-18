from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ArbResult:
    sum_asks: float
    net_margin_pct: float
    locked_profit: float

class DutchBookScanner:
    """
    Scans real-time order books across all mutually exclusive outcomes
    to identify violations of Kolmogorov's third axiom (sum(P_i) < 1.0 - fees).
    """
    def __init__(self, taker_fee_per_contract: float = 0.001):
        self.taker_fee = taker_fee_per_contract

    def evaluate(self, books: Dict[str, Dict[str, float]], capital_per_arb: float = 100.0) -> Optional[ArbResult]:
        total_ask_cost = sum(b["ask"] for b in books.values())
        total_fees = len(books) * self.taker_fee
        net_edge = 1.0 - total_ask_cost - total_fees

        if net_edge > 0.001:  # Positive yield after platform taker fees
            margin_pct = (net_edge / total_ask_cost) * 100.0
            profit = capital_per_arb * (net_edge / total_ask_cost)
            return ArbResult(
                sum_asks=round(total_ask_cost, 4),
                net_margin_pct=round(margin_pct, 2),
                locked_profit=round(profit, 2)
            )
        return None