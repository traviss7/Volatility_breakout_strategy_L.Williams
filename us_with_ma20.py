import yfinance as yf
import pandas as pd
import numpy as np

top10 = ['TSLA', 'AVGO', 'NVDA', 'META', 'NKE', 
         'TXN', 'AMZN', 'GOOGL', 'DHR', 'AAPL']

print("="*80)
print("미국 TOP 10 + 20일선 필터 (2일 보유)")
print("="*80)

results = []

for symbol in top10:
    print(f"\n{symbol} 계산 중...")
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='10y')
        
        if len(df) < 100:
            continue
        
        # 20일선 필터 전략
        df['MA20'] = df['Close'].rolling(20).mean()
        df['range'] = df['High'].shift(1) - df['Low'].shift(1)
        df['target'] = df['Open'] + df['range'] * 0.5
        df['signal'] = (df['High'] >= df['target']) & (df['Close'].shift(1) > df['MA20'].shift(1))
        
        df.loc[df['target'] <= 0, 'signal'] = False
        
        # 2일 보유
        df['return'] = 0.0
        i = 0
        while i < len(df)-2:
            if df['signal'].iloc[i]:
                if df['Close'].iloc[i+1] > df['MA20'].iloc[i+1]:
                    ret = (df['Open'].iloc[i+2] - df['target'].iloc[i]) / df['target'].iloc[i] - 0.0036
                    df.loc[df.index[i], 'return'] = ret
                    i += 2
                else:
                    ret = (df['Open'].iloc[i+1] - df['target'].iloc[i]) / df['target'].iloc[i] - 0.0036
                    df.loc[df.index[i], 'return'] = ret
                    i += 1
            else:
                i += 1
        
        # 통계
        trades = (df['return'] != 0).sum()
        cum = (1 + df['return']).prod()
        years = len(df) / 252
        cagr = (cum ** (1/years) - 1) * 100
        
        df['cum'] = (1 + df['return']).cumprod()
        df['peak'] = df['cum'].cummax()
        df['dd'] = (df['cum'] - df['peak']) / df['peak'] * 100
        mdd = df['dd'].min()
        
        wins = (df[df['return'] != 0]['return'] > 0).sum()
        win_rate = wins / trades * 100 if trades > 0 else 0
        
        results.append({
            'Symbol': symbol,
            '거래': int(trades),
            '승률': round(win_rate, 1),
            'CAGR': round(cagr, 1),
            'MDD': round(mdd, 1)
        })
        
        print(f"  거래: {trades}회, 승률: {win_rate:.1f}%, CAGR: {cagr:.1f}%, MDD: {mdd:.1f}%")
        
    except Exception as e:
        print(f"  오류: {str(e)[:50]}")

print("\n" + "="*80)
print("요약")
print("="*80)

if len(results) > 0:
    df_result = pd.DataFrame(results)
    print(df_result.to_string(index=False))
    print(f"\n평균: CAGR {df_result['CAGR'].mean():.1f}%, MDD {df_result['MDD'].mean():.1f}%")
    
    df_result.to_csv('us_ma20_results.csv', encoding='utf-8-sig', index=False)
    print("\n✅ 저장: us_ma20_results.csv")