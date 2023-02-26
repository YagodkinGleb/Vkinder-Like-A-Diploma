from keyboard import sender
from main import *


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        msg = event.text.lower()
        if request == 'go':
            sender(user_id, 'Супер, теперь ты можешь мной пользоваться!')
        elif request == 'начать поиск':
            bot.write_msg(user_id, 'Пару мгновений...')
            creating_database()
            bot.get_similar_users_dict(user_id, 0)                   
            bot.write_msg(user_id, f'Нашёл для тебя пару, жми на кнопку "Вперёд"')
        elif request == 'вперёд':
            bot.find_persons(user_id, offset)
            offset += 1
        elif request == 'выход':
            bot.process_exit(event.user_id)
        else:
            bot.write_msg(user_id, f'Такая команда мне не знакома, напиши "Go", чтобы появились кнопки!')



