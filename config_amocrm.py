"""
Модуль для конфигурации интеграции с AmoCRM.

Этот модуль предназначен для чтения и обработки параметров конфигурации для подключения к AmoCRM,
используя библиотеку `environs` для работы с переменными окружения.

Классы:
- `AmoCRM`: Класс, представляющий конфигурацию для подключения к AmoCRM.

Функции:
- `load_amocrm`: Загружает параметры конфигурации из переменных окружения и возвращает объект `AmoCRM`.

Требуется установка environs (pip install environs)

Примеры использования:
>>> amocrm_config = load_amocrm('.env')
>>> print(amocrm_config.account_id)
'12345'
"""

from dataclasses import dataclass
from environs import Env 

@dataclass
class AmoCRM():
    """
    Класс, представляющий настройки API AmoCRM.

    Атрибуты:
        account_id (str): Идентификатор аккаунта AmoCRM.
        token (str): Токен доступа к API AmoCRM.
    """
    account_id: str 
    token: str


def load_amocrm(path: str | None = None) -> AmoCRM:
    """
    Загружает конфигурацию для доступа к API AmoCRM из .env файла.

    Аргументы:
        path (str | None): Опциональный путь к .env файлу. 
            Если не указан, будет использован файл по умолчанию.
    
    Возвращает:
        AmoCRM: Возвращает экземпляр класса AmoCRM, 
        содержащий идентификатор аккаунта и токен доступа.
    
    Исключения:
        Raises KeyError если переменные окружения (ACCOUNT_ID или TOKEN_AMOCRM) не найдены.
    """
    
    env = Env()
    env.read_env(path) 
    return AmoCRM(
            account_id=env('ACCOUNT_ID'),
            token=env('TOKEN_AMOCRM')) 

    