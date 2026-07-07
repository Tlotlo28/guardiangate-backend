from app.core.security import (
    hash_password, verify_password,
    create_access_token, decode_access_token,
)

h = hash_password("MySecret123")
print("stored hash:", h[:29], "...")
print("correct password ->", verify_password("MySecret123", h))
print("wrong password   ->", verify_password("wrongpass", h))

token = create_access_token({"sub": "thandi@example.com", "role": "parent"})
print("token:", token[:40], "...")
print("decoded:", decode_access_token(token))
print("tampered token:", decode_access_token(token + "x"))