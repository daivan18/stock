# 📦 webhook.py測試說明：LINE Webhook + FastAPI + ngrok 範例說明

本專案為一個使用 Python FastAPI 框架撰寫的 LINE Bot Webhook 範例，透過 `ngrok` 將本地開發環境公開至外網，並與 LINE Messaging API 整合，實現接收與回覆 LINE 訊息的功能。

---

## 🧱 專案結構

stock/ 
├── .env              ← # 儲存 LINE access token 與其他環境變數 （不要上傳到 GitHub）
├── .env.example      ← 範例環境變數檔，供團隊參考
├── webhook.py # FastAPI 主程式，處理 webhook 請求 
├── requirements.txt # 安裝依賴（選用） 
└── README.md # 說明文件

📌 總結：哪些檔案建議上傳 GitHub？
檔案名稱	            是否上傳	    說明
README.md	            ✅ 要	    專案說明，必要
.env	                ❌ 不要	    含敏感資訊，要加入 .gitignore
.env.example	        ✅ 要	    給他人參考的範本
requirements.txt	    ✅ 要	    方便安裝相依套件
webhook.py 等程式碼	     ✅ 要	     主要程式碼

📦 requirements.txt

請在專案根目錄新增 requirements.txt 並貼上下列內容：

fastapi
uvicorn
python-dotenv
requests
redis

⚙️ .env.example
請在專案根目錄新增 .env.example 並貼上下列內容，這是 .env 的範本（不包含實際敏感資訊）：
# LINE Messaging API Token (請至 LINE Developers 取得)
LINE_CHANNEL_ACCESS_TOKEN=你的長效AccessToken

# Redis 設定（如未使用可略過）
REDIS_HOST=localhost
REDIS_PORT=6379

--- yaml

## 🔧 開發流程說明

### 1️⃣ 使用者傳送訊息 ➜ LINE 官方帳號收到  
- 使用者對 LINE 官方帳號傳送訊息（例如：`hi`）。

### 2️⃣ LINE Server 發送 Webhook ➜ 傳到你設定的網址  

- 在 [LINE Developers Console](https://developers.line.biz/console/) 的「Messaging API」設定中，填寫 Webhook URL（例如）：

https://0406-61-57-231-229.ngrok-free.app/webhook


### 3️⃣ ngrok ➜ 將 LINE 傳來的請求轉發到本地 FastAPI  
- 執行：
```bash
ngrok http 8000

將生成的網址（例如：https://xxxxx.ngrok-free.app）填入 LINE Webhook URL。

4️⃣ FastAPI webhook.py 接收 LINE 請求 ➜ 解 JSON ➜ 回覆訊息
webhook.py 接收到 LINE 的 POST 請求後，會讀取 replyToken 與訊息，並向 LINE Messaging API 發送回覆訊息：

https://api.line.me/v2/bot/message/reply

須在 Authorization Header 中附上 Channel Access Token。

5️⃣ LINE Messaging API 驗證 Token ➜ 成功回覆使用者訊息

若 Token 正確，LINE Server 會將回覆訊息傳回給原本的使用者。

📦 .env 範例

請將 .env 檔案放在專案根目錄，內容如下：

LINE_CHANNEL_ACCESS_TOKEN=你的ChannelAccessToken
REDIS_HOST=localhost
REDIS_PORT=6379

🚀 執行專案

# 安裝依賴
pip install -r requirements.txt

# 執行 webhook server
uvicorn webhook:app --reload

➕ ngrok 執行方式

ngrok config add-authtoken 你的Token
ngrok http 8000


🧪 Webhook.py單元測試流程說明

1. Python專案在終端機下輸入以下指令啟動webhook.py FastAPI監聽

uvicorn webhook:app --reload

2. 執行ngrok

[Windows] 執行官網下載的ngrok.exe

[MacOS] VS Code開啟終端機

執行以下指令：

ngrok config add-authtoken “ngrok Authtoken”

📝 備註：“ngrok Authtoken” 登入ngrok官網 \ Your Authtoken取得

ngrok http 8000 or ngrok http http://localhost:8000

這段執行完，ngrok執行視窗會顯示如下

Forwarding https://0406-61-57-231-229.ngrok-free.app

將Forwarding後的URL更新至
Line Developer後台 \ Messaging API \ Webhook settings \ Webhook URL

URL後須加上”需要呼叫的FastAPI Route”
https://0406-61-57-231-229.ngrok-free.app/FastAPI Route

以webhook.py為例：
@app.post("/webhook") → FastAPI Route
async def line_webhook(req: Request):
    body = await req.body()
    data = json.loads(body)
e.g. 
https://0406-61-57-231-229.ngrok-free.app/webhook


🚀測試流程說明

[1] 使用者在 LINE 官方帳號 傳送訊息
        │
        ▼
[2] LINE 官方伺服器 把訊息送到你在
    LINE Developers 後台設定的 Webhook URL
        │
        ▼
[3] Webhook URL: https://xxxx.ngrok-free.app/webhook
    ⇨ ngrok 把這個請求「轉發」給你本機的 FastAPI Server
        │
        ▼
[4] FastAPI 的 webhook.py 內這段會被呼叫：
        @app.post("/webhook")
        async def line_webhook(req: Request)
        │
        ▼
[5] webhook.py 解析 LINE 傳來的 JSON，抓出 replyToken 和訊息內容
        │
        ▼
[6] webhook.py 用 LINE_CHANNEL_ACCESS_TOKEN 呼叫
    LINE 的 reply API 把訊息回覆給使用者



