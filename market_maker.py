import numpy as np

class InventoryMarketMaker:
    """
    Continuous liquidity quoter implementing the Avellaneda-Stoikov framework
    to dynamically adjust reservation prices and mitigate inventory buildup.
    """
    def __init__(self, gamma: float = 0.35, kappa: float = 1.5, target_symbol: str = "Candidate_A"):
        self.gamma = gamma          # Risk aversion penalty
        self.kappa = kappa          # Order-book liquidity parameter
        self.target = target_symbol
        self.inventory = 0
        self.cash = 0.0

    def quote(self, fair_price: float, t_remaining: float) -> tuple[float, float]:
        """Skews reservation price R away from current inventory balance."""
        skew = self.inventory * self.gamma * (0.2 ** 2) * max(t_remaining, 0.01)
        reservation_price = float(np.clip(fair_price - skew, 0.02, 0.98))
        
        half_spread = (1.0 / self.gamma) * np.log(1.0 + self.gamma / self.kappa)
        half_spread = max(half_spread, 0.01)
        
        my_bid = round(max(0.01, reservation_price - half_spread), 3)
        my_ask = round(min(0.99, reservation_price + half_spread), 3)
        return my_bid, my_ask

    def process_fills(self, my_bid: float, my_ask: float, market_book: dict):
        """Simulates fills against market book liquidity."""
        if my_bid >= market_book["bid"] and self.inventory < 15:
            if np.random.uniform() < 0.40:
                self.inventory += 1
                self.cash -= my_bid

        if my_ask <= market_book["ask"] and self.inventory > -15:
            if np.random.uniform() < 0.40:
                self.inventory -= 1
                self.cash += my_ask