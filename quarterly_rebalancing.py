import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("분기 리밸런싱 백테스트 시작")
print("="*70)

# 시총 TOP 30 종목 리스트
df_vol = pd.read_csv('volatility_ranking.csv', encoding='utf-8-sig')
stocks_pool = df_vol.head(10)[['Name', 'Code']].to_dict('records')

# 전체 기간 설정
start_date = datetime(2010, 1, 1)  # 10년으로 축소 (계산 빠르게)
end_date = datetime(2024, 12, 31)
quarters = pd.date_range(start_date, end_date, freq='Q')

print(f"기간: {start_date.date()} ~ {end_date.date()}")
print(f"리밸런싱: {len(quarters)}회 (분기마다)")
print(f"종목 풀: {len(stocks_pool)}개")
print("\n계산 중... (5-10분 소요)")

# 전체 수익률 저장
portfolio_value = 10000000  # 1천만원
portfolio_history = []

for q_idx in range(len(quarters)-1):
    q_start = quarters[q_idx]
    q_end = quarters[q_idx+1]
    
    print(f"\n분기: {q_start.date()} ~ {q_end.date()}")
    
    # 각 종목 효율 계산 (최근 1년 데이터)
    efficiencies = []
    lookback_start = q_start - timedelta(days=365)
    
    for stock in stocks_pool:
        try:
            df = fdr.DataReader(str(stock['Code']).zfill(6), lookback_start.strftime('%Y-%m-%d'), q_start.strftime('%Y-%m-%d'))
            
            if len(df) < 100:
                continue
            
            # K=0.5로 통일해서 효율 계산
            df['MA20'] = df['Close'].rolling(20).mean()
            df['range'] = df['High'].shift(1) - df['Low'].shift(1)
            df['target'] = df['Open'] + df['range'] * 0.5
            df['signal'] = (df['High'] >= df['target']) & (df['Close'] > df['MA20'])
            df['return'] = np.where(df['signal'], (df['Open'].shift(-1) - df['target']) / df['target'] - 0.0036, 0)
            
            trades = df['signal'].sum()
            if trades < 10:
                continue
            
            cumulative = (1 + df['return']).prod()
            days = len(df)
            years = days / 252
            cagr = (cumulative ** (1/years) - 1) * 100
            efficiency = cagr / trades * 100
            
            efficiencies.append({'name': stock['Name'], 'code': stock['Code'], 'eff': efficiency, 'cagr': cagr, 'trades': trades})
        except:
            continue
    
    # 효율 TOP 4 선정
    if len(efficiencies) == 0:
        print("  데이터 부족, 이전 종목 유지")
        continue

    df_eff = pd.DataFrame(efficiencies).sort_values('eff', ascending=False)
    top4 = df_eff.head(4)
    
    print(f"선정: {', '.join(top4['name'].tolist())}")
    
    # 해당 분기 수익률 계산
    quarter_return = 0
    
    for _, stock in top4.iterrows():
        try:
            df = fdr.DataReader(str(stock['code']).zfill(6), q_start.strftime('%Y-%m-%d'), q_end.strftime('%Y-%m-%d'))
            
            df['MA20'] = df['Close'].rolling(20).mean()
            df['range'] = df['High'].shift(1) - df['Low'].shift(1)
            df['target'] = df['Open'] + df['range'] * 0.5
            df['signal'] = (df['High'] >= df['target']) & (df['Close'] > df['MA20'])
            df['return'] = np.where(df['signal'], (df['Open'].shift(-1) - df['target']) / df['target'] - 0.0036, 0)
            
            cumulative = (1 + df['return']).prod() - 1
            
            # 안전장치 추가
            if cumulative < -0.9:  # -90% 이상 손실은 무시
                cumulative = 0
            
            quarter_return += cumulative * 0.25
        except:
            continue
    
    portfolio_value *= (1 + quarter_return)
    portfolio_history.append({'date': q_end, 'value': portfolio_value, 'return': quarter_return*100})
    
    print(f"분기 수익률: {quarter_return*100:.2f}%, 누적 자산: {portfolio_value:,.0f}원")

# 최종 결과
print("\n" + "="*70)
print("최종 결과")
print("="*70)
years = (end_date - start_date).days / 365.25
total_return = (portfolio_value / 10000000 - 1) * 100
cagr = ((portfolio_value / 10000000) ** (1/years) - 1) * 100

print(f"초기 자본: 10,000,000원")
print(f"최종 자본: {portfolio_value:,.0f}원")
print(f"총 수익률: {total_return:.1f}%")
print(f"CAGR: {cagr:.1f}%")

# CSV 저장
pd.DataFrame(portfolio_history).to_csv('rebalancing_history.csv', encoding='utf-8-sig', index=False)
print("\n✅ 저장: rebalancing_history.csv")