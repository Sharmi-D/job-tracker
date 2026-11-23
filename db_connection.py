import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv("DB_URL")

def get_connection():
    try:
        conn = psycopg.connect(os.getenv("DB_URL"))
        print("Connected successfully!")
        return conn
    except psycopg.Error as e:
        print("OOPS! Connection failed:", e)
        return None


