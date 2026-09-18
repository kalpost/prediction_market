import numpy as np
from simulator import MultiOutcomeMarket
from arbitrage import DutchBookScanner
from market_maker import InventoryMarketMaker

def run_single_path(steps: int = 1000):
    market = MultiOutcomeMarket()
    scanner = DutchBookScanner(taker_fee_per_contract=0.001)
    mm = InventoryMarketMaker(gamma=0.35, target_symbol="Candidate_A")

    arb_count = 0
    arb_profit = 0.0

    for step in range(steps):
        t_remaining = 1.0 - (step / steps)
        market.step(jump_probability=0.08)
        fair_probs = market.get_fair_probabilities()
        books = market.get_order_books(retail_inefficiency=0.035)

        # 1. Arbitrage Scanner
        arb = scanner.evaluate(books, capital_per_arb=100.0)
        if arb:
            arb_count += 1
            arb_profit += arb.locked_profit

        # 2. Market Maker
        my_bid, my_ask = mm.quote(fair_probs[mm.target], t_remaining)
        mm.process_fills(my_bid, my_ask, books[mm.target])

    fair_terminal = market.get_fair_probabilities()[mm.target]
    mm_mtm = mm.cash + (mm.inventory * fair_terminal)

    return arb_count, arb_profit, mm.inventory, mm_mtm

def run_monte_carlo(n_simulations: int = 500, steps_per_sim: int = 1000):
    print("=" * 70)
    print(f"RUNNING MONTE CARLO HARNESS ({n_simulations} PATHS x {steps_per_sim} TICKS)")
    print("=" * 70)

    results = [run_single_path(steps_per_sim) for _ in range(n_simulations)]
    
    arb_counts, arb_profits, mm_inventories, mm_pnls = zip(*results)
    
    arb_counts = np.array(arb_counts)
    arb_profits = np.array(arb_profits)
    mm_inventories = np.array(mm_inventories)
    mm_pnls = np.array(mm_pnls)

    print(f"Combinatorial Arbitrage Yield (Mean +/- Std): ${np.mean(arb_profits):.2f} +/- ${np.std(arb_profits):.2f}")
    print(f"Expected Arb Frequency per 1k Ticks       : {np.mean(arb_counts):.1f} events ({np.mean(arb_counts)/10:.1f}% capture rate)")
    print("-" * 70)
    print(f"MM Terminal Inventory (Mean +/- Std)      : {np.mean(mm_inventories):.2f} +/- {np.std(mm_inventories):.2f} contracts")
    print(f"MM Mark-to-Market PnL (Mean +/- Std)      : ${np.mean(mm_pnls):.2f} +/- ${np.std(mm_pnls):.2f}")
    print(f"MM 95% Parametric Value-at-Risk (VaR_95)   : ${np.percentile(mm_pnls, 5):.2f}")
    print("=" * 70)

if __name__ == "__main__":
    run_monte_carlo(n_simulations=500, steps_per_sim=1000)