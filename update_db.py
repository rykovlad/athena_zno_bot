import csv
import pprint
import sqlite3
import gspread
import os
import shutil
from models import *
from config import NAME_FILE_ON_DISK
from config import KEY_GOOGLE_API


def create_tables():
    with db:
        db.create_tables([Users, Subjects, Questions, Answers, PollQuestion])


create_tables()


def update_data():
    gc = gspread.service_account(filename=KEY_GOOGLE_API)
    sh = gc.open(NAME_FILE_ON_DISK)

    lists = [repr(x.title)[1:-1] for x in sh.worksheets()]
    if not os.path.exists("listsdir"):
        os.mkdir("listsdir")

    with sqlite3.connect('db/athena_zno.db') as db:
        create_tables()
        cursor = db.cursor()
        query = "DROP TABLE subjects"
        cursor.execute(query)
        query = "DROP TABLE questions"
        cursor.execute(query)
        query = "DROP TABLE answers"
        cursor.execute(query)
        create_tables()
        insert_list_of_subj = []
        for l in lists:
            insert_list_of_subj.append((l,))
        query = """INSERT INTO subjects(subject) VALUES(?)"""
        cursor.executemany(query, insert_list_of_subj)

    for i in range(len(lists)):
        worksheet = lists[i]
        filename = "listsdir/" + worksheet + '.csv'
        wksh = sh.get_worksheet(i)

        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(wksh.get_all_values())

        insert_quetions = []
        with open(filename, 'r') as f:
            for row in csv.reader(f):
                answers = "@".join(row[2:])
                while answers[-1] == '@':
                    answers = answers[0:-1]
                q = (row[0], int(row[1]) - 1, answers, i)
                insert_quetions.append(q)
        pprint.pprint(insert_quetions)

        with sqlite3.connect("db/athena_zno.db") as db:
            cursor = db.cursor()
            query = """INSERT INTO questions(question, correct_answer, answers, subject_id)
            VALUES(?,?,?,?);"""
            cursor.executemany(query, insert_quetions)
            db.commit()

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'listsdir')
    shutil.rmtree(path)


# update_data()
