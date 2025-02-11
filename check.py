import sqlite3

def print_all_data():
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    # Виведення користувачів
    print("Користувачі:")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(user)

    # Виведення валентинок
    print("\nВалентинки:")
    cursor.execute("SELECT * FROM valentines")
    valentines = cursor.fetchall()
    for valentine in valentines:
        print(valentine)

    conn.close()

# Викликаємо функцію для виведення даних
print_all_data()