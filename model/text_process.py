from peewee import *

from config import MYSQL_CRED


# Connect to a MySQL database on network.
cursor = MySQLDatabase(
    MYSQL_CRED['db_name'],
    user=MYSQL_CRED['user'],
    password=MYSQL_CRED['password'],
    host=MYSQL_CRED['host'],
    port=MYSQL_CRED['port']
)


class TextProcess(Model):
    word = CharField(primary_key=True, unique=True)
    asyc_word = CharField()
    qty = IntegerField()

    class Meta:
        database = cursor


class SentimentAnalysis(Model):
    salt_url = CharField(unique=True)
    url = CharField(unique=True)
    situation = CharField()

    class Meta:
        database = cursor
        primary_key = CompositeKey('salt_url', 'url')


cursor.connect()
cursor.create_tables([TextProcess, SentimentAnalysis])
