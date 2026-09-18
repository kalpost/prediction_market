import numpy as np
from typing import Dict, List

class MultiOutcomeMarket:
    """
    Simulates a multi-outcome event market where true underlying probabilities
    are guaranteed to sum to 1.0 via softmax normalization.
    """
    def __init__(self, outcomes: List[str] = None):
        self.outcomes = outcomes or ["Candidate_A", "Candidate_B", "Candidate_C"]
        self.n = len(self.outcomes)
        self.logits = np.zeros(self.n)

    def get_fair_probabilities(self) -> Dict[str, float]:
        """Softmax projection: mathematically guarantees sum(p) == 1.0 and p_i > 0."""
        exp_logits = np.exp(self.logits - np.max(self.logits))
        probs = exp_logits / np.sum(exp_logits)
        return {name: float(probs[i]) for i, name in enumerate(self.outcomes)}

    def step(self, jump_probability: float = 0.05):
        """Diffuses odds and injects Poisson-like news shocks."""
        self.logits += np.random.normal(0, 0.05, size=self.n)
        
        # Surprise news shock favoring or hurting one candidate
        if np.random.uniform() < jump_probability:
            shock_target = np.random.randint(0, self.n)
            self.logits[shock_target] += np.random.choice([-0.4, 0.4])

    def get_order_books(self, retail_inefficiency: float = 0.035) -> Dict[str, Dict[str, float]]:
        """
        Generates best bid/ask per contract with retail quoting friction,
        guaranteeing all quotes are strictly bounded within [0.01, 0.99].
        """
        fair = self.get_fair_probabilities()
        books = {}
        for name in self.outcomes:
            p = fair[name]
            half_spread = 0.012
            noise = np.random.uniform(-retail_inefficiency, retail_inefficiency)
            
            bid = float(np.clip(p - half_spread + noise, 0.01, 0.97))
            ask = float(np.clip(max(bid + 0.01, p + half_spread + noise), 0.02, 0.99))
            
            books[name] = {"bid": round(bid, 3), "ask": round(ask, 3)}
        return books