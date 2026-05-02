import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

# ==================================
# CONFIG
# ==================================
DATA_FILE = "nifty50_1hr_ohlcv_2y.csv"

BASE_CAPITAL = 50000
LEVERAGE = 5
TRADING_DAYS = 252

ALPHA_CUTOFF_TIME = dt.time(12,15)
EXIT_TIME = dt.time(15,15)

TP_RS = 90
SL_RS = 1
BROKERAGE = 0

LAMBDA = 0.5

# ==================================
# LOAD DATA
# ==================================
df = pd.read_csv(DATA_FILE,parse_dates=["Date"])
df = df.sort_values("Date")

if "Ticker" not in df.columns and "symbol" in df.columns:
    df["Ticker"] = df["symbol"].str.split(":").str[-1]

df["TradeDate"] = df["Date"].dt.date
df["Time"] = df["Date"].dt.time

for c in ["Open","High","Low","Close"]:
    df[c] = pd.to_numeric(df[c],errors="coerce")

df = df.dropna(subset=["Close","Ticker"])

# ==================================
# BUILD ALPHA SNAPSHOTS
# ==================================
snapshots = []

for d in df["TradeDate"].unique():

    day = df[df["TradeDate"]==d].sort_values("Date")

    entry = day[day["Time"]<=ALPHA_CUTOFF_TIME]
    exit_ = day[day["Time"]<=EXIT_TIME]

    if entry.empty or exit_.empty:
        continue

    open_px = day.groupby("Ticker").first()["Close"]
    entry_px = entry.groupby("Ticker").last()["Close"]
    exit_px = exit_.groupby("Ticker").last()["Close"]

    common = open_px.index.intersection(entry_px.index).intersection(exit_px.index)

    if len(common) < 10:
        continue

    ret = entry_px[common]/open_px[common] - 1

    snapshots.append(pd.DataFrame({
        "Date":pd.to_datetime(d),
        "Ticker":ret.index,
        "EntryPx":entry_px[ret.index].values,
        "ExitPx":exit_px[ret.index].values,
        "Alpha":ret.values
    }))

alpha_df = pd.concat(snapshots,ignore_index=True)

# ==================================
# BACKTEST ENGINE (NO COMPOUNDING)
# ==================================
equity = BASE_CAPITAL
equity_curve = []
equity_dates = []
daily_returns = []

# trade log
trades = []

for d,day in alpha_df.groupby("Date"):

    tickers = day["Ticker"].values

    trading_capital = BASE_CAPITAL

    intraday = (
        df[(df["TradeDate"]==d.date()) & (df["Time"]<=ALPHA_CUTOFF_TIME)]
        .pivot(index="Date",columns="Ticker",values="Close")
        .pct_change()
        .dropna()
    )

    if intraday.shape[0] < 2:
        continue

    corr = intraday.corr().fillna(0)

    J = corr.loc[tickers,tickers].values
    h = day["Alpha"].values

    # ==================================
    # HAMILTONIAN
    # ==================================
    H = LAMBDA*J - np.diag(h)

    vals,vecs = np.linalg.eigh(H)

    sigma = np.sign(vecs[:,0])
    sigma[sigma==0] = 1

    capital_per_trade = trading_capital/len(tickers)

    day_pnl = 0

    for i,r in enumerate(day.itertuples()):

        entry = r.EntryPx
        exitp = r.ExitPx
        ticker = r.Ticker

        side = sigma[i]

        qty = capital_per_trade/entry

        if side == 1:
            raw = exitp - entry
            side_name = "LONG"
        else:
            raw = -(entry - exitp)
            side_name = "SHORT"

        move = np.clip(raw,-SL_RS,TP_RS)

        pnl = (move * qty * LEVERAGE) - BROKERAGE

        day_pnl += pnl

        # save trade
        trades.append({
            "Date": d,
            "Ticker": ticker,
            "Side": side_name,
            "EntryPrice": entry,
            "ExitPrice": exitp,
            "Quantity": qty,
            "PnL": pnl
        })

    equity += day_pnl

    daily_returns.append(day_pnl/BASE_CAPITAL)

    equity_curve.append(equity)
    equity_dates.append(d)

# ==================================
# SAVE TRADES CSV
# ==================================
trades_df = pd.DataFrame(trades)

trades_df.to_csv("ising_hamiltonian_trades.csv",index=False)

print("Trades saved to ising_hamiltonian_trades.csv")

# ==================================
# METRICS
# ==================================
equity_series = pd.Series(equity_curve,index=pd.to_datetime(equity_dates))
returns = pd.Series(daily_returns,index=pd.to_datetime(equity_dates))

mean_ret = returns.mean()
vol = returns.std()

sharpe = (mean_ret/vol)*np.sqrt(TRADING_DAYS)
total_return = equity_series.iloc[-1]/BASE_CAPITAL - 1

ann_return = (1+returns.mean())**TRADING_DAYS - 1
ann_vol = returns.std()*np.sqrt(TRADING_DAYS)

drawdown = equity_series/equity_series.cummax()-1

print("\n===== BACKTEST RESULTS =====")

print(f"Base Capital  : ₹{BASE_CAPITAL:,.0f}")
print(f"Final Equity  : ₹{equity_series.iloc[-1]:,.2f}")
print(f"Total Return  : {total_return*100:.2f}%")
print(f"Annual Return : {ann_return*100:.2f}%")
print(f"Annual Vol    : {ann_vol*100:.2f}%")
print(f"Sharpe        : {sharpe:.2f}")
print(f"Max Drawdown  : {drawdown.min()*100:.2f}%")

# ==================================
# PLOT
# ==================================
equity_plot = equity_series[equity_series.index<=pd.Timestamp("2025-11-30")]

plt.figure(figsize=(13,5))
plt.plot(equity_plot.index,equity_plot.values,linewidth=2)

plt.title("Ising Hamiltonian Intraday Portfolio")

plt.ylabel("Equity")

plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
