Sirius Contest Events Bot
=========================

Telegram-бот, который может записывать пользователей на мероприятия,
проходящие на [Федеральной территории Сириус](https://sirius-ft.ru/).

Установка
---------
1. Установите Python версии (на 2.x работать точно не будет, 
   работоспособность на более ранних 3.x версиях не проверялась): 
```bash
python --version
Python 3.9.6
```

2. Установите pip и необходимые зависимости:
```bash
pip install pyTelegramBotAPI
pip install qrcode[pil]
```

3. Чтобы запустить бота введите команду:
```bash
export EVENTS_BOT_TOKEN="<Ваш токен>"
export EVENTS_BOT_DB="<Путь к файлу базы данных, если файла нет, автоматически создается новая>"
export EVENTS_BOT_ADMIN_USERS="<Разделенные ':' идентификаторы telegram-пользователей, которым нужно предоставить права администратора (создание, редактирование мероприятий)>"
python events_bot/main.py
```
