import yfinance as yf
import pandas as pd
import numpy as np

# 변동성 TOP 10
top10 = ['TSLA', 'AVGO', 'NVDA', 'META', 'NKE', 
         'TXN', 'AMZN', 'GOOGL', 'DHR', 'AAPL']

print("="*80)
print("래리 윌리엄스 원본 전략 - 미국 변동성 TOP 10")
print("="*80)

results = []

for symbol in top10:
    print(f"\n{symbol} 계산 중...")
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='10y')
        
        if len(df) < 100:
            print(f"  데이터 부족")
            continue
        
        # 원본 전략
        df['range'] = df['High'].shift(1) - df['Low'].shift(1)
        df['target'] = df['Open'] + df['range'] * 0.5
        df['signal'] = (df['High'] >= df['target'])
        
        # 안전장치
        df.loc[df['target'] <= 0, 'signal'] = False
        
        # 1일 보유
        df['buy_price'] = df['target'].where(df['signal'], None)
        df['sell_price'] = df['Open'].shift(-1)
        df['return'] = ((df['sell_price'] - df['buy_price']) / df['buy_price'] - 0.0036).where(df['signal'], 0)
        
        df['return'] = df['return'].replace([np.inf, -np.inf], 0).fillna(0)
        
        # 통계
        trades = df['signal'].sum()
        cum = (1 + df['return']).prod()
        years = len(df) / 252
        cagr = (cum ** (1/years) - 1) * 100
        
        df['cum'] = (1 + df['return']).cumprod()
        df['peak'] = df['cum'].cummax()
        df['dd'] = (df['cum'] - df['peak']) / df['peak'] * 100
        mdd = df['dd'].min()
        
        wins = (df[df['signal']]['return'] > 0).sum()
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
    print(f"\n평균: 거래 {df_result['거래'].mean():.0f}회, CAGR {df_result['CAGR'].mean():.1f}%, MDD {df_result['MDD'].mean():.1f}%")
    
    df_result.to_csv('us_original_results.csv', encoding='utf-8-sig', index=False)
    print("\n✅ 저장: us_original_results.csv")
else:
    print("결과 없음")