import sqlite3

def create_base():

    sql = """
        CREATE TABLE reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        remind_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        sent_at TIMESTAMP
    );
    """

    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    conn.close()

def create_remind(user_id, text, remind_at):
    sql = """ 
    INSERT INTO reminders (user_id, text, remind_at)
        VALUES (?, ?, ?)
    """
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute(sql, (user_id, text, remind_at))
    conn.commit()
    conn.close()


def read_remind(reminder_id):
    sql = """
    SELECT * FROM reminders
        WHERE user_id = ?
    """
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute(sql, (reminder_id,))
    result = c.fetchone()
    print(result)
    if result is None:
        return None

    text = result[2]
    return text