# -*- coding: utf-8 -*-
import telebot
from telebot import apihelper, types, util
import os
import sqlite3
from datetime import datetime
import time

token = ''
bot = telebot.TeleBot(token)
Data = [-1001200656978]
global Sent
Sent = []


@bot.message_handler(content_types=['text', 'new_chat_members'])
def authentification(message, num1=False):
    if not message.from_user.id == '1000819361' and message.chat.id in Data:  # Проверяет тот ли чат ему пишет
        global Sent

        def bd(message):
            global Sent
            Sent = []
            conn = sqlite3.connect("telegram_group.db")
            cursor = conn.cursor()
            nick = message.from_user.first_name
            user_id = message.from_user.id
            now = datetime.now()
            sql = f"SELECT * FROM users WHERE user_id = '{user_id}'"
            result = ''

            for result in cursor.execute(sql):
                print(result)

            sql = f"""
                   SELECT nick_name, user_id, last_message_date FROM users
                   WHERE last_message_date <= '{datetime.fromtimestamp(time.time() - 1210000).strftime("%Y-%m-%d")}';
                   """
            users = []
            for old in cursor.execute(sql):
                users.append(old)
            users = ''.join([i for i in str(users) if i not in '\'\"[]'])
            if message.text == "/old":
                bot.send_message(message.chat.id, text=f'{users}')

            if message.text == "/del":
                sql =  f"""
                       DELETE FROM users
                       WHERE last_message_date <= '{datetime.fromtimestamp(time.time() - 1210000).strftime("%Y-%m-%d")}';
                       """
            for dell in cursor.execute(sql):
                print(dell)

            if message.text in "/kick":
                sql = f"""
                       DELETE FROM users
                       WHERE last_message_date == ''
                       """
            for dell in cursor.execute(sql):
                print(dell)

            sql = f"""
                   SELECT count(id) FROM users;
                   """

            for count in cursor.execute(sql):
                print(count)

            if not result:
                #   Если нету в БД
                sql = f"""
                INSERT INTO users
                VALUES ({count[0] + 1}, '{nick}', '{user_id}', '{now.year}-{now.month}-{now.day}');
                """
                cursor.execute(sql)
                conn.commit()
                group(message)

            else:
                #   Если уже есть
                sql = f"""
                UPDATE users
                SET nick_name = '{nick}', last_message_date = '{now.year}-{now.month}-{now.day}'
                WHERE user_id = '{user_id}';
                """
                cursor.execute(sql)
                conn.commit()
                group(message)

        def group(message):
            if message.text == "/keyboard":
                keyboard = types.InlineKeyboardMarkup()
                callback_button = types.InlineKeyboardButton(text="Не жми меня", callback_data="button_1")
                keyboard.add(callback_button)
                bot.send_message(message.chat.id, "Пример текста сверху кнопки", reply_markup=keyboard)

        #   Это id юзера
        user_id = message.from_user.id

        #   Проверка новый пользователь или старый
        conn = sqlite3.connect("telegram_group.db")
        cursor = conn.cursor()
        sql = f"SELECT * FROM users WHERE user_id = '{user_id}'"
        result = ''

        for result in cursor.execute(sql):
            print(result)

        if result:
            bd(message)
        else:
            #   Если человек написал до нажатия по кнопке его кикнет
            if message.text == "Не бот":
                bd(message)
                return bot.delete_message(message.chat.id, message.message_id)
            elif user_id in Sent:
                return bot.kick_chat_member(message.chat.id, '{kickid}'.format(kickid=message.from_user.id))

            Sent.append(user_id)

            a = on_user_joins(message)
            bot.reply_to(message,
                         f"Пожалуйста {message.from_user.first_name} нажмите кнопку на кнопку что-бы подтвердить что вы не бот",
                         parse_mode='HTML', reply_markup=a)


def on_user_joins(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn = types.KeyboardButton("Не бот")
    keyboard.add(btn)

    return keyboard


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
