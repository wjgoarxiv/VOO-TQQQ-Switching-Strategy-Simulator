"""basic logic
1. 매달 (every month) 1,000 $ 만큼의 voo를 적립한다. 타이밍은 상관 없다. 월급날은 1일이고, 월급날에 voo를 매번 적립해야 한다. 
2. ixic 차트의 하방 채널을 최초로 터치한다면, voo를 **전량 매도**하고 tqqq로 종목을 옮긴다. 이 때부터는 월급을 받으면 tqqq에 적립한다. 
3. spx가 -3% 이상 하락한다면, 다음 날 tqqq를 **전량 매도**하고 voo로 종목을 옮긴다. 이 때부터는 월급을 받으면 voo에 적립한다. 

즉, ixic와 spx가 voo / tqqq 종목 변화를 위한 주요 트리거가 되는데, 
- ixic의 경우 -> 하방 채널을 터치한다
- spx의 경우 -> -3%의 하락세를 보인다
일 경우 월급으로 적립해야 할 품목을 tqqq / voo로 토글하면 된다. 
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rcparams import *

def get_first_trading_day_of_month(data):
    return data.resample('M').first().dropna().index

def simulate_investment(start_date, end_date): 
    # Data loading
    voo_data = yf.download('VOO', start_date, end_date)
    ixic_data = yf.download('^IXIC', start_date, end_date)
    spx_data = yf.download('^GSPC', start_date, end_date)
    tqqq_data = yf.download('TQQQ', start_date, end_date)

    # 1. ixic 하방 채널 기준 
    ixic_data['MA20'] = ixic_data['Close'].rolling(window=100).mean()
    ixic_data['stddev'] = ixic_data['Close'].rolling(window=100).std()
    ixic_data['upper'] = ixic_data['MA20'] + (ixic_data['stddev'] * 2)
    ixic_data['lower'] = ixic_data['MA20'] - (ixic_data['stddev'] * 2)

    # Window = 100 is reasonble 

    # 2. spx -3% 하락 여부 기준
    is_spx_below_three = spx_data['Close'].pct_change().rolling(window=2).sum() < -0.03

    # 월급
    monthly_income = 1000

    # Identify the first trading day of each month
    first_trading_days = voo_data.asfreq('BM').dropna().index

    # 자산 상태 초기화
    holding_voo = True  # 처음에는 VOO를 보유하고 시작
    voo_shares = 0
    tqqq_shares = 0
    cash = 0
    cash_accumulated = 0  # 월급만 모았을 때의 총 금액

    # 결과를 저장할 데이터프레임 생성
    results_df = pd.DataFrame(index=ixic_data.index, columns=['Total_Value', 'Cash_Accumulated'])

    # 날짜별로 루프 실행
    # first_trading_days = get_first_trading_day_of_month(voo_data)
    for next_trading_day in ixic_data.index:
        if next_trading_day in first_trading_days:
            # 월급 투자 실행
            cash_accumulated += monthly_income

            if holding_voo:
                cash += monthly_income
                voo_price = voo_data.loc[next_trading_day, 'Close'] if next_trading_day in voo_data.index else np.nan
                voo_shares += cash // voo_price
                cash %= voo_price
            else:
                cash += monthly_income
                tqqq_price = tqqq_data.loc[next_trading_day, 'Close'] if next_trading_day in tqqq_data.index else np.nan
                tqqq_shares += cash // tqqq_price
                cash %= tqqq_price

        # IXIC이 하방 채널을 터치하면 VOO 매도 후 TQQQ 매수
        if ixic_data.loc[next_trading_day, 'Close'] <= ixic_data.loc[next_trading_day, 'lower'] and holding_voo:
            voo_price = voo_data.loc[next_trading_day, 'Close']
            cash += voo_shares * voo_price
            voo_shares = 0
            tqqq_price = tqqq_data.loc[next_trading_day, 'Close']
            tqqq_shares += cash // tqqq_price
            cash %= tqqq_price
            holding_voo = False

        # SPX가 -3% 이상 하락하면 TQQQ 매도 후 VOO 매수
        if is_spx_below_three.loc[next_trading_day] and not holding_voo:
            tqqq_price = tqqq_data.loc[next_trading_day, 'Close']
            cash += tqqq_shares * tqqq_price
            tqqq_shares = 0
            voo_price = voo_data.loc[next_trading_day, 'Close']
            voo_shares += cash // voo_price
            cash %= voo_price
            holding_voo = True

        # 현재 날짜의 총 자산 가치 계산
        if holding_voo:
            voo_price = voo_data.loc[next_trading_day, 'Close'] if next_trading_day in voo_data.index else np.nan
            total_value = voo_shares * voo_price + cash
        else:
            tqqq_price = tqqq_data.loc[next_trading_day, 'Close'] if next_trading_day in tqqq_data.index else np.nan
            total_value = tqqq_shares * tqqq_price + cash

        # 데이터프레임에 결과 저장
        results_df.loc[next_trading_day, 'Total_Value'] = total_value
        results_df.loc[next_trading_day, 'Cash_Accumulated'] = cash_accumulated

        # 제일 
        if next_trading_day >= ixic_data.index[-10]:
            print(next_trading_day, f'VOO 보유: {holding_voo}', f'VOO 보유량: {voo_shares} 주', 
                        f'TQQQ 보유량: {tqqq_shares} 주', f'현금: {cash} 불', f'총 자산: {total_value} 불', 
                        f'월급만 모았을 때의 총 금액: {cash_accumulated} 불', sep='\n', end='\n\n')

    results_df.to_csv(f'investment_simulation_{start_date}_to_{end_date}.csv')

    # 플롯
    rcparams()

    # After the loop, save the results and plot
    results_df.to_csv(f'investment_simulation_{start_date}_to_{end_date}.csv')
    plt.figure(figsize=(8, 5))
    plt.plot(results_df.index, results_df['Total_Value'], label='With investment', color='blue')
    plt.plot(results_df.index, results_df['Cash_Accumulated'], label='Without investment', color='orange')
    leg = plt.legend(frameon=True, facecolor='white', edgecolor='black') 
    for text, color in zip(leg.get_texts(), ['blue', 'orange']):
        text.set_color(color)
    plt.xlabel('Date')
    plt.ylabel('Value ($)')
    plt.title(f'Backtesting from {start_date} to {end_date}')
    plt.xticks(rotation=60)
    plt.tight_layout()
    plt.show()

    return results_df