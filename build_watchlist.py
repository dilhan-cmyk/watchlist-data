import json
import yfinance as yf

TICKERS = ["MU", "SNDK", "TSM", "SMH", "ANET"]

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    return 100 - (100 / (1 + avg_gain / avg_loss))

def num(v):
    try:
        return round(float(v), 2)
    except (TypeError, ValueError):
        return 0.0

out = []
for sym in TICKERS:
    t = yf.Ticker(sym)
    daily = t.history(period="2y", interval="1d")["Close"]
    if len(daily) < 200:
        print(f"skipping {sym}, not enough history")
        continue

    weekly  = t.history(period="5y",  interval="1wk")["Close"]
    monthly = t.history(period="10y", interval="1mo")["Close"]

    price  = float(daily.iloc[-1])
    prev   = float(daily.iloc[-2])
    sma20  = float(daily.rolling(20).mean().iloc[-1])
    sma200 = float(daily.rolling(200).mean().iloc[-1])
    info   = t.info

    out.append({
        "sym":    sym,
        "price":  round(price, 2),
        "chg":    round((price / prev   - 1) * 100, 2),
        "sma20":  round((price / sma20  - 1) * 100, 2),
        "sma200": round((price / sma200 - 1) * 100, 2),
        "pe":     num(info.get("trailingPE")),
        "fpe":    num(info.get("forwardPE")),
        "peg":    num(info.get("trailingPegRatio")),
        "rsiD":   int(round(rsi(daily).iloc[-1])),
        "rsiW":   int(round(rsi(weekly).iloc[-1])),
        "rsiM":   int(round(rsi(monthly).iloc[-1])),
    })

with open("watchlist.json", "w") as f:
    json.dump({"stocks": out}, f, indent=2)

print(f"wrote {len(out)} tickers")
