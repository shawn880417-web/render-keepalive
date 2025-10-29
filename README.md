# Render KeepAlive 自動資金監測 Bot

## 這是什麼？
- 持續在雲端運作
- 每 5 分鐘檢查加密市場資金動向
- 兩個時間視窗同時監控：近 3 小時 / 近 24 小時
- 有沒有「新錢進場」會直接用 Telegram 私訊我
- 時間顯示台北時間

## 報告包含：
- 穩定幣鑄造變化量（USDT/USDC）
- 交易所穩定幣淨流入變化量（淨入所資金）
- BTC/ETH 現貨成交量變化率
- 短線 3h + 日內 24h

## 觸發警報條件（用 3h 視窗來判斷）：
- 鑄造變化量 ≥ 50,000,000 美元
- 淨流入變化量 ≥ 30,000,000 美元
- 成交量變化率 ≥ +20%

符合任一條 → 推 Telegram：「⚠️ 資金疑似快速進場」

## 我要怎麼把它丟上 Render（免費方案）
1. 把這個 repo 連到 Render：
   - 到 https://render.com
   - New → Web Service
   - 連 GitHub，選這個 repo

2. Render 會問：
   - Build Command:
     pip install -r requirements.txt
   - Start Command:
     python main.py
   - Plan: Free

3. 建立後，在 Render 服務頁左邊點「Environment」，
   新增兩個環境變數：
   - BOT_TOKEN = 你的 Telegram bot token（@BotFather 給你的那串）
   - CHAT_ID = 你的 chat id（例如 7896xxxxxx）

4. 存完後按 Redeploy / Deploy Latest

5. 打開 Logs：
   - 每 5 分鐘你會看到一段中文監測報告
   - 如果觸發條件，它會直接 Telegram 私訊你（中文）
