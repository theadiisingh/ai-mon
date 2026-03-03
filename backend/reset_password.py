import sys
sys.path.insert(0, '.')

import sqlite3
import bcrypt

# Generate new hash for TestPass123
password = "TestPass123"
new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"New hash: {new_hash}")

# Update database
conn = sqlite3.connect('aimon.db')
c = conn.cursor()
c.execute("UPDATE users SET hashed_password = ? WHERE email = ?", (new_hash, 'test@example.com'))
conn.commit()
print(f"Updated rows: {c.rowcount}")
conn.close()

# Verify
conn = sqlite3.connect('aimon.db')
c = conn.cursor()
c.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", ('test@example.com',))
user = c.fetchone()
print(f"User after update: {user}")
conn.close()
