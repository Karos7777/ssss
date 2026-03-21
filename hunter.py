import requests
import time
import datetime
import random
import threading
import telebot # Добавили библиотеку для бота
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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

# Инициализируем бота
bot = telebot.TeleBot(TG_BOT_TOKEN)

# --- БАЗА КООРДИНАТ ДЛЯ КАРТ ---
# ВАЖНО: Ключ в словаре должен ТОЧНО совпадать с названием точки, которое выдает сервер!
# Замени нули на реальные координаты широты (lat) и долготы (lon)
LOCATIONS = {
    'loc_1': {'title': 'Next new', 'lat': 41.297773, 'lon': 69.249518, 'address': 'Ташкент'},
    'loc_2': {'title': 'Ecopark', 'lat': 41.310891, 'lon': 69.295064, 'address': 'Ташкент'},
    'loc_3': {'title': 'Хамза', 'lat': 41.277050, 'lon': 69.309304, 'address': 'Ташкент'},
    'loc_4': {'title': 'Компас', 'lat': 41.239107, 'lon': 69.328735, 'address': 'Ташкент'},
    'loc_5': {'title': 'Evos Vodnik', 'lat': 41.254433, 'lon': 69.373943, 'address': 'Ташкент'},
    'loc_6': {'title': 'Турон new', 'lat': 41.210690, 'lon': 69.234009, 'address': 'Ташкент'},
    'loc_7': {'title': 'Сергели new', 'lat': 41.220839, 'lon': 69.208723, 'address': 'Ташкент'},
    'loc_8': {'title': 'Северный вокзал new', 'lat': 41.298205, 'lon': 69.280666, 'address': 'Ташкент'},
    'loc_9': {'title': 'Кушбеги new', 'lat': 41.267813, 'lon': 69.245708, 'address': 'Ташкент'},
    'loc_10': {'title': 'Айбек new', 'lat': 41.295091, 'lon': 69.268025, 'address': 'Ташкент'},
    'loc_11': {'title': 'Мукими new', 'lat': 41.283513, 'lon': 69.250288, 'address': 'Ташкент'},
    'loc_12': {'title': 'Чиланзар new', 'lat': 41.274358, 'lon': 69.204907, 'address': 'Ташкент'},
    'loc_13': {'title': 'Эшон new', 'lat': 41.279378, 'lon': 69.197978, 'address': 'Ташкент'},
    'loc_14': {'title': '26-квартал Чиланзар new', 'lat': 41.278429, 'lon': 69.175985, 'address': 'Ташкент'},
    'loc_15': {'title': 'Новза new', 'lat': 41.293438, 'lon': 69.212942, 'address': 'Ташкент'},
    'loc_16': {'title': 'Бешкайрач new', 'lat': 41.308305, 'lon': 69.166052, 'address': 'Ташкент'},
    'loc_17': {'title': 'Кукча', 'lat': 41.322375, 'lon': 69.214996, 'address': 'Ташкент'},
    'loc_18': {'title': 'Цирк new', 'lat': 41.324182, 'lon': 69.242967, 'address': 'Ташкент'},
    'loc_19': {'title': 'Беруни new', 'lat': 41.345170, 'lon': 69.206932, 'address': 'Ташкент'},
    'loc_20': {'title': 'Фараби new', 'lat': 41.349068, 'lon': 69.178269, 'address': 'Ташкент'},
    'loc_21': {'title': 'Каракамыш new', 'lat': 41.364242, 'lon': 69.203741, 'address': 'Ташкент'},
    'loc_22': {'title': 'Алайский рынок new', 'lat': 41.320219, 'lon': 69.281739, 'address': 'Ташкент'},
    'loc_23': {'title': 'Малика new', 'lat': 41.338937, 'lon': 69.271314, 'address': 'Ташкент'},
    'loc_24': {'title': 'Яшнабад new', 'lat': 41.291723, 'lon': 69.340694, 'address': 'Ташкент'},
    'loc_25': {'title': 'Паркентский new', 'lat': 41.315182, 'lon': 69.328165, 'address': 'Ташкент'},
    'loc_26': {'title': 'Бий new', 'lat': 41.326520, 'lon': 69.329992, 'address': 'Ташкент'},
    'loc_27': {'title': 'Корасу new', 'lat': 41.334586, 'lon': 69.370051, 'address': 'Ташкент'},
    'loc_28': {'title': 'Экобазар new', 'lat': 41.353421, 'lon': 69.351013, 'address': 'Ташкент'},
    'loc_29': {'title': 'Юнусабад', 'lat': 41.365258, 'lon': 69.295216, 'address': 'Ташкент'},
    'loc_30': {'title': 'Туркестан new', 'lat': 41.373312, 'lon': 69.308444, 'address': 'Ташкент'}
}

http = requests.Session()
http.trust_env = False 

HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile)",
    "Accept": "application/json"
}

# --- ПАМЯТЬ БОТА ---
seen_alerts = set()
last_cleared_day = None

# ОБНОВЛЕННАЯ функция отправки сообщений (теперь через telebot)
def send_tg_message(text, markup=None):
    try:
        # Отправляем сообщение, и если есть клавиатура (markup), прикрепляем её
        bot.send_message(chat_id=TG_CHAT_ID, text=text, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        print(f"Ошибка в Telegram: {e}")

def check_date(date_str, is_today):
    global seen_alerts
    
    url = f"https://couriers.uzumtezkor.uz/app/v3/available-shifts?limit=100&offset=0&desiredDate={date_str}"
    try:
        response = http.get(url, headers=HEADERS, timeout=10)
        print(f"   - {date_str}: Статус {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            for item in items:
                start_raw = item.get("startAt", "")
                end_raw = item.get("endAt", "")
                
                start = start_raw.split("T")[-1][:5] if "T" in start_raw else "..."
                end = end_raw.split("T")[-1][:5] if "T" in end_raw else "..."
                point = item.get("startingPoint", {}).get("title", "Неизвестно")
                
                shift_signature = f"{date_str}_{point}_{start}_{end}"
                is_bonus = item.get("bonuses") or (item.get("bonusIDs") and len(item.get("bonusIDs")) > 0)
                
                # --- ГЕНЕРАЦИЯ КНОПКИ С КАРТОЙ ---
                markup = None
                # Проверяем, есть ли эта точка в нашей базе LOCATIONS
                if point in LOCATIONS:
                    loc_data = LOCATIONS[point]
                    markup = InlineKeyboardMarkup()
                    btn = InlineKeyboardButton(
                        text="📍 Показать на карте", 
                        callback_data=f"map_{loc_data['id']}" # Зашиваем короткий ID в кнопку
                    )
                    markup.add(btn)
                
                if is_bonus:
                    alert_key = f"bonus_{shift_signature}"
                    if alert_key not in seen_alerts:
                        seen_alerts.add(alert_key)
                        msg = f"💰 *БОНУС НАЙДЕН!*\n📅 *Дата:* {date_str}\n📍 *Точка:* {point}\n⏰ *Время:* {start} - {end}"
                        print(f"!!! НАЙДЕН БОНУС: {point} {start}-{end}")
                        send_tg_message(msg, markup) # Отправляем с кнопкой
                
                if is_today and not is_bonus:
                    alert_key = f"today_{shift_signature}"
                    if alert_key not in seen_alerts:
                        seen_alerts.add(alert_key)
                        msg = f"🆕 *Появилась смена на СЕГОДНЯ!*\n📍 *Точка:* {point}\n⏰ *Время:* {start} - {end}\n_Скорее забирай!_"
                        print(f"!!! НОВАЯ СМЕНА СЕГОДНЯ: {point} {start}-{end}")
                        send_tg_message(msg, markup) # Отправляем с кнопкой
                        
            return True 
            
        elif response.status_code == 401:
            return "AUTH_ERROR"
            
    except Exception as e:
        print(f"Ошибка запроса {date_str}: {e}")
        
    return False

def main_logic():
    global last_cleared_day, seen_alerts
    last_report_date = None

    print("🚀 Мониторинг слотов запущен.")
    while True:
        today_date = datetime.date.today()
        now = datetime.datetime.now()
        
        if last_cleared_day != today_date:
            seen_alerts.clear()
            last_cleared_day = today_date
            
        if now.hour == 9 and last_report_date != today_date:
            send_tg_message(f"✅ *Утренний отчет*\nБот успешно проработал ночь и продолжает искать смены!\n_Текущее время: {now.strftime('%H:%M')}_")
            last_report_date = today_date

        print(f"\n--- [ {now.strftime('%H:%M:%S')} ] Начинаю новый круг проверки ---")
        
        for i in range(DAYS_AHEAD):
            current_date = (today_date + datetime.timedelta(days=i)).isoformat()
            is_today = (i == 0)
            
            res = check_date(current_date, is_today)
            
            if res == "AUTH_ERROR":
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: Токен устарел!")
                send_tg_message("🛑 *БОТ ОСТАНОВЛЕН:* Обнови токен Bearer в коде!")
                return 
            
            time.sleep(random.uniform(2, 5))
        
        wait_time = random.randint(60, 120)
        print(f"✅ Круг завершен успешно. Спим {wait_time} сек...")
        time.sleep(wait_time)

# --- ОБРАБОТЧИК КНОПОК ДЛЯ КАРТ ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('map_'))
def handle_map_button(call):
    # Достаем ID (например, 'loc_1')
    loc_id = call.data.replace('map_', '')
    
    # Ищем эту точку в нашей базе
    found_point = None
    for point_name, data in LOCATIONS.items():
        if data['id'] == loc_id:
            found_point = data
            found_title = point_name
            break
            
    if found_point:
        if found_point['lat'] == 0.0 or found_point['lon'] == 0.0:
            bot.answer_callback_query(call.id, f"⚠️ Координаты для {found_title} еще не настроены!", show_alert=True)
        else:
            bot.send_venue(
                chat_id=call.message.chat.id,
                latitude=found_point['lat'],
                longitude=found_point['lon'],
                title=found_title,
                address=found_point['address']
            )
            bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(call.id, "Ошибка: локация не найдена.", show_alert=True)

if __name__ == "__main__":
    # 1. Запускаем веб-сервер в фоне для Render
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # 2. Запускаем мониторинг слотов в отдельном фоне
    threading.Thread(target=main_logic, daemon=True).start()
    
    # 3. Запускаем бота-слушателя в главном потоке (чтобы код не закрывался)
    print("🤖 Бот Telegram запущен и ждет нажатий на кнопки!")
    bot.polling(none_stop=True)