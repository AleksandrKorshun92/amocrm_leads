# AmoCRM Leads Integration Script

AmoCRM Leads Notifier — это скрипт, который извлекает информацию о сделках (лидах) из вашей учетной записи AmoCRM и отправляет ежедневный отчет о выручке в Telegram. 
Скрипт написан на Python и использует библиотеки для работы с API AmoCRM и Telegram.


## Установка

Для установки необходимых зависимостей используйте следующий код:

```bash
pip install -r requirements.txt
```

## Конфигурация

Перед использованием скрипта необходимо создать файл `.env` в корневой директории проекта и заполнить его следующими параметрами:

```
BOT_TOKEN = '9999999888888888777777777666sssssssss'
ADMIN_IDS = '1234567891'
ACCOUNT_ID = '1234567891'
TOKEN_AMOCRM = '9999999888888888777777777666sssssssss'
```


## Использование

Чтобы запустить скрипт, выполните следующую команду:

```bash
python amocrm.py
```

Либо запустить через docker:
```bash
docker-compose up --build
```
