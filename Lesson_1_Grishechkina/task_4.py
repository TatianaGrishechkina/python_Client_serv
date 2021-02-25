"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""

my_list = ['разработка', 'администрирование', 'protocol', 'standard']
my_list_e = list(map(lambda word: str.encode(word, encoding='utf-8'), my_list))
my_list_d = list(map(lambda word: bytes.decode(word, encoding='utf-8'), my_list_e))

print(my_list)
print(my_list_e)
print(my_list_d)
