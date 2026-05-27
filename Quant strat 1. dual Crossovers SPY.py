import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Download historical data for S&P500 (2018 to 2026)
data = yf.download("SPY", start="2018-01-01", end="2026-05-26", auto_adjust=True)

# Look at the first few rows to confirm it worked
print(data.head())
print(data.tail())
print(len(data), "days of data")
# Calculate the two moving averages
data["SMA_50"] = data["Close"].rolling(window=50).mean()
data["SMA_200"] = data["Close"].rolling(window=200).mean()

# Preview to confirm they appear
print(data[["Close", "SMA_50", "SMA_200"]].tail(10))

# Generate buy/sell signals
data["Signal"] = 0
data.loc[data["SMA_50"] > data["SMA_200"], "Signal"] = 1   # Buy
data.loc[data["SMA_50"] < data["SMA_200"], "Signal"] = -1  # Sell

# See the signals
print(data[["Close", "SMA_50", "SMA_200", "Signal"]].tail(10))
# Calculate daily returns
data["Market_Return"] = data["Close"].pct_change()
data["Strategy_Return"] = data["Market_Return"] * data["Signal"].shift(1)

# Calculate cumulative returns
data["Cumulative_Market"] = (1 + data["Market_Return"]).cumprod()
data["Cumulative_Strategy"] = (1 + data["Strategy_Return"]).cumprod()

# Print performance summary
print("=== STRATEGY PERFORMANCE ===")
print(f"Market Return:   {(data['Cumulative_Market'].iloc[-1] - 1) * 100:.2f}%")
print(f"Strategy Return: {(data['Cumulative_Strategy'].iloc[-1] - 1) * 100:.2f}%")

# Plot the results
plt.figure(figsize=(12, 6))
plt.plot(data["Cumulative_Market"], label="Buy & Hold SPY", color="blue")
plt.plot(data["Cumulative_Strategy"], label="MA Crossover Strategy", color="green")
plt.title("MA Crossover Strategy vs Buy & Hold — SPY (2018-2026)")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.grid(True)
plt.show()
import numpy as np

# Sharpe Ratio
sharpe = (data["Strategy_Return"].mean() / data["Strategy_Return"].std()) * np.sqrt(252)

# Volatility (annualised)
volatility = data["Strategy_Return"].std() * np.sqrt(252)

# Max Drawdown
cumulative = data["Cumulative_Strategy"]
rolling_max = cumulative.cummax()
drawdown = (cumulative - rolling_max) / rolling_max
max_drawdown = drawdown.min()

print("=== STRATEGY PERFORMANCE ===")
print(f"Sharpe Ratio:  {sharpe:.2f}")
print(f"Volatility:    {volatility * 100:.2f}%")
print(f"Max Drawdown:  {max_drawdown * 100:.2f}%")