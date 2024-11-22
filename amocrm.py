""" 
Модуль для генерации и отправки ежедневного отчета в определенное время
по доходам в AmoCRM через Telegram.

Этот модуль предоставляет функционал для сбора данных о сделках из AmoCRM, 
расчета ежедневной выручки по менеджерам и отправки отчета в Telegram.

Основные функции:
- send_to_telegram: Асинхронная функция для отправки сообщений в Telegram.
- get_leads_from_amocrm: Функция для получения данных по сделкам из AmoCRM.
- daily_report_revenue: Функция для генерации ежедневного отчета по доходам.
- main: Основная функция, которая запускает процесс генерации и отправки отчета.

"""

from aiogram import Bot, exceptions
import requests
import schedule
import asyncio
import datetime
import time
import logging
from config_tg import Config,load_config
from config_amocrm import AmoCRM, load_amocrm


# Настройка логирования. Логи сохраняются в файл "amocrm.log".
logging.basicConfig(
    filename = 'amocrm.log',  
    level = logging.INFO,  
    format = '%(asctime)s - %(levelname)s - %(message)s', 
)


async def send_to_telegram(message: str):
    """Отправка сообщения в Telegram определенному пользователю.

    Эта функция отправляет сообщение в Telegram с использованием токена и идентификатора чата,
    указанных в конфигурации. Обрабатываются различные исключения, возникающие при работе с API Telegram.

    Параметры:
    - message (str): Сообщение, которое необходимо отправить.

    Исключения:
    - BadRequest: Ошибка возникает, когда запрос некорректен.
    - Unauthorized: Ошибка возникает, когда токен бота недействителен.
    - ChatNotFound: Ошибка возникает, когда чат с указанным идентификатором не найден.
    - TelegramAPIError: Ошибка возникает при любой другой ошибке API Telegram.
    - Exception: Любая другая неожиданная ошибка.

    Возвраты:
    - None: Функция ничего не возвращает.
    """
    logging.info('Start - send_to_telegram')
    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token)

    try:
        await bot.send_message(chat_id=config.tg_bot.admin_ids, text=message)
    except exceptions.BadRequest as e:
        logging.error(f'BadRequest error occurred: {e}')
    except exceptions.Unauthorized as e:
        logging.error(f'Unauthorized error: {e}. Check your bot token.')
    except exceptions.ChatNotFound as e:
        logging.error(f'ChatNotFound error: {e}. Check the chat ID.')
    except exceptions.TelegramAPIError as e:
        logging.error(f'Telegram API error: {e}')
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')

    logging.info('send_to_telegram - finish')
    return 
    

def get_leads_from_amocrm(account_id, token):
    """Получение данных по всем сделкам из AmoCRM.

    Эта функция выполняет GET-запрос к API AmoCRM для получения информации о сделках.
    В случае возникновения ошибок HTTP, проблем с соединением или таймаута, они будут логированы,
    и функция вернет `None`.

    Параметры:
    - account_id (str): Идентификатор аккаунта AmoCRM.
    - token (str): Токен для доступа к AmoCRM.

    Возвращаемое значение:
    - requests.Response: Ответ от сервера AmoCRM, если запрос успешный.
    - None: Если произошла ошибка.

    Исключения:
    - requests.exceptions.HTTPError: Ошибка HTTP.
    - requests.exceptions.ConnectionError: Ошибка соединения.
    - requests.exceptions.Timeout: Таймаут запроса.
    - requests.exceptions.RequestException: Общая ошибка запроса.
    """
    logging.info('Start get_leads_from_amocrm')
    url = f'https://{account_id}.amocrm.ru/api/v4/leads'
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTPError occurred: {http_err}')  # Ошибка HTTP
        return None
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f'ConnectionError occurred: {conn_err}')  # Ошибка соединения
        return None
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f'TimeoutError occurred: {timeout_err}')  # Время ожидания истекло
        return None
    except requests.exceptions.RequestException as req_err:
        logging.error(f'General exception occurred: {req_err}')  # Общая ошибка запроса
        return None

    logging.info('Finished get_leads_from_amocrm')
    return response


def daily_report_revenue():
    """Генерация ежедневного отчета по доходам.

    Эта функция собирает данные о сделках из AmoCRM, фильтрует сделки, созданные сегодня, и суммирует доходы по менеджерам.
    Затем формирует отчет, в котором каждому менеджеру соответствует сумма доходов за день.

    Возвращаемое значение:
    - dict: Словарь, ключами которого являются идентификаторы менеджеров, а значениями — суммы доходов за сегодняшний день.
      Например: `{123: 10000, 456: 5000}`, где `123` и `456` — идентификаторы менеджеров, а `10000` и `5000` — соответствующие им доходы.

    Исключения:
    - Exception: Может возникнуть любая непредвиденная ошибка при загрузке конфигурации AmoCRM или получении данных сделок.
    - KeyError: При отсутствии ожидаемых ключей в ответе от AmoCRM.
    - TypeError: При неверном формате ответа от AmoCRM.
    """
    logging.info('Start - daily_report_revenue')
    # проверяем успешную конфигурации для AmoCRM
    try:
        config_amocrm: AmoCRM = load_amocrm() 
    except Exception as e:
        logging.error(f'Error loading AmoCRM configuration: {e}')
        return {}
    # проверяем успешную загрузку данных по сделкам для AmoCRM
    try:
        data = get_leads_from_amocrm(account_id=config_amocrm.account_id, token=config_amocrm.token)
    except Exception as e:
        logging.error(f'Error getting leads from AmoCRM: {e}')
        return {}

    if data is None:
        logging.error('No data returned from get_leads_from_amocrm')
        return {}

    if isinstance(data, dict) and data.get('status_code') != 200:
        logging.error(f'Error fetching deals: {data.get("status_code")}')
        return {}

    try:
        deals = data.json()['_embedded']['leads']
    except (KeyError, TypeError) as e:
        logging.error(f'Error processing deals data: {e}. Data received: {data}')
        return {}
    # список менеджеров в виде словаря. Заполняется id менеджера - доходы
    revenue_by_manager = {}
    # проходимся по всем сделкам и сравниваем дату создания. Если дата совпадает с сегодня - делаем расчет дохода
    for deal in deals:
        created_at = deal.get('created_at')
        responsible_user_id = deal.get('responsible_user_id')
        price = deal.get('price', 0)

        if created_at and responsible_user_id:
            created_date = datetime.datetime.fromtimestamp(created_at).date()
            current_date = datetime.date.today()

            if created_date == current_date:
                if responsible_user_id not in revenue_by_manager:
                    revenue_by_manager[responsible_user_id] = 0
                revenue_by_manager[responsible_user_id] += price

    logging.info('daily_report_revenue - finish')
    return revenue_by_manager

   
def main():
    """Основная функция программы.

    Эта функция запускает процесс генерации ежедневного отчета по доходам и отправки его в Telegram.
    В случае успешного сбора данных отчет формируется и отправляется в виде сообщения в Telegram.
    Если возникают ошибки, они логируются, и пользователю отправляется соответствующее уведомление.

    Исключения:
    - Exception: Может возникнуть любая непредвиденная ошибка при выполнении главной функции.
    """
    logging.info('Start - main')
    try:
        revenue = daily_report_revenue()

        if revenue:
            message = f'Отчет по выручке на {datetime.date.today()}:\n\n'
            for manager_id, total_revenue in revenue.items():
                message += f"Менеджер ID: {manager_id}, Выручка: {total_revenue}\n"
            #отправка сообщения в телеграмм с данными по доходам
            asyncio.run(send_to_telegram(message))
            logging.info('Report sent to Telegram user')
        else:
            error_message = "Не удалось получить данные по выручке."
            asyncio.run(send_to_telegram(error_message))
            logging.error(error_message)

    except Exception as e:
        logging.error(f'Error in main execution: {e}')
        asyncio.run(send_to_telegram("Не удалось выполнить главную функцию."))

# Отправка отчета каждый день в 18:00
schedule.every().day.at("18:00").do(main)  


if __name__ == '__main__':
    # Запускаем цикл для проверки задач. 
    while True:
        logging.info('Checking scheduled tasks...')
        schedule.run_pending()
        time.sleep(60) # Проверка задач каждую минуту


