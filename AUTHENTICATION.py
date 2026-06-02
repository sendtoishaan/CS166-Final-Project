import hashlib
import secrets
from DATABASE_CONNECTION import query
 
def _hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()
 
def register_user(login: str, password: str, phone: str, address: str, favorite_category: str = None) -> dict:
    existing = query("SELECT login FROM Users WHERE login = %s", (login,), fetchone=True)
    
    if existing:
        return {"ok": False, "error": "Username already taken."}
 
    hashed = _hash_password(password)
    query(
        """
        INSERT INTO Users (login, password, phoneNum, role, address, favoriteCategory)
        VALUES (%s, %s, %s, 'Buyer', %s, %s)
        """,
        (login, hashed, phone, address, favorite_category or None),
        commit=True,
    )
    
    return {"ok": True}
 
 
def login_user(login: str, password: str) -> dict:
    hashed = _hash_password(password)
    user = query(
        "SELECT * FROM Users WHERE login = %s",
        (login,),
        fetchone=True,
    )
    
    if not user:
        return {"ok": False, "error": "Invalid username or password."}
 
    stored = user["password"]
    
    if stored != hashed and stored != password:
        return {"ok": False, "error": "Invalid username or password."}
 
    if stored == password and stored != hashed:
        query(
            "UPDATE Users SET password = %s WHERE login = %s",
            (hashed, login),
            commit=True,
        )
 
    return {"ok": True, "user": dict(user)}
 
def change_password(login: str, old_password: str, new_password: str) -> dict:
    result = login_user(login, old_password)
    
    if not result["ok"]:
        return {"ok": False, "error": "Current password is incorrect."}
    
    hashed = _hash_password(new_password)
    
    query("UPDATE Users SET password = %s WHERE login = %s", (hashed, login), commit=True)
    
    return {"ok": True}