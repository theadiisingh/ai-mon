import sys
import bcrypt

# Test bcrypt directly
password = b"TestPass123"

# Generate hash
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)
print(f"Generated hash: {hashed}")
print(f"Hash length: {len(hashed)}")

# Test verification
result = bcrypt.checkpw(password, hashed)
print(f"Verification result: {result}")

# Test with stored hash
stored = b"$2b$12$gSmwFHtvbcND6pYc0A6HYezk2uUXd8dm/ZXqrkf2vItGNed4du8Dq"
try:
    result2 = bcrypt.checkpw(password, stored)
    print(f"Stored hash verification: {result2}")
except Exception as e:
    print(f"Error with stored hash: {e}")
