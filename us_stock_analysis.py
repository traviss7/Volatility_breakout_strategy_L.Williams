import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*80)
print("미국 주식 변동성 분석")
print("="*80)

# 미국 주요 종목
us_stocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
    'TSLA', 'META', 'BRK-B', 'V', 'JNJ',
    'WMT', 'JPM', 'MA', 'PG', 'XOM',
    'HD', 'CVX', 'MRK', 'PFE', 'KO',
    'PEP', 'ABBV', 'COST', 'AVGO', 'TMO',
    'CSCO', 'ACN', 'NKE', 'DHR', 'TXN'
]

results = []
end_date = datetime.now()

for idx, symbol in enumerate(us_stocks):
    print(f"분석 중: {symbol} ({idx+1}/30)", end='\r')
    
    try:
        # 10년 데이터
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='10y')
        
        if len(df) < 1000:
            continue
        
        # 변동성 계산
        vol_data = {'Symbol': symbol}
        
        for period, days in [('1년', 365), ('3년', 1095), ('10년', 3650)]:
            df_period = df.tail(int(days * 252 / 365))  # 거래일 기준으로 변경
            if len(df_period) < 100:
                continue
            vol = df_period['Close'].pct_change().std() * np.sqrt(252) * 100
            vol_data[period] = round(vol, 2)
        
        if '1년' in vol_data and '3년' in vol_data:
            vol_data['평균'] = round((vol_data['1년'] + vol_data['3년']) / 2, 2)
            results.append(vol_data)
            
    except Exception as e:
        print(f"\n{symbol} 오류: {str(e)[:30]}")
        continue

print("\n\n변동성 TOP 15:")
if len(results) > 0:
    df_vol = pd.DataFrame(results).sort_values('평균', ascending=False)
    print(df_vol.head(15).to_string(index=False))
    df_vol.to_csv('us_volatility_ranking.csv', encoding='utf-8-sig', index=False)
    print("\n✅ 저장: us_volatility_ranking.csv")