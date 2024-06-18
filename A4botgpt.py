import openai
import telebot
import requests
from io import BytesIO
from random import choice


# Ключи доступа
telegram_key = 'None'
KEY = 'None'
GOOGLE_API_KEY = 'None'
GOOGLE_CSE_ID = 'None'
openai.api_key = KEY


bot = telebot.TeleBot(telegram_key)


# Структура для хранения истории и текущего состояния каждого пользователя
users_state = {}


authorization_keys = {
       "gpt4_dalle": ["KIbZpNpBaBli", "qjmXqSKjvLHB", "GMxWtVObmQTc"],
   "gpt3": ["xfCIOUPEeSsv", "yOoDmVmgldEU", "jhbqhIXIQFEG"]
}
preliminary_replies = {
   "gpt3": [
       "Принято! Дайте мне секундочку, скоро всё будет готово.",
       "Отличный запрос! Сейчас я подумаю и отвечу.",
       "Размышляю... Пожалуйста, ожидайте ответа.",
       "Ваш запрос отправлен в обработку. Скоро узнаете результат!",
       "Задача понята, начинаю работу над ответом.",
       "Интересный вопрос! Позвольте мне немного подумать.",
       "Хорошо, сейчас я подготовлю для вас всю необходимую информацию.",
       "Ваше обращение в процессе обработки. Ответ не заставит себя долго ждать.",
       "Приступаю к генерации ответа. Спасибо за ваше терпение!",
       "Обрабатываю ваш запрос... Подготовка ответа уже началась."
   ],
   "gpt4": [
       "Принято! Дайте мне секундочку, скоро всё будет готово.",
       "Отличный запрос! Сейчас я подумаю и отвечу.",
       "Размышляю... Пожалуйста, ожидайте ответа.",
       "Ваш запрос отправлен в обработку. Скоро узнаете результат!",
       "Задача понята, начинаю работу над ответом.",
       "Интересный вопрос! Позвольте мне немного подумать.",
       "Хорошо, сейчас я подготовлю для вас всю необходимую информацию.",
       "Ваше обращение в процессе обработки. Ответ не заставит себя долго ждать.",
       "Приступаю к генерации ответа. Спасибо за ваше терпение!",
       "Обрабатываю ваш запрос... Подготовка ответа уже началась."
   ],
   "dalle": [
       "Запускаю волшебство DALL-E! Скоро ваше изображение будет готово.",
       "Интересный выбор! Давайте посмотрим, что у нас получится.",
       "Ваше творческое задание принято. Начинаю создание шедевра.",
       "Генерирую изображение... Пожалуйста, подождите немного.",
       "Подготавливаю что-то особенное для вас. Ожидайте секундочку!",
       "Принято к исполнению. Ваше искусство на подходе!",
       "Идет процесс создания... Ваш запрос воплощается в изображение.",
       "Секундочку, я превращаю ваш запрос в визуальный шедевр.",
       "О, это будет интересно! Сейчас увидите результат моей работы.",
       "Ваше воображение вдохновляет! Приступаю к генерации изображения."
   ]
}


@bot.message_handler(commands=['start'])
def start(message):
   user_id = message.chat.id
   if user_id not in users_state:
       users_state[user_id] = {"mode": None, "history": [], "image_prompt": "", "authorized": False, "command_selected": False}
   reply = "Привет, это ChatGPT бот для сотрудников A4 Production. Чтобы получить ключ авторизации, напишите @bullfinch"
   bot.reply_to(message, reply)


@bot.message_handler(commands=['command'])
def command(message):
   commands_list = """
Привет, это все команды бота:
/start - Запуск бота
/gpt4 - Перейти на модель ChatGPT4
/gpt3 - Перейти на модель ChatGPT3
/dalle - Генерация изображений
/info - Информация о своем аккаунте
/help - Техническая поддержка
/command - Все доступные команды
"""
   bot.reply_to(message, commands_list)


@bot.message_handler(commands=['help'])
def help_command(message):
   help_message = "Для получения технической поддержки, помощи по запросам и промтам, обращайтесь к @PandaPanda322"
   bot.reply_to(message, help_message)


@bot.message_handler(func=lambda message: not users_state.get(message.chat.id, {}).get("authorized", False))
def handle_authorization(message):
   user_id = message.chat.id
   key = message.text.strip()
   welcome_message = ""
   if key in authorization_keys["gpt4_dalle"]:
       users_state[user_id].update({"authorized": True, "authorization_level": "gpt4_dalle", "command_selected": False})
       welcome_message = (
           "Поздравляю, вы успешно авторизованы для использования команд /gpt4 и /dalle.\n\n"
           "Перед тем, как приступить к работе с ботом, пожалуйста, ознакомьтесь с командами и советами. Все доступные команды:\n"
           "/start - Запуск бота\n"
           "/gpt4 - Перейти на модель ChatGPT4\n"
           "/dalle - Генерация изображений\n"
           "/info - Информация о своем аккаунте\n"
           "/help - Техническая поддержка\n"
           "/command - Все доступные команды\n\n"
           "Для того, чтобы найти информацию в интернете, воспользуйтесь ключевым словом \"Найди:\". Например, \"Найди: Погода в Москве сегодня?\"\n\n"
           "Если вы используете команду /dalle для генерации изображений, то каждое ваше сгенерированное новое изображение будет отталкиваться от предыдущего, тем самым, вы можете исправлять свой прошлый запрос и генерировать на основе этой истории новое изображение. Но если вы хотите, чтобы бот сгенерировал совсем другое изображение без привязки к истории, то используйте ключевое слово \"Сгенерируй изображение\". Например: \"Сгенерируй изображение спортивного автомобиля на трассе\"."
       )
   elif key in authorization_keys["gpt3"]:
       users_state[user_id].update({"authorized": True, "authorization_level": "gpt3", "command_selected": False})
       welcome_message = (
           "Поздравляю, вы успешно авторизованы для использования команды /gpt3.\n\n"
           "Перед тем, как приступить к работе с ботом, пожалуйста, ознакомьтесь с командами и советами. Все доступные команды:\n"
           "/start - Запуск бота\n"
           "/gpt3 - Перейти на модель ChatGPT3\n"
           "/info - Информация о своем аккаунте\n"
           "/help - Техническая поддержка\n"
           "/command - Все доступные команды\n\n"
           "Для того, чтобы найти информацию в интернете, воспользуйтесь ключевым словом \"Найди:\". Например, \"Найди: Погода в Москве сегодня?\""
       )
   else:
       bot.send_message(user_id, "Неправильный ключ авторизации. Пожалуйста, попробуйте снова.")
       return


   bot.send_message(user_id, welcome_message)


@bot.message_handler(commands=['start', 'command', 'help', 'info', 'gpt3', 'gpt4', 'dalle'])
def command_handler(message):
   if message.text == '/start':
       start(message)
   elif message.text == '/command':
       command(message)
   elif message.text == '/help':
       help_command(message)
   elif message.text == '/info':
       send_user_info(message)
   elif message.text in ['/gpt3', '/gpt4', '/dalle']:
       set_mode(message)


@bot.message_handler(func=lambda message: message.text.startswith("/"))
def unknown_command(message):
   bot.reply_to(message, "К сожалению, такой команды не существует. Пожалуйста, используйте /command, чтобы увидеть список всех доступных команд.")


def google_search(query):
   search_url = "https://www.googleapis.com/customsearch/v1"
   params = {'key': GOOGLE_API_KEY, 'cx': GOOGLE_CSE_ID, 'q': query}
   response = requests.get(search_url, params=params)
   result = response.json()
   return result


@bot.message_handler(commands=['info'])
def send_user_info(message):
   user_id = message.chat.id
   user_info = users_state.get(user_id, {})


   if not user_info.get("authorized", False):
       bot.reply_to(message, "Статус авторизации: Вы не авторизованы.")
       return


   authorization_level_msg = "Неизвестно"
   if user_info.get("authorization_level") == "gpt4_dalle":
       authorization_level_msg = "Вам доступен ChatGPT4 и DALL-E"
   elif user_info.get("authorization_level") == "gpt3":
       authorization_level_msg = "Вам доступен ChatGPT3"


   mode = "Не выбран"
   if user_info.get("mode") == "gpt3":
       mode = "ChatGPT3"
   elif user_info.get("mode") == "gpt4":
       mode = "ChatGPT4"
   elif user_info.get("mode") == "dalle":
       mode = "DALL-E"


   total_requests = len([msg for msg in user_info.get("history", []) if msg["role"] == "user"])


   response_message = (
       f"Статус авторизации: Авторизован\n"
       f"Уровень доступа: {authorization_level_msg}\n"
       f"Текущий режим: {mode}\n"
       f"Количество запросов: {total_requests}\n"
   )
   bot.send_message(user_id, response_message)


@bot.message_handler(commands=['gpt3', 'gpt4', 'dalle'])
def set_mode(message):
   user_id = message.chat.id
   if users_state[user_id].get("authorized", False):
       mode = message.text[1:]  # Убираем / из команды для определения режима
       authorization_level = users_state[user_id].get("authorization_level", "")
       if (mode == "gpt3" and authorization_level == "gpt3") or (mode in ["gpt4", "dalle"] and authorization_level == "gpt4_dalle"):
           users_state[user_id].update({"mode": mode, "command_selected": True})
           bot.reply_to(message, f"Режим установлен на {mode.upper()}. Введите ваш запрос.")
       else:
           bot.reply_to(message, "У вас нет доступа к этой команде.")
   else:
       bot.reply_to(message, "Вы не авторизованы. Пожалуйста, введите ключ авторизации.")


@bot.message_handler(func=lambda message: message.text.lower().startswith("найди:"))
def handle_search_query(message):
   # Удаляем начальное "найди:" (вместе с возможным пробелом) из сообщения, независимо от регистра
   query = message.text.lower().split("найди:",1)[1].lstrip()
   search_results = google_search(query)
   reply = "Вот что я нашел:\n\n"
   for item in search_results.get('items', [])[:3]:  # Выводим первые 5 результатов
       reply += f"{item.get('title')}\n{item.get('link')}\n\n"
   bot.reply_to(message, reply)




@bot.message_handler(func=lambda message: True)
def handle_message(message):
   user_id = message.chat.id
   text = message.text


   if user_id not in users_state or not users_state[user_id].get("authorized", False):
       bot.send_message(user_id, "Вы не авторизованы. Пожалуйста, введите ключ авторизации.")
       return
   elif not users_state[user_id].get("mode", False):
       bot.send_message(user_id, "Пожалуйста, выберите режим работы сначала (/gpt3, /gpt4, /dalle).")
       return


   mode = users_state[user_id]["mode"]
   preliminary_reply = choice(preliminary_replies[mode])
   message_to_delete = bot.reply_to(message, preliminary_reply)


   if mode == "dalle":
       process_dalle_request(user_id, text, message_to_delete.message_id)
   else:
       process_gpt_request(user_id, text, mode, message_to_delete.message_id, message)




def process_dalle_request(user_id, text, message_to_delete_id):
   if text.startswith("Сгенерируй изображение"):
       users_state[user_id]["image_prompt"] = text[len("Сгенерируй изображение"):].strip()
   else:
       if users_state[user_id]["image_prompt"]:
           users_state[user_id]["image_prompt"] += ", " + text
       else:
           users_state[user_id]["image_prompt"] = text


   # Вызываем функцию генерации изображения
   generate_image(users_state[user_id]["image_prompt"], user_id, message_to_delete_id)




def generate_image(prompt, user_id, message_to_delete_id):
   try:
       response = requests.post(
           "https://api.openai.com/v1/images/generations",
           headers={"Authorization": f"Bearer {KEY}"},
           json={"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "1024x1024"}
       )
       response.raise_for_status()
       image_url = response.json()['data'][0]['url']
       image_response = requests.get(image_url)
       bot.send_photo(user_id, photo=BytesIO(image_response.content))


       # Запись в историю при успешной генерации
       users_state[user_id]["history"].append({"role": "user", "content": prompt})
   except Exception as e:
       bot.send_message(user_id, "Извините, произошла ошибка при генерации изображения.")
   finally:
       try:
           bot.delete_message(chat_id=user_id, message_id=message_to_delete_id)
       except Exception as e:
           print(f"Не удалось удалить сообщение: {e}")




def process_gpt_request(user_id, text, mode, message_to_delete_id, message):
   if text.startswith("/"):
       # Пропускаем команды, начинающиеся с "/"
       return


   model = "gpt-3.5-turbo-0125" if mode == "gpt3" else "gpt-4-0125-preview"


   if not users_state[user_id].get("history"):
       # Если история пуста, добавляем начальное сообщение
       users_state[user_id]["history"] = [{"role": "system", "content": "Чат начат"}]


   messages = users_state[user_id]["history"]


   # Добавляем сообщение пользователя в историю
   users_state[user_id]["history"].append({"role": "user", "content": text})


   try:
       response = openai.ChatCompletion.create(
           model=model,
           messages=messages,
           max_tokens=1000,
           temperature=0.7
       )
       reply_text = response.choices[0].message['content'].strip()


       bot.send_message(user_id, reply_text)
       # Добавляем ответ бота в историю
       users_state[user_id]["history"].append({"role": "assistant", "content": reply_text})


   except Exception as e:
       bot.send_message(user_id, f"Извините, произошла ошибка: {e}")
   finally:
       try:
           bot.delete_message(chat_id=user_id, message_id=message_to_delete_id)
       except Exception as e:
           print(f"Не удалось удалить сообщение: {e}")




bot.polling(none_stop=True)


#model = "gpt-3.5-turbo-0125" if mode == "gpt3" else "gpt-4-0125-preview"

