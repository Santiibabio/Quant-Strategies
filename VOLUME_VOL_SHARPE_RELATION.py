import pandas as pd
import numpy as np
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go

tickers = ['MU', 'NVDA', 'AMD', 'INTC', 'BA', 'JPM', 'GS', 'SQM']
data = yf.download(tickers, start="2015-01-01", end='2026-06-17', auto_adjust=True)

results = {}

for ticker in tickers:
    returns = data["Close"][ticker].pct_change(fill_method=None).dropna()
    rolling_vol = returns.rolling(window=20).std()
    rolling_mean = returns.rolling(window=20).mean()
    rolling_sharpe = (rolling_mean / rolling_vol) * np.sqrt(252)

    # correlation
    correlation = np.corrcoef(data["Volume"][ticker].values[20:], rolling_vol.dropna().values)[0,1]

    # asymmetry
    vol_change = rolling_vol.diff().dropna()
    rolling_vol_clean = rolling_vol.dropna()[1:]
    volume_clean = data["Volume"][ticker].values[21:]
    rising_mask = (vol_change > 0).values
    falling_mask = (vol_change < 0).values
    corr_rising = np.corrcoef(volume_clean[rising_mask], rolling_vol_clean.values[rising_mask])[0,1]
    corr_falling = np.corrcoef(volume_clean[falling_mask], rolling_vol_clean.values[falling_mask])[0,1]

    # signal
    vol_signal = rolling_vol > rolling_vol.rolling(20).mean()
    volume_ma = data["Volume"][ticker].rolling(20).mean()
    volume_signal = data["Volume"][ticker] > volume_ma
    combined_signal = vol_signal & volume_signal
    signal_dates = combined_signal[combined_signal == True].index

    # forward returns — 5, 10, 20 days
    fwd_5, fwd_10, fwd_20 = [], [], []
    for date in signal_dates:
        try:
            cp = data["Close"][ticker].loc[date]
            fwd_5.append((data["Close"][ticker].loc[date:].iloc[5] - cp) / cp)
            fwd_10.append((data["Close"][ticker].loc[date:].iloc[10] - cp) / cp)
            fwd_20.append((data["Close"][ticker].loc[date:].iloc[20] - cp) / cp)
        except:
            pass

    results[ticker] = {
        "correlation": correlation,
        "corr_rising": corr_rising,
        "corr_falling": corr_falling,
        "signals": len(signal_dates),
        "fwd_5": np.mean(fwd_5),
        "fwd_10": np.mean(fwd_10),
        "fwd_20": np.mean(fwd_20),
        "wr_5": np.mean(np.array(fwd_5) > 0),
        "wr_10": np.mean(np.array(fwd_10) > 0),
        "wr_20": np.mean(np.array(fwd_20) > 0),
    }

    # chart
    fig = make_subplots(rows=2, cols=1,
                        specs=[[{"secondary_y": True}], [{}]],
                        subplot_titles=(f"{ticker} — Volume vs Sharpe", "Rolling Volatility"),
                        shared_xaxes=True)

    fig.add_trace(go.Bar(x=data.index, y=data["Volume"][ticker],
                         name="Volume", marker_color='red'),
                  row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=returns.index, y=rolling_sharpe,
                             name="Sharpe", line=dict(color="green")),
                  row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(x=returns.index, y=rolling_vol,
                             name="Volatility", line=dict(color="blue")),
                  row=2, col=1)
    fig.update_layout(title=f"{ticker} — Volume, Sharpe & Volatility")
    fig.show()

# print summary
print("\n=== BACKTEST SUMMARY ===\n")
for ticker, r in results.items():
    print(f"{ticker}:")
    print(f"  Correlation (overall):        {r['correlation']:.3f}")
    print(f"  Correlation (vol rising):     {r['corr_rising']:.3f}")
    print(f"  Correlation (vol falling):    {r['corr_falling']:.3f}")
    print(f"  Signal count:                 {r['signals']}")
    print(f"  5-day  return / win rate:     {r['fwd_5']:.3%} / {r['wr_5']:.1%}")
    print(f"  10-day return / win rate:     {r['fwd_10']:.3%} / {r['wr_10']:.1%}")
    print(f"  20-day return / win rate:     {r['fwd_20']:.3%} / {r['wr_20']:.1%}")
    print()