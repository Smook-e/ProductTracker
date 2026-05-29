from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()  # Use the recommended hashing algorithm (currently bcrypt)
dummy_hash = password_hasher.hash("dummy_password")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)