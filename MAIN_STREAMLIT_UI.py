import streamlit as st

import AUTHENTICATION
import USERS
import ITEMS
import AUCTIONS
import BIDS
import PAYMENTS

st.set_page_config(page_title="CS166 Auction System", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = None

def login_user(login, password):
    result = AUTHENTICATION.login_user(login, password)
    
    if result["ok"]:
        st.session_state.user = result["user"]
        
        return True, result["user"]
    
    return False, result["error"]


def logout():
    st.session_state.user = None


def _status_label(status: str) -> str:
    icons = {
        "Pending": "🟡",
        "Completed": "🟢",
        "Failed": "🔴",
        "Shipped": "🔵",
        "Delivered": "🟢",
    }
    return f"{icons.get(status, '⚪')} {status}"


def _render_seller_ship_controls(user, shipment_id, payment_status, shipment_status, tracking_number=None, key_prefix="ship"):
    """Shared ship / deliver controls for sellers and admins."""
    role = user["role"]
    payment_status = payment_status or "Pending"
    shipment_status = shipment_status or "Pending"

    if shipment_status == "Pending":
        if payment_status != "Completed":
            st.warning("Waiting for the buyer to complete payment before you can ship.")
        else:
            st.success("Payment received — ready to ship.")
            tracking = st.text_input(
                "Tracking number",
                value=tracking_number or "",
                key=f"{key_prefix}_tracking_{shipment_id}",
            )
            if st.button("Mark as Shipped", key=f"{key_prefix}_mark_shipped_{shipment_id}"):
                res = PAYMENTS.update_shipment(
                    user["login"],
                    role,
                    shipment_id,
                    "Shipped",
                    tracking_number=tracking,
                )
                if res["ok"]:
                    st.success("Shipment marked as shipped.")
                    st.rerun()
                else:
                    st.error(res["error"])

    elif shipment_status == "Shipped":
        st.info(f"Item shipped. Tracking: {tracking_number or 'N/A'}")
        if st.button("Mark as Delivered", key=f"{key_prefix}_mark_delivered_{shipment_id}"):
            res = PAYMENTS.update_shipment(
                user["login"], role, shipment_id, "Delivered"
            )
            if res["ok"]:
                st.success("Shipment marked as delivered.")
                st.rerun()
            else:
                st.error(res["error"])

    elif shipment_status == "Delivered":
        st.success("Order delivered.")


def _render_payments_page(user):
    role = user["role"]
    if role == "Seller":
        payments = PAYMENTS.get_seller_fulfillment(user["login"])
    else:
        payments = PAYMENTS.get_payments(user["login"], role)

    if role == "Buyer":
        st.caption("Complete payment for auctions you won. Sellers ship after payment is completed.")
    elif role == "Seller":
        st.caption("Track buyer payments and ship items once payment is completed.")
    else:
        st.caption("View and manage all auction payments.")

    if not payments:
        st.info("No payments yet. Payments are created automatically when an auction with bids is closed.")
        return

    for payment in payments:
        payment_id = payment["paymentid"]
        item_name = payment.get("itemname", "Unknown item")
        status = payment.get("paymentstatus", "Pending")
        shipment_id = payment.get("shipmentid")
        shipment_status = payment.get("shipmentstatus")

        with st.container(border=True):
            st.subheader(item_name)
            st.write(f"**Payment ID:** {payment_id}")
            st.write(f"**Auction ID:** {payment['auctionid']}")
            st.write(f"**Amount:** ${float(payment['amount']):.2f}")
            st.write(f"**Payment Status:** {_status_label(status)}")

            if role in ("Seller", "Admin"):
                st.write(f"**Buyer:** {payment['buyerlogin']}")
            if role in ("Buyer", "Admin") and payment.get("sellerlogin"):
                st.write(f"**Seller:** {payment['sellerlogin']}")

            if role == "Seller":
                if status == "Completed":
                    st.success("Buyer has paid for this item.")
                elif status == "Failed":
                    st.error("Buyer payment failed.")
                else:
                    st.warning("Waiting for buyer to complete payment.")

                if shipment_status:
                    st.write(f"**Shipment Status:** {_status_label(shipment_status)}")
                    if payment.get("shipaddress"):
                        st.write(f"**Ship To:** {payment['shipaddress']}")

                if shipment_id and role == "Seller":
                    st.markdown("---")
                    _render_seller_ship_controls(
                        user,
                        shipment_id,
                        status,
                        shipment_status,
                        payment.get("trackingnumber"),
                        key_prefix="pay_ship",
                    )

            if role == "Buyer" and status == "Pending":
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Complete Payment", key=f"pay_complete_{payment_id}"):
                        res = PAYMENTS.complete_payment(user["login"], payment_id)
                        if res["ok"]:
                            st.success("Payment marked as completed.")
                            st.rerun()
                        else:
                            st.error(res["error"])
                with col2:
                    if st.button("Mark Failed", key=f"pay_fail_{payment_id}"):
                        res = PAYMENTS.fail_payment(user["login"], payment_id)
                        if res["ok"]:
                            st.warning("Payment marked as failed.")
                            st.rerun()
                        else:
                            st.error(res["error"])

            if role == "Admin":
                st.markdown("---")
                new_status = st.selectbox(
                    "Update status (Admin)",
                    PAYMENTS.VALID_PAYMENT_STATUSES,
                    index=PAYMENTS.VALID_PAYMENT_STATUSES.index(status),
                    key=f"admin_pay_status_{payment_id}",
                )
                if st.button("Update Payment", key=f"admin_pay_update_{payment_id}"):
                    res = PAYMENTS.update_payment_status(
                        user["login"], role, payment_id, new_status
                    )
                    if res["ok"]:
                        st.success("Payment updated.")
                        st.rerun()
                    else:
                        st.error(res["error"])


def _render_shipments_page(user):
    role = user["role"]
    shipments = PAYMENTS.get_shipments(user["login"], role)

    if role == "Buyer":
        st.caption("Track your orders. Update the shipping address before the seller ships.")
    elif role == "Seller":
        st.caption("Ship items after the buyer's payment is completed.")
    else:
        st.caption("View and manage all shipments.")

    if not shipments:
        st.info("No shipments yet. Shipments are created automatically when an auction with bids is closed.")
        return

    for shipment in shipments:
        shipment_id = shipment["shipmentid"]
        item_name = shipment.get("itemname", "Unknown item")
        status = shipment["shipmentstatus"]

        # Always fetch fresh payment status for seller/admin views
        payment = PAYMENTS.get_payment_for_auction(shipment["auctionid"])
        payment_status = payment["paymentstatus"] if payment else shipment.get("paymentstatus", "Unknown")

        with st.container(border=True):
            st.subheader(item_name)
            st.write(f"**Shipment ID:** {shipment_id}")
            st.write(f"**Auction ID:** {shipment['auctionid']}")
            st.write(f"**Ship To:** {shipment['address']}")
            st.write(f"**Payment Status:** {_status_label(payment_status)}")
            st.write(f"**Shipment Status:** {_status_label(status)}")

            if payment:
                st.write(f"**Amount Paid:** ${float(payment['amount']):.2f}")

            if shipment.get("trackingnumber"):
                st.write(f"**Tracking Number:** {shipment['trackingnumber']}")

            if role in ("Seller", "Admin") and shipment.get("buyerlogin"):
                st.write(f"**Buyer:** {shipment['buyerlogin']}")

            if role == "Buyer" and status == "Pending":
                st.markdown("---")
                new_address = st.text_input(
                    "Update shipping address",
                    value=shipment["address"],
                    key=f"ship_address_{shipment_id}",
                )
                if st.button("Save Address", key=f"ship_save_address_{shipment_id}"):
                    res = PAYMENTS.update_shipment_address(
                        user["login"], shipment_id, new_address
                    )
                    if res["ok"]:
                        st.success("Shipping address updated.")
                        st.rerun()
                    else:
                        st.error(res["error"])

            if role in ("Seller", "Admin") and status in ("Pending", "Shipped"):
                st.markdown("---")
                _render_seller_ship_controls(
                    user,
                    shipment_id,
                    payment_status,
                    status,
                    shipment.get("trackingnumber"),
                    key_prefix="ship_page",
                )

            if role == "Admin":
                st.markdown("---")
                new_status = st.selectbox(
                    "Update status (Admin)",
                    PAYMENTS.VALID_SHIPMENT_STATUSES,
                    index=PAYMENTS.VALID_SHIPMENT_STATUSES.index(status),
                    key=f"admin_ship_status_{shipment_id}",
                )
                admin_tracking = st.text_input(
                    "Tracking number (optional)",
                    value=shipment.get("trackingnumber") or "",
                    key=f"admin_ship_tracking_{shipment_id}",
                )
                if st.button("Update Shipment", key=f"admin_ship_update_{shipment_id}"):
                    res = PAYMENTS.update_shipment(
                        user["login"],
                        role,
                        shipment_id,
                        new_status,
                        tracking_number=admin_tracking,
                    )
                    if res["ok"]:
                        st.success("Shipment updated.")
                        st.rerun()
                    else:
                        st.error(res["error"])

st.sidebar.title("Navigation")

if st.session_state.user:
    page = st.sidebar.radio(
        "Go to",
        [
            "Dashboard",
            "Auctions",
            "My Bids",
            "Seller Items",
            "Create Item",
            "Create Auction",
            "Payments",
            "Shipments",
            "Profile",
            "Admin"
        ]
    )

    if st.sidebar.button("Logout"):
        logout()
        st.rerun()
else:
    page = "Login"

if page == "Login":
    st.title("Login")

    login = st.text_input("Login")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        ok, res = login_user(login, password)
        if ok:
            st.success(f"Welcome {res['login']}")
            st.rerun()
        else:
            st.error(res)

    st.markdown("---")
    st.subheader("Register")

    r_login = st.text_input("New Login")
    r_pass = st.text_input("New Password", type="password")
    phone = st.text_input("Phone")
    address = st.text_input("Address")
    fav = st.text_input("Favorite Category")

    if st.button("Create Account"):
        result = AUTHENTICATION.register_user(
            login=r_login,
            password=r_pass,
            phone=phone,
            address=address,
            favorite_category=fav
        )

        if result["ok"]:
            st.success("Account created! Please log in.")
        else:
            st.error(result["error"])

else:
    user = st.session_state.user

    if page == "Dashboard":
        st.title("Dashboard")

        auctions = AUCTIONS.list_auctions(status="Active")
        items = ITEMS.list_items()

        st.metric("Active Auctions", len(auctions))
        st.metric("Total Items", len(items))

        st.subheader("Recent Auctions")
        for a in auctions[:5]:
            st.write(a)

    elif page == "Auctions":
        st.title("Auctions")

        auctions = AUCTIONS.list_auctions(status="Active")

        for a in auctions:
            st.write(a)

            if st.button(f"View {a['auctionid']}"):
                st.session_state.selected_auction = a["auctionid"]

        if "selected_auction" in st.session_state:
            aid = st.session_state.selected_auction
            st.subheader(f"Auction {aid}")

            auction = AUCTIONS.get_auction(aid)
            bids = BIDS.get_bids_for_auction(aid)

            st.write(auction)
            st.write("Bids:")
            st.write(bids)

            if auction["auctionstatus"] == "Active":
                if auction["sellerlogin"] == user["login"]:
                    st.info("You cannot bid on your own auction.")
                else:
                    min_bid = float(auction["currenthighestbid"]) + 0.01
                    amount = st.number_input(
                        "Bid Amount",
                        min_value=min_bid,
                        value=min_bid,
                        step=0.01,
                        format="%.2f",
                    )

                    if st.button("Place Bid"):
                        res = BIDS.place_bid(user["login"], aid, amount)
                        if res["ok"]:
                            st.success("Bid placed")
                            st.rerun()
                        else:
                            st.error(res["error"])

            can_close = (user["role"] == "Admin") or (auction["sellerlogin"] == user["login"])
            if can_close and auction["auctionstatus"] == "Active":
                if st.button("Close Auction"):
                    res = AUCTIONS.close_auction(user["login"], aid, user["role"])
                    if res["ok"]:
                        winner = res["winner"]
                        if winner:
                            st.success(
                                f"Auction closed. Winner: {winner['buyerlogin']} "
                                f"(${winner['bidamount']}). Pending payment and shipment created."
                            )
                        else:
                            st.success("Auction closed with no bids.")
                    else:
                        st.error(res["error"])

    elif page == "My Bids":
        st.title("My Bids")

        bids = BIDS.get_bids_for_buyer(user["login"])
        st.write(bids)

    elif page == "Seller Items":
        st.title("My Items")

        items = ITEMS.list_items(
            seller_login=user["login"] if user["role"] == "Seller" else None
        )

        for i in items:
            st.write(i)

    elif page == "Create Item":
        st.title("Create Item")

        name = st.text_input("Name")
        category = st.text_input("Category")
        price = st.number_input("Starting Price", min_value=0.0)
        desc = st.text_area("Description")

        if st.button("Create"):
            res = ITEMS.create_item(
                seller_login=user["login"],
                name=name,
                category=category,
                starting_price=price,
                description=desc
            )

            if res["ok"]:
                st.success("Item created")
            else:
                st.error(res["error"])

    elif page == "Create Auction":
        st.title("Create Auction")

        items = ITEMS.list_items(seller_login=user["login"])
        item_map = {f"{i['itemid']} - {i['itemname']}": i["itemid"] for i in items}

        selected = st.selectbox("Select Item", list(item_map.keys()))

        if st.button("Start Auction"):
            res = AUCTIONS.create_auction(user["login"], item_map[selected])

            if res["ok"]:
                st.success("Auction created")
            else:
                st.error(res["error"])

    elif page == "Payments":
        st.title("Payments")
        _render_payments_page(user)

    elif page == "Shipments":
        st.title("Shipments")
        _render_shipments_page(user)

    elif page == "Profile":
        st.title("Profile")

        st.write(user)

        phone = st.text_input("Phone", value=user.get("phonenum", ""))
        address = st.text_input("Address", value=user.get("address", ""))

        if st.button("Update"):
            res = USERS.update_profile(
                user["login"],
                phone,
                address,
                user.get("favoriteCategory")
            )

            if res["ok"]:
                st.success("Updated")
                st.session_state.user = USERS.get_user(user["login"])
 
    elif page == "Admin":
        if user["role"] != "Admin":
            st.error("Access denied")
        else:
            st.title("Admin Panel")

            st.subheader("Users")
            st.write(USERS.list_users())

            st.subheader("All Auctions")
            st.write(AUCTIONS.list_auctions())

            st.subheader("Payments")
            _render_payments_page(user)

            st.subheader("Shipments")
            _render_shipments_page(user)