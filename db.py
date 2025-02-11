import sqlite3

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    # Таблиця користувачів
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            registered_at TEXT
        )
    """)

    # Таблиця валентинок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS valentines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            text TEXT,
            is_anonymous INTEGER,
            sent_at TEXT
        )
    """)

    conn.commit()
    conn.close()

# Додавання користувача
def add_user(user_id, username, first_name, last_name):
    if not username:
        username = ""  # Встановити порожнє значення, якщо username немає
    full_name = f"{first_name} {last_name}"
    print(f"Adding user: {user_id}, {username}, {full_name}")  # Логування
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, name, registered_at)
        VALUES (?, ?, ?, datetime('now'))
    """, (user_id, username, full_name))

    conn.commit()
    conn.close()


# Отримання користувачів
def get_all_users():
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()

    conn.close()
    return users

def get_user_by_id(user_id):
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, name FROM users WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user

# Збереження валентинки
def save_valentine(sender_id, receiver_id, text, is_anonymous):
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO valentines (sender_id, receiver_id, text, is_anonymous, sent_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (sender_id, receiver_id, text, int(is_anonymous)))

    conn.commit()
    conn.close()

def find_users_by_username(username):
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name FROM users 
        WHERE username LIKE ?
    """, (f"%{username}%",))

    users = cursor.fetchall()
    conn.close()
    return users

def find_users_by_name(name):
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name FROM users 
        WHERE name LIKE ?
    """, (f"%{name}%",))

    users = cursor.fetchall()
    conn.close()
    return users

# Отримання валентинок
def get_user_valentines(user_id):
    conn = sqlite3.connect("valentine_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT text, 
               (SELECT name FROM users WHERE id = valentines.sender_id) AS sender_name, 
               is_anonymous 
        FROM valentines 
        WHERE receiver_id = ?
    """, (user_id,))

    valentines = cursor.fetchall()
    conn.close()
    return valentines