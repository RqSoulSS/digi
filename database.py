import sqlite3

def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            unique_code TEXT UNIQUE,
            quantity INTEGER,
            status TEXT DEFAULT 'waiting',
            timestamp INTEGER DEFAULT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_order(unique_code, quantity):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO orders (unique_code, quantity) VALUES (?, ?)", (unique_code, quantity))
    conn.commit()
    conn.close()

def update_order(unique_code, status, timestamp=None):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status=?, timestamp=? WHERE unique_code=?", (status, timestamp, unique_code))
    conn.commit()
    conn.close()

def get_orders_by_status(status):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT unique_code FROM orders WHERE status=?", (status,))
    orders = cursor.fetchall()
    conn.close()
    return [order[0] for order in orders]

def get_order(unique_code):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE unique_code=?", (unique_code,))
    order = cursor.fetchone()
    conn.close()
    return order
