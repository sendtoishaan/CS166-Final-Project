from DATABASE_CONNECTION import query

def get_user(login: str) -> dict | None:
    row = query("SELECT * FROM Users WHERE login = %s", (login,), fetchone=True)
    
    return dict(row) if row else None
 
 
def update_profile(login: str, phone: str, address: str, favorite_category: str = None) -> dict:
    query(
        """
        UPDATE Users
        SET phoneNum = %s, address = %s, favoriteCategory = %s
        WHERE login = %s
        """,
        (phone, address, favorite_category or None, login),
        commit=True,
    )
    
    return {"ok": True}
 
def list_users() -> list:
    return query("SELECT login, phoneNum, role, address, favoriteCategory FROM Users ORDER BY login", fetchall=True)

def change_role(admin_login: str, target_login: str, new_role: str) -> dict:
    admin = query("SELECT role FROM Users WHERE login = %s", (admin_login,), fetchone=True)
    
    if not admin or admin["role"] != "Admin":
        return {"ok": False, "error": "Permission denied."}
    
    if new_role not in ("Buyer", "Seller", "Admin"):
        return {"ok": False, "error": "Invalid role."}
    
    query("UPDATE Users SET role = %s WHERE login = %s", (new_role, target_login), commit=True)
    
    return {"ok": True}
 
 
def delete_user(admin_login: str, target_login: str) -> dict:
    admin = query("SELECT role FROM Users WHERE login = %s", (admin_login,), fetchone=True)
    
    if not admin or admin["role"] != "Admin":
        return {"ok": False, "error": "Permission denied."}
    
    query("DELETE FROM Users WHERE login = %s", (target_login,), commit=True)
    
    return {"ok": True}