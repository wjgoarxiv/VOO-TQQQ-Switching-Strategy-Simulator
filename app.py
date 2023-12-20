import pandas as pd
import streamlit as st
from rcparams import *
from simulate_investment_function import simulate_investment  # Assuming your function is in this file

st.title('VOO-TQQQ 스위칭 투자 백테스팅 시뮬레이션')
st.write('> Written by [**Woojin Go**](https://woojingo.site/) \n')
st.write('> Inspired by the blog column written by [닥터음양](https://m.cafe.naver.com/ca-fe/web/cafes/likeusstock/articles/958099?useCafeId=false&tc)')

# Introduction
st.write('### 1. 시뮬레이션 개요')
st.write('본 시뮬레이션은 [yahoo finance](http://finance.yahoo.com/)를 통해 불러온 `VOO`, `TQQQ`, `IXIC`, 그리고 `QQQ` 데이터를 기반으로 진행됩니다.')
st.write('로직은 다음과 같습니다.')
st.write("""
         1. 매달 (every month) 1,000 $ 만큼의 `voo`를 적립합니다. 타이밍은 상관 없습니다. 월급날은 1일이고, 월급날에 `voo`를 매번 적립해야 합니다. 
2. `ixic` 차트의 하방 채널을 최초로 터치한다면, `voo`를 **전량 매도**하고 `tqqq`로 종목을 옮깁니다. 이 때부터는 월급을 받으면 `tqqq`에 적립합니다. 
3. `spx`가 **-3% 이상 하락**한다면, 다음 날 `tqqq`를 **전량 매도**하고 `voo`로 종목을 옮긴다. 이 때부터는 월급을 받으면 `voo`에 적립합니다.

즉, `ixic`와 `spx`가 `voo` / `tqqq` 종목 변화를 위한 주요 트리거가 되는데, 
- `ixic`의 경우 -> **하방 채널을 터치**한다
- `spx`의 경우 -> **-3%의 하락세**를 보인다
\n 일 경우 월급으로 적립해야 할 품목을 `tqqq` / `voo`로 토글하는 원리입니다.""")

# How to use
st.write('### 2. 사용 방법')
st.write(""" 
         1. `Start Date`와 `End Date`를 선택합니다. 단, 시작년도는 **2011년보다 빠르게 설정할 수 없습니다.**
         2. `Run Simulation` 버튼을 누릅니다.
         3. 결과를 확인합니다.""")

# User inputs for the start and end dates
start_date = st.date_input("Start Date", value=pd.to_datetime('2021-01-01'))
end_date = st.date_input("End Date", value=pd.to_datetime('2021-12-31'))

if st.button('Run Simulation'):
    # Run the simulation
    results_df = simulate_investment(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    # Ensure the columns are numeric
    results_df['Total_Value'] = pd.to_numeric(results_df['Total_Value'], errors='coerce')
    results_df['Cash_Accumulated'] = pd.to_numeric(results_df['Cash_Accumulated'], errors='coerce')

    # Display results
    st.write('### 3. 그래프')
    st.write('아래 그래프는 총 자산 가치와 월급만 합산했을 때를 비교하여 보여줘요.')
    st.write('월급만 합산했을 경우는 `Total_Value`, 투자를 통한 총 자산 가치는 `Cash_Accumulated`로 표시돼요.')
    st.line_chart(results_df[['Total_Value', 'Cash_Accumulated']])

    # Display the major 10 rows of df
    st.write('### 4. 결과 테이블')
    st.write('스크롤을 내리면 전체 결과를 확인해볼 수 있어요.')
    st.write('`Total_Value`는 총 자산 가치를, `Cash_Accumulated`는 월급만 합산했을 때의 총 금액을 의미해요.')
    st.write(results_df)

st.write("주의: 해당 시뮬레이션 결과는 어디까지나 이전 데이터를 기반으로 한 가상의 결과에요. 실제 투자에 참고하시기 바랍니다.")
