from DATABASE_CONNECTION import query
 
def get_payments(login: str, role: str) -> list:
    if role == "Admin":
        return query("SELECT * FROM Payment ORDER BY paymentID DESC", fetchall=True)
    
    if role == "Buyer":
        return query(
            """
            SELECT p.*, i.itemName, a.auctionStatus
            FROM Payment p
            JOIN Auction a ON p.auctionID = a.auctionID
            JOIN Item i ON a.itemID = i.itemID
            WHERE p.buyerLogin = %s
            ORDER BY p.paymentID DESC
            """,
            (login,),
            fetchall=True,
        )
    
    return query(
        """
        SELECT p.*, i.itemName
        FROM Payment p
        JOIN Auction a ON p.auctionID = a.auctionID
        JOIN Item i ON a.itemID = i.itemID
        WHERE a.sellerLogin = %s
        ORDER BY p.paymentID DESC
        """,
        (login,),
        fetchall=True,
    )

def update_payment_status(login: str, role: str, payment_id: int, new_status: str) -> dict:
    if role not in ("Admin", "Buyer"):
        return {"ok": False, "error": "Permission denied."}
    
    if new_status not in ("Pending", "Completed", "Failed"):
        return {"ok": False, "error": "Invalid status."}
 
    payment = query(
        "SELECT * FROM Payment WHERE paymentID = %s", (payment_id,), fetchone=True
    )
    
    if not payment:
        return {"ok": False, "error": "Payment not found."}
    
    if role == "Buyer" and payment["buyerlogin"] != login:
        return {"ok": False, "error": "Permission denied."}
 
    query(
        "UPDATE Payment SET paymentStatus = %s WHERE paymentID = %s",
        (new_status, payment_id),
        commit=True,
    )
    
    return {"ok": True}
 
def get_shipments(login: str, role: str) -> list:
    if role == "Admin":
        return query(
            """
            SELECT s.*, i.itemName, a.sellerLogin, p.buyerLogin
            FROM Shipment s
            JOIN Auction a ON s.auctionID = a.auctionID
            JOIN Item i ON a.itemID = i.itemID
            LEFT JOIN Payment p ON p.auctionID = a.auctionID
            ORDER BY s.shipmentID DESC
            """,
            fetchall=True,
        )
    
    if role == "Seller":
        return query(
            """
            SELECT s.*, i.itemName
            FROM Shipment s
            JOIN Auction a ON s.auctionID = a.auctionID
            JOIN Item i ON a.itemID = i.itemID
            WHERE a.sellerLogin = %s
            ORDER BY s.shipmentID DESC
            """,
            (login,),
            fetchall=True,
        )

    return query(
        """
        SELECT s.*, i.itemName
        FROM Shipment s
        JOIN Auction a ON s.auctionID = a.auctionID
        JOIN Item i ON a.itemID = i.itemID
        JOIN Payment p ON p.auctionID = a.auctionID
        WHERE p.buyerLogin = %s
        ORDER BY s.shipmentID DESC
        """,
        (login,),
        fetchall=True,
    )

def update_shipment(login: str, role: str, shipment_id: int, new_status: str, tracking_number: str = None) -> dict:
    if role not in ("Admin", "Seller"):
        return {"ok": False, "error": "Permission denied."}
    
    if new_status not in ("Pending", "Shipped", "Delivered"):
        return {"ok": False, "error": "Invalid status."}
 
    shipment = query(
        "SELECT * FROM Shipment WHERE shipmentID = %s", (shipment_id,), fetchone=True
    )
    
    if not shipment:
        return {"ok": False, "error": "Shipment not found."}
 
    if role == "Seller":
        auction = query(
            "SELECT sellerLogin FROM Auction WHERE auctionID = %s",
            (shipment["auctionid"],),
            fetchone=True,
        )
        
        if not auction or auction["sellerlogin"] != login:
            return {"ok": False, "error": "Permission denied."}
 
    query(
        """
        UPDATE Shipment
        SET shipmentStatus = %s, trackingNumber = COALESCE(%s, trackingNumber)
        WHERE shipmentID = %s
        """,
        (new_status, tracking_number, shipment_id),
        commit=True,
    )
    
    return {"ok": True}