import streamlit as st
import datetime
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 使用者輸入股票代碼與 Put 模擬口數
st.set_page_config(page_title="單股分析板", layout="centered")
st.title(":bar_chart: 單股即時分析")
symbol = st.text_input("輸入股票代碼（例如：TD.TO / AAPL）", value="TD.TO").upper()
put_lots = st.number_input("輸入 Put 模擬口數", min_value=1, max_value=20, value=5, step=1)
exp_date = st.date_input("模擬履約日期", value=datetime.date.today() + datetime.timedelta(days=30))

if symbol:
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.info
        data = ticker.history(period="6mo")
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
        st.header("[ 技術指標圖表 ]")

        # K 線圖 + MA20
        ma20_series = data['Close'].rolling(window=20).mean()
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(data.index, data['Close'], label='Close Price')
        ax.plot(ma20_series, label='MA20', linestyle='--')
        ax.set_title(f"{symbol} 股價與 MA20")
        ax.legend()
        st.pyplot(fig)

        # RSI 線圖
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi_series = 100 - (100 / (1 + rs))

        fig2, ax2 = plt.subplots(figsize=(10, 2))
        ax2.plot(rsi_series, label="RSI", color="orange")
        ax2.axhline(70, color='red', linestyle='--')
        ax2.axhline(30, color='green', linestyle='--')
        ax2.set_title("RSI 指標")
        st.pyplot(fig2)

        rsi = rsi_series.iloc[-1]
        ma20 = ma20_series.iloc[-1]
        macd_trend = "多方趨勢" if current > ma20 else "盤整/偏空"

        st.text(f"MA20: ${ma20:.2f}    RSI: {rsi:.1f}    MACD: {macd_trend}")

        st.divider()
        st.header("[ 期權模擬：多履約價賣出 Put ]")

        put_rows = []
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        for pct in [0.95, 0.975, 1.0, 1.025]:
            strike_price = round(current * pct, 2)
            premium = round(1.0 + (1.05 - pct) * 3.5, 2)  # 模擬權利金
            capital_req = strike_price * 100 * put_lots * 0.8
            total_income = premium * 100 * put_lots
            return_rate = total_income / capital_req * 100
            put_rows.append({
                "日期": today_str,
                "履約日": exp_date.strftime("%Y-%m-%d"),
                "履約價": f"${strike_price}",
                "權利金": f"${premium}",
                "總收入({put_lots}口)": f"${total_income:.0f}",
                "保證金需求": f"${capital_req:,.0f}",
                "報酬率": f"{return_rate:.2f}%"
            })

        st.table(pd.DataFrame(put_rows))

        st.divider()
        st.header("[ AI 建議 ]")

        ai_comment = ""
        if rsi > 70:
            ai_comment += f"{symbol} 處於超買區，短線可能面臨壓力，建議觀望或設好停利點。\n"
        elif rsi < 30:
            ai_comment += f"{symbol} 處於超賣區，可能有反彈空間，Put Sell 策略可逐步佈局。\n"
        else:
            ai_comment += f"{symbol} RSI 中性 ({rsi:.1f})，整體偏多，觀察是否回測 MA20 (${ma20:.2f})。\n"

        if current > ma20:
            ai_comment += "目前價格在 MA20 之上，顯示多頭格局。"
        else:
            ai_comment += "目前價格低於 MA20，建議保守操作或等待企穩。"

        st.info(ai_comment)

    except Exception as e:
        st.error("無法取得股票資料，請確認代碼正確。")