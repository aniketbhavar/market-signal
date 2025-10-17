import yfinance as yf
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# -----------------------------
# Corrected Ticker Symbols
# -----------------------------
INDICES = {
    "NIFTY_50": "^NSEI",
    "SENSEX": "^BSESN"
}

SECTORS = {
    "BANK_NIFTY": "^NSEBANK",
    "NIFTY_IT": "^CNXIT",
    "NIFTY_PHARMA": "^CNXPHARMA",
    "NIFTY_AUTO": "^CNXAUTO",
    "NIFTY_FMCG": "^CNXFMCG"
}

STOCKS = {
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "ITC": "ITC.NS",
    "SBIN": "SBIN.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS"
}

# -----------------------------
# Safe percentage function
# -----------------------------
def safe_pct_change(a, b):
    try:
        return round(((a - b) / b * 100), 2) if b else 0.0
    except Exception:
        return 0.0


# -----------------------------
# Fetch symbol data
# -----------------------------
def fetch_symbol_data(symbol, name):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    try:
        # auto_adjust=False ensures columns are standard
        df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False, progress=False)

        if df is None or df.empty:
            print(f"✗ {name}: No data for {symbol}")
            return None

        # Handle multi-index or multi-column DataFrame
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        if "Close" not in df.columns or "Volume" not in df.columns:
            print(f"✗ {name}: Missing Close/Volume columns")
            return None

        # Convert to lists safely
        closes = df["Close"].values.tolist()
        volumes = df["Volume"].values.tolist()

        if len(closes) < 7:
            print(f"✗ {name}: Insufficient data points")
            return None

        closes = closes[-60:]
        volumes = volumes[-60:]

        current = closes[-1]
        prev = closes[-2]
        week_ago = closes[-7]
        month_ago = closes[0]

        vol_current = int(volumes[-1])
        vol_avg = int(sum(volumes[-20:]) / len(volumes[-20:])) if len(volumes) >= 20 else vol_current
        vol_ratio = round(vol_current / vol_avg, 2) if vol_avg > 0 else 1.0

        high_52w = float(df["High"].max())
        low_52w = float(df["Low"].min())

        return {
            "symbol": symbol,
            "current_price": round(float(current), 2),
            "daily_change": safe_pct_change(current, prev),
            "weekly_change": safe_pct_change(current, week_ago),
            "monthly_change": safe_pct_change(current, month_ago),
            "volume": {
                "current": vol_current,
                "average_20d": vol_avg,
                "ratio": vol_ratio
            },
            "price_levels": {
                "high_52w": round(high_52w, 2),
                "low_52w": round(low_52w, 2),
                "distance_from_high": safe_pct_change(current, high_52w),
                "distance_from_low": safe_pct_change(current, low_52w)
            },
            "historical_closes": [round(float(x), 2) for x in closes],
            "sentiment": 0
        }

    except Exception as e:
        print(f"✗ {name}: {str(e)[:70]}")
        return None


# -----------------------------
# Main runner
# -----------------------------
def main():
    print("=" * 60)
    print("📊 FETCHING MARKET DATA VIA YFINANCE")
    print("=" * 60)

    market_data = {"indices": {}, "sectors": {}, "stocks": {}, "fetch_time": datetime.now().isoformat()}

    print("\n📈 Fetching Indices...")
    for name, symbol in tqdm(INDICES.items()):
        data = fetch_symbol_data(symbol, name)
        if data:
            market_data["indices"][name] = data
        time.sleep(0.5)

    print("\n🏦 Fetching Sectoral Indices...")
    for name, symbol in tqdm(SECTORS.items()):
        data = fetch_symbol_data(symbol, name)
        if data:
            market_data["sectors"][name] = data
        time.sleep(0.5)

    print("\n💹 Fetching Stocks...")
    for name, symbol in tqdm(STOCKS.items()):
        data = fetch_symbol_data(symbol, name)
        if data:
            market_data["stocks"][name] = data
        time.sleep(0.5)

    with open("market_data.json", "w") as f:
        json.dump(market_data, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ market_data.json saved successfully")
    print(f"  - Indices fetched: {len(market_data['indices'])}")
    print(f"  - Sectors fetched: {len(market_data['sectors'])}")
    print(f"  - Stocks fetched:  {len(market_data['stocks'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
