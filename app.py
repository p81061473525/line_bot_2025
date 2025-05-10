from apscheduler.schedulers.background import BackgroundScheduler
import datetime
# ...existing code...

# 自動推播訊息（每1分鐘）
def send_greeting():
    user_id = "<你的用戶ID或群組ID>"  # 請填入你的 LINE User ID 或 Group ID
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

# ...existing code...
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)