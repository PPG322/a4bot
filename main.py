import openai
import telebot
import requests
from io import BytesIO
from random import choice

# Ключи доступа
telegram_key = '6935184645:AAE9yi2SaC_HYnV7-aHI2GHSyaW-CjnBpkA'
KEY = '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'
openai.api_key = KEY

bot = telebot.TeleBot(telegram_key)

# Структура для хранения истории и текущего состояния каждого пользователя
users_state = {}

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
        "Запускаю волшебство DALL-E! Скоро ваше изображение будет готово."
        "Интересный выбор! Давайте посмотрим, что у нас получится."
        "Ваше творческое задание принято. Начинаю создание шедевра."
        "Генерирую изображение... Пожалуйста, подождите немного."
        "Подготавливаю что-то особенное для вас. Ожидайте секундочку!"
        "Принято к исполнению. Ваше искусство на подходе!"
        "Идет процесс создания... Ваш запрос воплощается в изображение."
        "Секундочку, я превращаю ваш запрос в визуальный шедевр."
        "О, это будет интересно! Сейчас увидите результат моей работы."
        "Ваше воображение вдохновляет! Приступаю к генерации изображения."
    ]
}


@bot.message_handler(commands=['gpt3', 'gpt4', 'dalle'])
def set_mode(message):
    user_id = message.chat.id
    mode = message.text[1:]  # Убираем / из команды для определения режима
    users_state[user_id] = {"mode": mode, "history": [], "image_prompt": ""}
    bot.reply_to(message, f"Режим установлен на {mode.upper()}. Введите ваш запрос.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text
    if user_id not in users_state or "mode" not in users_state[user_id]:
        bot.send_message(user_id, "Пожалуйста, выберите режим работы сначала (/gpt3, /gpt4, /dalle).")
        return

    mode = users_state[user_id]["mode"]
    preliminary_reply = choice(preliminary_replies[mode])
    message_to_delete = bot.reply_to(message, preliminary_reply)  # Сохраняем сообщение для последующего удаления
    if mode == "dalle":
        process_dalle_request(user_id, text, message_to_delete.message_id)
    else:
        process_gpt_request(user_id, text, mode, message_to_delete.message_id)

def process_dalle_request(user_id, text, message_to_delete_id):
    if text.startswith("Сгенерируй изображение"):
        users_state[user_id]["image_prompt"] = text[len("Сгенерируй изображение"):].strip()
    else:
        if users_state[user_id]["image_prompt"]:
            users_state[user_id]["image_prompt"] += ", " + text
        else:
            users_state[user_id]["image_prompt"] = text
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
    except Exception as e:
        bot.send_message(user_id, "Извините, произошла ошибка при генерации изображения.")
    finally:
        try:
            bot.delete_message(chat_id=user_id, message_id=message_to_delete_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")

def process_gpt_request(user_id, text, mode, message_to_delete_id):
    model = "gpt-3.5-turbo-0125" if mode == "gpt3" else "gpt-4-0125-preview"
    users_state[user_id]["history"].append({"role": "user", "content": text})
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=users_state[user_id]["history"],
            max_tokens=1000,
            temperature=0.7
        )
        reply = response.choices[0].message["content"]
        users_state[user_id]["history"].append({"role": "assistant", "content": reply})
        bot.send_message(user_id, reply)
    except Exception as e:
        bot.send_message(user_id, f"Извините, произошла ошибка: {e}")
    finally:
        try:
            bot.delete_message(chat_id=user_id, message_id=message_to_delete_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")

bot.polling(none_stop=True)


