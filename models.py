from peewee import *

from config import DB_NAME

db = SqliteDatabase(DB_NAME)


class BaseModel(Model):
    id = PrimaryKeyField(primary_key=True)

    class Meta:
        database = db
        order_by = 'id'


class Users(BaseModel):
    id_user = IntegerField()
    name = CharField()
    subjects = CharField()

    class Meta:
        db_table = "users"


class Subjects(BaseModel):
    subject = CharField(unique=True)

    class Meta:
        db_table = "subjects"


class Questions(BaseModel):
    question = CharField()
    correct_answer = IntegerField()
    subject = ForeignKeyField(Subjects)
    answers = CharField()

    class Meta:
        db_table = "questions"


class Answers(Model):
    id = PrimaryKeyField(primary_key=True)
    id_user = IntegerField()
    is_right = BooleanField()
    quetion = ForeignKeyField(Questions)

    class Meta:
        database = db
        db_table = "answers"
        order_by = "id"
        indexes = ((('id_user', 'quetion_id'), True),)


class PollQuestion(Model):
    poll_id = PrimaryKeyField(primary_key=True)
    question = ForeignKeyField(Questions)

    class Meta:
        database = db
        db_table = "polls_questions"
        order_by = 'poll_id'
