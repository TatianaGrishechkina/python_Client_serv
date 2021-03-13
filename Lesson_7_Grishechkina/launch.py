"""Лаунчер"""

import subprocess

process = []

while True:
    action = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if action == 'q':
        break
    elif action == 's':
        process.append(subprocess.Popen('python server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(2):
            process.append(subprocess.Popen('python client.py 127.0.0.1 7777 send',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(3):
            process.append(subprocess.Popen('python client.py 127.0.0.1 7777 listen',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'x':
        while process:
            damned = process.pop()
            damned.kill()