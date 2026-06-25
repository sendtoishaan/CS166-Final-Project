import streamlit as st

import AUTHENTICATION
import USERS
import ITEMS
import AUCTIONS
import BIDS
import PAYMENTS
import UI_THEME

st.set_page_config(
    page_title="BidVault — Online Auctions",
    page_icon="🔨",
    layout="wide",
)

UI_THEME.inject_theme()

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Login"


def _format_currency(amount) -> str:
    if amount is None:
        return "—"
    return f"${float(amount):,.2f}"


def _format_timestamp(ts) -> str:
    if ts is None:
        return "—"
    if hasattr(ts, "strftime"):
        return ts.strftime("%b %d, %Y · %I:%M %p")
    return str(ts)


def _auction_status_label(status: str) -> str:
    icons = {"Active": "🟢", "Closed": "🔴"}
    return f"{icons.get(status, '⚪')} {status}"


def _role_label(role: str) -> str:
    icons = {"Buyer": "🛒", "Seller": "🏪", "Admin": "⚙️"}
    return f"{icons.get(role, '👤')} {role}"


def _detail(label: str, value) -> None:
    st.markdown(f"**{label}**  \n{value}")


def _render_item_card(item: dict, *, show_seller: bool = True) -> None:
    image_url = UI_THEME.item_image_url(item)
    with st.container(border=True):
        img_col, header_col = st.columns([1, 2])
        with img_col:
            st.image(image_url, use_container_width=True)
        with header_col:
            st.subheader(item.get("itemname", "Unknown item"))
            st.caption(f"Category: {item.get('category', '—')}")
            if item.get("condition"):
                st.caption(f"Condition: **{item['condition']}**")
            st.metric("Starting price", _format_currency(item.get("startingprice")))

        info_col, meta_col = st.columns(2)
        with info_col:
            if item.get("description"):
                st.markdown(f"**Description**  \n{item['description']}")
        with meta_col:
            _detail("Item ID", item.get("itemid", "—"))
            if show_seller and item.get("sellerlogin"):
                _detail("Seller", item["sellerlogin"])


def _render_auction_summary(auction: dict) -> None:
    image_url = UI_THEME.item_image_url(auction)
    img_col, info_col = st.columns([1, 2])
    with img_col:
        st.image(image_url, use_container_width=True)
    with info_col:
        st.markdown(
            UI_THEME.status_pill(auction.get("auctionstatus", "Unknown")),
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current bid", _format_currency(auction.get("currenthighestbid")))
        with col2:
            st.metric("Starting price", _format_currency(auction.get("startingprice")))

    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        _detail("Auction ID", auction.get("auctionid", "—"))
        _detail("Seller", auction.get("sellerlogin", "—"))
        if auction.get("category"):
            _detail("Category", auction["category"])
    with detail_col2:
        if auction.get("createdat"):
            _detail("Listed", _format_timestamp(auction["createdat"]))
        if auction.get("description"):
            _detail("Description", auction["description"])


def _render_bid_history(bids: list) -> None:
    st.markdown("**Bid history**")
    if not bids:
        st.info("No bids yet. Be the first to bid!")
        return

    rows = []
    for rank, bid in enumerate(bids, start=1):
        rows.append(
            {
                "#": rank,
                "Buyer": bid["buyerlogin"],
                "Amount": _format_currency(bid["bidamount"]),
                "Placed": _format_timestamp(bid.get("bidtimestamp")),
            }
        )
    st.table(rows)


def _render_bid_card(bid: dict) -> None:
    auction_status = bid.get("auctionstatus", "Unknown")
    with st.container(border=True):
        header_col, amount_col = st.columns([3, 1])
        with header_col:
            st.subheader(bid.get("itemname", "Unknown item"))
            st.caption(f"{bid.get('category', '—')} · Auction #{bid.get('auctionid', '—')}")
            st.markdown(UI_THEME.status_pill(auction_status), unsafe_allow_html=True)
        with amount_col:
            st.metric("Your bid", _format_currency(bid.get("bidamount")))

        col1, col2, col3 = st.columns(3)
        with col1:
            _detail("Bid ID", bid.get("bidid", "—"))
        with col2:
            _detail("Auction status", _auction_status_label(auction_status))
        with col3:
            _detail("Placed", _format_timestamp(bid.get("bidtimestamp")))


def _render_user_profile(user: dict) -> None:
    with st.container(border=True):
        profile_col, details_col = st.columns([1, 2])
        with profile_col:
            st.markdown(f"### {user.get('login', 'User')}")
            st.markdown(_role_label(user.get("role", "Buyer")))
        with details_col:
            col1, col2 = st.columns(2)
            with col1:
                _detail("Phone", user.get("phonenum") or "—")
                _detail("Favorite category", user.get("favoritecategory") or "—")
            with col2:
                _detail("Address", user.get("address") or "—")


def _render_users_table(users: list) -> None:
    if not users:
        st.info("No users found.")
        return

    rows = [
        {
            "Login": u["login"],
            "Role": u["role"],
            "Phone": u.get("phonenum") or "—",
            "Address": u.get("address") or "—",
            "Favorite category": u.get("favoritecategory") or "—",
        }
        for u in users
    ]
    st.table(rows)


def login_user(login, password):
    result = AUTHENTICATION.login_user(login, password)
    
    if result["ok"]:
        st.session_state.user = result["user"]
        st.session_state.page = "Dashboard"
        return True, result["user"]
    
    return False, result["error"]


def logout():
    st.session_state.user = None
    st.session_state.page = "Login"


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
            col1, col2, col3 = st.columns(3)
            with col1:
                _detail("Payment ID", payment_id)
                _detail("Auction ID", payment["auctionid"])
            with col2:
                st.metric("Amount", _format_currency(payment["amount"]))
            with col3:
                _detail("Payment status", _status_label(status))

            if role in ("Seller", "Admin"):
                _detail("Buyer", payment["buyerlogin"])
            if role in ("Buyer", "Admin") and payment.get("sellerlogin"):
                _detail("Seller", payment["sellerlogin"])

            if role == "Seller":
                if status == "Completed":
                    st.success("Buyer has paid for this item.")
                elif status == "Failed":
                    st.error("Buyer payment failed.")
                else:
                    st.warning("Waiting for buyer to complete payment.")

                if shipment_status:
                    _detail("Shipment status", _status_label(shipment_status))
                    if payment.get("shipaddress"):
                        _detail("Ship to", payment["shipaddress"])

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
            col1, col2 = st.columns(2)
            with col1:
                _detail("Shipment ID", shipment_id)
                _detail("Auction ID", shipment["auctionid"])
                _detail("Ship to", shipment["address"])
            with col2:
                _detail("Payment status", _status_label(payment_status))
                _detail("Shipment status", _status_label(status))
                if payment:
                    st.metric("Amount paid", _format_currency(payment["amount"]))
                if shipment.get("trackingnumber"):
                    _detail("Tracking number", shipment["trackingnumber"])

            if role in ("Seller", "Admin") and shipment.get("buyerlogin"):
                _detail("Buyer", shipment["buyerlogin"])

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

if st.session_state.user:
    page = st.session_state.page
    if page not in UI_THEME.NAV_PAGES:
        page = "Dashboard"
        st.session_state.page = page
    UI_THEME.render_top_nav(st.session_state.user, page)
else:
    page = "Login"
    st.session_state.page = "Login"

if page == "Login":
    UI_THEME.hero_banner(
        "Welcome to BidVault",
        "Discover rare finds, place live bids, and win exclusive items from trusted sellers.",
        "login",
        badge="CS166 Auction Platform",
    )
    UI_THEME.login_feature_strip()

    form_col1, form_col2 = st.columns(2)

    with form_col1:
        with st.container(border=True):
            UI_THEME.section_header("Sign in", "🔑")
            login = st.text_input("Login")
            password = st.text_input("Password", type="password")

            if st.button("Login", use_container_width=True, type="primary"):
                ok, res = login_user(login, password)
                if ok:
                    st.success(f"Welcome back, {res['login']}!")
                    st.rerun()
                else:
                    st.error(res)

    with form_col2:
        with st.container(border=True):
            UI_THEME.section_header("Create account", "✨")
            r_login = st.text_input("New login")
            r_pass = st.text_input("New password", type="password")
            phone = st.text_input("Phone")
            address = st.text_input("Address")
            fav = st.text_input("Favorite category")

            if st.button("Create account", use_container_width=True):
                result = AUTHENTICATION.register_user(
                    login=r_login,
                    password=r_pass,
                    phone=phone,
                    address=address,
                    favorite_category=fav
                )

                if result["ok"]:
                    st.success("Account created! Please sign in.")
                else:
                    st.error(result["error"])

else:
    user = st.session_state.user

    if page == "Dashboard":
        UI_THEME.hero_banner(
            f"Good to see you, {user['login']}",
            "Your marketplace at a glance — track live auctions, your bids, and trending listings.",
            "dashboard",
            badge="Dashboard",
        )

        auctions = AUCTIONS.list_auctions(status="Active")
        items = ITEMS.list_items()
        my_bids = BIDS.get_bids_for_buyer(user["login"])

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            UI_THEME.metric_tile("Active auctions", len(auctions))
        with metric_col2:
            UI_THEME.metric_tile("Total items", len(items))
        with metric_col3:
            UI_THEME.metric_tile("Your bids", len(my_bids))

        UI_THEME.section_header("Featured live auctions", "🔥")
        if not auctions:
            st.info("No active auctions right now.")
        else:
            cols = st.columns(3)
            for idx, a in enumerate(auctions[:6]):
                with cols[idx % 3]:
                    st.markdown(
                        UI_THEME.auction_tile_html(
                            title=a["itemname"],
                            category=a.get("category", "—"),
                            seller=a["sellerlogin"],
                            auction_id=a["auctionid"],
                            bid=_format_currency(a["currenthighestbid"]),
                            status=a["auctionstatus"],
                            image_url=UI_THEME.item_image_url(a),
                        ),
                        unsafe_allow_html=True,
                    )

    elif page == "Auctions":
        UI_THEME.hero_banner(
            "Live Auction Floor",
            "Browse active listings, place bids in real time, and close out your sales.",
            "auctions",
            badge=f"{len(AUCTIONS.list_auctions(status='Active'))} live now",
        )

        auctions = AUCTIONS.list_auctions(status="Active")

        if not auctions:
            st.info("No active auctions at the moment. Check back soon!")
        else:
            for a in auctions:
                bid_label = _format_currency(a["currenthighestbid"])
                with st.expander(
                    f"🏷️ {a['itemname']}  ·  {bid_label}  ·  {a['auctionstatus']}",
                ):
                    _render_auction_summary(a)

                    st.markdown("---")
                    bids = BIDS.get_bids_for_auction(a["auctionid"])
                    _render_bid_history(bids)

                    if a["auctionstatus"] == "Active":
                        st.markdown("---")
                        if a["sellerlogin"] == user["login"]:
                            st.info("This is your auction — you cannot place bids on it.")
                        else:
                            min_bid = float(a["currenthighestbid"]) + 0.01
                            bid_col1, bid_col2 = st.columns([2, 1])
                            with bid_col1:
                                amount = st.number_input(
                                    "Your bid amount",
                                    min_value=min_bid,
                                    value=min_bid,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"bid_amount_{a['auctionid']}",
                                )
                            with bid_col2:
                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button(
                                    "Place bid",
                                    key=f"place_bid_{a['auctionid']}",
                                    type="primary",
                                ):
                                    res = BIDS.place_bid(user["login"], a["auctionid"], amount)
                                    if res["ok"]:
                                        st.success("Bid placed successfully!")
                                        st.rerun()
                                    else:
                                        st.error(res["error"])

                    can_close = (user["role"] == "Admin") or (a["sellerlogin"] == user["login"])
                    if can_close and a["auctionstatus"] == "Active":
                        st.markdown("---")
                        if st.button("Close auction", key=f"close_auction_{a['auctionid']}"):
                            res = AUCTIONS.close_auction(user["login"], a["auctionid"], user["role"])
                            if res["ok"]:
                                winner = res["winner"]
                                if winner:
                                    st.success(
                                        f"Auction closed. Winner: **{winner['buyerlogin']}** "
                                        f"({_format_currency(winner['bidamount'])}). "
                                        "Payment and shipment records were created."
                                    )
                                else:
                                    st.success("Auction closed with no bids.")
                                st.rerun()
                            else:
                                st.error(res["error"])

    elif page == "My Bids":
        UI_THEME.hero_banner(
            "My Bids",
            "Track every bid you've placed and see how each auction is performing.",
            "bids",
        )

        bids = BIDS.get_bids_for_buyer(user["login"])
        if not bids:
            st.info("You haven't placed any bids yet. Visit the Auctions page to get started.")
        else:
            for bid in bids:
                _render_bid_card(bid)

    elif page == "Seller Items":
        UI_THEME.hero_banner(
            "My Items",
            "Your inventory of listed items ready for the auction floor.",
            "items",
        )

        items = ITEMS.list_items(
            seller_login=user["login"] if user["role"] == "Seller" else None
        )

        if not items:
            st.info("No items found. Create one from the Create Item page.")
        else:
            for item in items:
                _render_item_card(item, show_seller=False)

    elif page == "Create Item":
        UI_THEME.hero_banner(
            "List a New Item",
            "Add a product to your inventory and get it ready for auction.",
            "create",
        )

        with st.container(border=True):
            UI_THEME.section_header("Item details", "📦")
            name = st.text_input("Item name")
            category = st.text_input("Category")
            price = st.number_input("Starting price", min_value=0.0, step=1.0, format="%.2f")
            desc = st.text_area("Description")
            image_url = st.text_input(
                "Image URL (optional)",
                placeholder="https://images.unsplash.com/photo-...",
            )

            if st.button("Create item", use_container_width=True, type="primary"):
                res = ITEMS.create_item(
                    seller_login=user["login"],
                    name=name,
                    category=category,
                    starting_price=price,
                    description=desc,
                    image_url=image_url or None,
                )

                if res["ok"]:
                    st.success(f"Item created successfully (ID #{res['itemID']}).")
                else:
                    st.error(res["error"])

    elif page == "Create Auction":
        UI_THEME.hero_banner(
            "Start an Auction",
            "Pick an item from your inventory and open the bidding floor.",
            "auctions",
        )

        items = ITEMS.list_items(seller_login=user["login"])

        if not items:
            st.info("You don't have any items yet. Create an item first.")
        else:
            with st.container(border=True):
                UI_THEME.section_header("Select inventory", "🎯")
                preview_cols = st.columns(min(len(items), 3))
                for idx, item in enumerate(items[:3]):
                    with preview_cols[idx]:
                        st.image(UI_THEME.item_image_url(item), use_container_width=True)
                        st.caption(item["itemname"])

                for item in items:
                    st.markdown(
                        f"- **{item['itemname']}** ({item['category']}) — "
                        f"{_format_currency(item['startingprice'])}"
                    )

                item_map = {f"{i['itemid']} — {i['itemname']}": i["itemid"] for i in items}
                selected = st.selectbox("Select item to auction", list(item_map.keys()))

                if st.button("Start auction", use_container_width=True, type="primary"):
                    res = AUCTIONS.create_auction(user["login"], item_map[selected])

                    if res["ok"]:
                        st.success(f"Auction started successfully (ID #{res['auctionID']}).")
                    else:
                        st.error(res["error"])

    elif page == "Payments":
        UI_THEME.hero_banner(
            "Payments",
            "Complete purchases, track buyer payments, and manage transactions.",
            "payments",
        )
        _render_payments_page(user)

    elif page == "Shipments":
        UI_THEME.hero_banner(
            "Shipments",
            "Track deliveries, update addresses, and manage fulfillment.",
            "shipments",
        )
        _render_shipments_page(user)

    elif page == "Profile":
        UI_THEME.hero_banner(
            "Your Profile",
            "Manage your account details and contact information.",
            "profile",
        )

        _render_user_profile(user)

        st.markdown("---")
        UI_THEME.section_header("Update contact info", "✏️")

        phone = st.text_input("Phone", value=user.get("phonenum", ""))
        address = st.text_input("Address", value=user.get("address", ""))

        if st.button("Save changes", type="primary"):
            res = USERS.update_profile(
                user["login"],
                phone,
                address,
                user.get("favoriteCategory")
            )

            if res["ok"]:
                st.success("Profile updated successfully.")
                st.session_state.user = USERS.get_user(user["login"])
                st.rerun()
            else:
                st.error(res.get("error", "Update failed."))
 
    elif page == "Admin":
        if user["role"] != "Admin":
            st.error("Access denied")
        else:
            UI_THEME.hero_banner(
                "Admin Console",
                "Manage users, auctions, payments, and shipments across the platform.",
                "admin",
                badge="Administrator",
            )

            UI_THEME.section_header("Users", "👥")
            _render_users_table(USERS.list_users())

            st.markdown("---")
            UI_THEME.section_header("All auctions", "🏷️")
            all_auctions = AUCTIONS.list_auctions()
            if not all_auctions:
                st.info("No auctions found.")
            else:
                for a in all_auctions:
                    with st.expander(
                        f"🏷️ {a['itemname']}  ·  {_format_currency(a['currenthighestbid'])}  ·  {a['auctionstatus']}",
                    ):
                        _render_auction_summary(a)

            st.markdown("---")
            UI_THEME.section_header("Payments", "💳")
            _render_payments_page(user)

            st.markdown("---")
            UI_THEME.section_header("Shipments", "📦")
            _render_shipments_page(user)