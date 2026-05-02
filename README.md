# portfolio-optimization-using-Ising-model-model
# Ising Portfolio Optimization

A research-style Python repository for **portfolio optimization using an Ising model**, with a practical bridge from correlation-based interaction matrices to Hamiltonian minimization and trade simulation.

This repo is designed from the intraday portfolio script you shared and restructures it into a cleaner, reusable project suitable for GitHub.

## Overview

The project uses:
- intraday OHLCV data,
- an **alpha vector** derived from morning price action,
- a correlation matrix across assets,
- an Ising-style Hamiltonian of the form:

$$
H = \lambda J - \mathrm{diag}(h)
$$

where:
- `J` is the interaction matrix derived from intraday correlations,
- `h` is the asset-wise alpha term,
- `lambda` controls the trade-off between diversification/correlation penalty and alpha preference.

The ground-state sign structure of the lowest-eigenvector is used to assign long/short directions.

## Features

- Clean project structure for research and experimentation
- Config-driven backtests
- Intraday alpha snapshot construction
- Ising Hamiltonian signal generation
- Long/short portfolio simulation with stop-loss / take-profit clipping
- Trade log export
- Equity curve and performance metrics
- Ready for extension to QUBO / quantum optimization workflows

## Repository structure

```text
ising-portfolio-optimization/
├── src/ising_portfolio_opt/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── alpha.py
│   ├── hamiltonian.py
│   ├── backtest.py
│   ├── metrics.py
│   └── plots.py
├── examples/
│   └── run_backtest.py
├── tests/
│   └── test_hamiltonian.py
├── notebooks/
│   └── research_notes.md
├── data/
│   └── .gitkeep
├── .github/workflows/
│   └── python-ci.yml
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Installation

```bash
git clone https://github.com/your-username/ising-portfolio-optimization.git
cd ising-portfolio-optimization
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Input data format

The backtest expects an hourly or intraday CSV with columns similar to:

- `Date`
- `Ticker` or `symbol`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume` (optional)

If `symbol` is present instead of `Ticker`, the loader extracts the ticker from strings such as `NSE:RELIANCE`.

## Quick start

Place your dataset in `data/nifty50_1hr_ohlcv_2y.csv`, then run:

```bash
python examples/run_backtest.py
```

## Method

1. For each trading day, compute each asset's open-to-cutoff return.
2. Use those returns as the **alpha field**.
3. Build an intraday correlation matrix from returns observed up to the cutoff time.
4. Form an Ising-inspired Hamiltonian combining correlation interactions and alpha.
5. Solve the lowest-eigenvalue mode and convert its sign pattern into long/short positions.
6. Execute positions from entry snapshot to exit snapshot.
7. Record PnL, equity curve, Sharpe, annualized return, annualized volatility, and drawdown.

## Why Ising?

In quantum and combinatorial finance literature, portfolio allocation can be mapped to Ising/QUBO formulations so that binary decisions encode inclusion, exclusion, or directional exposure. Quantum-portfolio examples commonly frame the optimization step by converting covariance information into an Ising problem and minimizing the resulting Hamiltonian.[1]

This repository keeps the implementation fully classical while preserving that Ising-style formulation, which makes it useful for:
- classical baseline experiments,
- quantum-inspired optimization,
- future QAOA/VQE comparisons,
- research demos and academic portfolios.

## Suggested future improvements

- Replace eigenvector-sign heuristic with explicit binary optimization
- Add transaction costs, slippage, and borrow costs
- Add walk-forward validation
- Support sector constraints and position limits
- Compare against Markowitz baseline and equal-weight baseline
- Add QUBO export for quantum solvers
- Add hyperparameter sweeps for `lambda`, TP, and SL

## Example GitHub topics

`portfolio-optimization`, `ising-model`, `quant-finance`, `algorithmic-trading`, `backtesting`, `quantum-finance`, `qubo`, `python`

## References

Quantum portfolio optimization examples frequently describe transforming covariance information into an Ising problem and minimizing the Hamiltonian with variational methods, which closely matches the conceptual framing used here.[1]

General portfolio-optimization repositories on GitHub commonly organize code into `data`, `notebooks`, `scripts/src`, and a README-driven workflow, which informed this repo structure.[2][3]
