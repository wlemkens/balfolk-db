import sys

from pydub import AudioSegment
import mysql.connector

from tools.common import *

def get_sample(id, db):
    cursor = db.cursor()
    sql = "SELECT * FROM samples WHERE id = %s"
    val = (id, )
    cursor.execute(sql, val)
    result = cursor.fetchall()
    if len(result) > 0:
        data = result[0][2]
        with open("restored.mp3", 'wb') as file:
            file.write(data)


def extract_sample(id):
    db = login_to_db()
    get_sample(id, db)

if __name__ == "__main__":
    extract_sample(sys.argv[1])