from pprint import pprint
import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from config import offset
from random import randrange
from database import *


class VKinder:

    def __init__(self):
        print('Bot was created')
        self.vk = vk_api.VkApi(token=comm_token)  # АВТОРИЗАЦИЯ СООБЩЕСТВА
        self.longpoll = VkLongPoll(self.vk)  # РАБОТА С СООБЩЕНИЯМИ
        self.profiles = []

    def write_msg(self, user_id, message):
        """МЕТОД ДЛЯ ОТПРАВКИ СООБЩЕНИЙ"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    def get_user_data(self, user_id):
        """Получение данных о пользователе"""
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'sex, bdate, city',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_dict = response['response']      # для получения имени и города (по ключу)
            information_list = response['response']      # для получения остальных данных (по индексу в списках)
        except KeyError:
            print(f'Ошибка получения данных API {user_id}'
                  f', проверьте валидность токенов')



        '''получение пола пользователя, меняет на противоположный'''
        def get_sex():
            for i in information_list:
                if i.get('sex') == 2:
                    find_sex = 1
                    return find_sex
                elif i.get('sex') == 1:
                    find_sex = 2
                    return find_sex

        '''получение возраста пользователя или нижней границы для поиска'''
        def get_age_low(user_id):
            for i in information_list:
                date = i.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                age = year_now - year
                return age
            elif len(date_list) == 2 or date not in information_list:
                self.write_msg(user_id, 'Введите нижний порог возраста (min - 16): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age

        '''получение возраста пользователя или верхней границы для поиска'''
        def get_age_high(user_id):
            for i in information_list:
                date = i.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in information_list:
                self.write_msg(user_id, 'Введите верхний порог возраста (max - 65): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age

        '''получение информации о городе пользователя'''
        def find_city(user_id):
            for i in information_dict:
                if 'city' in i:
                    city = i.get('city')
                    id = int(city.get('id'))
                    return id
                elif 'city' not in i:
                    self.write_msg(user_id, 'Введите название вашего города: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.cities(user_id, city_name)
                            if id_city != '' or id_city != None:
                                return int(id_city)
                            else:
                                break


        sex = get_sex()                                # ПОЛУЧЕНИЕ ПОЛА ПОЛЬЗОВАТЕЛЯ
        age_or_age_low = get_age_low(user_id)
        age_or_age_high = get_age_high(user_id)              # ПОЛУЧЕНИЕ ВОЗРАСТА ПОЛЬЗОВАТЕЛЯ
        city = find_city(user_id)                                  # ПОЛУЧЕНИЕ ГОРОДА ПОЛЬЗОВАТЕЛЯ

        return [sex, age_or_age_low, age_or_age_high, city]


    def cities(self, user_id, city_name):
        """ПОЛУЧЕНИЕ ID ГОРОДА ПОЛЬЗОВАТЕЛЯ ПО НАЗВАНИЮ"""
        url = f'https://api.vk.com/method/database.getCities'
        params = {'access_token': user_token,
                  'country_id': 1,
                  'q': f'{city_name}',
                  'need_all': 0,
                  'count': 1000,
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            information_list = response['response']
        except KeyError:
            print(f'Ошибка получения данных API {user_id} (id города пользователя)'
                  f', проверьте валидность токенов, либо наличие данных по реализованным методам')

        list_cities = information_list['items']
        for i in list_cities:
            found_city_name = i.get('title')
            if found_city_name == city_name:
                found_city_id = i.get('id')
                return int(found_city_id)

    def get_similar_users_dict(self, user_id, offset_value, count=100) -> list[dict]:
        """ПОИСК ЛЮДЕЙ И ФОРМИРОВАНИЕ СПИСКА ПО ПОЛУЧЕННЫМ ДАННЫМ"""
        url = f'https://api.vk.com/method/users.search'
        user_data = self.get_user_data(user_id)
        params = {'access_token': user_token,
                  'v': '5.131',
                  'offset': offset_value,
                  'sex': user_data[0],
                  'age_from': user_data[1],
                  'age_to': user_data[2],
                  'city': user_data[3],
                  'fields': 'is_closed, id, first_name, last_name, bdate, city',
                  'status': '1' or '6',
                  'count': count,
                  'sort': 0}
        resp = requests.get(url, params=params)
        resp_json = resp.json()
        try:
            dict_1 = resp_json['response']
        except KeyError:
            print(f'Ошибка получения данных API {user_id} (по ранее полученным данным) '
                  f', проверьте валидность токенов, реализованных методов')


        list_1 = dict_1['items']
        list_similar_users = []
        for person_dict in list_1:
            if person_dict.get('is_closed') == False:
                first_name = person_dict.get('first_name')
                last_name = person_dict.get('last_name')
                vk_id = str(person_dict.get('id'))
                vk_link = 'vk.com/id' + str(person_dict.get('id'))

            else:
                continue
            list_similar_users.append({'first_name': first_name, 'last_name': last_name, 'id': vk_id, 'link': vk_link})

        self.profiles = list_similar_users

    def get_user_name_and_link(self, user_id, offset_value):
        dicts_persons = self.profiles
        ids = get_ids_from_db()
        dicts_persons = [d for d in dicts_persons if d['id'] not in ids]
        print(dicts_persons)
        while not dicts_persons:
            offset_value = offset_value + 100
            self.get_similar_users_dict(user_id, offset_value)
        profile = dicts_persons.pop(0)
        return {
            'name': profile['first_name'],
            'lastname': profile['last_name'],
            'id': profile['id'],
            'link': profile['link'],
        }


    # def get_user_name_and_link(self, user_id, offset, line):
    #     dicts_persons = self.profiles
    #     ids = get_ids_from_db()
    #     new_dicts_persons = [d for d in dicts_persons if d['id'] not in ids]
    #     pprint(new_dicts_persons)
    #     if new_dicts_persons:
    #         list_person = list(new_dicts_persons[offset].values())
    #         return {
    #             'name': list_person[0],
    #             'lastname': list_person[1],
    #             'id': list_person[2],
    #             'link': list_person[3],
    #         }
    #     else:
    #         line = line + 10
    #         self.get_similar_users_dict(user_id, line)
    #         self.get_user_name_and_link(user_id, offset, line)

    # def get_user_name_and_link(self, user_id, offset):
    #     dicts_persons = (self.find_similar_users(user_id))
    #     ids = get_ids_from_db()
    #     new_dicts_persons = [d for d in dicts_persons if d['id'] not in ids]
    #     list_person = list(new_dicts_persons[offset].values())

    def get_photos_id(self, user_id):
        """ПОЛУЧЕНИЕ ID ФОТОГРАФИЙ С РАНЖИРОВАНИЕМ В ОБРАТНОМ ПОРЯДКЕ"""
        url = 'https://api.vk.com/method/photos.getAll'
        params = {'access_token': user_token,
                  'type': 'album',
                  'owner_id': user_id,
                  'extended': 1,
                  'count': 25,
                  'v': '5.131'}
        resp = requests.get(url, params=params)
        dict_photos = dict()
        resp_json = resp.json()
        try:
            dict_1 = resp_json['response']
        except KeyError:
            print(f'Ошибка получения данных API {user_id} (фотографии пользователя) '
                  f', проверьте валидность токенов, либо наличие данных по реализованным методам')

        list_1 = dict_1['items']
        for i in list_1:
            photo_id = str(i.get('id'))
            i_likes = i.get('likes')
            if i_likes.get('count'):
                likes = i_likes.get('count')
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse=True)
        return list_of_ids[:3]                                      # выборка трёх фотографий


    def send_photos(self, user_id, owner_id, photos, index):
        """ОТПРАВКА ФОТОГРАФИЙ"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'attachment': 'photo{owner_id}_{media_id}'.format(
                                             owner_id=owner_id,
                                             media_id=int(photos[index][1])
                                         ),
                                         'random_id': 0})


    def find_persons(self, user_id, offset_value):
        user_name_and_link = self.get_user_name_and_link(user_id, offset_value)

        self.write_msg(user_id, f'{user_name_and_link["name"]} {user_name_and_link["lastname"]} \n{user_name_and_link["link"]}')
        photos = self.get_photos_id(user_name_and_link["id"])
        try:
            insert_data_seen_users(user_name_and_link["id"])
            self.send_photos(user_id, user_name_and_link["id"], photos,  0)
            self.send_photos(user_id, user_name_and_link["id"], photos,  1)
            self.send_photos(user_id, user_name_and_link["id"], photos,  2)
        except: self.write_msg(user_id, f'Больше фотографий нет')


    def process_exit(self, user_id):
        # Отправляем сообщение с прощальным текстом
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': 'До свидания!',
                                         'random_id': randrange(10 ** 7)})
        quit()


bot = VKinder()
