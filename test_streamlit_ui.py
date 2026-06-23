"""Streamlit UI smoke tests using AppTest. Requires local PostgreSQL on port 5433."""
from __future__ import annotations

import os
import sys

os.environ.setdefault("DB_PORT", "5433")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "")
os.environ.setdefault("DB_NAME", "CS166_AUCTION_AND_BIDDING_DATABASE")

from streamlit.testing.v1 import AppTest


def login(at: AppTest, username: str, password: str):
    for t in at.text_input:
        if t.label == "Login":
            t.input(username)
        elif t.label == "Password":
            t.input(password)
    at.run()
    for b in at.button:
        if b.label == "Login":
            b.click().run()
            break
    assert not at.exception, f"Login crashed for {username}: {at.exception}"
    assert at.radio, f"Login failed for {username} — sidebar not shown"


def go_to(at: AppTest, page: str):
    at.radio[0].set_value(page).run()
    assert not at.exception, f"{page} page crashed: {at.exception}"


def main():
    passed = failed = 0

    def check(name, ok, detail=""):
        nonlocal passed, failed
        if ok:
            passed += 1
            print(f"  PASS  {name}")
        else:
            failed += 1
            print(f"  FAIL  {name} — {detail}")

    print("\n=== STREAMLIT UI TESTS ===")

    at = AppTest.from_file("MAIN_STREAMLIT_UI.py", default_timeout=30)
    at.run()
    check("app loads", not at.exception)
    check("login page shown", any(t.label == "Login" for t in at.text_input))

    login(at, "carol", "carol123")
    check("carol logged in", bool(at.radio))

    go_to(at, "Payments")
    check("payments page title", any("Payments" in t.value for t in at.title))
    check("payments cards shown", len(at.subheader) >= 1)
    check("complete payment button", any("Complete Payment" in b.label for b in at.button))

    go_to(at, "Shipments")
    check("shipments page title", any("Shipments" in t.value for t in at.title))

    go_to(at, "Auctions")
    check("auctions page loads", any("Auctions" in t.value for t in at.title))

    go_to(at, "My Bids")
    check("my bids page loads", any("My Bids" in t.value for t in at.title))

    # Buyer completes payment via UI
    go_to(at, "Payments")
    for b in at.button:
        if b.label == "Complete Payment":
            b.click().run()
            break
    check("complete payment via UI", not at.exception)

    # Seller flow
    at2 = AppTest.from_file("MAIN_STREAMLIT_UI.py", default_timeout=30)
    at2.run()
    login(at2, "dave", "dave123")
    go_to(at2, "Shipments")
    check("dave shipments page", any("Shipments" in t.value for t in at2.title))
    has_ship = any("Mark as Shipped" in b.label for b in at2.button)
    has_wait = any("payment" in w.value.lower() for w in at2.warning)
    check("dave sees ship or wait message", has_ship or has_wait or len(at2.subheader) >= 1)

    if has_ship:
        for t in at2.text_input:
            if "tracking" in t.label.lower():
                t.input("UI-TEST-TRACK-001")
                break
        for b in at2.button:
            if b.label == "Mark as Shipped":
                b.click().run()
                break
        check("dave ships via UI", not at2.exception)

    # Admin flow
    at3 = AppTest.from_file("MAIN_STREAMLIT_UI.py", default_timeout=30)
    at3.run()
    login(at3, "admin", "admin123")
    go_to(at3, "Admin")
    check("admin panel loads", any("Admin" in t.value for t in at3.title))
    check("admin sees payments section", any("Payments" in s.value for s in at3.subheader))
    check("admin sees shipments section", any("Shipments" in s.value for s in at3.subheader))

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
