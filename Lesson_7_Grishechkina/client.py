"""Программа-клиент"""

import sys
import json
import socket
import time
from errors import ReqFieldMissingError, NonDictInputError
from common.jimbase import JIMBase
from common.json_messenger import JSONMessenger
from decorator import Log, LOGGER


class JIMClient(JIMBase):
    transport = None
    messenger = None

    @Log()
    def message_from_server(self):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        message = self.messenger.get_message()
        if self.ACTION in message and message[self.ACTION] == self.MESSAGE and \
                self.SENDER in message and self.MESSAGE_TEXT in message:
            LOGGER.info(f'Получено сообщение от пользователя '
                               f'{message[self.SENDER]}:\n{message[self.MESSAGE_TEXT]}')
            return message[self.SENDER], message[self.MESSAGE_TEXT]
        else:
            LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            return None, None

    @Log()
    def send_message(self, text):
        self.messenger.send_message(self.create_message(text))

    @classmethod
    @Log()
    def create_presence(cls, account_name='Guest'):
        """
        Функция генерирует запрос о присутствии клиента
        :param account_name: по умолчанию = Guest
        :return: словарь
        """
        LOGGER.debug(f'Сформировано {cls.PRESENCE} сообщение для пользователя {account_name}')
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
        LOGGER.debug(f'Разбор сообщения от сервера: {message}')

        if cls.RESPONSE in message:
            if message[cls.RESPONSE] == 200:
                return 'Подключение к серверу установлено!'
            return f'400 : {message[cls.ERROR]}'
        raise ValueError

    @Log()
    def start(self, server_address, server_port):
        # Инициализация сокета и обмен
        try:
            self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.transport.connect((server_address, server_port))
            self.messenger = JSONMessenger(self.transport)
            message_to_server = self.create_presence()
            self.messenger.send_message(message_to_server)
            answer = self.process_ans(self.messenger.get_message())
            LOGGER.info(f'Принят ответ от сервера {answer}')
            print(answer)
        except (ValueError, json.JSONDecodeError):
            LOGGER.error('Не удалось декодировать полученную Json строку.')
            print('Не удалось декодировать сообщение сервера.')
        except NonDictInputError:
            LOGGER.error(f'Аргумент функции должен быть словарем!')
        except ReqFieldMissingError as missing_error:
            LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                f'{missing_error.missing_field}')
        except ConnectionRefusedError:
            LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                                   f'конечный компьютер отверг запрос на подключение.')
        except TimeoutError:
            LOGGER.error('Попытка установить соединение была безуспешной, '
                                'т.к. от другого компьютера за требуемое время не получен нужный отклик.')
            print('Попытка установить соединение была безуспешной, '
                  'т.к. от другого компьютера за требуемое время не получен нужный отклик.')

    @Log()
    def stop(self):
        self.transport.close()
        LOGGER.info('Завершение работы по команде пользователя.')


def main():
    """Загружаем параметы коммандной строки"""
    # client.py 127.0.0.1 7777 send
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        client_mode = sys.argv[3]
        if server_port < 1024 or server_port > 65535:
            LOGGER.critical(
                f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
                f' Допустимы адреса с 1024 до 65535. Клиент завершается.')
            raise ValueError
        LOGGER.info(f'Запущен клиент с парамертами: '
                           f'адрес сервера: {server_address}, порт: {server_port}')
    except IndexError:
        server_address = JIMBase.DEFAULT_IP_ADDRESS
        server_port = JIMBase.DEFAULT_PORT
        client_mode = 'send'
    except ValueError:
        LOGGER.error('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    if client_mode == 'send':
        print('Поздравляем, ваш режим - send и вы можете отправлять сообщения!')
    elif client_mode == 'listen':
        print('Поздравляю! Ваш режим - listen и вы можете читать все сообщения!')
    else:
        print(f'Поздравляю! Ваш режим {client_mode}! Как только мы придумаем такой - мы вас пустим!')
        sys.exit(1)

    my_client = JIMClient()
    my_client.start(server_address, server_port)

    while True:
        # режим работы - отправка сообщений
        if client_mode == 'send':
            try:
                message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
                if message == '!!!':
                    my_client.stop()
                    print('Спасибо за использование нашего сервиса!')
                    sys.exit(0)
                my_client.send_message(message)
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                sys.exit(1)

        # Режим работы приём:
        if client_mode == 'listen':
            try:
                sender, message = my_client.message_from_server()
                if sender is None:
                    print('Получено некорректное сообщение от сервера!')
                else:
                    print(f'Получено сообщение от пользователя {sender}:\n{message}')
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                sys.exit(1)


if __name__ == '__main__':
    main()
