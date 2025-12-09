import FinanceDataReader as fdr
import pandas as pd
import numpy as np

portfolio = [
    {'name': '네이버', 'code': '035420', 'weight': 0.35},
    {'name': '셀트리온', 'code': '068270', 'weight': 0.35},
    {'name': '알테오젠', 'code': '196170', 'weight': 0.15},
    {'name': '두산에너빌리티', 'code': '034020', 'weight': 0.15}
]

print("="*80)
print("필터 없음 vs 20일선 필터 비교")
print("="*80)

for test_name in ['필터없음', '20일선필터', '7:3필터없음', '7:3_20일선']:
    print(f"\n{test_name} 계산 중...")
    
    if '7:3' in test_name:
        # 7:3 포트폴리오
        all_returns = []
        
        for stock in portfolio:
            df = fdr.DataReader(stock['code'], '2005-01-01')
            df['MA20'] = df['Close'].rolling(20).mean()
            df['range'] = df['High'].shift(1) - df['Low'].shift(1)
            df['target'] = df['Open'] + df['range'] * 0.5
            
            if '필터없음' in test_name:
                df['signal'] = (df['High'] >= df['target'])
            else:
                df['signal'] = (df['High'] >= df['target']) & (df['Close'].shift(1) > df['MA20'].shift(1))
            
            # 2일 보유
            df['return'] = 0.0
            i = 0
            while i < len(df)-2:
                if df['signal'].iloc[i]:
                    if i+1 < len(df) and df['Close'].iloc[i+1] > df['MA20'].iloc[i+1]:
                        ret = (df['Open'].iloc[i+2] - df['target'].iloc[i]) / df['target'].iloc[i] - 0.0036
                        df.loc[df.index[i], 'return'] = ret
                        i += 2
                    else:
                        ret = (df['Open'].iloc[i+1] - df['target'].iloc[i]) / df['target'].iloc[i] - 0.0036
                        df.loc[df.index[i], 'return'] = ret
                        i += 1
                else:
                    i += 1
            
            df['weighted'] = df['return'] * stock['weight']
            all_returns.append(df[['weighted']].rename(columns={'weighted': stock['name']}))
        
        df_port = all_returns[0]
        for i in range(1, len(all_returns)):
            df_port = df_port.join(all_returns[i], how='outer')
        
        df_port = df_port.fillna(0)
        df_port['total'] = df_port.sum(axis=1)
        
    else:
        # 균등 (네이버만 테스트)
        df = fdr.DataReader('035420', '2005-01-01')
        df['MA20'] = df['Close'].rolling(20).mean()
        df['range'] = df['High'].shift(1) - df['Low'].shift(1)
        df['target'] = df['Open'] + df['range'] * 0.5
        
        if '필터없음' in test_name:
            df['signal'] = (df['High'] >= df['target'])
        else:
            df['signal'] = (df['High'] >= df['target']) & (df['Close'].shift(1) > df['MA20'].shift(1))
        
        df['return'] = 0.0
        i = 0
        while i < len(df)-2:
            if df['signal'].iloc[i]:
                if i+1 < len(df) and df['Close'].iloc[i+1] > df['MA20'].iloc[i+1]:
                    ret = (df['Open'].iloc[i+2] - df['target'].iloc[i]) / df['target'].iloc[i] - 0.0036
                    df.loc[df.index[i], 'return'] = ret
                    i += 2
                else:
                    ret = (df['Open'].iloc[i+1] - df['target'].iloc[i]) / df['target'].iloc[i] - 0.0036
                    df.loc[df.index[i], 'return'] = ret
                    i += 1
            else:
                i += 1
        
        df_port = df[['return']].rename(columns={'return': 'total'})
    
    # 통계
    cum = (1 + df_port['total']).prod()
    years = len(df_port) / 252
    cagr = (cum ** (1/years) - 1) * 100
    
    df_port['cum'] = (1 + df_port['total']).cumprod()
    df_port['peak'] = df_port['cum'].cummax()
    df_port['dd'] = (df_port['cum'] - df_port['peak']) / df_port['peak'] * 100
    mdd = df_port['dd'].min()
    
    trades = (df_port['total'] != 0).sum()
    
    print(f"  CAGR: {cagr:.1f}%, MDD: {mdd:.1f}%, 거래: {trades}회")

print("\n완료!")