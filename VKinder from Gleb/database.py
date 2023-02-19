import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True

def create_table_seen_users():  # references users(vk_id)
    """СОЗДАНИЕ ТАБЛИЦЫ SEEN_USERS (ПРОСМОТРЕННЫЕ ПОЛЬЗОВАТЕЛИ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(50) PRIMARY KEY);"""
        )
    print("[INFO] Table SEEN_USERS was created.")


def insert_data_seen_users(vk_id):
    """ВСТАВКА ДАННЫХ В ТАБЛИЦУ SEEN_USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id) 
            VALUES ('{vk_id}');"""
        )

def select_seen_users(offset):
    """ВЫБОРКА ИЗ ПРОСМОТРЕННЫХ ЛЮДЕЙ"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT 
                        su.vk_id
                        FROM seen_users AS su
                        OFFSET '{offset}';"""
        )
        return cursor.fetchone()

def get_ids_from_db():
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT su.vk_id
                        FROM seen_users AS su;"""
        )
        rows = cursor.fetchall()
        list_of_ids = []
        [list_of_ids.extend(t) for t in rows]
        return list_of_ids

def drop_seen_users():
    """УДАЛЕНИЕ ТАБЛИЦЫ SEEN_USERS КАСКАДОМ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS seen_users CASCADE;"""
        )
        print('[INFO] Table SEEN_USERS was deleted.')

@run_once
def creating_database():
    create_table_seen_users()




