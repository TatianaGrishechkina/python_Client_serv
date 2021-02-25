"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""
from subprocess import Popen, PIPE
from chardet import detect


sites = ['yandex.ru', 'youtube.com']

for site in sites:
    ping = Popen(f'ping {site}', stdout=PIPE)
    for line in ping.stdout:
        result = detect(line)
        print(line.decode(result['encoding']), end='')
