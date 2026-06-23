from __future__ import annotations

from DATABASE_CONNECTION import query

def create_item(seller_login: str, name: str, category: str, starting_price: float, description: str = None, condition: str = None, image_url: str = None) -> dict:
    row = query(
        """
        INSERT INTO Item (itemName, category, startingPrice, description,
                          condition, imageURL, sellerLogin)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING itemID
        """,
        (name, category, starting_price, description, condition, image_url, seller_login),
        fetchone=True,
        commit=True,
    )
    
    return {"ok": True, "itemID": row["itemid"]}
 
def get_item(item_id: int) -> dict | None:
    row = query("SELECT * FROM Item WHERE itemID = %s", (item_id,), fetchone=True)
    
    return dict(row) if row else None
 
def list_items(seller_login: str = None, category: str = None) -> list:
    sql = "SELECT * FROM Item WHERE 1=1"
    params = []
    
    if seller_login:
        sql += " AND sellerLogin = %s"
        params.append(seller_login)
    
    if category:
        sql += " AND category = %s"
        params.append(category)
    
    sql += " ORDER BY itemID DESC"
    
    return query(sql, params or None, fetchall=True)

def update_item(seller_login: str, item_id: int, name: str, category: str, starting_price: float, description: str = None, condition: str = None, image_url: str = None) -> dict:
    item = get_item(item_id)
    
    if not item:
        return {"ok": False, "error": "Item not found."}
    
    if item["sellerlogin"] != seller_login:
        return {"ok": False, "error": "You do not own this item."}
    
    query(
        """
        UPDATE Item
        SET itemName=%s, category=%s, startingPrice=%s,
            description=%s, condition=%s, imageURL=%s
        WHERE itemID=%s
        """,
        (name, category, starting_price, description, condition, image_url, item_id),
        commit=True,
    )
    
    return {"ok": True}
 
def delete_item(login: str, role: str, item_id: int) -> dict:
    item = get_item(item_id)
    
    if not item:
        return {"ok": False, "error": "Item not found."}
    
    if role != "Admin" and item["sellerlogin"] != login:
        return {"ok": False, "error": "Permission denied."}
    
    query("DELETE FROM Item WHERE itemID = %s", (item_id,), commit=True)
    
    return {"ok": True}
 
def search_items(keyword: str) -> list:
    like = f"%{keyword}%"
    
    return query(
        """
        SELECT * FROM Item
        WHERE itemName ILIKE %s OR category ILIKE %s OR description ILIKE %s
        ORDER BY itemID DESC
        """,
        (like, like, like),
        fetchall=True,
    )
 
def get_categories() -> list:
    rows = query("SELECT DISTINCT category FROM Item ORDER BY category", fetchall=True)
    
    return [r["category"] for r in rows]