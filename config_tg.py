""" 
Модуль для конфигурации Telegram-бота.

Этот модуль предназначен для чтения и обработки параметров конфигурации Telegram-бота,
используя библиотеку `environs` для работы с переменными окружения.

Классы:
- `TgBot`: Класс, представляющий конфигурацию Telegram-бота.
- `Config`: Класс, содержащий объект `TgBot` и предоставляющий доступ ко всей конфигурации.

Функции:
- `load_config`: Загружает параметры конфигурации из переменных окружения и возвращает объект `Config`.

Требуется установка environs (pip install environs)

Примеры использования:
>>> config = load_config('.env')
>>> print(config.tg_bot.token)
'1234567890:ABCDEFghijklmnopqrstuvwxyz'

"""

from dataclasses import dataclass
from environs import Env 

@dataclass
class TgBot():
    """
    Класс, представляющий настройки Telegram бота.

    Атрибуты:
        token (str): Токен для доступа к боту.
        admin_ids (str): Идентификаторы администраторов бота.
    """
    token: str 
    admin_ids: str


@dataclass
class Config:
    """
    Класс, представляющий общую конфигурацию приложения.

    Атрибуты:
        tg_bot (TgBot): Экземпляр класса TgBot, содержащий настройки бота.
    """
    tg_bot: TgBot 


def load_config(path: str | None = None) -> Config:
    """
    Загружает конфигурацию для Telegram бота из .env файла.

    Аргументы:
        path (str | None): Опциональный путь к .env файлу. 
                           Если не указан, будет использован файл по умолчанию.

    Возвращает:
        Config: Возвращает экземпляр класса Config, который содержит 
                настройки бота (токен и идентификаторы администраторов).

    Исключения:
        Raises KeyError если переменные окружения (BOT_TOKEN или ADMIN_ID) не найдены.
    """
    
    env = Env()
    env.read_env(path) 
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=env('ADMIN_ID')) 
        )
    