import numpy as np
from simulator import MultiOutcomeMarket
from arbitrage import DutchBookScanner
from market_maker import InventoryMarketMaker

def main():
    steps = 1000
    market = MultiOutcomeMarket()
    scanner = DutchBookScanner(taker_fee_per_contract=0.001)
    mm = InventoryMarketMaker(gamma=0.35, target_symbol="Candidate_A")

    arb_triggers = 0
    total_arb_profit = 0.0

    print("=" * 65)
    print("RUNNING MULTI-OUTCOME PREDICTION MARKET ENGINE")
    print("=" * 65)

    for step in range(steps):
        t_remaining = 1.0 - (step / steps)
        market.step(jump_probability=0.08)
        
        fair_probs = market.get_fair_probabilities()
        books = market.get_order_books(retail_inefficiency=0.035)

        # 1. Arbitrage Scanner Tick across all 3 contracts
        arb = scanner.evaluate(books, capital_per_arb=100.0)
        if arb:
            arb_triggers += 1
            total_arb_profit += arb.locked_profit

        # 2. Market Maker Quoting Tick on Candidate_A
        my_bid, my_ask = mm.quote(fair_probs[mm.target], t_remaining)
        mm.process_fills(my_bid, my_ask, books[mm.target])

    fair_terminal = market.get_fair_probabilities()[mm.target]
    mm_mtm = mm.cash + (mm.inventory * fair_terminal)

    print(f"Discrete Simulation Ticks   : {steps}")
    print("-" * 65)
    print("ARBITRAGE STRATEGY (Combinatorial Dutch-Book):")
    print(f"  Opportunities Captured    : {arb_triggers}")
    print(f"  Total Locked-in Profit    : ${total_arb_profit:.2f}")
    print("-" * 65)
    print(f"MARKET MAKING STRATEGY ({mm.target}):")
    print(f"  Terminal Inventory        : {mm.inventory} contracts")
    print(f"  Cash Flow Balance         : ${mm.cash:.2f}")
    print(f"  Mark-to-Market Total PnL  : ${mm_mtm:.2f}")
    print("=" * 65)

if __name__ == "__main__":
    main()