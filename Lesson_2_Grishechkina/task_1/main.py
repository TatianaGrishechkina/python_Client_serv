"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
from csv import writer
from re import compile
from os import walk, path


def get_data(n, titles, file_name):
    result = [n]
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for heading in titles:
            reg_exp = compile(f"{heading}: *(.+)$")
            for i in lines:
                m = reg_exp.match(i)
                if m:
                    result.append(m.group(1))
    return result


def write_to_csv(name, data):
    with open(name, 'w', newline='', encoding='utf-8') as f_n:
        my_writer = writer(f_n)
        for row in data:
            my_writer.writerow(row)


titles = ["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]
main_data = [titles]
os_prod_list = []
os_name_list = []
os_code_list = []
os_type_list = []
lists = [os_prod_list, os_name_list, os_code_list, os_type_list]
for root, dirs, files in walk('./'):
    for i, f in enumerate(files):
        full_path = path.join(root, f)
        if path.splitext(full_path)[1] == '.txt':
            my_data = get_data(i, titles, full_path)
            main_data.append(my_data)
            for d, l in zip(my_data[1:], lists):
                l.append(d)
write_to_csv('main_data.csv', main_data)
