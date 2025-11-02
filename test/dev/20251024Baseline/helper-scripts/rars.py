from polygon import RESTClient
import pandas as pd
import numpy as np

# Paste the tickers list here
tickers = [...]  # from earlier extraction
client = RESTClient(api_key='your_key')  # Replace with your key
results = []
for ticker in set(tickers):
    try:
        aggs = client.get_aggs(ticker, 1, "day", "2020-10-24", "2025-10-24", adjusted=True)
        if len(aggs) < 1000: continue
        df = pd.DataFrame([agg.__dict__ for agg in aggs])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')
        first_close = df['close'].iloc[0]
        last_close = df['close'].iloc[-1]
        ann_return = ((last_close / first_close) ** (1/5) - 1) * 100
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        daily_ret = df['log_ret'].dropna()
        rf_daily = 0.03 / 252
        excess_mean = daily_ret.mean() - rf_daily
        vol = daily_ret.std()
        sharpe = excess_mean / vol * np.sqrt(252) if vol > 0 else np.nan
        aggs52 = client.get_aggs(ticker, 1, "day", "2024-10-24", "2025-10-24", adjusted=True)
        if len(aggs52) == 0: continue
        df52 = pd.DataFrame([agg.__dict__ for agg in aggs52])
        df52['timestamp'] = pd.to_datetime(df52['timestamp'], unit='ms')
        df52 = df52.sort_values('timestamp')
        max_high = df52['high'].max()
        current_close = df52['close'].iloc[-1]
        pct_from_high = ((current_close / max_high) - 1) * 100
        results.append({'Ticker': ticker, 'Ann_Total_Return_%': round(ann_return, 2), 'Sharpe_Ratio': round(sharpe, 2), '%_from_52w_High': round(pct_from_high, 2)})
    except: continue
df_res = pd.DataFrame(results).sort_values('Ticker')
print(df_res.to_csv(index=False))