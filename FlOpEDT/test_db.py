import os
import psycopg

POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

# Connect to the database.
#
db = psycopg.connect(
    host=POSTGRES_HOST,
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
)

cursor = db.cursor()

print(cursor)

cursor.close()
db.close()
