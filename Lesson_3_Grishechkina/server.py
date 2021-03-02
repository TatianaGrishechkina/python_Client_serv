"""Программа-сервер"""

import socket
import sys
import json
from common.jimbase import JIMBase
from common.json_messenger import JSONMessenger


class JIMServer(JIMBase):
    def start(self, listen_address, listen_port):
        # Готовим сокет

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))

        # Слушаем порт

        transport.listen(self.MAX_CONNECTIONS)

        while True:
            client, client_address = transport.accept()
            self.process_client(client)

    def process_client(self, client):
        try:
            messenger = JSONMessenger(client)
            message_from_client = messenger.get_message()
            print(message_from_client)
            # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            response = self.process_client_message(message_from_client)
            messenger.send_message(response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')
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
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print(
            'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Затем загружаем какой адрес слушать

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        print(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    my_server = JIMServer()
    my_server.start(listen_address, listen_port)


if __name__ == '__main__':
    main()
