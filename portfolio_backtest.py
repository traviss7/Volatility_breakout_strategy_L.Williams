import FinanceDataReader as fdr
import pandas as pd
import numpy as np

# 효율 TOP 4
portfolio = [
    {'name': 'HD현대중공업', 'code': '329180', 'K': 0.3},
    {'name': '알테오젠', 'code': '196170', 'K': 0.6},
    {'name': '두산에너빌리티', 'code': '034020', 'K': 0.3},
    {'name': 'HD현대일렉트릭', 'code': '267260', 'K': 0.5}
]

print("="*70)
print("포트폴리오 백테스트 (4종목 균등 분산, 각 25%)")
print("="*70)

all_returns = []

for stock in portfolio:
    print(f"\n{stock['name']} (K={stock['K']}) 계산 중...")
    
    df = fdr.DataReader(stock['code'], '2005-01-01')
    
    df['MA20'] = df['Close'].rolling(20).mean()
    df['range'] = df['High'].shift(1) - df['Low'].shift(1)
    df['target'] = df['Open'] + df['range'] * stock['K']
    df['signal'] = (df['High'] >= df['target']) & (df['Close'] > df['MA20'])
    df['return'] = np.where(df['signal'], (df['Open'].shift(-1) - df['target']) / df['target'] - 0.0036, 0)
    
    df.loc[df['target'] <= 0, 'return'] = 0
    df['return'] = df['return'].replace([np.inf, -np.inf], 0)
    
    all_returns.append(df[['return']].rename(columns={'return': stock['name']}))

# 날짜 맞춰서 합치기
df_portfolio = all_returns[0]
for i in range(1, len(all_returns)):
    df_portfolio = df_portfolio.join(all_returns[i], how='outer')

df_portfolio = df_portfolio.fillna(0)

# 포트폴리오 수익률 (균등 분산)
df_portfolio['portfolio'] = df_portfolio.mean(axis=1)
df_portfolio['cumulative'] = (1 + df_portfolio['portfolio']).cumprod()

# 통계
years = len(df_portfolio) / 252
final = df_portfolio['cumulative'].iloc[-1]
cagr = (final ** (1/years) - 1) * 100
total_return = (final - 1) * 100

df_portfolio['peak'] = df_portfolio['cumulative'].cummax()
df_portfolio['dd'] = (df_portfolio['cumulative'] - df_portfolio['peak']) / df_portfolio['peak'] * 100
mdd = df_portfolio['dd'].min()

print("\n" + "="*70)
print("포트폴리오 결과")
print("="*70)
print(f"총 수익률: {total_return:.1f}%")
print(f"CAGR: {cagr:.1f}%")
print(f"MDD: {mdd:.1f}%")
print(f"최종 자본 (1천만원 시작): {final*10000000:,.0f}원")