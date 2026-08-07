import streamlit as st

st.title("NFL 승패 요인 분석")
st.write("NFL 경기 데이터로 승패 요인을 분석하고 예측하는 대시보드입니다.")

st.header("홈 어드벤티지")
st.metric("홈팀 승률", "53.5%")
st.write("홈 승 291 / 원정 승 252 / 무승부 1 (2024~2025 정규시즌)")

st.header("승패 요인 분석")

st.subheader("턴오버와 승률")
st.image("turnover_winrate.png")
st.write("턴오버가 많을수록 승률이 급락 (0회 72.6% → 3회 14.6%)")

st.subheader("3rd Down 전환율과 승률")
st.image("thirddown_winrate.png")
st.write("전환율이 높을수록 승률이 꾸준히 상승")

st.subheader("패스야드와 승률")
st.image("passyard_winrate.png")
st.write("패스야드는 승률과 약하게 연결 (지는 팀이 추격하며 패스를 늘리는 영향)")

st.subheader("페널티와 승률")
st.image("penalty_winrate.png")
st.write("페널티는 승패와 뚜렷한 관계 없음")

st.header("요인 종합 비교")
st.image("correlation_summary.png")
st.write("상관계수 기준: 턴오버(-0.40)와 3rd down(+0.26)이 승패에 가장 큰 영향. 패스야드·페널티는 약함")

st.header("승패 예측 모델")
st.write("경기 후 스탯으로 '설명'하는 것과, 경기 전 정보로 '예측'하는 것은 다른 문제입니다.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("기준선 (홈팀 찍기)", "53.5%")
with col2:
    st.metric("설명 모델 (경기 후)", "67%")
with col3:
    st.metric("예측 모델 (경기 전)", "67%")

st.write("경기 후 스탯을 다 알든(설명), 경기 전 정보만 알든(예측) 정확도가 67%로 같습니다. 즉 박스스코어의 높은 정확도는 착시이며, 실제 예측력은 경기 전 정보(특히 베팅 스프레드)에 있습니다.")

st.subheader("검증: 스프레드가 예측력의 핵심")
col4, col5 = st.columns(2)
with col4:
    st.metric("스프레드 포함", "67%")
with col5:
    st.metric("스프레드 제외", "49%", delta="-18%p", delta_color="inverse")
st.write("베팅 스프레드를 빼면 정확도가 49%로 급락해 기준선(53.5%)보다도 낮아집니다. 예측력의 대부분이 시장 예측(스프레드)에서 나온 것입니다.")

st.header("턴오버별 승률 조회")

# 턴오버 개수별 승률 (explore.py 분석 결과)
turnover_win_rates = {0: 72.6, 1: 51.7, 2: 30.0, 3: 14.6}

# 슬라이더로 턴오버 개수 선택
selected = st.slider("턴오버 개수를 선택하세요", 0, 3, 0)

# 선택한 개수의 승률 표시
rate = turnover_win_rates[selected]
st.metric(f"턴오버 {selected}회일 때 승률", f"{rate}%")