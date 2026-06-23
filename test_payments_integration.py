"""
Integration tests for payment/shipment workflow.
Uses an in-memory mock DB when PostgreSQL is unavailable.
Run: python test_payments_integration.py
"""
from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# In-memory database mock (mirrors PostgreSQL RealDictCursor lowercase keys)
# ---------------------------------------------------------------------------

DB = {
    "users": [
        {"login": "alice", "role": "Seller", "address": "123 Oak St"},
        {"login": "bob", "role": "Buyer", "address": "456 Pine Ave"},
        {"login": "carol", "role": "Buyer", "address": "789 Maple Dr"},
        {"login": "dave", "role": "Seller", "address": "321 Elm Blvd"},
        {"login": "admin", "role": "Admin", "address": "System"},
    ],
    "items": [
        {"itemid": 1, "itemname": "Camera", "category": "Electronics", "startingprice": 25.0, "sellerlogin": "alice"},
        {"itemid": 2, "itemname": "Book", "category": "Books", "startingprice": 50.0, "sellerlogin": "dave"},
    ],
    "auctions": [
        {"auctionid": 1, "itemid": 1, "sellerlogin": "alice", "currenthighestbid": 42.0, "auctionstatus": "Active"},
        {"auctionid": 2, "itemid": 2, "sellerlogin": "dave", "currenthighestbid": 120.0, "auctionstatus": "Closed"},
    ],
    "bids": [
        {"bidid": 1, "auctionid": 1, "buyerlogin": "bob", "bidamount": 30.0},
        {"bidid": 2, "auctionid": 1, "buyerlogin": "carol", "bidamount": 42.0},
        {"bidid": 3, "auctionid": 2, "buyerlogin": "carol", "bidamount": 120.0},
    ],
    "payments": [],
    "shipments": [],
    "next_payment_id": 1,
    "next_shipment_id": 1,
}

INITIAL_DB = deepcopy(DB)


def _reset_db():
    global DB
    DB = deepcopy(INITIAL_DB)


def _mock_query(sql: str, params=None, fetchone=False, fetchall=False, commit=False):
    sql_norm = " ".join(sql.split()).lower()
    params = params or ()

    # --- Payment lookups ---
    if "from payment where paymentid" in sql_norm:
        pid = params[0]
        row = next((p for p in DB["payments"] if p["paymentid"] == pid), None)
        return row if fetchone else None

    if "from payment where auctionid" in sql_norm:
        aid = params[0]
        row = next((p for p in DB["payments"] if p["auctionid"] == aid), None)
        return row if fetchone else None

    # --- Shipment lookups ---
    if "from shipment where shipmentid" in sql_norm:
        sid = params[0]
        row = next((s for s in DB["shipments"] if s["shipmentid"] == sid), None)
        return row if fetchone else None

    if "from shipment where auctionid" in sql_norm:
        aid = params[0]
        row = next((s for s in DB["shipments"] if s["auctionid"] == aid), None)
        return row if fetchone else None

    # --- Auction lookups ---
    if "from auction where auctionid" in sql_norm and "sellerlogin" not in sql_norm:
        aid = params[0]
        row = next((a for a in DB["auctions"] if a["auctionid"] == aid), None)
        return row if fetchone else None

    if "select sellerlogin from auction" in sql_norm:
        aid = params[0]
        row = next((a for a in DB["auctions"] if a["auctionid"] == aid), None)
        return {"sellerlogin": row["sellerlogin"]} if row else None

    # --- User address ---
    if "select address from users" in sql_norm:
        login = params[0]
        row = next((u for u in DB["users"] if u["login"] == login), None)
        return {"address": row["address"]} if row else None

    # --- Winner query (close auction) ---
    if "from bid" in sql_norm and "order by bidamount desc" in sql_norm:
        aid = params[0]
        bids = [b for b in DB["bids"] if b["auctionid"] == aid]
        if not bids:
            return None
        winner = max(bids, key=lambda b: b["bidamount"])
        return {"buyerlogin": winner["buyerlogin"], "bidamount": winner["bidamount"]}

    # --- Inserts ---
    if "insert into payment" in sql_norm and "returning paymentid" in sql_norm:
        aid, buyer, amount = params
        row = {
            "paymentid": DB["next_payment_id"],
            "auctionid": aid,
            "buyerlogin": buyer,
            "amount": amount,
            "paymentstatus": "Pending",
        }
        DB["next_payment_id"] += 1
        DB["payments"].append(row)
        return row

    if "insert into shipment" in sql_norm and "returning shipmentid" in sql_norm:
        aid, address = params
        row = {
            "shipmentid": DB["next_shipment_id"],
            "auctionid": aid,
            "address": address,
            "shipmentstatus": "Pending",
            "trackingnumber": None,
        }
        DB["next_shipment_id"] += 1
        DB["shipments"].append(row)
        return row

    # --- Updates ---
    if "update auction set auctionstatus" in sql_norm:
        aid = params[0]
        for a in DB["auctions"]:
            if a["auctionid"] == aid:
                a["auctionstatus"] = "Closed"
        return None

    if "update payment set paymentstatus" in sql_norm:
        status, pid = params
        for p in DB["payments"]:
            if p["paymentid"] == pid:
                p["paymentstatus"] = status
        return None

    if "update shipment set address" in sql_norm:
        address, sid = params
        for s in DB["shipments"]:
            if s["shipmentid"] == sid:
                s["address"] = address
        return None

    if "update shipment" in sql_norm and "shipmentstatus" in sql_norm:
        status, tn1, tn2, tn3, sid = params
        for s in DB["shipments"]:
            if s["shipmentid"] == sid:
                s["shipmentstatus"] = status
                if tn1 and tn1.strip():
                    s["trackingnumber"] = tn1
        return None

    # --- List queries (simplified joins) ---
    if "from payment p" in sql_norm:
        rows = []
        for p in DB["payments"]:
            auction = next(a for a in DB["auctions"] if a["auctionid"] == p["auctionid"])
            item = next(i for i in DB["items"] if i["itemid"] == auction["itemid"])
            row = {**p, "itemname": item["itemname"], "auctionstatus": auction["auctionstatus"], "sellerlogin": auction["sellerlogin"]}
            if "where p.buyerlogin" in sql_norm and p["buyerlogin"] != params[0]:
                continue
            if "where a.sellerlogin" in sql_norm and auction["sellerlogin"] != params[0]:
                continue
            rows.append(row)
        rows.sort(key=lambda r: r["paymentid"], reverse=True)
        return rows if fetchall else None

    if "from shipment s" in sql_norm:
        rows = []
        for s in DB["shipments"]:
            auction = next(a for a in DB["auctions"] if a["auctionid"] == s["auctionid"])
            item = next(i for i in DB["items"] if i["itemid"] == auction["itemid"])
            payment = next((p for p in DB["payments"] if p["auctionid"] == s["auctionid"]), None)
            row = {
                **s,
                "itemname": item["itemname"],
                "sellerlogin": auction["sellerlogin"],
                "buyerlogin": payment["buyerlogin"] if payment else None,
                "paymentstatus": payment["paymentstatus"] if payment else None,
            }
            if "where a.sellerlogin" in sql_norm and auction["sellerlogin"] != params[0]:
                continue
            if "where p.buyerlogin" in sql_norm and (not payment or payment["buyerlogin"] != params[0]):
                continue
            rows.append(row)
        rows.sort(key=lambda r: r["shipmentid"], reverse=True)
        return rows if fetchall else None

    raise NotImplementedError(f"Unmocked SQL: {sql_norm[:120]}")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_tests():
    import importlib.util
    from pathlib import Path

    def load_module(name, path):
        src = Path(path).read_text()
        if not src.startswith("from __future__"):
            src = "from __future__ import annotations\n" + src
        spec = importlib.util.spec_from_loader(name, loader=None)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        exec(compile(src, path, "exec"), mod.__dict__)
        return mod

    # Ensure DATABASE_CONNECTION is loaded first
    if "DATABASE_CONNECTION" not in sys.modules:
        load_module("DATABASE_CONNECTION", "DATABASE_CONNECTION.py")

    PAYMENTS = load_module("PAYMENTS", "PAYMENTS.py")
    AUCTIONS = load_module("AUCTIONS", "AUCTIONS.py")

    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  PASS  {name}")
        else:
            failed += 1
            print(f"  FAIL  {name} — {detail}")

    with patch("DATABASE_CONNECTION.query", side_effect=_mock_query), \
         patch("PAYMENTS.query", side_effect=_mock_query), \
         patch("AUCTIONS.query", side_effect=_mock_query):

        print("\n=== 1. Close auction creates payment + shipment ===")
        _reset_db()
        res = AUCTIONS.close_auction("alice", 1, "Seller")
        check("close succeeds", res["ok"], res)
        check("winner is carol", res["winner"]["buyerlogin"] == "carol")
        check("payment created", len(DB["payments"]) == 1)
        check("shipment created", len(DB["shipments"]) == 1)
        check("payment amount matches bid", float(DB["payments"][0]["amount"]) == 42.0)
        check("shipment uses buyer address", DB["shipments"][0]["address"] == "789 Maple Dr")

        print("\n=== 2. Buyer completes payment ===")
        pid = DB["payments"][0]["paymentid"]
        res = PAYMENTS.complete_payment("carol", pid)
        check("complete payment ok", res["ok"], res)
        check("status is Completed", DB["payments"][0]["paymentstatus"] == "Completed")

        print("\n=== 3. Seller cannot ship before payment (already paid, test negative) ===")
        sid = DB["shipments"][0]["shipmentid"]
        # Reset payment to pending to test gate
        DB["payments"][0]["paymentstatus"] = "Pending"
        res = PAYMENTS.update_shipment("alice", "Seller", sid, "Shipped", tracking_number="TRK123")
        check("ship blocked without payment", not res["ok"] and "payment" in res["error"].lower(), res)
        DB["payments"][0]["paymentstatus"] = "Completed"

        print("\n=== 4. Seller ships with tracking ===")
        res = PAYMENTS.update_shipment("alice", "Seller", sid, "Shipped", tracking_number="TRK123")
        check("ship succeeds", res["ok"], res)
        check("status Shipped", DB["shipments"][0]["shipmentstatus"] == "Shipped")
        check("tracking saved", DB["shipments"][0]["trackingnumber"] == "TRK123")

        print("\n=== 5. Seller marks delivered ===")
        res = PAYMENTS.update_shipment("alice", "Seller", sid, "Delivered")
        check("deliver succeeds", res["ok"], res)
        check("status Delivered", DB["shipments"][0]["shipmentstatus"] == "Delivered")

        print("\n=== 6. Permission checks ===")
        _reset_db()
        PAYMENTS.create_payment_and_shipment(2, "carol", 120.0, "789 Maple Dr")
        pid = DB["payments"][0]["paymentid"]
        sid = DB["shipments"][0]["shipmentid"]
        res = PAYMENTS.complete_payment("bob", pid)
        check("wrong buyer denied", not res["ok"])
        res = PAYMENTS.update_shipment("alice", "Seller", sid, "Shipped", tracking_number="X")
        check("wrong seller denied", not res["ok"])

        print("\n=== 7. Buyer updates address while pending ===")
        res = PAYMENTS.update_shipment_address("carol", sid, "999 New Address")
        check("address update ok", res["ok"], res)
        check("address saved", DB["shipments"][0]["address"] == "999 New Address")

        print("\n=== 8. Buyer cannot update address after shipped ===")
        DB["payments"][0]["paymentstatus"] = "Completed"
        PAYMENTS.update_shipment("dave", "Seller", sid, "Shipped", tracking_number="TRK999")
        res = PAYMENTS.update_shipment_address("carol", sid, "Another Address")
        check("address blocked after ship", not res["ok"])

        print("\n=== 9. Duplicate payment prevention ===")
        res = PAYMENTS.create_payment_and_shipment(2, "carol", 120.0, "789 Maple Dr")
        check("duplicate rejected", not res["ok"])

        print("\n=== 10. Role-based listing ===")
        carol_payments = PAYMENTS.get_payments("carol", "Buyer")
        dave_payments = PAYMENTS.get_payments("dave", "Seller")
        admin_payments = PAYMENTS.get_payments("admin", "Admin")
        check("buyer sees own payment", len(carol_payments) == 1)
        check("seller sees sale payment", len(dave_payments) == 1)
        check("admin sees all", len(admin_payments) == 1)

        carol_shipments = PAYMENTS.get_shipments("carol", "Buyer")
        dave_shipments = PAYMENTS.get_shipments("dave", "Seller")
        check("buyer sees own shipment", len(carol_shipments) == 1)
        check("seller sees own shipment", len(dave_shipments) == 1)

    print("\n=== 11. UI wiring checks ===")
    import inspect

    ui_src = Path("MAIN_STREAMLIT_UI.py").read_text()

    ui_funcs = {
        "get_payments", "get_shipments", "complete_payment", "fail_payment",
        "update_payment_status", "update_shipment", "update_shipment_address",
        "VALID_PAYMENT_STATUSES", "VALID_SHIPMENT_STATUSES",
    }
    for name in ui_funcs:
        check(f"PAYMENTS.{name} exists", hasattr(PAYMENTS, name))

    check("_render_payments_page in UI", "def _render_payments_page" in ui_src)
    check("_render_shipments_page in UI", "def _render_shipments_page" in ui_src)
    check("_status_label in UI", "def _status_label" in ui_src)

    check("UI calls complete_payment", "complete_payment" in ui_src)
    check("UI calls fail_payment", "fail_payment" in ui_src)
    check("UI calls update_shipment", "update_shipment" in ui_src)
    check("UI calls update_shipment_address", "update_shipment_address" in ui_src)
    check("Payments page wired", '_render_payments_page(user)' in ui_src)
    check("Shipments page wired", '_render_shipments_page(user)' in ui_src)

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
