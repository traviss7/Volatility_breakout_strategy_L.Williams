import FinanceDataReader as fdr
import pandas as pd
import numpy as np

print("K값 최적화 테스트 시작")

# TOP 10 종목
df_vol = pd.read_csv('volatility_ranking.csv', encoding='utf-8-sig')
print(f"변동성 데이터 로드: {len(df_vol)}개")
print(df_vol.columns)
top10 = df_vol.head(10)

k_values = [0.3, 0.4, 0.5, 0.6, 0.7]
all_results = []

for idx in range(len(top10)):
    stock = top10.iloc[idx]
    code = str(stock['Code']).zfill(6)  # 종목코드 6자리로
    name = str(stock['Name'])
    print(f"\n{'='*60}")
    print(f"{name} 분석 중...")
    
    try:
        df = fdr.DataReader(code, '2005-01-01')
        
        if len(df) < 100:
            print(f"  데이터 부족 (스킵)")
            continue
        
        for K in k_values:
            # 전략 계산
            df_test = df.copy()
            df_test['MA20'] = df_test['Close'].rolling(20).mean()
            df_test['prev_high'] = df_test['High'].shift(1)
            df_test['prev_low'] = df_test['Low'].shift(1)
            df_test['range'] = df_test['prev_high'] - df_test['prev_low']
            df_test['target'] = df_test['Open'] + df_test['range'] * K
            df_test['signal'] = (df_test['High'] >= df_test['target']) & (df_test['Close'] > df_test['MA20'])
            
            df_test['buy_price'] = np.where(df_test['signal'], df_test['target'], np.nan)
            df_test['sell_price'] = df_test['Open'].shift(-1)
            # 기존: 수수료+거래세 0.26%
            # 추가: 슬리피지 0.1%
            # 총: 0.36%
            df_test['return'] = np.where(df_test['signal'], (df_test['sell_price'] - df_test['buy_price']) / df_test['buy_price'] - 0.0036, 0)
            
            df_test.loc[df_test['buy_price'] <= 0, 'return'] = 0
            df_test['return'] = df_test['return'].replace([np.inf, -np.inf], 0)
            df_test = df_test.dropna()
            
            # 통계
            trades = int(df_test['signal'].sum())
            
            if trades == 0:
                continue
            
            wins = int((df_test[df_test['signal']]['return'] > 0).sum())
            win_rate = (wins / trades * 100)
            
            cumulative = (1 + df_test['return']).cumprod().iloc[-1]
            years = (df_test.index[-1] - df_test.index[0]).days / 365.25
            cagr = (cumulative ** (1/years) - 1) * 100
            
            print(f"  K={K}: 거래 {trades}회, 승률 {win_rate:.1f}%, CAGR {cagr:.1f}%")
            
            all_results.append({
                '종목': name,
                'K': K,
                '거래': trades,
                '승률': round(win_rate, 1),
                'CAGR': round(cagr, 1)
            })
            
    except Exception as e:
        print(f"  오류: {str(e)[:60]}")
        continue

# 결과 저장
if len(all_results) > 0:
    df_results = pd.DataFrame(all_results)
    df_results.to_csv('k_optimization_results.csv', encoding='utf-8-sig', index=False)
    
    print("\n" + "="*60)
    print("K값별 평균 성과")
    print("="*60)
    
    for k in k_values:
        k_data = df_results[df_results['K'] == k]
        if len(k_data) > 0:
            avg_trades = k_data['거래'].mean()
            avg_win = k_data['승률'].mean()
            avg_cagr = k_data['CAGR'].mean()
            print(f"K={k}: 평균 거래 {avg_trades:.0f}회, 승률 {avg_win:.1f}%, CAGR {avg_cagr:.1f}%")
    
    print("\n✅ 저장: k_optimization_results.csv")
else:
    print("\n❌ 결과 없음")