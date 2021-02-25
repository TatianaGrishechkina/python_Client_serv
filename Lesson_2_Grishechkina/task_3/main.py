"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""
from yaml import load, dump, FullLoader
from unicodedata import lookup
from deepdiff import DeepDiff


def write_to_yaml(dict):
    with open('data.yaml', 'w', encoding='utf-8') as f_n:
        dump(dict, f_n, default_flow_style=False, allow_unicode=True)


def read_from_yaml():
    with open('file.yaml', encoding='utf-8') as f_n:
        my_data = load(f_n, Loader=FullLoader)
    return my_data


my_dict1 = {
    'items': [
        'computer',
        'printer',
        'keyboard',
        'mouse'
    ],
    'items_price': {
        'computer': f"200{lookup('EURO SIGN')}-1000{lookup('EURO SIGN')}",
        'keyboard': f"5{lookup('EURO SIGN')}-50{lookup('EURO SIGN')}",
        'mouse': f"4{lookup('EURO SIGN')}-7{lookup('EURO SIGN')}",
        'printer': f"100{lookup('EURO SIGN')}-300{lookup('EURO SIGN')}"
    },
    'items_quantity': 4
}

write_to_yaml(my_dict1)
my_dict2 = read_from_yaml()
diff = DeepDiff(my_dict2, my_dict1)
if len(diff) == 0:
    print('Различий нет!')
else:
    print(f'Списки отличаются! {diff}')
