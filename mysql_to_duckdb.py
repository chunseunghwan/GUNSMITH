# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

conn_mysql = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset='utf8mb4',
)