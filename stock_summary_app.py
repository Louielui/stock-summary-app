
import streamlit as st
import datetime

# 假設資料
price = 79.45
change = -0.38
volume = "1.2M"
open_price = 80.00
prev_close = 79.83
ma20 = 78.95
rsi = 62.1
macd = "多方趨勢"
strike_price = 77.5
premium = 1.35
lots = 5
capital_req = 19375
return_rate = 3.5
ai_comment = "此股處於上升通道，短線回測支撐。Put Sell 策略可考慮於 $77.5～$80 範圍佈局。"

st.set_page_config(page_title="單股分析板", layout="centered")
st.title(":bar_chart: 單股即時分析")
st.markdown(f"_Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")

st.header("[ 即時報價 ]")
col1, col2 = st.columns(2)
with col1:
    st.metric("股價", f"${price:.2f}", f"{change}%")
    st.text(f"成交量: {volume}")
with col2:
    st.text(f"開盤: ${open_price:.2f}")
    st.text(f"昨收: ${prev_close:.2f}")

st.divider()
st.header("[ 技術指標 ]")
st.text(f"MA20: ${ma20:.2f}    RSI: {rsi} (偏多)    MACD: {macd}")

st.divider()
st.header(f"[ 期權模擬：賣出 Put @ ${strike_price} ]")
col1, col2 = st.columns(2)
with col1:
    st.text(f"權利金: ${premium}")
    st.text(f"可收總金額 ({lots}口): ${premium * lots * 100:.0f}")
with col2:
    st.text(f"保證金需求: ${capital_req:,.0f}")
    st.text(f"報酬率: {return_rate:.1f}%")

st.success(":bulb: 建議：可建倉，風險偏低 (進場價低於 MA60)")

st.divider()
st.header("[ AI 建議 ]")
st.info(ai_comment)
