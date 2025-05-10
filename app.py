from dotenv import load_dotenv
import os
import random
from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# 讀取 Render Secret File
load_dotenv('/etc/secrets/.env')

app = Flask(__name__)

# 從 .env 讀取金鑰
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 冷笑話庫
jokes = [
    "蛤蜊麵擺久了會變什麼？ 白酒蛤蜊麵",
    "川普跌倒變甚麼？　三普",
    "曹操字孟德 \n劉備字玄德 \n伍佰呢？ \n五百字心得",
    "西醫治標\n中醫治本\n中西合璧\n治成標本",
    "我講一個笑裡藏刀的笑話，... 哈哈哈哈哈哈哈哈刀哈哈哈哈哈哈哈哈"
]

# 自動推播訊息（每1分鐘）
def send_greeting():
    user_id = "CHANNEL_ACCESS_TOKEN"  # 請填入你的 LINE User ID 或 Group ID
    try:
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text="午安！（每1分鐘發送一次測試）")
        )
        print(f"{datetime.datetime.now()} 已推播午安訊息")
    except Exception as e:
        print("推播失敗：", e)

# 啟動排程，每1分鐘執行一次
scheduler = BackgroundScheduler()
scheduler.add_job(send_greeting, 'interval', minutes=1)
scheduler.start()

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK\n'

# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "冷笑話":
        joke = random.choice(jokes)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=joke)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入「冷笑話」來聽冷笑話！")
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)