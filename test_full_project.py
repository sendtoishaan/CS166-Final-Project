"""
Full end-to-end tests against live PostgreSQL.
Run with local postgres on port 5433:
  DB_PORT=5433 DB_USER=postgres DB_PASSWORD= python test_full_project.py
"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


def reset_database():
    root = Path(__file__).parent
    pg_bin = root / ".local/pgsql/bin"
    env = {**os.environ, "PATH": f"{pg_bin}:{os.environ.get('PATH', '')}"}
    port = os.environ.get("DB_PORT", "5433")
    user = os.environ.get("DB_USER", "postgres")
    db = os.environ.get("DB_NAME", "CS166_AUCTION_AND_BIDDING_DATABASE")

    subprocess.run(
        ["dropdb", "-p", port, "-U", user, "--if-exists", db],
        env=env, check=False, capture_output=True,
    )
    subprocess.run(["createdb", "-p", port, "-U", user, db], env=env, check=True)
    subprocess.run(
        ["psql", "-p", port, "-U", user, "-d", db, "-f", str(root / "AUCTION_AND_BIDDING_SCHEMA.sql")],
        env=env, check=True, capture_output=True,
    )
    subprocess.run(
        ["psql", "-p", port, "-U", user, "-d", db, "-f", str(root / "SAMPLE_AUCTION_AND_BIDDING_DATA.sql")],
        env=env, check=True, capture_output=True,
    )


def main():
    os.environ.setdefault("DB_PORT", "5433")
    os.environ.setdefault("DB_USER", "postgres")
    os.environ.setdefault("DB_PASSWORD", "")
    os.environ.setdefault("DB_NAME", "CS166_AUCTION_AND_BIDDING_DATABASE")

    print("Resetting database for clean test run...")
    reset_database()

    import AUTHENTICATION as AUTH
    import USERS
    import ITEMS
    import AUCTIONS
    import BIDS
    import PAYMENTS

    passed = failed = 0

    def check(name: str, ok: bool, detail=""):
        nonlocal passed, failed
        if ok:
            passed += 1
            print(f"  PASS  {name}")
        else:
            failed += 1
            print(f"  FAIL  {name} — {detail}")

    print("\n=== AUTHENTICATION ===")
    res = AUTH.login_user("admin", "admin123")
    check("admin login", res["ok"], res.get("error"))
    check("admin role", res.get("user", {}).get("role") == "Admin")

    res = AUTH.login_user("admin", "wrong")
    check("bad password rejected", not res["ok"])

    res = AUTH.register_user("testuser99", "pass123", "555-0000", "1 Test St", "Books")
    check("register new user", res["ok"], res.get("error"))
    res = AUTH.register_user("testuser99", "pass123", "555-0000", "1 Test St")
    check("duplicate username rejected", not res["ok"])

    res = AUTH.login_user("testuser99", "pass123")
    check("new user login", res["ok"])

    print("\n=== USERS ===")
    user = USERS.get_user("alice")
    check("get_user alice", user and user["role"] == "Seller")
    users = USERS.list_users()
    check("list_users", len(users) >= 6)
    res = USERS.update_profile("bob", "555-111-2222", "999 Updated Ave", "Sports")
    check("update_profile", res["ok"])
    bob = USERS.get_user("bob")
    check("profile saved", bob["address"] == "999 Updated Ave")

    print("\n=== ITEMS ===")
    res = ITEMS.create_item("alice", "Test Widget", "Electronics", 10.0, "desc", "New")
    check("create_item", res["ok"], res.get("error"))
    item_id = res.get("itemID")
    item = ITEMS.get_item(item_id)
    check("get_item", item and item["itemname"] == "Test Widget")
    items = ITEMS.list_items(seller_login="alice")
    check("list_items seller", any(i["itemid"] == item_id for i in items))
    res = ITEMS.update_item("alice", item_id, "Updated Widget", "Electronics", 15.0)
    check("update_item owner", res["ok"])
    res = ITEMS.update_item("bob", item_id, "Hack", "X", 1.0)
    check("update_item non-owner denied", not res["ok"])
    found = ITEMS.search_items("Widget")
    check("search_items", len(found) >= 1)
    cats = ITEMS.get_categories()
    check("get_categories", "Electronics" in cats)

    print("\n=== AUCTIONS & BIDS ===")
    res = AUCTIONS.create_auction("alice", item_id)
    check("create_auction", res["ok"], res.get("error"))
    auction_id = res.get("auctionID")

    res = AUCTIONS.create_auction("alice", item_id)
    check("duplicate active auction rejected", not res["ok"])

    res = BIDS.place_bid("bob", auction_id, 5.0)
    check("low bid rejected", not res["ok"])
    res = BIDS.place_bid("alice", auction_id, 20.0)
    check("own auction bid rejected", not res["ok"])
    res = BIDS.place_bid("bob", auction_id, 20.0)
    check("valid bid placed", res["ok"], res.get("error"))
    res = BIDS.place_bid("carol", auction_id, 25.0)
    check("outbid placed", res["ok"])

    auction = AUCTIONS.get_auction(auction_id)
    check("current highest bid updated", float(auction["currenthighestbid"]) == 25.0)

    bids = BIDS.get_bids_for_auction(auction_id)
    check("get_bids_for_auction", len(bids) >= 2)
    buyer_bids = BIDS.get_bids_for_buyer("carol")
    check("get_bids_for_buyer", any(b["auctionid"] == auction_id for b in buyer_bids))

    active = AUCTIONS.list_auctions(status="Active")
    check("list_auctions active", any(a["auctionid"] == auction_id for a in active))

    print("\n=== CLOSE AUCTION → PAYMENT + SHIPMENT ===")
    res = AUCTIONS.close_auction("alice", auction_id, "Seller")
    check("close_auction", res["ok"], res.get("error"))
    check("winner is carol", res.get("winner", {}).get("buyerlogin") == "carol")

    payment = PAYMENTS.get_payment_for_auction(auction_id)
    shipment = PAYMENTS.get_shipment_for_auction(auction_id)
    check("payment auto-created", payment is not None)
    check("shipment auto-created", shipment is not None)
    check("payment pending", payment["paymentstatus"] == "Pending")

    print("\n=== PAYMENTS WORKFLOW ===")
    pid = payment["paymentid"]
    sid = shipment["shipmentid"]

    carol_payments = PAYMENTS.get_payments("carol", "Buyer")
    check("buyer sees payment", any(p["paymentid"] == pid for p in carol_payments))

    alice_payments = PAYMENTS.get_payments("alice", "Seller")
    check("seller sees payment", any(p["paymentid"] == pid for p in alice_payments))

    res = PAYMENTS.update_shipment("alice", "Seller", sid, "Shipped", tracking_number="TRK1")
    check("ship blocked before payment", not res["ok"])

    res = PAYMENTS.complete_payment("carol", pid)
    check("buyer completes payment", res["ok"], res.get("error"))

    seller_view = PAYMENTS.get_seller_fulfillment("alice")
    seller_payment = next(p for p in seller_view if p["paymentid"] == pid)
    check("seller sees completed payment", seller_payment["paymentstatus"] == "Completed")
    check("seller sees shipment info", seller_payment.get("shipmentid") == sid)

    res = PAYMENTS.update_shipment_address("carol", sid, "111 New Ship St")
    check("buyer updates address", res["ok"])
    shipment = PAYMENTS.get_shipment(sid)
    check("address saved", shipment["address"] == "111 New Ship St")

    res = PAYMENTS.update_shipment("alice", "Seller", sid, "Shipped", tracking_number="TRK-FULL-TEST")
    check("seller ships item", res["ok"], res.get("error"))
    res = PAYMENTS.update_shipment("alice", "Seller", sid, "Delivered")
    check("seller marks delivered", res["ok"])

    shipment = PAYMENTS.get_shipment(sid)
    check("final status delivered", shipment["shipmentstatus"] == "Delivered")
    check("tracking saved", shipment["trackingnumber"] == "TRK-FULL-TEST")

    print("\n=== SAMPLE DATA SCENARIOS ===")
    # Auction 4: carol pending payment ($120)
    p4 = PAYMENTS.get_payment_for_auction(4)
    check("sample: auction 4 pending payment", p4 and p4["paymentstatus"] == "Pending")
    # Auction 3: eve paid, dave can ship
    p3 = PAYMENTS.get_payment_for_auction(3)
    s3 = PAYMENTS.get_shipment_for_auction(3)
    check("sample: auction 3 payment completed", p3 and p3["paymentstatus"] == "Completed")
    check("sample: auction 3 shipment pending", s3 and s3["shipmentstatus"] == "Pending")
    res = PAYMENTS.update_shipment("dave", "Seller", s3["shipmentid"], "Shipped", tracking_number="TRK-3")
    check("sample: dave ships auction 3", res["ok"], res.get("error"))
    # Auction 5: delivered
    s5 = PAYMENTS.get_shipment_for_auction(5)
    check("sample: auction 5 delivered", s5 and s5["shipmentstatus"] == "Delivered")

    print("\n=== ADMIN & DELETE ===")
    admin_payments = PAYMENTS.get_payments("admin", "Admin")
    check("admin sees all payments", len(admin_payments) >= 4)
    admin_shipments = PAYMENTS.get_shipments("admin", "Admin")
    check("admin sees all shipments", len(admin_shipments) >= 4)

    res = ITEMS.delete_item("bob", "Buyer", item_id)
    check("buyer delete denied", not res["ok"])

    # Use a fresh item with no auction/payment for admin delete
    res = ITEMS.create_item("dave", "Disposable Item", "Sports", 5.0)
    disposable_id = res["itemID"]
    res = ITEMS.delete_item("admin", "Admin", disposable_id)
    check("admin delete item", res["ok"])

    print("\n=== UI MODULE ===")
    ui_src = Path("MAIN_STREAMLIT_UI.py").read_text()
    check("UI has Payments page", 'elif page == "Payments"' in ui_src)
    check("UI has Shipments page", 'elif page == "Shipments"' in ui_src)
    check("UI renders payment actions", "_render_payments_page" in ui_src)
    check("UI renders shipment actions", "_render_shipments_page" in ui_src)

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
