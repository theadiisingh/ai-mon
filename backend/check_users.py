import sqlite3

conn = sqlite3.connect('aimon.db')
c = conn.cursor()
c.execute('SELECT id, email, username, hashed_password, is_active FROM users')
users = c.fetchall()
for user in users:
    print(f"ID: {user[0]}, Email: {user[1]}, Username: {user[2]}, is_active: {user[4]}")
    print(f"  Hash: {user[3]}")
conn.close()
