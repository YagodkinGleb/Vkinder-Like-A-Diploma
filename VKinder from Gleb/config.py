user_token = '' # ключ доступа пользователя
comm_token = '' # ключ доступа сообщества

offset = 0                          # параметр, указывающий с какой строки начинать выборку
line = range(0, 1000)               # последовательность для перебора найденных пользователей

host = 'localhost'
user = 'postgres'
password = 'EnOO6SYHK'
db_name = 'test'

'''Декоратор, использующийся для единичного вызова функции создании базы данных (database.py)'''
def run_once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
    wrapper.has_run = False
    return wrapper





