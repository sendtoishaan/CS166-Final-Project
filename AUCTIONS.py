from __future__ import annotations

from DATABASE_CONNECTION import query
import PAYMENTS
 
def create_auction(seller_login: str, item_id: int) -> dict:
    item = query(
        "SELECT * FROM Item WHERE itemID = %s AND sellerLogin = %s",
        (item_id, seller_login),
        fetchone=True,
    )
    
    if not item:
        return {"ok": False, "error": "Item not found or you do not own it."}
 
    existing = query(
        "SELECT auctionID FROM Auction WHERE itemID = %s AND auctionStatus = 'Active'",
        (item_id,),
        fetchone=True,
    )
    
    if existing:
        return {"ok": False, "error": "An active auction already exists for this item."}
 
    row = query(
        """
        INSERT INTO Auction (itemID, sellerLogin, currentHighestBid, auctionStatus)
        VALUES (%s, %s, %s, 'Active')
        RETURNING auctionID
        """,
        (item_id, seller_login, item["startingprice"]),
        fetchone=True,
        commit=True,
    )
    
    return {"ok": True, "auctionID": row["auctionid"]}

def get_auction(auction_id: int) -> dict | None:
    row = query(
        """
        SELECT a.*, i.itemName, i.category, i.description, i.condition,
               i.imageURL, i.startingPrice
        FROM Auction a
        JOIN Item i ON a.itemID = i.itemID
        WHERE a.auctionID = %s
        """,
        (auction_id,),
        fetchone=True,
    )
    
    return dict(row) if row else None
 
def list_auctions(status: str = None, seller_login: str = None, category: str = None, search: str = None) -> list:
    sql = """
        SELECT a.*, i.itemName, i.category, i.imageURL, i.startingPrice
        FROM Auction a
        JOIN Item i ON a.itemID = i.itemID
        WHERE 1=1
    """
    
    params = []
    
    if status:
        sql += " AND a.auctionStatus = %s"
        params.append(status)
    
    if seller_login:
        sql += " AND a.sellerLogin = %s"
        params.append(seller_login)
    
    if category:
        sql += " AND i.category = %s"
        params.append(category)
    
    if search:
        sql += " AND (i.itemName ILIKE %s OR i.description ILIKE %s)"
        like = f"%{search}%"
        params.extend([like, like])
    
    sql += " ORDER BY a.auctionID DESC"
    
    return query(sql, params or None, fetchall=True)

def close_auction(seller_login: str, auction_id: int, role: str = "Seller") -> dict:
    auction = query(
        "SELECT * FROM Auction WHERE auctionID = %s", (auction_id,), fetchone=True
    )
    
    if not auction:
        return {"ok": False, "error": "Auction not found."}
    
    if role != "Admin" and auction["sellerlogin"] != seller_login:
        return {"ok": False, "error": "Permission denied."}
    
    if auction["auctionstatus"] == "Closed":
        return {"ok": False, "error": "Auction is already closed."}
 
    query(
        "UPDATE Auction SET auctionStatus = 'Closed' WHERE auctionID = %s",
        (auction_id,),
        commit=True,
    )

    winner = query(
        """
        SELECT buyerLogin, bidAmount FROM Bid
        WHERE auctionID = %s
        ORDER BY bidAmount DESC, bidTimestamp ASC
        LIMIT 1
        """,
        (auction_id,),
        fetchone=True,
    )
    
    if winner:
        buyer = query(
            "SELECT address FROM Users WHERE login = %s",
            (winner["buyerlogin"],),
            fetchone=True,
        )

        PAYMENTS.create_payment_and_shipment(
            auction_id=auction_id,
            buyer_login=winner["buyerlogin"],
            amount=float(winner["bidamount"]),
            address=buyer["address"] if buyer else "TBD",
        )
    
    return {"ok": True, "winner": dict(winner) if winner else None}

def get_auction_winner(auction_id: int) -> dict | None:
    row = query(
        """
        SELECT b.buyerLogin, b.bidAmount, b.bidTimestamp
        FROM Bid b
        WHERE b.auctionID = %s
        ORDER BY b.bidAmount DESC, b.bidTimestamp ASC
        LIMIT 1
        """,
        (auction_id,),
        fetchone=True,
    )
    
    return dict(row) if row else None