import pprint
import random
import sqlite3
import time

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, italic, code
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN, ID_ADMINS, DB_NAME
from states import *
from update_db import update_data
from user_settings import UserSettings
from quetion import Quetion

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def taking_name(message):
    if message.from_user.last_name and message.from_user.username:
        name = message.from_user.first_name + " " + message.from_user.last_name + " aka @" + message.from_user.username
    elif message.chat.username:
        name = message.from_user.first_name + " aka @" + message.from_user.username
    else:
        name = message.from_user.first_name
    return name


def log_in_console(message: types.Message):
    print(taking_name(message), "-->", message.text)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    log_in_console(message)
    await bot.send_message(message.chat.id, 'привіт майбутній студенте, натисни /help \n'
                                            'щоб задонатити на збір дронів -> https://t.me/supreme_clown_memes/2177')

    with sqlite3.connect(DB_NAME) as db:
        cursor = db.cursor()
        query = f"SELECT id_user from users"
        cursor.execute(query)

        flag = False
        for i in cursor:
            if message.chat.id in i:
                flag = True
                break
        if not flag:
            query = f"SELECT COUNT(id) FROM subjects"
            count = cursor.execute(query)
            full_list = [x+1 for x in range(list(count)[0][0])]

            query = f"INSERT INTO users(id_user, name, subjects) VALUES('{message.from_user.id}', " \
                    f"'{taking_name(message)}', '{str(full_list)}') "
            cursor.execute(query)


@dp.message_handler(state=TestStates.all(), commands=['help'])
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    log_in_console(message)
    msg = """доступні команди: 
/start - початок роботи
/help - виклик цього меню
/start_testing - безпосередній перехід до тестів
/get_info - подивитись, які параметри вибрані для вас
/set_subj - обрати предмети, по яких ви хочете проходити тести
/cancel - вихід у головне (початкове) меню
"""
    await message.reply(msg)


@dp.message_handler(commands="update_db")
async def process_update_db_command(message: types.Message):
    log_in_console(message)

    if message.from_user.id in ID_ADMINS:
        await message.reply("ок, зараз", reply=False)
        await bot.send_chat_action(message.from_user.id, "upload_document")
        update_data()
        time.sleep(3)
        await message.reply("готово", reply=False)
    else:
        await message.reply("ти не адмін -_-")
        await bot.send_sticker(message.chat.id,
                               'CAACAgIAAxkBAAIGT2KT4hPY68C8Wif9giYpMscRilS7AAJAAAM0Itk1dSH4edIqdZ0kBA')


@dp.message_handler(state=TestStates.all(), commands=['cancel'])
@dp.message_handler(commands=['cancel'])
async def process_cancel_command(message: types.Message):
    log_in_console(message)
    remove_keyboard = types.ReplyKeyboardRemove()
    await message.reply("ви в основному меню", reply_markup=remove_keyboard)
    await dp.current_state(user=message.from_user.id).reset_state()


@dp.message_handler(state='*', commands=['start_testing'])
async def process_start_testing_command(message: types.Message):
    log_in_console(message)
    state = dp.current_state(user=message.from_user.id)
    answer = """розпочато тестування. предмети можна змінити в /set_subj
напишіть 'наступне запитання'
коли захочете вийти - напишіть /cancel 
"""
    kb1 = ReplyKeyboardMarkup(resize_keyboard=True,
                              ).add(KeyboardButton('наступне запитання'))

    await state.set_state('main_testing1')
    await message.reply(answer, reply_markup=kb1)


@dp.message_handler(state=TestStates.MAIN_TESTING1, text="наступне запитання")
async def process_main_testing1_command(msg: types.Message):
    log_in_console(msg)
    with sqlite3.connect(DB_NAME) as db:
        cursor = db.cursor()
        query = f"SELECT subjects FROM users WHERE id_user=={msg.from_user.id}"
        s = cursor.execute(query)

        list_of_subj = UserSettings.list_of_subj_str_to_list(list(s)[0][0])

        query = f"SELECT question, correct_answer, answers, id FROM questions WHERE "
        for i in list_of_subj:
            query += f"subject_id == {int(i) - 1} OR "
        query = query[:-4]

        s = list(cursor.execute(query))
        singl_quetion = s[random.randint(0, len(s) - 1)]
        id_q = singl_quetion[-1]

        q = Quetion(singl_quetion)
        pprint.pprint(q)
        poll = await bot.send_poll(msg.from_user.id, q.question, q.answers,
                                   is_anonymous=False,
                                   correct_option_id=q.correct_answer,
                                   type="quiz")
        query = f"INSERT INTO polls_questions(poll_id, question_id) VALUES({poll.poll.id}, {id_q})"
        cursor.execute(query)


@dp.message_handler(state='*', commands=['set_subj'])
async def process_set_subject0_command(msg: types.Message):
    log_in_console(msg)
    m = "обери предмети, що хочеш вибрати, й впиши через пробіл. наприклад '1 3'\nсписок предметів:\n\n"
    state = dp.current_state(user=msg.from_user.id)

    with sqlite3.connect(DB_NAME) as db:
        cursor = db.cursor()
        query = """SELECT id, subject FROM subjects """
        s = cursor.execute(query)
        for i in s:
            m += str(i[0]) + ') ' + str(i[1]) + "\n"

        await bot.send_message(msg.from_user.id, m)

    await state.set_state('subject_selection_menu')


@dp.message_handler(commands=['get_info'])
async def process_get_settings_command(message: types.Message):
    log_in_console(message)
    with sqlite3.connect(DB_NAME) as db:
        cursor = db.cursor()
        query = f"SELECT subjects FROM users WHERE id_user == {message.from_user.id}"
        subjs = list(cursor.execute(query))[0][0]

        query = f"SELECT id, subject FROM subjects WHERE id IN ({subjs[1:-1]}) "
        list_of_subjs = list(cursor.execute(query))

        msg_answer = "subjects: \n"
        for id, subj in list_of_subjs:
            msg_answer += str(id) + ") " + subj + "\n"

        query = """SELECT count(id) FROM answers WHERE id_user == ?"""
        total = list(cursor.execute(query, (message.from_user.id,)))[0][0]
        query = """SELECT count(id) FROM answers WHERE id_user == ? AND is_right == 1"""
        right_answer = list(cursor.execute(query, (message.from_user.id,)))[0][0]
        if total:
            stat = round(right_answer / total, 2)
        else:
            stat = 0
            
        msg_answer += "\nstat: " + str(stat) + "% (" + str(right_answer) + "/" + str(
            total) + ")"

        await bot.send_message(message.from_user.id, msg_answer)


@dp.message_handler(state=TestStates.SUBJECT_SELECTION_MENU)
async def process_set_subject1_command(msg: types.Message):
    log_in_console(msg)

    answer = msg.text.split(' ')

    with sqlite3.connect(DB_NAME) as db:
        cursor = db.cursor()
        query = f"SELECT id, subject FROM subjects "
        s = cursor.execute(query)
        sub_ids_list = []
        for i in s:
            sub_ids_list.append(int(i[0]))

        if not all(i.isdigit() for i in answer):
            await bot.send_message(msg.from_user.id, "якусь діч ти написав(ла), а якщо це образа - сам такий"
                                                     ". \nправильний варіант/приклад: '1 2'")
            return

        if not all(int(i) in sub_ids_list for i in answer):
            await bot.send_message(msg.from_user.id, "ти вписав(ла) номери, що не існують -_-")
            return

        answer = [int(i) for i in answer]

        query = f"UPDATE users SET subjects = '{answer}' WHERE id_user == {msg.from_user.id}"
        cursor.execute(query)

        await msg.reply("ok")
        await dp.current_state(user=msg.from_user.id).reset_state()


@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: types.PollAnswer):
    with sqlite3.connect(DB_NAME) as db:
        cursor = db.cursor()
        query = f"SELECT questions.id, correct_answer FROM questions, polls_questions WHERE polls_questions.poll_id " \
                f"== {quiz_answer.poll_id} AND polls_questions.question_id == questions.id"
        correct_answer = list(cursor.execute(query))[0][1]

        query = f"INSERT INTO  answers(id_user, is_right, quetion_id)" \
                f"VALUES({quiz_answer.user.id}, {correct_answer == quiz_answer.option_ids[0]}, {list(cursor.execute(query))[0][0]})" \
                f"ON CONFLICT (id_user, quetion_id) " \
                f"DO UPDATE SET is_right = 1 " \
                f"WHERE is_right = 0 AND excluded.is_right = 1"

        cursor.execute(query)


@dp.message_handler(state=TestStates.all(), content_types=ContentType.ANY)
@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    log_in_console(msg)
    message_text = text('я не знаю що з тим робити(',
                        italic('\nпросто нагадаю, що є '),
                        code('команда'), ' /help')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp)
