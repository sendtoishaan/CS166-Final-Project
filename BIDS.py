from DATABASE_CONNECTION import query

def place_bid(buyer_login: str, auction_id: int, bid_amount: float) -> dict:
    auction = query(
        "SELECT * FROM Auction WHERE auctionID = %s",
        (auction_id,),
        fetchone=True,
    )
    
    if not auction:
        return {"ok": False, "error": "Auction not found."}
    
    if auction["auctionstatus"] != "Active":
        return {"ok": False, "error": "This auction is not active."}
    
    if auction["sellerlogin"] == buyer_login:
        return {"ok": False, "error": "Sellers cannot bid on their own auctions."}
    
    if bid_amount <= float(auction["currenthighestbid"]):
        return {
            "ok": False,
            "error": f"Bid must exceed current highest bid of ${auction['currenthighestbid']:.2f}.",
        }
 
    query(
        """
        INSERT INTO Bid (auctionID, buyerLogin, bidAmount)
        VALUES (%s, %s, %s)
        """,
        (auction_id, buyer_login, bid_amount),
        commit=True,
    )
    
    query(
        "UPDATE Auction SET currentHighestBid = %s WHERE auctionID = %s",
        (bid_amount, auction_id),
        commit=True,
    )
    
    return {"ok": True}

def get_bids_for_auction(auction_id: int) -> list:
    return query(
        """
        SELECT * FROM Bid
        WHERE auctionID = %s
        ORDER BY bidAmount DESC, bidTimestamp ASC
        """,
        (auction_id,),
        fetchall=True,
    )

def get_bids_for_buyer(buyer_login: str) -> list:
    return query(
        """
        SELECT b.*, a.auctionStatus, i.itemName, i.category
        FROM Bid b
        JOIN Auction a ON b.auctionID = a.auctionID
        JOIN Item i ON a.itemID = i.itemID
        WHERE b.buyerLogin = %s
        ORDER BY b.bidTimestamp DESC
        """,
        (buyer_login,),
        fetchall=True,
    )