"""Программа-клиент"""

import sys
import json
import socket
import time
from common.jimbase import JIMBase
from common.json_messenger import JSONMessenger


class JIMClient(JIMBase):
    @classmethod
    def create_presence(cls, account_name='Guest'):
        """
        Функция генерирует запрос о присутствии клиента
        :param account_name: по умолчанию = Guest
        :return: словарь
        """
        # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        return {
            cls.ACTION: cls.PRESENCE,
            cls.TIME: time.time(),
            cls.USER: {
                cls.ACCOUNT_NAME: account_name
            }
        }

    @classmethod
    def process_ans(cls, message):
        """
        Функция разбирает ответ сервера
        :param message: словарь - сообщение от сервера
        :return: ответ от сервера
        """
        if cls.RESPONSE in message:
            if message[cls.RESPONSE] == 200:
                return 'Hello!'
            return f'Error : {message[cls.ERROR]}'
        raise ValueError

    def start(self, server_address, server_port):
        # Инициализация сокета и обмен

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        messenger = JSONMessenger(transport)
        message_to_server = self.create_presence()
        messenger.send_message(message_to_server)
        try:
            answer = self.process_ans(messenger.get_message())
            print(answer)
        except (ValueError, json.JSONDecodeError):
            print('Не удалось декодировать сообщение сервера.')


def main():
    """Загружаем параметы коммандной строки"""
    # client.py 192.168.1.2 8079
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = JIMBase.DEFAULT_IP_ADDRESS
        server_port = JIMBase.DEFAULT_PORT
    except ValueError:
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    my_client = JIMClient()
    my_client.start(server_address, server_port)


if __name__ == '__main__':
    main()
