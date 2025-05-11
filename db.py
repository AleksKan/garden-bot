import sqlite3

def init_db():
    conn = sqlite3.connect('garden.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vegetables (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    quantity TEXT,
                    price REAL
                )''')
    conn.commit()
    conn.close()

def add_vegetable(name, quantity, price):
    conn = sqlite3.connect('garden.db')
    c = conn.cursor()
    c.execute("INSERT INTO vegetables (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()

def get_vegetables():
    conn = sqlite3.connect('garden.db')
    c = conn.cursor()
    c.execute("SELECT id, name, quantity, price FROM vegetables")
    items = c.fetchall()
    conn.close()
    return items
