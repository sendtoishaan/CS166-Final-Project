from __future__ import annotations

from DATABASE_CONNECTION import query

VALID_PAYMENT_STATUSES = ("Pending", "Completed", "Failed")
VALID_SHIPMENT_STATUSES = ("Pending", "Shipped", "Delivered")

PAYMENT_TRANSITIONS = {
    "Pending": {"Completed", "Failed"},
    "Completed": set(),
    "Failed": set(),
}

SHIPMENT_TRANSITIONS = {
    "Pending": {"Shipped"},
    "Shipped": {"Delivered"},
    "Delivered": set(),
}


def get_payments(login: str, role: str) -> list:
    if role == "Admin":
        return query(
            """
            SELECT p.*, i.itemName, a.auctionStatus, a.sellerLogin
            FROM Payment p
            JOIN Auction a ON p.auctionID = a.auctionID
            JOIN Item i ON a.itemID = i.itemID
            ORDER BY p.paymentID DESC
            """,
            fetchall=True,
        )

    if role == "Buyer":
        return query(
            """
            SELECT p.*, i.itemName, a.auctionStatus, a.sellerLogin
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
        SELECT p.*, i.itemName, a.auctionStatus, p.buyerLogin,
               s.shipmentID, s.shipmentStatus, s.trackingNumber, s.address AS shipAddress
        FROM Payment p
        JOIN Auction a ON p.auctionID = a.auctionID
        JOIN Item i ON a.itemID = i.itemID
        LEFT JOIN Shipment s ON s.auctionID = a.auctionID
        WHERE a.sellerLogin = %s
        ORDER BY p.paymentID DESC
        """,
        (login,),
        fetchall=True,
    )


def get_seller_fulfillment(login: str) -> list:
    """Payments and shipment details for a seller's closed auctions."""
    return query(
        """
        SELECT p.paymentID, p.auctionID, p.buyerLogin, p.amount, p.paymentStatus,
               i.itemName, a.auctionStatus,
               s.shipmentID, s.shipmentStatus, s.trackingNumber, s.address AS shipAddress
        FROM Payment p
        JOIN Auction a ON p.auctionID = a.auctionID
        JOIN Item i ON a.itemID = i.itemID
        LEFT JOIN Shipment s ON s.auctionID = a.auctionID
        WHERE a.sellerLogin = %s
        ORDER BY p.paymentID DESC
        """,
        (login,),
        fetchall=True,
    )


def get_payment(payment_id: int) -> dict | None:
    row = query("SELECT * FROM Payment WHERE paymentID = %s", (payment_id,), fetchone=True)
    return dict(row) if row else None


def get_payment_for_auction(auction_id: int) -> dict | None:
    row = query(
        "SELECT * FROM Payment WHERE auctionID = %s",
        (auction_id,),
        fetchone=True,
    )
    return dict(row) if row else None


def _can_manage_payment(login: str, role: str, payment: dict) -> bool:
    if role == "Admin":
        return True
    if role == "Buyer" and payment["buyerlogin"] == login:
        return True
    return False


def update_payment_status(login: str, role: str, payment_id: int, new_status: str) -> dict:
    if role not in ("Admin", "Buyer"):
        return {"ok": False, "error": "Permission denied."}

    if new_status not in VALID_PAYMENT_STATUSES:
        return {"ok": False, "error": "Invalid status."}

    payment = get_payment(payment_id)
    if not payment:
        return {"ok": False, "error": "Payment not found."}

    if not _can_manage_payment(login, role, payment):
        return {"ok": False, "error": "Permission denied."}

    current = payment["paymentstatus"]
    if role == "Buyer":
        allowed = PAYMENT_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            return {
                "ok": False,
                "error": f"Cannot change payment from {current} to {new_status}.",
            }
    elif role == "Admin" and new_status == current:
        return {"ok": True}

    query(
        "UPDATE Payment SET paymentStatus = %s WHERE paymentID = %s",
        (new_status, payment_id),
        commit=True,
    )

    return {"ok": True}


def complete_payment(buyer_login: str, payment_id: int) -> dict:
    return update_payment_status(buyer_login, "Buyer", payment_id, "Completed")


def fail_payment(buyer_login: str, payment_id: int) -> dict:
    return update_payment_status(buyer_login, "Buyer", payment_id, "Failed")


def get_shipments(login: str, role: str) -> list:
    if role == "Admin":
        return query(
            """
            SELECT s.*, i.itemName, a.sellerLogin, p.buyerLogin, p.paymentStatus
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
            SELECT s.*, i.itemName, p.buyerLogin, p.paymentStatus
            FROM Shipment s
            JOIN Auction a ON s.auctionID = a.auctionID
            JOIN Item i ON a.itemID = i.itemID
            LEFT JOIN Payment p ON p.auctionID = a.auctionID
            WHERE a.sellerLogin = %s
            ORDER BY s.shipmentID DESC
            """,
            (login,),
            fetchall=True,
        )

    return query(
        """
        SELECT s.*, i.itemName, a.sellerLogin, p.paymentStatus
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


def get_shipment(shipment_id: int) -> dict | None:
    row = query("SELECT * FROM Shipment WHERE shipmentID = %s", (shipment_id,), fetchone=True)
    return dict(row) if row else None


def get_shipment_for_auction(auction_id: int) -> dict | None:
    row = query(
        "SELECT * FROM Shipment WHERE auctionID = %s",
        (auction_id,),
        fetchone=True,
    )
    return dict(row) if row else None


def _seller_owns_shipment(login: str, shipment: dict) -> bool:
    auction = query(
        "SELECT sellerLogin FROM Auction WHERE auctionID = %s",
        (shipment["auctionid"],),
        fetchone=True,
    )
    return bool(auction and auction["sellerlogin"] == login)


def _buyer_owns_shipment(login: str, shipment: dict) -> bool:
    payment = get_payment_for_auction(shipment["auctionid"])
    return bool(payment and payment["buyerlogin"] == login)


def update_shipment_address(buyer_login: str, shipment_id: int, address: str) -> dict:
    shipment = get_shipment(shipment_id)
    if not shipment:
        return {"ok": False, "error": "Shipment not found."}

    if not _buyer_owns_shipment(buyer_login, shipment):
        return {"ok": False, "error": "Permission denied."}

    if shipment["shipmentstatus"] != "Pending":
        return {"ok": False, "error": "Address can only be updated before shipping."}

    if not address.strip():
        return {"ok": False, "error": "Address is required."}

    query(
        "UPDATE Shipment SET address = %s WHERE shipmentID = %s",
        (address.strip(), shipment_id),
        commit=True,
    )

    return {"ok": True}


def update_shipment(
    login: str,
    role: str,
    shipment_id: int,
    new_status: str,
    tracking_number: str = None,
) -> dict:
    if role not in ("Admin", "Seller"):
        return {"ok": False, "error": "Permission denied."}

    if new_status not in VALID_SHIPMENT_STATUSES:
        return {"ok": False, "error": "Invalid status."}

    shipment = get_shipment(shipment_id)
    if not shipment:
        return {"ok": False, "error": "Shipment not found."}

    if role == "Seller" and not _seller_owns_shipment(login, shipment):
        return {"ok": False, "error": "Permission denied."}

    current = shipment["shipmentstatus"]
    if role != "Admin":
        allowed = SHIPMENT_TRANSITIONS.get(current, set())
        if new_status != current and new_status not in allowed:
            return {
                "ok": False,
                "error": f"Cannot change shipment from {current} to {new_status}.",
            }

    payment = get_payment_for_auction(shipment["auctionid"])
    if new_status == "Shipped" and role != "Admin":
        if not payment or payment["paymentstatus"] != "Completed":
            return {
                "ok": False,
                "error": "Payment must be completed before the item can be shipped.",
            }
        if not tracking_number or not tracking_number.strip():
            return {"ok": False, "error": "Tracking number is required when marking as shipped."}

    if new_status == "Delivered" and role != "Admin" and current != "Shipped":
        return {"ok": False, "error": "Shipment must be shipped before it can be delivered."}

    query(
        """
        UPDATE Shipment
        SET shipmentStatus = %s,
            trackingNumber = CASE
                WHEN %s IS NOT NULL AND %s <> '' THEN %s
                ELSE trackingNumber
            END
        WHERE shipmentID = %s
        """,
        (new_status, tracking_number, tracking_number, tracking_number, shipment_id),
        commit=True,
    )

    return {"ok": True}


def create_payment_and_shipment(auction_id: int, buyer_login: str, amount: float, address: str) -> dict:
    existing = get_payment_for_auction(auction_id)
    if existing:
        return {"ok": False, "error": "Payment already exists for this auction."}

    payment_row = query(
        """
        INSERT INTO Payment (auctionID, buyerLogin, amount, paymentStatus)
        VALUES (%s, %s, %s, 'Pending')
        RETURNING paymentID
        """,
        (auction_id, buyer_login, amount),
        fetchone=True,
        commit=True,
    )

    shipment_row = query(
        """
        INSERT INTO Shipment (auctionID, address, shipmentStatus)
        VALUES (%s, %s, 'Pending')
        RETURNING shipmentID
        """,
        (auction_id, address),
        fetchone=True,
        commit=True,
    )

    return {
        "ok": True,
        "paymentID": payment_row["paymentid"],
        "shipmentID": shipment_row["shipmentid"],
    }
