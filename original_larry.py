import FinanceDataReader as fdr
import pandas as pd
import numpy as np

stocks = [
    {'name': '네이버', 'code': '035420'},
    {'name': '셀트리온', 'code': '068270'},
    {'name': '삼성전자', 'code': '005930'},
    {'name': 'SK하이닉스', 'code': '000660'}
]

print("="*80)
print("래리 윌리엄스 원본 전략 (필터 없음, 1일 보유)")
print("="*80)

results = []

for stock in stocks:
    print(f"\n{stock['name']} 계산 중...")
    
    df = fdr.DataReader(stock['code'], '2005-01-01')
    
    # 원본 전략
    df['range'] = df['High'].shift(1) - df['Low'].shift(1)
    df['target'] = df['Open'] + df['range'] * 0.5
    df['signal'] = (df['High'] >= df['target'])
    
    # 안전장치: target <= 0 제거
    df.loc[df['target'] <= 0, 'signal'] = False
    
    # 1일 보유 (다음날 시가 매도)
    df['buy_price'] = np.where(df['signal'], df['target'], np.nan)
    df['sell_price'] = df['Open'].shift(-1)
    df['return'] = np.where(df['signal'], (df['sell_price'] - df['buy_price']) / df['buy_price'] - 0.0036, 0)
    
    # 이상치 제거
    df['return'] = df['return'].replace([np.inf, -np.inf], 0)
    df = df.dropna()
    
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
        '종목': stock['name'],
        '거래': trades,
        '승률': round(win_rate, 1),
        'CAGR': round(cagr, 1),
        'MDD': round(mdd, 1)
    })
    
    print(f"  거래: {trades}회, 승률: {win_rate:.1f}%, CAGR: {cagr:.1f}%, MDD: {mdd:.1f}%")

print("\n" + "="*80)
print("요약")
print("="*80)

df_result = pd.DataFrame(results)
print(df_result.to_string(index=False))

print(f"\n평균: CAGR {df_result['CAGR'].mean():.1f}%, MDD {df_result['MDD'].mean():.1f}%")