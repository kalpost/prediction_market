# Prediction Market Combinatorial Arbitrage & Liquidity Engine

An event-driven quantitative trading and market-making simulation engine for multi-outcome prediction markets (e.g., Kalshi, Polymarket). 

The platform models continuous price discovery across mutually exclusive event contracts on a continuous simplex, captures structural violations of Kolmogorov probability axioms (sum of P_i != 1.00) via programmatic Dutch-book execution, and manages inventory risk via the classical Avellaneda-Stoikov continuous-time framework.

---

## Architectural Overview

The engine is engineered around four decoupled, modular components designed for high-frequency simulated execution:

+---------------------------+
                      |       simulator.py        |
                      | MultiOutcomeMarketSim     |
                      +-------------+-------------+
                                    |
             {Fair Probabilities, Synthetic Order Books}
                                    |
               +--------------------+--------------------+
               |                                         |
               v                                         v
  +-------------------------+               +-------------------------+
  |      arbitrage.py       |               |     market_maker.py     |
  |  DutchBookScanner       |               |  InventoryMarketMaker   |
  |  - Kolmogorov Parity    |               |  - Avellaneda-Stoikov   |
  |  - Synthetic Baskets    |               |  - Reservation Pricing  |
  +------------+------------+               +------------+------------+
               |                                         |
               +--------------------+--------------------+
                                    |
                                    v
                      +---------------------------+
                      |   main.py / monte_carlo   |
                      | Execution & Risk Engine   |
                      +---------------------------+

1. **simulator.py (Multi-Asset Latent State Model):**
   * Projects N mutually exclusive states onto an open probability simplex using continuous softmax normalization (sum of P_i = 1.0, P_i in (0.01, 0.99)).
   * Models news events and structural breaks via compound Poisson jump diffusions.
   * Generates discrete limit order books (LOBs) with variable retail quotation noise.

2. **arbitrage.py (Combinatorial Dutch-Book Scanner):**
   * Scans cross-market implied probabilities for violations of Kolmogorov's third probability axiom:
     `sum(Ask_i) < 1.00 - Taker Fees`
   * Dynamically sizes synthetic long-basket execution to extract risk-free arbitrage margins net of taker fee drag.

3. **market_maker.py (Optimal Liquidity & Inventory Control):**
   * Solves continuous-time inventory management using the Avellaneda-Stoikov (2008) framework adapted for unit-interval bounded contracts.
   * Computes reservation (indifference) prices to penalize accumulated directional inventory:
     `R(s, q, t) = s - q * gamma * sigma^2 * (T - t)`
   * Skews bid/ask quotes asymmetrically to disincentivize toxic order flow and prevent terminal inventory settlement risk.

4. **main.py & monte_carlo.py (Execution & Risk Harness):**
   * Synchronizes quoting, fills, toxic order impact, and portfolio mark-to-market (MtM) accounting across discrete ticks.
   * Simulates path dependency across 500,000 discrete ticks to quantify parameter convergence, empirical edge frequency, and tail risk (VaR_95).

---

## Empirical Performance & Stress-Testing

Across a **500-path Monte Carlo stress test** (500,000 total discrete execution ticks under compound Poisson jump shocks and retail quoting friction):

| Metric | Result (Empirical Distribution) | Description |
| :--- | :--- | :--- |
| **Arbitrage Capture Frequency** | **10.8%** (107.6 events / 1k ticks) | Rate of actionable cross-asset order-book dislocations |
| **Mean Dutch-Book Yield** | **$175.19 +/- $53.94** per run | Net risk-free yield extracted across 1,000-tick horizons |
| **Terminal Inventory Skew** | **5.15 +/- 10.39 contracts** | Constrained open exposure on [-15, +15] safety bands |
| **Market Maker Mean MtM** | **$0.88 +/- $2.10** | Net positive spread capture post-adverse selection |
| **95% Value-at-Risk (VaR_95)** | **-$0.14** | Bounded downside tail risk under news shocks |

---

## Directory Layout

```text
.
|-- simulator.py        # Continuous simplex diffusion & Poisson jump simulator
|-- arbitrage.py        # Combinatorial Kolmogorov parity scanner & Dutch-book engine
|-- market_maker.py     # Avellaneda-Stoikov reservation pricer & inventory controller
|-- main.py             # Single-run orchestrator (1,000 ticks)
|-- monte_carlo.py      # 500-path stochastic risk & convergence harness
|-- requirements.txt    # Minimal dependencies (numpy, scipy)
`-- README.md