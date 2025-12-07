import pandas as pd

# K값 최적화 결과 로드
df = pd.read_csv('k_optimization_results.csv', encoding='utf-8-sig')

print("="*70)
print("종목별 K값 성과 일관성 분석")
print("="*70)

# 종목별로 그룹화
stocks = df['종목'].unique()

for stock in stocks:
    stock_data = df[df['종목'] == stock]
    
    print(f"\n{stock}:")
    print(stock_data[['K', '거래', '승률', 'CAGR']].to_string(index=False))
    
    # K=0.4, 0.5 비교
    k4 = stock_data[stock_data['K'] == 0.4]
    k5 = stock_data[stock_data['K'] == 0.5]
    
    if len(k4) > 0 and len(k5) > 0:
        cagr_diff = k4['CAGR'].values[0] - k5['CAGR'].values[0]
        trade_diff = k4['거래'].values[0] - k5['거래'].values[0]
        print(f"  → K 0.4→0.5: CAGR {cagr_diff:+.1f}%p, 거래 {trade_diff:+.0f}회")

# 종목별 최적 K값 (CAGR/거래횟수 비율)
print("\n" + "="*70)
print("종목별 효율성 (CAGR ÷ 거래횟수 × 100)")
print("="*70)

df['효율'] = (df['CAGR'] / df['거래'] * 100).round(2)

for stock in stocks:
    stock_data = df[df['종목'] == stock].sort_values('효율', ascending=False)
    best = stock_data.iloc[0]
    print(f"{stock}: K={best['K']} (효율 {best['효율']}, CAGR {best['CAGR']}%, 거래 {best['거래']}회)")
    