import sys
sys.path.insert(0, '.')

from app.core.security import verify_password, get_password_hash

# Test password verification
stored_hash = "$2b$12$n4xmw80I0Vwwhg1M5hL3/.pB3Jxy8arEwtClyRggAAFKomlE3e1RC"

# Try different passwords
test_passwords = ["TestPass123", "test", "password", "TestPass", "testpass123"]

for pwd in test_passwords:
    result = verify_password(pwd, stored_hash)
    print(f"Password '{pwd}': {result}")

# Generate a new hash for TestPass123
new_hash = get_password_hash("TestPass123")
print(f"\nNew hash for 'TestPass123': {new_hash}")

# Verify it
print(f"Verify new hash: {verify_password('TestPass123', new_hash)}")
