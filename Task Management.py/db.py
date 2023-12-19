import sqlite3

conn = sqlite3.connect("task_list.sqlite")

cursor = conn.cursor()
sql_query = """ CREATE TABLE task_list(
          id integer PRIMARY KEY,
          Title text NOT NULL,
          Description text NOT NULL,
          DueDate  NOT NULL,
          Status text NOT NULL
)"""
cursor.execute(sql_query)