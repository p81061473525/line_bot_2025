from dotenv import load_dotenv
import os
from flask import Flask, request, abort

from linebot import (
  LineBotApi, WebhookHandler
)

from linebot.exceptions import (
  InvalidSignatureError
)

from linebot.models import (
  MessageEvent, TextMessage, TextSendMessage,
)

load_dotenv('/etc/secrets/.env')

app = Flask(__name__)  

# 從 .env 讀取金鑰
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))  
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

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
        joke = "有一天小明走在路上，突然跌倒，因為地球有引力。"
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