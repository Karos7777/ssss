import requests
import time
import datetime
import random
import threading
from flask import Flask

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Бот активен и работает!"

def run_web_server():
    # Render передает порт через переменную окружения
    app.run(host='0.0.0.0', port=10000)

# --- ТВОИ НАСТРОЙКИ ---
TOKEN = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImdlbmVyYWwiLCJ0eXAiOiJKV1QifQ.eyJjb3VyaWVyX2lkIjoiODE3ODAiLCJleHAiOjE3NzQxMDQ2MzUsInJlYWxtIjoiY291cmllciIsInNjb3BlIjoiY291cmllci5hdXRob3JpemVkIiwic3ViIjoiZmQ0Njc2MDUtNjY1NC00YjQ1LWFjMTQtNmRlNWZhMWRlNTA4In0.lssiM8Yl1LmRcMxcdfqvljS_jfyzAdltAgyKSNG4yXwjKRMWljbk7p4cidLXTwInba7815eWc9j9pXpBJ2aNF4v8sI0exXFq-tJphVanHZOToY7jIktTZJM6Q7VhQVPen45MNHyVOCvbPI08UrbwOKPNmIvn_FG1x8Y6guprKM6AQHN2bIykpAFkief5kc5QnMONtK_HjkbJHGgYV86S--MUBT2OK2LZ81fkHy2TpXTxhjASUPomR3xBbn-WC4ReSaOTxoHaJuddescJ89YJVBiCZeXD9vVzVuqHftuCpcIm6w90zdW0PFPXdj3ZFmgh7fjRRQcizqEBVq3mTJd7Og"
TG_BOT_TOKEN = "6740270464:AAFq4N8Wm3Tnhow5ltuzqluDAVr8OO8tN1E"
TG_CHAT_ID = "853232715"
DAYS_AHEAD = 7

http = requests.Session()
http.trust_env = False 

HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile)",
    "Accept": "application/json"
}

def send_tg_message(text):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        http.post(url, json={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Ошибка в Telegram: {e}")

def check_date(date_str):
    url = f"https://couriers.uzumtezkor.uz/app/v3/available-shifts?limit=100&offset=0&desiredDate={date_str}"
    try:
        response = http.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            for item in items:
                if item.get("bonuses") or (item.get("bonusIDs") and len(item.get("bonusIDs")) > 0):
                    start = item.get("startAt").split("T")[1][:5]
                    end = item.get("endAt").split("T")[1][:5]
                    point = item.get("startingPoint", {}).get("title", "Неизвестно")
                    msg = f"💰 *БОНУС НАЙДЕН!*\n📅 *Дата:* {date_str}\n📍 *Точка:* {point}\n⏰ *Время:* {start} - {end}"
                    send_tg_message(msg)
                    return True
            return False
        elif response.status_code == 401:
            return "AUTH_ERROR"
    except Exception as e:
        print(f"Ошибка запроса {date_str}: {e}")
    return False

def main_logic():
    print("🚀 Мониторинг запущен.")
    while True:
        today = datetime.date.today()
        for i in range(DAYS_AHEAD):
            current_date = (today + datetime.timedelta(days=i)).isoformat()
            res = check_date(current_date)
            if res == "AUTH_ERROR":
                send_tg_message("🛑 Токен протух!")
                return
            time.sleep(random.uniform(2, 5))
        
        wait_time = random.randint(60, 120)
        print(f"Круг завершен. Ждем {wait_time} сек.")
        time.sleep(wait_time)

if __name__ == "__main__":
    # Запускаем веб-сервер в фоне
    t = threading.Thread(target=run_web_server)
    t.start()
    # Запускаем логику бота
    main_logic()