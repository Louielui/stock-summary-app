...        
        st.divider()
        st.header("[ AI 建議 ]")

        if 'rsi_series' in locals() and not rsi_series.isna().all():
            ai_comment = ""
            summary_score = 0

            # RSI 分析
            if rsi > 70:
                ai_comment += f"🔺 RSI > 70：{symbol} 處於超買區，可能出現拉回修正，建議保守觀望或分批停利。\n"
                summary_score -= 1
            elif rsi < 30:
                ai_comment += f"🔻 RSI < 30：{symbol} 處於超賣區，技術面可能反彈，Put Sell 策略具吸引力。\n"
                summary_score += 1
            else:
                ai_comment += f"➤ RSI 在中性區 ({rsi:.1f})，觀察是否轉強或失守 MA20 (${ma20:.2f})。\n"

            # MACD 分析
            macd_diff = macd_line.iloc[-1] - signal_line.iloc[-1]
            if macd_diff > 0 and macd_line.iloc[-1] > 0:
                ai_comment += "✅ MACD 處於多頭排列，趨勢偏多。\n"
                summary_score += 1
            elif macd_diff < 0 and macd_line.iloc[-1] < 0:
                ai_comment += "⚠️ MACD 處於空頭排列，建議保守操作。\n"
                summary_score -= 1
            else:
                ai_comment += "🔄 MACD 處於轉折點附近，需觀察方向明朗化。\n"

            # KD 指標分析
            k_val = k_line.iloc[-1]
            d_val = d_line.iloc[-1]
            if k_val > 80 and d_val > 80:
                ai_comment += "🔺 KD 高檔鈍化，短線漲多須防回落。\n"
                summary_score -= 1
            elif k_val < 20 and d_val < 20:
                ai_comment += "🔻 KD 低檔鈍化，可能進入反彈階段，可考慮進場。\n"
                summary_score += 1
            else:
                ai_comment += f"➤ KD 中性 (K={k_val:.1f}, D={d_val:.1f})，等待轉折明確訊號。\n"

            # MA 趨勢分析
            if current > ma20:
                ai_comment += "📈 價格站上 MA20，技術面維持偏多格局。\n"
                summary_score += 1
            else:
                ai_comment += "📉 價格低於 MA20，短線弱勢，建議保守。\n"
                summary_score -= 1

            st.info(ai_comment)

            # 綜合策略建議
            st.subheader("策略等級判斷：")
            if summary_score >= 2:
                st.success("✅ 綜合建議：積極建倉（偏多）")
            elif summary_score <= -2:
                st.error("⚠️ 綜合建議：保守觀望（偏空）")
            else:
                st.warning("➤ 綜合建議：中性偏觀望，留意轉折")
        else:
            st.warning("⚠️ 無法執行 AI 分析：資料不足或尚未產生技術指標。請輸入有效股票代碼並重試。")
