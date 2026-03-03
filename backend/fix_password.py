"""
Script to fix password hash for user in database.
"""
import sqlite3
import bcrypt

def fix_password(email: str, new_password: str, db_path: str):
    """Update password hash for a user."""
    # Hash the new password
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Update password
    cursor.execute(
        "UPDATE users SET hashed_password = ? WHERE email = ?",
        (hashed.decode('utf-8'), email.lower())
    )
    
    conn.commit()
    
    # Verify update
    cursor.execute("SELECT id, email, username FROM users WHERE email = ?", (email.lower(),))
    user = cursor.fetchone()
    
    if user:
        print(f"✓ Updated password for user: {user[1]} (ID: {user[0]})")
    else:
        print(f"✗ User not found: {email}")
    
    conn.close()
    return user is not None

if __name__ == "__main__":
    email = "adityaveer.singh.2212@gmail.com"
    new_password = "password123"
    
    # Fix in both databases
    databases = [
        "c:/Users/ADITYA VEER SINGH/Desktop/ai-mon/aimon.db",
        "c:/Users/ADITYA VEER SINGH/Desktop/ai-mon/backend/aimon.db"
    ]
    
    for db_path in databases:
        print(f"\nProcessing: {db_path}")
        fix_password(email, new_password, db_path)
