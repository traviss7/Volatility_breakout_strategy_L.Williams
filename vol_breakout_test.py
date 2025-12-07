import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print("변동성 돌파 전략 백테스트 (20년, 상세)")
print("=" * 80)

# 1단계: 시총 TOP 30 추출
print("\n[1단계] 시총 TOP 30 추출 중...")
df_krx = fdr.StockListing('KRX')
df_top30 = df_krx.nlargest(30, 'Marcap')
print(f"✅ 완료: {len(df_top30)}개 종목")

# 2단계: 1/2/3년 변동성 계산
print("\n[2단계] 변동성 분석 중...")
vol_results = []
end_date = datetime.now()

for idx, row in df_top30.iterrows():
    code, name = row['Code'], row['Name']
    print(f"  분석 중: {name} ({idx+1}/30)", end='\r')
    
    try:
        df_3y = fdr.DataReader(code, (end_date - timedelta(days=1095)).strftime('%Y-%m-%d'))
        if len(df_3y) < 100:
            continue
            
        vol_data = {'Name': name, 'Code': code}
        
        for period, days in [('1년', 365), ('2년', 730), ('3년', 1095)]:
            df_period = df_3y[df_3y.index >= (end_date - timedelta(days=days))]
            vol = df_period['Close'].pct_change().std() * np.sqrt(252) * 100
            vol_data[period] = round(vol, 2)
        
        vol_data['평균'] = round((vol_data['1년'] + vol_data['2년'] + vol_data['3년']) / 3, 2)
        vol_results.append(vol_data)
    except:
        continue

df_volatility = pd.DataFrame(vol_results).sort_values('평균', ascending=False)
print("\n\n변동성 TOP 10 (1/2/3년 평균 기준):")
print(df_volatility.head(10).to_string(index=False))

# CSV 저장
df_volatility.to_csv('volatility_ranking.csv', encoding='utf-8-sig', index=False)
print("\n✅ 저장: volatility_ranking.csv")

# 3단계: 백테스트 (20년)
print("\n" + "=" * 80)
print("[3단계] 백테스트 (2005-2025, 변동성 돌파 + 20일선)")
print("=" * 80)

top10_stocks = df_volatility.head(10)
backtest_results = []

for idx, stock in top10_stocks.iterrows():
    code, name = stock['Code'], stock['Name']
    print(f"\n분석 중: {name}")
    
    try:
        # 20년 데이터
        df = fdr.DataReader(code, '2005-01-01')
        if len(df) < 100:
            print(f"  ⚠️ 데이터 부족")
            continue
            
        # 전략 계산
        df['MA20'] = df['Close'].rolling(20).mean()
        df['prev_high'] = df['High'].shift(1)
        df['prev_low'] = df['Low'].shift(1)
        df['range'] = df['prev_high'] - df['prev_low']
        df['target_price'] = df['Open'] + df['range'] * 0.5
        
        # 매수 조건: 돌파 + 20일선 위
        df['buy_signal'] = (df['High'] >= df['target_price']) & (df['Close'] > df['MA20'])
        
        # 수익률 계산
        df['buy_price'] = np.where(df['buy_signal'], df['target_price'], np.nan)
        df['sell_price'] = df['Open'].shift(-1)
        df['return'] = np.where(
            df['buy_signal'],
            (df['sell_price'] - df['buy_price']) / df['buy_price'] - 0.0026,
            0
        )
        
        # 이상치 제거
        df.loc[df['buy_price'] <= 0, 'return'] = 0
        df['return'] = df['return'].replace([np.inf, -np.inf], 0)
        df = df.dropna()
        
        # 통계
        total_days = len(df)
        total_trades = df['buy_signal'].sum()
        winning_trades = (df[df['buy_signal']]['return'] > 0).sum()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # 누적 수익률
        df['cumulative'] = (1 + df['return']).cumprod()
        final_value = df['cumulative'].iloc[-1]
        total_return = (final_value - 1) * 100
        
        # CAGR
        years = (df.index[-1] - df.index[0]).days / 365.25
        cagr = ((final_value) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        # MDD
        df['peak'] = df['cumulative'].cummax()
        df['drawdown'] = (df['cumulative'] - df['peak']) / df['peak'] * 100
        mdd = df['drawdown'].min()
        
        # 출력
        print(f"  기간: {df.index[0].date()} ~ {df.index[-1].date()} ({years:.1f}년)")
        print(f"  거래일: {total_days:,}일 | 매수: {total_trades}회 | 승률: {win_rate:.1f}%")
        print(f"  수익률: {total_return:.1f}% | CAGR: {cagr:.1f}% | MDD: {mdd:.1f}%")
        
        # 결과 저장
        backtest_results.append({
            '종목명': name,
            '종목코드': code,
            '기간(년)': round(years, 1),
            '거래일수': total_days,
            '매수횟수': total_trades,
            '승률(%)': round(win_rate, 1),
            '총수익률(%)': round(total_return, 1),
            'CAGR(%)': round(cagr, 1),
            'MDD(%)': round(mdd, 1)
        })
        
    except Exception as e:
        print(f"  ❌ 오류: {str(e)[:50]}")
        continue

# 결과 저장
df_results = pd.DataFrame(backtest_results)
df_results.to_csv('backtest_results.csv', encoding='utf-8-sig', index=False)

print("\n" + "=" * 80)
print("✅ 백테스트 완료!")
print("✅ 저장 파일:")
print("   - volatility_ranking.csv (변동성 순위)")
print("   - backtest_results.csv (백테스트 결과)")
print("=" * 80)