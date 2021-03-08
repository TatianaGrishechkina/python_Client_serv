"""Программа-сервер"""

import socket
import sys
import json
import logging
import logs.config_server_log
from errors import IncorrectDataRecivedError, NonDictInputError
from common.jimbase import JIMBase
from common.json_messenger import JSONMessenger

# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')


class JIMServer(JIMBase):
    def start(self, listen_address, listen_port):
        SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                           f'адрес с которого принимаются подключения: {listen_address}. '
                           f'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))

        # Слушаем порт

        transport.listen(self.MAX_CONNECTIONS)

        while True:
            client, client_address = transport.accept()
            SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
            self.process_client(client, client_address)

    def process_client(self, client, client_address):
        try:
            messenger = JSONMessenger(client)
            message_from_client = messenger.get_message()
            SERVER_LOGGER.debug(f'Получено сообщение {message_from_client}')
            print(message_from_client)
            # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            response = self.process_client_message(message_from_client)
            SERVER_LOGGER.info(f'Cформирован ответ клиенту {response}')
            messenger.send_message(response)
            SERVER_LOGGER.debug(f'Соединение с клиентом {client_address} закрывается.')
            client.close()
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.error(f'Не удалось декодировать JSON строку, полученную от '
                                f'клиента {client_address}. Соединение закрывается.')
            print('Принято некорретное сообщение от клиента.')
            client.close()
        except IncorrectDataRecivedError:
            SERVER_LOGGER.error(f'От клиента {client_address} приняты некорректные данные. '
                                f'Соединение закрывается.')
            client.close()
        except NonDictInputError:
            SERVER_LOGGER.error(f'Аргумент функции должен быть словарем!')
            client.close()

    @classmethod
    def process_client_message(cls, message):
        """
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message: словарь, полученный от клиента
        :return: возвращает словарь с ответом сервера
        """
        SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')

        if cls.ACTION in message and message[cls.ACTION] == cls.PRESENCE and cls.TIME in message \
                and cls.USER in message and message[cls.USER][cls.ACCOUNT_NAME] == 'Guest':
            return {cls.RESPONSE: 200}
        return {
            cls.RESPONSE: 400,
            cls.ERROR: 'Bad Request'
        }


def main():
    """
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8079 -a 192.168.1.2
    """
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = JIMBase.DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                                   f'{listen_port}. Допустимы адреса с 1024 до 65535.')
            raise ValueError
    except IndexError:
        SERVER_LOGGER.critical('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        SERVER_LOGGER.critical('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Затем загружаем какой адрес слушать

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        SERVER_LOGGER.critical('После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    my_server = JIMServer()
    my_server.start(listen_address, listen_port)


if __name__ == '__main__':
    main()
