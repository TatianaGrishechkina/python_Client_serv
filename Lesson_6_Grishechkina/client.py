"""Программа-клиент"""

import sys
import json
import socket
import time
import logging
import logs.config_client_log
from errors import ReqFieldMissingError, NonDictInputError
from common.jimbase import JIMBase
from common.json_messenger import JSONMessenger
from decorator import Log

# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


class JIMClient(JIMBase):
    @classmethod
    @Log()
    def create_presence(cls, account_name='Guest'):
        """
        Функция генерирует запрос о присутствии клиента
        :param account_name: по умолчанию = Guest
        :return: словарь
        """
        CLIENT_LOGGER.debug(f'Сформировано {cls.PRESENCE} сообщение для пользователя {account_name}')
        # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        return {
            cls.ACTION: cls.PRESENCE,
            cls.TIME: time.time(),
            cls.USER: {
                cls.ACCOUNT_NAME: account_name
            }
        }

    @classmethod
    @Log()
    def process_ans(cls, message):
        """
        Функция разбирает ответ сервера
        :param message: словарь - сообщение от сервера
        :return: ответ от сервера
        """
        CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')

        if cls.RESPONSE in message:
            if message[cls.RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[cls.ERROR]}'
        raise ValueError

    @Log()
    def start(self, server_address, server_port):
        # Инициализация сокета и обмен
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((server_address, server_port))
            messenger = JSONMessenger(transport)
            message_to_server = self.create_presence()
            messenger.send_message(message_to_server)
            answer = self.process_ans(messenger.get_message())
            CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
            print(answer)
        except (ValueError, json.JSONDecodeError):
            CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
            print('Не удалось декодировать сообщение сервера.')
        except NonDictInputError:
            CLIENT_LOGGER.error(f'Аргумент функции должен быть словарем!')
        except ReqFieldMissingError as missing_error:
            CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                f'{missing_error.missing_field}')
        except ConnectionRefusedError:
            CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                                   f'конечный компьютер отверг запрос на подключение.')
        except TimeoutError:
            CLIENT_LOGGER.error('Попытка установить соединение была безуспешной, '
                                'т.к. от другого компьютера за требуемое время не получен нужный отклик.')
            print('Попытка установить соединение была безуспешной, '
                  'т.к. от другого компьютера за требуемое время не получен нужный отклик.')


def main():
    """Загружаем параметы коммандной строки"""
    # client.py 192.168.1.2 8079
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            CLIENT_LOGGER.critical(
                f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
                f' Допустимы адреса с 1024 до 65535. Клиент завершается.')
            raise ValueError
        CLIENT_LOGGER.info(f'Запущен клиент с парамертами: '
                           f'адрес сервера: {server_address}, порт: {server_port}')
    except IndexError:
        server_address = JIMBase.DEFAULT_IP_ADDRESS
        server_port = JIMBase.DEFAULT_PORT
    except ValueError:
        CLIENT_LOGGER.error('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    my_client = JIMClient()
    my_client.start(server_address, server_port)


if __name__ == '__main__':
    main()
