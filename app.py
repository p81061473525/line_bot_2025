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
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
)

# 讀取 Render Secret File
load_dotenv('/etc/secrets/.env')

app = Flask(__name__)

# 從 .env 讀取金鑰
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
group_id = os.getenv("GROUP_ID")

# 冷笑話庫
jokes = [
    "蛤蜊麵擺久了會變什麼？ 白酒蛤蜊麵",
    "川普跌倒變甚麼？　三普",
    "曹操字孟德 \n劉備字玄德 \n伍佰呢？ \n五百字心得",
    "西醫治標\n中醫治本\n中西合璧\n治成標本",
    "我講一個笑裡藏刀的笑話，... 哈哈哈哈哈哈哈哈刀哈哈哈哈哈哈哈哈"
]

# 帥哥圖片網址（dict，key僅內部辨識用）
image_urls = {
    #"肖戰1": "https://img.shoplineapp.com/media/image_clips/620b69a4b62f160029421122/original.png?1644915107",
    #"肖戰2": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Xiao_Zhan_at_the_Weibo_Night_Ceremony_January_11_2020.jpg",
    "肖戰3": "https://pgw.worldjournal.com/gw/photo.php?u=https://uc.udn.com.tw/photo/wj/realtime/2024/07/22/30084454.jpg",
    #"林俊傑": "https://media.vogue.com.tw/photos/609de8f91029df917ac3094a/2:3/w_2240,c_limit/1080x1080-%E9%9F%B3%E6%A8%82%E5%9A%AE%E5%B0%8EJJ-%E9%96%8B%E8%BB%8A%E5%A5%BD%E5%BF%83%E6%83%85.png",
    #"林俊傑2": "https://cc.tvbs.com.tw/img/upload/2025/05/09/20250509155552-957cedfc.jpg",
    #"馬英九1": "https://images.plurk.com/d59ff28e446dcf746aa5dfd306680422.jpg"
}

# 狗狗圖片網址
dog_url = "https://img.shoplineapp.com/media/image_clips/62134cd7aea3ad002c617cf6/original.png?1645432022"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("來源ID：", event.source.user_id)
    print("群組ID：", getattr(event.source, "group_id", None))

    commands = {
        "/help": lambda: TextSendMessage(
            text=(
                "功能選單：\n"
                "=========================\n"
                "冷笑話 - 隨機獲得一則冷笑話\n"
                "帥哥 - 看一張帥哥圖\n"
                "狗狗 - 看一張狗狗圖\n"
                "/help - 顯示本功能選單\n"
            )
        ),
        "冷笑話": lambda: TextSendMessage(text=random.choice(jokes)),
        "帥哥": lambda: (
            lambda v: ImageSendMessage(
                original_content_url=v,
                preview_image_url=v
            )
        )(random.choice(list(image_urls.values()))),
        "狗狗": lambda: ImageSendMessage(
            original_content_url=dog_url,
            preview_image_url=dog_url
        ),
    }

    msg = event.message.text
    if msg in commands:
        line_bot_api.reply_message(
            event.reply_token,
            commands[msg]()
        )

# 自動推播訊息（每1分鐘）
def send_greeting():
    try:
        line_bot_api.push_message(
            group_id,
            TextSendMessage(text="午安！（每1分鐘發送一次測試）")
        )
        print(f"{datetime.datetime.now()} 已推播午安訊息")
    except Exception as e:
        print("推播失敗：", e)

# # 啟動排程，每1分鐘執行一次
# scheduler = BackgroundScheduler()
# scheduler.add_job(send_greeting, 'interval', minutes=1)
# scheduler.start()

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)