import sqlite3


def clear_db():
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    # Очищення таблиць
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM valentines")

    conn.commit()
    conn.close()


# Викликаємо функцію для очищення бази даних
clear_db()