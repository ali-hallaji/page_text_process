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
    word = CharField()
    asyc_word = CharField()
    qty = IntegerField()

    class Meta:
        database = cursor


cursor.connect()
cursor.create_tables([TextProcess])
