import pandas as pd

df = pd.read_csv('backtest_results.csv')
good = df[(df['CAGR(%)'] >= 20) & (df['MDD(%)'] >= -20) & (df['승률(%)'] >= 50)]
print(good[['종목명', 'CAGR(%)', 'MDD(%)', '승률(%)']])