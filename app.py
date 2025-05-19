import os
import random
import requests
import datetime
from dotenv import load_dotenv
from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler

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
    "肖戰3": "https://s.yimg.com/cl/api/res/1.2/ymkpoZnFjDnd36xwKFD5cA--/YXBwaWQ9eXR3YXVjdGlvbnNlcnZpY2U7aD03MDA7cT04NTtyb3RhdGU9YXV0bzt3PTU1Mg--/https://s.yimg.com/ob/image/c86c5bfa-0f8a-4ad6-aa70-126454a86c96.jpg",
    "肖戰4": "https://pgw.worldjournal.com/gw/photo.php?u=https://uc.udn.com.tw/photo/wj/realtime/2024/07/22/30084454.jpg&x=0&y=0&sw=0&sh=0&sl=W&fw=800&exp=3600&q=75&nt=1"
    #"林俊傑": "https://media.vogue.com.tw/photos/609de8f91029df917ac3094a/2:3/w_2240,c_limit/1080x1080-%E9%9F%B3%E6%A8%82%E5%9A%AE%E5%B0%8EJJ-%E9%96%8B%E8%BB%8A%E5%A5%BD%E5%BF%83%E6%83%85.png",
    #"林俊傑2": "https://cc.tvbs.com.tw/img/upload/2025/05/09/20250509155552-957cedfc.jpg",
    #"馬英九1": "https://images.plurk.com/d59ff28e446dcf746aa5dfd306680422.jpg"
}

# 狗狗圖片網址
dog_url = "https://img.shoplineapp.com/media/image_clips/62134cd7aea3ad002c617cf6/original.png?1645432022"

def fetch_youbike_data():
    url = "https://data.tycg.gov.tw/api/v1/rest/datastore/21bd0e7b-36af-4068-8e67-1d408b03457a?format=json"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return f"查詢失敗：API 回傳狀態碼 {response.status_code}"
        try:
            data = response.json()
        except Exception as e:
            return f"查詢失敗：無法解析資料 ({e})\n內容：{response.text[:200]}"
        result = ["查詢關鍵字：集福宮", "=" * 30]
        found = False
        for station in data['result']['records']:
            if "集福宮" in station['sna']:
                found = True
                result.append(f"站點名稱: {station['sna']}")
                result.append(f"站點類型: {'2.0E 電輔車' if '2.0E' in station['sna'] else '2.0 傳統車'}")
                result.append(f"可借車數: {station['sbi']}")
                result.append(f"可還車位: {station['bemp']}")
                result.append(f"更新時間: {station['updateTime']}")
                result.append('-' * 30)
        if not found:
            result.append("查無資料")
        return "\n".join(result)
    except Exception as e:
        return f"查詢失敗：{e}"

def fetch_stock_price(stock_id):
    """
    取得指定股票即時股價（台灣證交所公開資料，延遲約20秒）
    """
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if not data.get("msgArray"):
            return f"查詢股價失敗：查無 {stock_id} 資料"
        info = data["msgArray"][0]
        name = info.get("n", stock_id)
        price = info.get("z", "-")
        time = info.get("t", "")
        if price == "-":
            return f"{name}({stock_id}) 暫無即時股價"
        return f"{name}({stock_id}) 即時股價：{price} 元\n時間：{time}"
    except Exception as e:
        return f"查詢股價失敗：{e}"

def fetch_science_park_youbike():
    """
    查詢新竹科學園區 YouBike 站點資訊
    """
    url = "https://apis.youbike.com.tw/json/area-all.json"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        result = ["新竹科學園區 YouBike 站點", "=" * 30]
        found = False
        for station in data:
            if "科學園區" in station.get("sarea", ""):
                found = True
                result.append(f"站點名稱: {station['sna']}")
                result.append(f"可借車數: {station['sbi']}")
                result.append(f"可還車位: {station['bemp']}")
                result.append(f"地址: {station['ar']}")
                result.append(f"更新時間: {station['mday']}")
                result.append('-' * 30)
        if not found:
            result.append("查無新竹科學園區站點")
        return "\n".join(result)
    except Exception as e:
        return f"查詢失敗：{e}"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("來源ID：", event.source.user_id)
    print("群組ID：", getattr(event.source, "group_id", None))

    msg = event.message.text.strip()
    if msg.startswith("stock"):
        parts = msg.split()
        if len(parts) != 2:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入股票代碼，例如：stock 2330")
            )
            return
        stock_id = parts[1]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=fetch_stock_price(stock_id))
        )
        return

    commands = {
        "/help": lambda: TextSendMessage(
            text=(
                "功能選單：\n"
                "=========================\n"
                "冷笑話 - 隨機獲得一則冷笑話\n"
                "帥哥 - 看一張帥哥圖\n"
                "狗狗 - 看一張狗狗圖\n"
                "ubike - 查詢桃園 YouBike 集福宮站\n"
                "sciencepark - 查詢新竹科學園區 YouBike 站點\n"
                "stock [代碼] - 查詢指定股票即時股價\n"
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
        "ubike": lambda: TextSendMessage(text=fetch_youbike_data()),
        "sciencepark": lambda: TextSendMessage(text=fetch_science_park_youbike()),
    }

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

def notify_deploy_success():
    try:
        line_bot_api.push_message(
            group_id,
            TextSendMessage(text="部署成功 🎉")
        )
        print("已推播部署成功訊息到 LINE 群組")
    except Exception as e:
        print("推播部署成功訊息失敗：", e)

# 在主程式啟動時自動通知
if __name__ == "__main__":
    notify_deploy_success()
    app.run(host="0.0.0.0", port=10000)