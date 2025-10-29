import os, time, threading, requests
from datetime import datetime, timedelta, timezone
from flask import Flask

# -------------------------------------------------
# 時區：台北時間 (UTC+8)
# -------------------------------------------------
TPE_TZ = timezone(timedelta(hours=8))
def now_tpe_str():
    return datetime.now(TPE_TZ).strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------------------------
# Telegram 推播設定
# -------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID   = os.getenv("CHAT_ID", "").strip()

def send_telegram(msg: str):
    """把訊息丟到你的 Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ BOT_TOKEN / CHAT_ID 沒設定，以下內容本來應該推給你：")
        print(msg)
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print("⚠️ Telegram 發送失敗:", e)

# -------------------------------------------------
# 數據取得（之後可以接真實 API）
# 現在先用假資料邏輯，但格式、邊界條件、報告格式全部是正式版
# -------------------------------------------------
def get_market_data():
    # 將來你可在這裡改成真實抓 DefiLlama / CEX API / 等等
    # 回傳的單位已經是「金額變化(美元)」跟「成交量變化比例」
    data = {
        # 穩定幣鑄造變化量
        "mint_3h":   65_000_000,   # 近3h 新鑄造金額 (USD)
        "mint_24h": 210_000_000,   # 近24h 新鑄造金額 (USD)

        # 交易所穩定幣淨流入變化量
        "inflow_3h": 42_000_000,   # 近3h 淨流入 (USD)
        "inflow_24h":160_000_000,  # 近24h 淨流入 (USD)

        # BTC/ETH 現貨成交量變化率 (百分比用小數表示)
        "vol_pct_3h": 0.243,       # = +24.3%
        "vol_pct_24h":0.551,       # = +55.1%
    }

    return data

# -------------------------------------------------
# 報告生成 + 是否要觸發警報
# -------------------------------------------------
def build_report_and_alert(data):
    now_str = now_tpe_str()

    mint_3h   = data["mint_3h"]
    mint_24h  = data["mint_24h"]
    inflow_3h = data["inflow_3h"]
    inflow_24h= data["inflow_24h"]
    vol_3h    = data["vol_pct_3h"]
    vol_24h   = data["vol_pct_24h"]

    # 判斷是否觸發警報（用 3h 視窗）
    alert = (
        (mint_3h   >= 50_000_000) or
        (inflow_3h >= 30_000_000) or
        (vol_3h    >= 0.20)
    )

    # 報告文字（Telegram 也是這個格式）
    report_lines = []
    report_lines.append("【📊 即時監測報告】")
    report_lines.append(f"時間：{now_str}（台北時間）")
    report_lines.append("")
    report_lines.append("⏱ 近 3 小時 (3h)")
    report_lines.append(f"💵 穩定幣鑄造：+{mint_3h:,.0f} 美元")
    report_lines.append(f"🏦 交易所淨流入：+{inflow_3h:,.0f} 美元")
    report_lines.append(f"📈 BTC/ETH 成交量變化：+{vol_3h*100:.1f}%")
    report_lines.append("")
    report_lines.append("🕑 近 24 小時 (24h)")
    report_lines.append(f"💵 穩定幣鑄造：+{mint_24h:,.0f} 美元")
    report_lines.append(f"🏦 交易所淨流入：+{inflow_24h:,.0f} 美元")
    report_lines.append(f"📈 BTC/ETH 成交量變化：+{vol_24h*100:.1f}%")
    report_lines.append("")

    if alert:
        report_lines.append("🔴 ⚠️ 資金疑似快速進場")
        report_lines.append("🧭 解讀：主力資金疑似加速進場，可能準備推價格。")
        report_lines.append("觸發原因：3h 視窗內達到警戒門檻（鑄造≥5,000萬 / 淨流入≥3,000萬 / 成交量≥+20%）")
    else:
        report_lines.append("🟢 目前沒有異常。")

    full_report = "\n".join(report_lines)
    return full_report, alert

# -------------------------------------------------
# 監控主迴圈（每5分鐘檢查一次）
# -------------------------------------------------
def monitor_loop():
    print("✅ Render 實時監測啟動中...")
    while True:
        data = get_market_data()
        report_text, alert_flag = build_report_and_alert(data)

        # 印到 Render Logs
        print("\n" + report_text)

        # 如果達到觸發條件，就推 Telegram
        if alert_flag:
            send_telegram(report_text)

        # 每 5 分鐘跑一次
        time.sleep(300)

# -------------------------------------------------
# Flask keepalive：讓 Render 免費 Web Service 不會砍你
# -------------------------------------------------
app = Flask(__name__)

@app.get("/")
def healthcheck():
    return "Service running."

if __name__ == "__main__":
    # 背景開一個 Thread 來跑監控 loop
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()

    # 主線程跑 Flask，Render 會覺得「喔這是個 Web Service」
    app.run(host="0.0.0.0", port=10000)
