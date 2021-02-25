"""
2. Задание на закрепление знаний по модулю json. Есть файл orders
в формате JSON с информацией о заказах. Написать скрипт, автоматизирующий
его заполнение данными.

Для этого:
Создать функцию write_order_to_json(), в которую передается
5 параметров — товар (item), количество (quantity), цена (price),
покупатель (buyer), дата (date). Функция должна предусматривать запись
данных в виде словаря в файл orders.json. При записи данных указать
величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json()
с передачей в нее значений каждого параметра.

ПРОШУ ВАС НЕ УДАЛЯТЬ ИСХОДНЫЙ JSON-ФАЙЛ
ПРИМЕР ТОГО, ЧТО ДОЛЖНО ПОЛУЧИТЬСЯ

{
    "orders": [
        {
            "item": "printer",
            "quantity": "10",
            "price": "6700",
            "buyer": "Ivanov I.I.",
            "date": "24.09.2017"
        },
        {
            "item": "scaner",
            "quantity": "20",
            "price": "10000",
            "buyer": "Petrov P.P.",
            "date": "11.01.2018"
        }
    ]
}

вам нужно подгрузить JSON-объект
и достучаться до списка, который и нужно пополнять
а потом сохранять все в файл
"""
from json import load, dumps, JSONDecodeError


def write_order_to_json(item, quantity, price, buyer, date):
    try:
        with open('orders.json', encoding='utf-8') as f_n:
            root = load(f_n)
    except JSONDecodeError:
        root = {'orders': []}
    root['orders'].append({
        'item': item,
        'quantity': str(quantity),
        'price': str(price),
        'buyer': buyer,
        'date': date
    })
    with open('orders.json', 'w', encoding='utf-8') as f_n:
        f_n.write(dumps(root, indent=4, ensure_ascii=False))


write_order_to_json("компьютер", "5", "40000", "Sidorov S.S.", "2.05.2019")
write_order_to_json("монитор", "5", "50000", "Zalivaykin S.S.", "2.05.2021")