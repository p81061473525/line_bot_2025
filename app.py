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

load_dotenv()

app = Flask(__name__)  

# 必須放上自己的Channel Access Token 
line_bot_api = LineBotApi('Channel_Access_Token')  

# 必須放上自己的Channel Secret
handler = WebhookHandler('Chennel_Secret')

# 監聽所有來自 /callback 的 Post Request 
@app.route("/callback", methods=['POST']) 
def callback():
    return "123\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)