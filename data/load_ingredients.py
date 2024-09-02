import sqlite3
import csv

# from .data import ingredients



# Откройте файл CSV
with open('.data/ingredients.csv', 'r', encoding='utf-8') as f:
 reader = csv.reader(f)

# Создайте подключение к базе данных SQLite
conn = sqlite3.connect('db.sqlite3')

# Создайте таблицу, если она не существует
cursor = conn.cursor()
# cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")

# Импортируйте данные из CSV файла
for row in reader:
 cursor.execute("INSERT INTO recipes_ingredients VALUES (?, ?, ?)", row)

# Зафиксируйте изменения в базе данных
conn.commit()

# Закройте курсор и соединение
cursor.close()