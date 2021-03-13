"""Программа-сервер"""

import socket
import sys
import json
import select
from time import time
from errors import IncorrectDataRecivedError, NonDictInputError
from common.jimbase import JIMBase
from common.json_messenger import JSONMessenger
from decorator import Log, LOGGER


class JIMServer(JIMBase):
    transport = None
    clients = []
    messages = []

    @Log()
    def start(self, listen_address, listen_port):
        LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                           f'адрес с которого принимаются подключения: {listen_address}. '
                           f'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.bind((listen_address, listen_port))
        self.transport.settimeout(0.5)

        # Слушаем порт
        self.transport.listen(self.MAX_CONNECTIONS)

    # Основной цикл программы сервера
    def process(self):
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = self.transport.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Установлено соединение с ПК {client_address}')
            self.clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяем на наличие ждущих клиентов
        try:
            if self.clients:
                recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
        except OSError:
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            LOGGER.info('Есть сообщения от клиентов')
            for client_with_message in recv_data_lst:
                try:
                    messenger = JSONMessenger(client_with_message)
                    message = messenger.get_message()
                    self.process_client_message(messenger, message)
                except ConnectionResetError:
                    LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    self.clients.remove(client_with_message)
                except Exception as e:
                    LOGGER.info(f'Ошибка при получении сообщения: {e}')
                    self.clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if self.messages and send_data_lst:
            LOGGER.info('Есть сообщения для отправки и ожидающие клиенты')
            message = {
                self.ACTION: self.MESSAGE,
                self.SENDER: self.messages[0][0],
                self.TIME: time(),
                self.MESSAGE_TEXT: self.messages[0][1]
            }
            del self.messages[0]
            for waiting_client in send_data_lst:
                try:
                    messenger = JSONMessenger(waiting_client)
                    messenger.send_message(message)
                except:
                    LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    self.clients.remove(waiting_client)

    @Log()
    def process_client_message(self, messenger, message):
        """
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message: словарь, полученный от клиента
        :return: возвращает словарь с ответом сервера
        """
        LOGGER.info(f'Разбор сообщения от клиента : {message}')

        if self.ACTION in message and message[self.ACTION] == self.PRESENCE and self.TIME in message \
                and self.USER in message and message[self.USER][self.ACCOUNT_NAME] == 'Guest':
            # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            response = {self.RESPONSE: 200}
            LOGGER.info(f'Cформирован ответ клиенту {response}')
            messenger.send_message(response)
            return
        elif self.ACTION in message and message[self.ACTION] == self.MESSAGE and \
                self.TIME in message and self.MESSAGE_TEXT in message:
            self.messages.append((message[self.ACCOUNT_NAME], message[self.MESSAGE_TEXT]))
            LOGGER.info(f'Сообщение от клиента добавлено в очередь')
            return
        # Иначе отдаём Bad request
        response = {
            self.RESPONSE: 400,
            self.ERROR: 'Bad Request'
        }
        messenger.send_message(response)


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
            LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                                   f'{listen_port}. Допустимы адреса с 1024 до 65535.')
            raise ValueError
    except IndexError:
        LOGGER.critical('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        LOGGER.critical('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Затем загружаем какой адрес слушать

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        LOGGER.critical('После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    my_server = JIMServer()
    my_server.start(listen_address, listen_port)

    while True:
        my_server.process()

if __name__ == '__main__':
    main()
