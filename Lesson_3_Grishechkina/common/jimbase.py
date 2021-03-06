"""Константы"""


class JIMBase:
    # Порт по умолчанию для сетевого ваимодействия
    DEFAULT_PORT = 7777
    # IP адрес по умолчанию для подключения клиента
    DEFAULT_IP_ADDRESS = '127.0.0.1'
    # Максимальная очередь подключений
    MAX_CONNECTIONS = 5


    # Прококол JIM основные ключи:
    ACTION = 'action'
    TIME = 'time'
    USER = 'user'
    ACCOUNT_NAME = 'account_name'

    # Прочие ключи, используемые в протоколе
    PRESENCE = 'presence'
    RESPONSE = 'response'
    ERROR = 'error'
