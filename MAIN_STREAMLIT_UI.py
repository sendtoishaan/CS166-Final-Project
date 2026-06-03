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

            if user["role"] == "Buyer":
                amount = st.number_input("Bid Amount", min_value=0.0)

                if st.button("Place Bid"):
                    res = BIDS.place_bid(user["login"], aid, amount)
                    if res["ok"]:
                        st.success("Bid placed")
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
        item_map = {f"{i['itemid']} - {i['name']}": i["itemid"] for i in items}

        selected = st.selectbox("Select Item", list(item_map.keys()))

        if st.button("Start Auction"):
            res = AUCTIONS.create_auction(user["login"], item_map[selected])

            if res["ok"]:
                st.success("Auction created")
            else:
                st.error(res["error"])

    elif page == "Payments":
        st.title("Payments")

        data = PAYMENTS.get_payments(user["login"], user["role"])
        st.write(data)

    elif page == "Shipments":
        st.title("Shipments")

        data = PAYMENTS.get_shipments(user["login"], user["role"])
        st.write(data)

    elif page == "Profile":
        st.title("Profile")

        st.write(user)

        phone = st.text_input("Phone", value=user.get("phone", ""))
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
            st.write(PAYMENTS.get_payments("", "Admin"))