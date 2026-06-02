import sys, os
sys.path.insert(0, os.path.dirname(__file__))
 
from flask import (Flask, render_template, redirect, url_for, request, session, flash, jsonify)
from functools import wraps
 
import AUTHENTICATION, USERS, ITEMS, AUCTIONS, BIDS, PAYMENTS
 
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "cs166_auction_secret_key_change_in_prod"

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Please log in first.", "warning")
            
            return redirect(url_for("login"))
        
        return f(*args, **kwargs)
    
    return decorated
 
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("user", {}).get("role") not in roles:
                flash("Access denied.", "danger")
                
                return redirect(url_for("dashboard"))
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        result = AUTHENTICATION.login_user(request.form["login"], request.form["password"])
        
        if result["ok"]:
            session["user"] = result["user"]
            flash(f"Welcome back, {result['user']['login']}!", "success")
            
            return redirect(url_for("dashboard"))
        
        flash(result["error"], "danger")
    
    return render_template("login.html")
 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = AUTHENTICATION.register_user(login=request.form["login"], password=request.form["password"], phone=request.form["phone"], address=request.form["address"], favorite_category=request.form.get("favoriteCategory"),)
        
        if result["ok"]:
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        
        flash(result["error"], "danger")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    
    return redirect(url_for("login"))
 
@app.route("/dashboard")
@login_required
def dashboard():
    user = session["user"]
    role = user["role"]
 
    active_auctions = AUCTIONS.list_auctions(status="Active")
    stats = {"active_auctions": len(active_auctions), "total_items": len(ITEMS.list_items()), "my_bids": len(BIDS.get_bids_for_buyer(user["login"])) if role == "Buyer" else 0,}
    recent = active_auctions[:6]
    
    return render_template("dashboard.html", user=user, stats=stats, recent=recent)
 
@app.route("/auctions")
@login_required
def auction_list():
    status = request.args.get("status", "Active")
    category = request.args.get("category", "")
    search = request.args.get("search", "")
    auction_data = AUCTIONS.list_auctions(status=status or None, category=category or None, search=search or None,)
    cats = ITEMS.get_categories()
    
    return render_template("auctions.html", auctions=auction_data, status=status, category=category, search=search, categories=cats, user=session["user"])

@app.route("/auctions/<int:auction_id>")
@login_required
def auction_detail(auction_id):
    auction = AUCTIONS.get_auction(auction_id)
    
    if not auction:
        flash("Auction not found.", "danger")
        return redirect(url_for("auction_list"))
    
    bid_history = BIDS.get_bids_for_auction(auction_id)
    winner = AUCTIONS.get_auction_winner(auction_id) if auction["auctionstatus"] == "Closed" else None
    
    return render_template("auction_detail.html", auction=auction, bid_history=bid_history, winner=winner, user=session["user"])
 
@app.route("/auctions/<int:auction_id>/bid", methods=["POST"])
@login_required
@role_required("Buyer")
def place_bid(auction_id):
    try:
        amount = float(request.form["amount"])
    except ValueError:
        flash("Invalid bid amount.", "danger")
        
        return redirect(url_for("auction_detail", auction_id=auction_id))
 
    result = BIDS.place_bid(session["user"]["login"], auction_id, amount)
    
    if result["ok"]:
        flash("Bid placed successfully!", "success")
    else:
        flash(result["error"], "danger")
    
    return redirect(url_for("auction_detail", auction_id=auction_id))

@app.route("/my-bids")
@login_required
@role_required("Buyer")
def my_bids():
    my_bid_list = BIDS.get_bids_for_buyer(session["user"]["login"])
    
    return render_template("my_bids.html", bids=my_bid_list, user=session["user"])

@app.route("/seller/items")
@login_required
@role_required("Seller", "Admin")
def seller_items():
    item_list = ITEMS.list_items(seller_login=session["user"]["login"] if session["user"]["role"] == "Seller" else None)
    
    return render_template("seller_items.html", items=item_list, user=session["user"])

@app.route("/seller/items/new", methods=["GET", "POST"])
@login_required
@role_required("Seller")
def new_item():
    if request.method == "POST":
        result = ITEMS.create_item(seller_login=session["user"]["login"], name=request.form["name"], category=request.form["category"], starting_price=float(request.form["startingPrice"]), description=request.form.get("description"), condition=request.form.get("condition"), image_url=request.form.get("imageURL"),)
        
        if result["ok"]:
            flash("Item created!", "success")
            return redirect(url_for("seller_items"))
        
        flash(result["error"], "danger")
    
    return render_template("item_form.html", item=None, user=session["user"])

@app.route("/seller/items/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Seller", "Admin")
def edit_item(item_id):
    item = ITEMS.get_item(item_id)
    
    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("seller_items"))
    
    if request.method == "POST":
        result = ITEMS.update_item(seller_login=session["user"]["login"], item_id=item_id, name=request.form["name"], category=request.form["category"], starting_price=float(request.form["startingPrice"]), description=request.form.get("description"), condition=request.form.get("condition"), image_url=request.form.get("imageURL"),)
        
        if result["ok"]:
            flash("Item updated.", "success")
            return redirect(url_for("seller_items"))
        
        flash(result["error"], "danger")
    
    return render_template("item_form.html", item=item, user=session["user"])
 
@app.route("/seller/items/<int:item_id>/delete", methods=["POST"])
@login_required
@role_required("Seller", "Admin")
def delete_item(item_id):
    result = ITEMS.delete_item(session["user"]["login"], session["user"]["role"], item_id)
    
    flash(result.get("error", "Item deleted."), "danger" if not result["ok"] else "success")
    
    return redirect(url_for("seller_items"))

@app.route("/seller/auctions/new", methods=["GET", "POST"])
@login_required
@role_required("Seller")
def new_auction():
    seller_login = session["user"]["login"]
    item_list = ITEMS.list_items(seller_login=seller_login)
    
    if request.method == "POST":
        result = AUCTIONS.create_auction(seller_login, int(request.form["itemID"]))
        
        if result["ok"]:
            flash("Auction started!", "success")
            return redirect(url_for("auction_list"))
        
        flash(result["error"], "danger")
    
    return render_template("new_auction.html", items=item_list, user=session["user"])
 
@app.route("/seller/auctions/<int:auction_id>/close", methods=["POST"])
@login_required
@role_required("Seller", "Admin")
def close_auction(auction_id):
    result = AUCTIONS.close_auction(
        session["user"]["login"], auction_id, session["user"]["role"]
    )
    
    if result["ok"]:
        msg = "Auction closed."
        
        if result.get("winner"):
            msg += f" Winner: {result['winner']['buyerlogin']} with ${result['winner']['bidamount']:.2f}"
        
        flash(msg, "success")
    else:
        flash(result["error"], "danger")
    
    return redirect(url_for("auction_detail", auction_id=auction_id))
 
@app.route("/payments")
@login_required
def payment_list():
    user = session["user"]
    plist = PAYMENTS.get_payments(user["login"], user["role"])
    
    return render_template("payments.html", payments=plist, user=user)

@app.route("/payments/<int:payment_id>/update", methods=["POST"])
@login_required
def update_payment(payment_id):
    user = session["user"]
    new_status = request.form["status"]
    result = PAYMENTS.update_payment_status(user["login"], user["role"], payment_id, new_status)
    
    flash(result.get("error", "Payment updated."), "danger" if not result["ok"] else "success")
    
    return redirect(url_for("payment_list"))
 
@app.route("/shipments")
@login_required
def shipment_list():
    user = session["user"]
    slist = PAYMENTS.get_shipments(user["login"], user["role"])
    
    return render_template("shipments.html", shipments=slist, user=user)

@app.route("/shipments/<int:shipment_id>/update", methods=["POST"])
@login_required
@role_required("Seller", "Admin")
def update_shipment(shipment_id):
    user = session["user"]
    result = PAYMENTS.update_shipment(user["login"], user["role"], shipment_id, request.form["status"], request.form.get("trackingNumber") or None,)
    
    flash(result.get("error", "Shipment updated."), "danger" if not result["ok"] else "success")
    
    return redirect(url_for("shipment_list"))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = session["user"]
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "update_profile":
            result = USERS.update_profile(user["login"], request.form["phone"], request.form["address"], request.form.get("favoriteCategory"),)
            
            if result["ok"]:
                session["user"] = USERS.get_user(user["login"])
                flash("Profile updated.", "success")
        elif action == "change_password":
            result = AUTHENTICATION.change_password(user["login"], request.form["old_password"], request.form["new_password"],)
            
            flash(result.get("error", "Password changed."), "danger" if not result["ok"] else "success")
    
    return render_template("profile.html", user=session["user"])
 
@app.route("/admin")
@login_required
@role_required("Admin")
def admin_panel():
    user_list = USERS.list_users()
    all_auctions = AUCTIONS.list_auctions()
    all_payments = PAYMENTS.get_payments("", "Admin")
    
    return render_template("admin.html", users=user_list, auctions=all_auctions, payments=all_payments, user=session["user"])

@app.route("/admin/users/<string:target>/role", methods=["POST"])
@login_required
@role_required("Admin")
def admin_change_role(target):
    result = USERS.change_role(session["user"]["login"], target, request.form["role"])
    
    flash(result.get("error", f"Role updated for {target}."), "danger" if not result["ok"] else "success")
    
    return redirect(url_for("admin_panel"))
 
@app.route("/admin/users/<string:target>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def admin_delete_user(target):
    result = USERS.delete_user(session["user"]["login"], target)
    
    flash(result.get("error", f"User {target} deleted."), "danger" if not result["ok"] else "success")
    
    return redirect(url_for("admin_panel"))
 
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)