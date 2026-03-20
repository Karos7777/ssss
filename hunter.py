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
# Вставь сюда свои реальные токены и ID!
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

# --- ПАМЯТЬ БОТА (чтобы не спамить) ---
seen_alerts = set()
last_cleared_day = None

def send_tg_message(text):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        http.post(url, json={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Ошибка в Telegram: {e}")

def check_date(date_str, is_today):
    global seen_alerts
    
    url = f"https://couriers.uzumtezkor.uz/app/v3/available-shifts?limit=100&offset=0&desiredDate={date_str}"
    try:
        response = http.get(url, headers=HEADERS, timeout=10)
        
        # Печатаем статус ответа для каждой даты, чтобы видеть активность в логах
        print(f"   - {date_str}: Статус {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            for item in items:
                start_raw = item.get("startAt", "")
                end_raw = item.get("endAt", "")
                
                # Достаем время аккуратно
                start = start_raw.split("T")[-1][:5] if "T" in start_raw else "..."
                end = end_raw.split("T")[-1][:5] if "T" in end_raw else "..."
                point = item.get("startingPoint", {}).get("title", "Неизвестно")
                
                # Уникальный ID смены (чтобы отличать их друг от друга)
                shift_signature = f"{date_str}_{point}_{start}_{end}"
                
                # Проверка на бонусы
                is_bonus = item.get("bonuses") or (item.get("bonusIDs") and len(item.get("bonusIDs")) > 0)
                
                if is_bonus:
                    alert_key = f"bonus_{shift_signature}"
                    if alert_key not in seen_alerts:
                        seen_alerts.add(alert_key)
                        msg = f"💰 *БОНУС НАЙДЕН!*\n📅 *Дата:* {date_str}\n📍 *Точка:* {point}\n⏰ *Время:* {start} - {end}"
                        print(f"!!! НАЙДЕН БОНУС: {point} {start}-{end}")
                        send_tg_message(msg)
                
                # Проверка на обычные смены, если это СЕГОДНЯ
                if is_today and not is_bonus:
                    alert_key = f"today_{shift_signature}"
                    if alert_key not in seen_alerts:
                        seen_alerts.add(alert_key)
                        msg = f"🆕 *Появилась смена на СЕГОДНЯ!*\n📍 *Точка:* {point}\n⏰ *Время:* {start} - {end}\n_Скорее забирай!_"
                        print(f"!!! НОВАЯ СМЕНА СЕГОДНЯ: {point} {start}-{end}")
                        send_tg_message(msg)
                        
            return True # Успешно проверили
            
        elif response.status_code == 401:
            return "AUTH_ERROR"
            
    except Exception as e:
        print(f"Ошибка запроса {date_str}: {e}")
        
    return False

def main_logic():
    global last_cleared_day, seen_alerts
    last_report_date = None

    print("🚀 Мониторинг запущен.")
    while True:
        today_date = datetime.date.today()
        now = datetime.datetime.now()
        
        # 1. Очистка памяти бота при наступлении нового дня (полночь)
        if last_cleared_day != today_date:
            seen_alerts.clear()
            last_cleared_day = today_date
            
        # 2. Ежедневный утренний отчет (в 9:00 утра)
        if now.hour == 9 and last_report_date != today_date:
            send_tg_message(f"✅ *Утренний отчет*\nБот успешно проработал ночь и продолжает искать смены!\n_Текущее время: {now.strftime('%H:%M')}_")
            last_report_date = today_date

        print(f"\n--- [ {now.strftime('%H:%M:%S')} ] Начинаю новый круг проверки ---")
        
        for i in range(DAYS_AHEAD):
            current_date = (today_date + datetime.timedelta(days=i)).isoformat()
            is_today = (i == 0) # True, если проверяем текущий день
            
            res = check_date(current_date, is_today)
            
            if res == "AUTH_ERROR":
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: Токен устарел!")
                send_tg_message("🛑 *БОТ ОСТАНОВЛЕН:* Обнови токен Bearer в коде!")
                return # Выходим из цикла, бот остановится
            
            # Небольшая пауза между запросами внутри круга
            time.sleep(random.uniform(2, 5))
        
        # Большая пауза между кругами
        wait_time = random.randint(60, 120)
        print(f"✅ Круг завершен успешно. Спим {wait_time} сек...")
        time.sleep(wait_time)

if __name__ == "__main__":
    # Запускаем веб-сервер в фоне (чтобы Render не ругался)
    t = threading.Thread(target=run_web_server)
    t.start()
    
    # Запускаем основную логику бота
    main_logic()