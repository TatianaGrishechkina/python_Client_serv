"""
Задание 3.

Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b'' (без encode decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
--- обязательно!!! усложните задачу, "отловив" и обработав исключение,
придумайте как это сделать
"""


def test_word(word):
    try:
        print('Слово', eval(f"b'{word}'"), 'можно')
    except SyntaxError:
        print(f"Слово '{word}' нельзя")


my_list = ['attribute', 'класс', 'функция', 'type']

for word in my_list:
    test_word(word)