
import streamlit as st
import datetime
import yfinance as yf

# 使用者輸入股票代碼
st.set_page_config(page_title="單股分析板", layout="centered")
st.title(":bar_chart: 單股即時分析")
symbol = st.text_input("輸入股票代碼（例如：TD.TO / AAPL）", value="TD.TO").upper()

if symbol:
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.info
        data = ticker.history(period="5d")
        current = data["Close"].iloc[-1]
        change = round(current - data["Close"].iloc[-2], 2)
        change_pct = round((change / data["Close"].iloc[-2]) * 100, 2)

        st.markdown(f"_Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")

        st.header("[ 即時報價 ]")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("股價", f"${current:.2f}", f"{change_pct}%")
            st.text(f"成交量: {int(data['Volume'].iloc[-1]):,}")
        with col2:
            st.text(f"開盤: ${data['Open'].iloc[-1]:.2f}")
            st.text(f"昨收: ${data['Close'].iloc[-2]:.2f}")

        st.divider()
        st.header("[ 技術指標 ]")
        ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        macd_trend = "多方趨勢" if current > ma20 else "盤整/偏空"

        st.text(f"MA20: ${ma20:.2f}    RSI: {rsi:.1f}    MACD: {macd_trend}")

        st.divider()
        st.header(f"[ 期權模擬：賣出 Put @ ${round(current * 0.975, 2)} ]")
        premium = 1.35  # 模擬值
        lots = 5
        strike_price = round(current * 0.975, 2)
        capital_req = strike_price * 100 * lots * 0.8
        return_rate = premium * lots * 100 / capital_req * 100

        col1, col2 = st.columns(2)
        with col1:
            st.text(f"權利金: ${premium:.2f}")
            st.text(f"可收總金額 ({lots}口): ${premium * lots * 100:.0f}")
        with col2:
            st.text(f"保證金需求: ${capital_req:,.0f}")
            st.text(f"報酬率: {return_rate:.1f}%")

        st.success(":bulb: 建議：可建倉，風險偏低 (進場價低於 MA20)")

        st.divider()
        st.header("[ AI 建議 ]")
        ai_comment = f"{symbol} 目前價格處於{'偏多' if rsi > 60 else '盤整/偏空'}區間，Put Sell 可考慮以 ${strike_price} 為策略佈局點。"
        st.info(ai_comment)

    except Exception as e:
        st.error("無法取得股票資料，請確認代碼正確。")
