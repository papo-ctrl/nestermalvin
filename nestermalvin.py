import json
import requests
import telebot
import pytz
from telebot import types
from datetime import datetime, timedelta

# Настройки
STOCK_API = "https://growagardenapi.vercel.app/api/stock/GetStock"
BOT_TOKEN = "7743478989:AAFRO0MbmhHu3XjvMDjmJqgJDlOKp6M8Yok"

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения времени последнего обновления для каждого чата
last_update_times = {}

# Проверка возможности обновления (защита 30 секунд)
def can_update(chat_id):
    now = datetime.now()
    last_update = last_update_times.get(chat_id)
    if last_update is None:
        return True
    return (now - last_update) > timedelta(seconds=30)

# Обновление времени последнего обновления
def update_last_time(chat_id):
    last_update_times[chat_id] = datetime.now()

# Загружаем данные о семенах из файла
def load_seed_info():
    try:
        with open('seed_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки seed_info.json: {e}")
        return {}

def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    btn1 = types.KeyboardButton("📦 Посмотреть сток")
    btn2 = types.KeyboardButton("🌦️ Узнать погоду")
    markup.add(btn1, btn2)
    return markup

# Получаем информацию о стоке
def get_stock_with_info():
    try:
        # Получаем текущий сток из API
        stock_response = requests.get(STOCK_API, timeout=5)
        stock_data = stock_response.json()
        
        if not stock_data.get('seedsStock'):
            return None, "🛒 Магазин пуст, загляните позже"
        
        # Загружаем информацию о семенах из файла
        seed_info = load_seed_info()
        
        # Форматируем сообщение
        message = "*🌸🌻 МАГАЗИН СЕМЯН 🌻🌸*\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += "🌿 *Доступные семена:*\n\n"
        
        for seed in stock_data['seedsStock']:
            name = seed.get('name')
            value = seed.get('value', seed.get('count', 0))
            
            # Берем данные из seed_info.json
            info = seed_info.get(name, {}) if isinstance(seed_info, dict) else {}
            emoji = info.get('emoji', '🌱')
            price = info.get('price', '?')
            rarity = info.get('rarity', 'Неизвестно')
            
            message += (
                f"- {emoji} ***{name}***\n"
                f"  ├💰 Цена: {price}¢\n"
                f"  ├📦 В наличии: {value} ШТ.\n"
                f"  └🏷 Редкость: {rarity}\n\n"
            )
        
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        current_hour = now.strftime("%H")  # Текущий час
        
        # Получаем минуты из API
        time_response = requests.get("https://growagardenapi.vercel.app/api/stock/Restock-Time", timeout=5)
        time_data = time_response.json()
        api_time = time_data['seeds']['LastRestock']  # "2:10 PM"
        
        # Извлекаем минуты из времени API
        try:
            minutes = datetime.strptime(api_time, "%I:%M %p").strftime("%M")
            fixed_time = f"{current_hour}:{minutes}"  # Комбинируем текущий час + минуты из API
        except:
            fixed_time = now.strftime("%H:%M")  # Если ошибка - используем полностью текущее время
        
        message += (
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ Последнее обновление: *{fixed_time}*\n"
            f"⌛ Прошло времени: *{time_data['seeds']['timeSinceLastRestock']}*\n"
            f"⏳ До следующего: *{time_data['seeds']['countdown']}*\n"
        )
        
        return True, message
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False, f"⚠️ Ошибка загрузки данных"

def load_gear_info():
    try:
        with open('gear_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки gear_info.json: {e}")
        return {}

def get_gear_stock():
    try:
        # Получаем данные о стоке из API
        response = requests.get(STOCK_API, timeout=5)
        stock_data = response.json()
        
        if not stock_data.get('gearStock'):
            return None, "🛒 Раздел предметов пуст, загляните позже"
        
        # Загружаем информацию о предметах из файла
        gear_info = load_gear_info()
        
        # Форматируем сообщение
        message = "*🛠️⚙️ МАГАЗИН ПРЕДМЕТОВ ⚙️🛠️*\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += "📦 *Доступные предметы:*\n\n"
        
        for item in stock_data['gearStock']:
            name = item.get('name')
            value = item.get('value', item.get('count', 0))
            
            # Берем данные из gear_info.json
            info = gear_info.get(name, {}) if isinstance(gear_info, dict) else {}
            emoji = info.get('emoji', '🛠️')
            price = info.get('price', '?')
            rarity = info.get('rarity', 'Обычный')
            
            message += (
                f"- {emoji} ***{name}***\n"
                f"  ├💰 Цена: {price}¢\n"
                f"  ├📦 В наличии: {value} шт.\n"
                f"  └🏷 Редкость: {rarity}\n\n"
            )
        
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        current_hour = now.strftime("%H")
        
        # Получаем время обновления
        time_response = requests.get("https://growagardenapi.vercel.app/api/stock/Restock-Time", timeout=5)
        time_data = time_response.json()
        api_time = time_data['gear']['LastRestock']
        
        try:
            minutes = datetime.strptime(api_time, "%I:%M %p").strftime("%M")
            fixed_time = f"{current_hour}:{minutes}"
        except:
            fixed_time = now.strftime("%H:%M")
        
        message += (
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ Последнее обновление: *{fixed_time}*\n"
            f"⌛ Прошло времени: *{time_data['gear']['timeSinceLastRestock']}*\n"
            f"⏳ До следующего: *{time_data['gear']['countdown']}*\n"
        )
        
        return True, message
        
    except Exception as e:
        print(f"Ошибка загрузки стока предметов: {e}")
        return False, "⚠️ Ошибка загрузки данных"

def load_honey_info():
   try:
        with open('honey_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
   except Exception as e:
        print(f"Ошибка загрузки honey_info.json: {e}")
        return {}

def get_honey_stock():
    try:
        # Получаем данные о стоке из API
        response = requests.get(STOCK_API, timeout=5)
        stock_data = response.json()
        
        if not stock_data.get('honeyStock'):
            return None, "🍯 Ивентовые товары отсутствуют"
        
        # Загружаем информацию о товарах из файла
        honey_info = load_honey_info()
        
        # Форматируем сообщение
        message = "*🍯 ИВЕНТОВЫЕ ТОВАРЫ 🍯*\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += "🎁 *Доступные товары:*\n\n"
        
        for item in stock_data['honeyStock']:
            name = item.get('name')
            value = item.get('value', item.get('count', 0))
            
            # Берем данные из honey_info.json
            info = honey_info.get(name, {}) if isinstance(honey_info, dict) else {}
            emoji = info.get('emoji', '🎁')
            price = info.get('price', '?')
            rarity = info.get('rarity', 'Ивентовый')
            
            message += (
                f"- {emoji} ***{name}***\n"
                f"  ├💰 Цена: {price}¢\n"
                f"  ├📦 В наличии: {value} шт.\n"
                f"  └🏷 Редкость: {rarity}\n\n"
            )

        # Получаем время обновления
        time_response = requests.get("https://growagardenapi.vercel.app/api/stock/Restock-Time", timeout=5)
        time_data = time_response.json()
        event_time = time_data.get('Event', {})
        
        message += (
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ Последнее обновление: *{event_time.get('LastRestock', 'неизвестно')}*\n"
            f"⌛ Прошло времени: *{event_time.get('timeSinceLastRestock', 'неизвестно')}*\n"
            f"⏳ До следующего: *{event_time.get('countdown', 'неизвестно')}*\n"
        )
        
        return True, message
        
    except Exception as e:
        print(f"Ошибка загрузки ивентовых товаров: {e}")
        return False, "⚠️ Ошибка загрузки данных"

def load_cosmetic_info():
    try:
        with open('cosmetic_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки cosmetic_info.json: {e}")
        return {}

def get_cosmetic_stock():
    try:
        # Получаем данные о стоке из API
        response = requests.get(STOCK_API, timeout=5)
        stock_data = response.json()
        
        if not stock_data.get('cosmeticsStock'):
            return None, "💄 Раздел косметики пуст"
        
        # Загружаем информацию о косметике из файла
        cosmetic_info = load_cosmetic_info()
        
        # Форматируем сообщение
        message = "*💄 КОСМЕТИКА В МАГАЗИНЕ 💄*\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += "✨ *Доступные товары:*\n\n"
        
        for item in stock_data['cosmeticsStock']:
            name = item.get('name')
            value = item.get('value', item.get('count', 0))
            
            # Берем данные из cosmetic_info.json
            info = cosmetic_info.get(name, {}) if isinstance(cosmetic_info, dict) else {}
            emoji = info.get('emoji', '💄')
            price = info.get('price', '?')
            rarity = info.get('rarity', 'Обычная')
            
            message += (
                f"- {emoji} ***{name}***\n"
                f"  ├💰 Цена: {price}¢\n"
                f"  ├📦 В наличии: {value} шт.\n"
                f"  └🏷 Редкость: {rarity}\n\n"
            )

        # Получаем время обновления
        time_response = requests.get("https://growagardenapi.vercel.app/api/stock/Restock-Time", timeout=5)
        time_data = time_response.json()
        cosmetic_time = time_data.get('cosmetic', {})
        
        message += (
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ Последнее обновление: *{cosmetic_time.get('LastRestock', 'неизвестно')}*\n"
            f"⌛ Прошло времени: *{cosmetic_time.get('timeSinceLastRestock', 'неизвестно')}*\n"
            f"⏳ До следующего: *{cosmetic_time.get('countdown', 'неизвестно')}*\n"
        )
        
        return True, message
        
    except Exception as e:
        print(f"Ошибка загрузки косметики: {e}")
        return False, "⚠️ Ошибка загрузки данных"

def load_egg_info():
    try:
        with open('egg_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки egg_info.json: {e}")
        return {}

def get_egg_stock():
    try:
        # Получаем данные о стоке из API
        response = requests.get(STOCK_API, timeout=5)
        stock_data = response.json()
        
        if not stock_data.get('eggStock'):
            return None, "🥚 В данный момент яиц нет в продаже"
        
        # Загружаем информацию о яйцах из файла
        egg_info = load_egg_info()
        
        # Форматируем сообщение
        message = "*🥚 УНИКАЛЬНЫЙ АССОРТИМЕНТ ЯИЦ 🥚*\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += "🐣 *Доступные яйца:*\n\n"
        
        for egg in stock_data['eggStock']:
            name = egg.get('name')
            value = egg.get('value', egg.get('count', 0))
            
            # Берем данные из egg_info.json
            info = egg_info.get(name, {}) if isinstance(egg_info, dict) else {}
            emoji = info.get('emoji', '🥚')
            price = info.get('price', '?')
            rarity = info.get('rarity', 'Обычное')
            
            message += (
                f"- {emoji} ***{name}***\n"
                f"  ├💰 Цена: {price}¢\n"
                f"  ├📦 В наличии: {value} шт.\n"
                f"  └🏷 Редкость: {rarity}\n\n"
            )

        # Получаем время обновления
        time_response = requests.get("https://growagardenapi.vercel.app/api/stock/Restock-Time", timeout=5)
        time_data = time_response.json()
        egg_time = time_data.get('egg', {})
        
        # Форматируем время
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        current_hour = now.strftime("%H")
        try:
            minutes = datetime.strptime(egg_time.get('LastRestock', ''), "%I:%M %p").strftime("%M")
            fixed_time = f"{current_hour}:{minutes}"
        except:
            last_restock = now.strftime("%H:%M")
        
        message += (
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ Последнее обновление: *{fixed_time}*\n"
            f"⌛ Прошло времени: *{egg_time.get('timeSinceLastRestock', 'неизвестно')}*\n"
            f"⏳ До следующего: *{egg_time.get('countdown', 'неизвестно')}*\n"
        )
        
        return True, message
        
    except Exception as e:
        print(f"Ошибка загрузки яиц: {e}")
        return False, "⚠️ Ошибка загрузки данных"

# Функция для получения текущей погоды
def get_current_weather():
    try:
        # Получаем данные о погоде из API
        response = requests.get("https://growagardenapi.vercel.app/api/GetWeather", timeout=5)
        weather_data = response.json()
        
        # Создаем сообщение
        message = "***📡 ПОГОДНЫЕ УСЛОВИЯ ПРЯМО СЕЙЧАС:***\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━━\n"

        # Сопоставление weather_id с emoji и названиями
        weather_mapping = {
            "beeswarm": ("🌻", "Пчелиный рой"),
            "frost": ("🧊", "Заморозка"),
            "rain": ("💧", "Дождь"), 
            "thunderstorm": ("⚡", "Шторм"),
            "workingbeeswarm": ("🐝", "Рабочий рой пчел"),
            "nightevent": ("🌑", "Ночь"),
        }

        active_events = []
        max_duration = 0

        # Обрабатываем события из API
        for event in weather_data.get('weather', []):
            event_id = event['weather_id'].lower()
            if event_id in weather_mapping:
                emoji, name = weather_mapping[event_id]
                is_active = event.get('active', False)
                
                if is_active:
                    start_time = event.get('start_duration_unix', 0)
                    end_time = event.get('end_duration_unix', 0)
                    
                    # Форматируем время (жирным)
                    start_str = f"***{datetime.fromtimestamp(start_time).strftime('%H:%M')}***" if start_time > 0 else "??:??"
                    end_str = f"***{datetime.fromtimestamp(end_time).strftime('%H:%M')}***" if end_time > 0 else "??:??"
                    
                    active_events.append(
                        f"{emoji} {name}\n"
                        f"  ├ Статус: ***🟢 Активно***\n"
                        f"  ├ Начало: {start_str}\n"
                        f"  └ Окончание: {end_str}"
                    )
                    
                    current_duration = event.get('duration', 0)
                    if current_duration > max_duration:
                        max_duration = current_duration

        # Если есть активные события
        if active_events:
            message += "\n\n".join(active_events) + "\n\n"
            
            # Конвертируем продолжительность (жирным)
            if max_duration > 0:
                minutes = max_duration // 60
                seconds = max_duration % 60
                duration_str = f"***{minutes} мин {seconds} сек***" if minutes > 0 else f"***{seconds} сек***"
                message += f"⏱️ Продолжительность: {duration_str}\n"
        else:
            message += (
                "***🌤️ В данный момент нет активных погодных событий.***\n"
                "***Отдыхаем... но это ненадолго 👀***\n"
            )

        # Добавляем разделитель
        message += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Добавляем информацию о доступных событиях
        message += "***🌩️ Другие погодные события:***\n"
        for event_id, (emoji, name) in weather_mapping.items():
            message += f"├─ {emoji} {name}\n"
        message += "└───────────────\n"

        return True, message

    except Exception as e:
        print(f"Ошибка при получении погоды: {e}")
        return False, "⚠️ Не удалось получить данные о погоде"

# Текст для мутаций
MUTATIONS_TEXT = (
    "*Все виды мутаций в Grow a Garden:*\n\n"
    "💦 *Влажная мутация* — во время дождя и грозы или с небольшой вероятностью при попадании воды из разбрызгивателей. Умножает цену плода в 2 раза.\n\n"
    "❄️ *Охлаждённая мутация* — во время заморозков или рядом с белым медведем. Умножает цену плода в 2 раза.\n\n"
    "🍫 *Шоколадная мутация* — размещение шоколадного разбрызгивателя во время шоколадного дождя или использование шоколадного спрея мутаций. Умножает цену плода в 2 раза.\n\n"
    "🌑 *Лунная мутация* — ночью 6 растений освещаются лунным светом каждые 2 минуты в течение 10 минут. Умножает цену плода в 2 раза.\n\n"
    "🍯 *Опылённая мутация* — во время роя пчёл или с помощью домашних пчёл (пчела, медоносная пчела, лепестковая пчела, королева пчёл, оса, ястреб-птицеед). Умножает цену плода в 3 раза.\n\n"
    "🔴 *Кровавая мутация* — во время события «Кровавая Луна», которое появляется только при соответствующем ивенте. Умножает цену плода в 4 раза.\n\n"
    "⚫ *Сожжённая мутация* — урожай может сгореть из-за жареной совы. Умножает цену плода в 4 раза.\n\n"
    "✨ *Плазменная мутация* — во время лазерного шторма, который может быть создан только администраторами. Умножает цену плода в 5 раз.\n\n"
    "🍯 *Медовая глазурь мутация* — при использовании медового разбрызгивателя или пчелы Bear Bee. Умножает цену плода в 5 раз.\n\n"
    "😇 *Небесная мутация* — во время события «Летающий Джандель», создаваемого только администраторами. Умножает цену плода в 5 раз.\n\n"
    "🧊 *Замороженная мутация* — при наличии одновременно мутаций Влажная и Охлаждённая, либо у Полярного медведя. Умножает цену плода в 10 раз.\n\n"
    "🍗 *Приготовленная мутация* — с малой вероятностью применяется Жареной Совой вместо Сожжённой мутации. Умножает цену плода в 10 раз.\n\n"
    "🧈 *Золотая мутация* — 1% шанс вырастить замену обычному растению. Посевы могут получить её от стрекозы. Умножает цену плода в 20 раз.\n\n"
    "🧟 *Зомбированная мутация* — урожай может быть заражён недоступной зомби-курицей. Умножает цену плода в 25 раз.\n\n"
    "🌋 *Расплавленная мутация* — урожай может расплавиться из-за извержения вулкана. Умножает цену плода в 25 раз.\n\n"
    "🌈 *Радужная мутация* — 0,1% шанс заменить обычное растение. Также можно получить, если урожай имеет 5+ мутаций, и на него воздействует Бабочка (при этом все другие мутации удаляются). Умножает цену плода в 50 раз.\n\n"
    "⚡️ *Шокированная мутация* — когда в урожай попадает молния во время грозы или шторма Джанделя. Умножает цену плода в 100 раз.\n\n"
    "☄️ *Небесная мутация* — во время метеоритного дождя, при котором урожай поражается звёздами. Умножает цену плода в 120 раз.\n\n"
    "🪩 *Диско мутация* — во время Диско, создаваемого только администраторами. Также урожай может стать Диско от Диско-Пчелы. Умножает цену плода в 125 раз.\n\n"
    "💫 *Метеорная мутация* — во время Метеоритного удара, создаваемого только администраторами. Умножает цену плода в 125 раз.\n\n"
    "🌌 *Тронутая пустотой мутация* — во время события «Чёрная дыра», доступного только администраторам. Умножает цену плода в 135 раз.\n\n"
    "☀️ *Рассвет мутация* — во время события «Бог Солнца»: 4 игрока должны держать 4 урожая подсолнуха, соприкасаясь друг с другом перед Богом Солнца. Может быть создано только администраторами или с крайне низкой вероятностью произойти естественно.\n"
    "Эта мутация применяется только к подсолнуху. Умножает цену плода в 150 раз.\n\n"
    "*На данный момент это все существующие мутации в Grow a Garden!* 🌱"
)

# Глобальная переменная для хранения приветственного текста
WELCOME_TEXT = (
    "✨ *Добро пожаловать\!*\n\n"
    "Этот бот был создан командой @nestermalvin 🛠️\n\n"
    "Он поможет вам:\n"
    "• 📦 Посмотреть, что есть в наличии из семян\n"
    "• 🛠️ Узнать, какие предметы сейчас в стоке\n"
    "• 🍯 Проверить текущий ивент\-сток — там вкусности\n"  
    "• 🌦️ Проверить актуальную погоду\n"
    "• 🌈 Узнать о мутациях\n"
    "• 🥚 Посмотреть, какие яйца есть в наличии\n\n"
    "👇 Выберите нужный раздел:"
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📦 Сток семян", callback_data="show_stock")
    btn2 = types.InlineKeyboardButton("🛠️ Сток предметов", callback_data="show_items")
    btn3 = types.InlineKeyboardButton("🍯 Ивентовые товары", callback_data="show_event")
    btn4 = types.InlineKeyboardButton("🌦️ Текущая погода", callback_data="show_weather")
    btn5 = types.InlineKeyboardButton("🌈 Мутации", callback_data="show_mutations")
    btn6 = types.InlineKeyboardButton("🥚 Доступные яйца", callback_data="show_eggs")
    
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    
    bot.send_message(
        message.chat.id,
        WELCOME_TEXT,
        parse_mode='MarkdownV2',
        reply_markup=markup
    )
    
last_update = {}

# Функция проверки времени обновления
def check_update_time(call):
    user_id = call.from_user.id
    current_time = datetime.now()
    cooldown = timedelta(seconds=30)
    
    if user_id in last_update:
        time_passed = current_time - last_update[user_id]
        if time_passed < cooldown:
            remaining = (cooldown - time_passed).seconds
            bot.answer_callback_query(
                call.id, 
                f"⏰ Подождите еще {remaining} сек. перед обновлением!", 
                show_alert=True
            )
            return False
        else:
            bot.answer_callback_query(call.id, "✅ Обновлено!")
    
    last_update[user_id] = current_time
    return True

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    try:
        chat_id = call.message.chat.id
        
        if call.data == "refresh":
            if not check_update_time(call):
                return
            
            # Определяем, какой раздел обновляем
            if "МАГАЗИН СЕМЯН" in call.message.text:
                call.data = "show_stock"
            elif "МАГАЗИН ПРЕДМЕТОВ" in call.message.text:
                call.data = "show_items"
            elif "ИВЕНТОВЫЕ ТОВАРЫ" in call.message.text:
                call.data = "show_event"
            elif "КОСМЕТИКА" in call.message.text:
                call.data = "show_cosmetics"
            elif "ПОГОДНЫЕ УСЛОВИЯ" in call.message.text:
                call.data = "show_weather"
            elif "АССОРТИМЕНТ ЯИЦ" in call.message.text:
                call.data = "show_eggs"
       
        
        if call.data == "show_stock":
            success, response = get_stock_with_info()
            text = response if success else "⚠️ Ошибка при загрузке стока семян"
            
        elif call.data == "show_weather":
            success, response = get_current_weather()
            text = response if success else "⚠️ Ошибка при загрузке данных о погоде"
            
        elif call.data == "show_mutations":
            text = MUTATIONS_TEXT

        elif call.data == "show_items":
            success, response = get_gear_stock()
            text = response if success else "⚠️ Ошибка при загрузке стока предметов"

        elif call.data == "show_event":
            success, response = get_honey_stock()
            text = response if success else "⚠️ Ошибка при загрузке ивентовых товаров"
            
        elif call.data == "show_eggs":
            success, response = get_egg_stock()
            text = response if success else "⚠️ Ошибка при загрузке информации о яйцах"
            
        elif call.data == "show_cosmetics":
            success, response = get_cosmetic_stock()
            text = response if success else "⚠️ Ошибка при загрузке косметики"
            
        elif call.data == "main_menu":
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("📦 Сток семян", callback_data="show_stock")
            btn2 = types.InlineKeyboardButton("🛠️ Сток предметов", callback_data="show_items")
            btn3 = types.InlineKeyboardButton("🍯 Ивентовые товары", callback_data="show_event")
            btn4 = types.InlineKeyboardButton("🌦️ Текущая погода", callback_data="show_weather")
            btn5 = types.InlineKeyboardButton("🌈 Мутации", callback_data="show_mutations")
            btn6 = types.InlineKeyboardButton("🥚 Доступные яйца", callback_data="show_eggs")
            
            markup.row(btn1, btn2)
            markup.row(btn3, btn4)
            markup.row(btn5, btn6)
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=WELCOME_TEXT,
                parse_mode='MarkdownV2',
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            return
            
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("↩️ Вернуться назад", callback_data="main_menu")
        
        # Добавляем кнопку "Обновить" везде, кроме мутаций
        if call.data != "show_mutations":
            refresh_btn = types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh")
            markup.row(refresh_btn)
            markup.row(back_btn)
        else:
            markup.add(back_btn)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка обработки callback: {e}")
        bot.answer_callback_query(call.id, "⚠️ Произошла ошибка")

@bot.message_handler(func=lambda message: message.text == "📦 Посмотреть сток")
def show_stock(message):
    bot.send_chat_action(message.chat.id, 'typing')
    success, response = get_stock_with_info()
    
    if success:
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("↩️ Вернуться назад", callback_data="main_menu")
        refresh_btn = types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh")
        markup.row(refresh_btn)
        markup.row(back_btn)
        
        bot.send_message(
            message.chat.id,
            response,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Не удалось загрузить данные о стоке.",
            reply_markup=create_main_menu()
        )

@bot.message_handler(func=lambda message: message.text == "🌦️ Узнать погоду")
def show_weather(message):
    bot.send_chat_action(message.chat.id, 'typing')
    success, response = get_current_weather()
    
    if success:
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("↩️ Вернуться назад", callback_data="main_menu")
        refresh_btn = types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh")
        markup.row(refresh_btn)
        markup.row(back_btn)
        
        bot.send_message(
            message.chat.id,
            response,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            response,
            reply_markup=create_main_menu()
        )

@bot.message_handler(func=lambda message: message.text == "🛠️ Сток предметов")
def show_gear_stock(message):
    bot.send_chat_action(message.chat.id, 'typing')
    success, response = get_gear_stock()
    
    if success:
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("↩️ Вернуться назад", callback_data="main_menu")
        refresh_btn = types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh")
        markup.row(refresh_btn)
        markup.row(back_btn)
        bot.send_message(
            message.chat.id,
            response,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Не удалось загрузить данные о предметах",
            reply_markup=create_main_menu()
        )

@bot.message_handler(func=lambda message: message.text == "🍯 Ивентовые товары")
def show_honey_stock(message):
    bot.send_chat_action(message.chat.id, 'typing')
    success, response = get_honey_stock()
    
    if success:
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("↩️ Вернуться назад", callback_data="main_menu")
        refresh_btn = types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh")
        markup.row(refresh_btn)
        markup.row(back_btn)
        
        bot.send_message(
            message.chat.id,
            response,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Не удалось загрузить ивентовые товары",
            reply_markup=create_main_menu()
        )


@bot.message_handler(func=lambda message: message.text == "🥚 Доступные яйца")
def show_egg_stock(message):
    bot.send_chat_action(message.chat.id, 'typing')
    success, response = get_egg_stock()
    
    if success:
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("↩️ Вернуться назад", callback_data="main_menu")
        refresh_btn = types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh")
        markup.row(refresh_btn)
        markup.row(back_btn)
        bot.send_message(
            message.chat.id,
            response,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Не удалось загрузить информацию о яйцах",
            reply_markup=create_main_menu()
        )

if __name__ == '__main__':
    print("🌸 Бот запущен и готов к работе!")
    bot.infinity_polling()