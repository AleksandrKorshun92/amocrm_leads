""" 
Модуль содержит тесты (unitest) для функций работы с AmoCRM и Telegram ботом.

Тесты проверяют:
- Отправку сообщений в Telegram через функцию send_to_telegram.
- Получение данных по сделкам из AmoCRM через функцию get_leads_from_amocrm.
- Формирование ежедневного отчета о выручке через функцию daily_report_revenue.

Каждый тест использует патчинг для имитации поведения зависимостей и проверки корректной обработки данных.
"""

import unittest
from unittest.mock import patch, AsyncMock, Mock, MagicMock
from config_tg import Config, TgBot
from config_amocrm import AmoCRM
import asyncio
import datetime
from amocrm import send_to_telegram, get_leads_from_amocrm, daily_report_revenue, main


class TestFunctions(unittest.TestCase):
    @patch('amocrm.Bot')
    @patch('amocrm.load_config', return_value=Config(tg_bot=TgBot(token='fake_token', admin_ids='fake_ids')))
    @patch('logging.info')
    @patch('logging.error')
    # Проверка отправки сообщений через телеграмм 
    def test_send_to_telegram(self, mock_error, mock_info, mock_load_config, mock_bot):
        mock_bot.return_value.send_message = AsyncMock()

        message = "Test message"
        asyncio.run(send_to_telegram(message))

        # Проверка логирования
        mock_info.assert_any_call('Start - send_to_telegram')
        mock_bot.return_value.send_message.assert_called_once_with(chat_id='fake_ids', text=message)


    @patch('amocrm.requests.get')
    @patch('logging.info')
    @patch('logging.error')
    # Проверка получения данных по сделкам 
    def test_get_leads_from_amocrm(self, mock_error, mock_info, mock_requests_get):
        mock_response = Mock()
        mock_response.json.return_value = {'_embedded': {'leads': []}}
        mock_requests_get.return_value = mock_response

        account_id = "fake_account"
        token = "fake_token"
        result = get_leads_from_amocrm(account_id, token)

        # Проверка логов
        mock_info.assert_any_call('Start get_leads_from_amocrm')
        # Проверка результата
        self.assertEqual(result, mock_response)


    @patch('amocrm.load_amocrm', return_value=AmoCRM(account_id='fake_account_id', token='fake_token'))
    @patch('amocrm.get_leads_from_amocrm')
    @patch('logging.info')
    @patch('logging.error')
    # Проверка получения данных по еженедельным сделкам
    def test_daily_report_revenue_success(self, mock_error, mock_info, mock_get_leads_from_amocrm, mock_load_amocrm):
        mock_get_leads_from_amocrm.return_value = MagicMock()
        mock_get_leads_from_amocrm.return_value.json.return_value = {
            '_embedded': {
                'leads': [
                    {
                        'created_at': (datetime.datetime.now() - datetime.timedelta(days=0)).timestamp(),  # Сегодняшняя дата
                        'responsible_user_id': 1,
                        'price': 1000
                    },
                    {
                        'created_at': (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp(),  # Вчерашняя дата
                        'responsible_user_id': 2,
                        'price': 1500
                    }
                ]
            }
        }

        revenue = daily_report_revenue()

        # Проверка результата
        expected_result = {1: 1000}
        self.assertDictEqual(revenue, expected_result)


    @patch('amocrm.load_amocrm', return_value=AmoCRM(account_id='fake_account_id', token='fake_token'))
    @patch('amocrm.get_leads_from_amocrm')
    @patch('logging.info')
    @patch('logging.error')
    # Проверка получения данных по еженедельным сделкам при отсутствии сделок
    def test_daily_report_revenue_no_data(self, mock_error, mock_info, mock_get_leads_from_amocrm, mock_load_amocrm):
        mock_get_leads_from_amocrm.return_value = None

        revenue = daily_report_revenue()

        # Проверка результата
        self.assertDictEqual(revenue, {})
    
    
    @patch('amocrm.load_amocrm', return_value=AmoCRM(account_id='fake_account_id', token='fake_token'))
    @patch('amocrm.get_leads_from_amocrm')
    @patch('logging.info')
    @patch('logging.error')
    # Проверка получения данных по еженедельным сделкам при ошибке
    def test_daily_report_revenue_status_code_not_200(self, mock_error, mock_info, mock_get_leads_from_amocrm, mock_load_amocrm):
        mock_get_leads_from_amocrm.return_value = {'status_code': 400}

        revenue = daily_report_revenue()

        # Проверка результата
        self.assertDictEqual(revenue, {})
   
   
    @patch('amocrm.load_amocrm', return_value=AmoCRM(account_id='fake_account_id', token='fake_token'))
    @patch('amocrm.get_leads_from_amocrm')
    @patch('logging.info')
    @patch('logging.error')
    # Проверка при возникновении ошибки KeyError в процессе парсинга JSON-данных.
    def test_daily_report_revenue_keyerror_in_json(self, mock_error, mock_info, mock_get_leads_from_amocrm, mock_load_amocrm):
        mock_get_leads_from_amocrm.return_value = MagicMock()
        mock_get_leads_from_amocrm.return_value.json.side_effect = KeyError

        revenue = daily_report_revenue()

        # Проверка результата
        self.assertDictEqual(revenue, {})


    @patch('amocrm.send_to_telegram')
    @patch('amocrm.daily_report_revenue')
    @patch('logging.info')
    @patch('logging.error')
    # Проверка основной функции в части успешного получения данных о выручке за день
    def test_main(self, mock_error, mock_info, mock_daily_report_revenue, mock_send_to_telegram):
        mock_daily_report_revenue.return_value = {1: 1000}

        main()

        # Проверки
        message = f'Отчет по выручке на {datetime.date.today()}:\n\nМенеджер ID: 1, Выручка: 1000\n'
        mock_send_to_telegram.assert_called_once_with(message)
        mock_info.assert_any_call('Start - main')

    
if __name__ == '__main__':
    unittest.main()