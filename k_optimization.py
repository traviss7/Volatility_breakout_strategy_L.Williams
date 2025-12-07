import FinanceDataReader as fdr
import pandas as pd
import numpy as np

stocks = [
    {'code': '329180', 'name': 'HD현대중공업'},
    {'code': '006400', 'name': '삼성SDI'}
]

k_values = [0.3, 0.4, 0.5, 0.6, 0.7]

for stock in stocks:
    print(f"\n{'='*60}")
    print(f"{stock['name']} - K값 최적화")
    print('='*60)
    
    df = fdr.DataReader(stock['code'], '2005-01-01')
    
    for K in k_values:
        df_test = df.copy()
        df_test['MA20'] = df_test['Close'].rolling(20).mean()
        df_test['range'] = df_test['High'].shift(1) - df_test['Low'].shift(1)
        df_test['target'] = df_test['Open'] + df_test['range'] * K
        df_test['signal'] = (df_test['High'] >= df_test['target']) & (df_test['Close'] > df_test['MA20'])
        df_test['return'] = np.where(df_test['signal'], (df_test['Open'].shift(-1) - df_test['target']) / df_test['target'] - 0.0026, 0)
        df_test = df_test.dropna()
        
        trades = df_test['signal'].sum()
        win_rate = (df_test[df_test['signal']]['return'] > 0).sum() / trades * 100 if trades > 0 else 0
        cumulative = (1 + df_test['return']).cumprod().iloc[-1]
        years = (df_test.index[-1] - df_test.index[0]).days / 365.25
        cagr = (cumulative ** (1/years) - 1) * 100
        
        print(f"K={K}: 거래 {trades}회, 승률 {win_rate:.1f}%, CAGR {cagr:.1f}%")