import streamlit as st
import pandas as pd
import os
from datetime import datetime

# -------------------------------------------------
# PAGE CONFIG & CUSTOM CSS
# -------------------------------------------------
st.set_page_config(
    page_title="RetailSmart | Discount & Revenue Calculator",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Sidebar spacing and fonts
st.markdown("""
<style>
    /* Sidebar Radio Buttons styling */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 15px; /* Spacing between items */
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 1.15rem !important;
        font-weight: 500;
        padding: 8px 12px;
        border-radius: 8px;
        transition: background 0.2s;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# FILE PATHS
# -------------------------------------------------
INVENTORY_FILE = "inventory_store.csv"
SALES_FILE     = "sales_store.csv"
MEMBERS_FILE   = "members_store.csv"
SEED_CSV       = "electronics_100_items.csv"

# -------------------------------------------------
# DISCOUNT OFFERS & TIERS
# -------------------------------------------------
DISCOUNT_OFFERS = {
    "None (0%)": {
        "default": 0, "Accessories": 0, "Audio": 0, "Computing": 0,
        "Power": 0, "Smart Home": 0, "Wearables": 0, "Gaming": 0,
        "Photography": 0, "Health": 0, "Personal Care": 0,
        "Electronics": 0, "Automotive": 0, "Home": 0,
    },
    "🎉 Festival Sale (Accessories 15%, Audio 10%, Others 5%)": {
        "default": 5, "Accessories": 15, "Audio": 10,
    },
    "💻 Tech Week (Computing 20%, Accessories 10%, Others 5%)": {
        "default": 5, "Computing": 20, "Accessories": 10,
    },
    "🏠 Smart Home Week (Smart Home 20%, Power 10%, Others 5%)": {
        "default": 5, "Smart Home": 20, "Power": 10,
    },
    "🎮 Gaming Bonanza (Gaming 25%, Accessories 10%, Others 5%)": {
        "default": 5, "Gaming": 25, "Accessories": 10,
    },
    "🧹 Clearance (Everything 30%)": {
        "default": 30,
    },
    "🔥 Mega Blowout (Everything 40%)": {
        "default": 40,
    },
}

LOYALTY_TIERS = [
    (50000, 12.0),
    (20000, 10.0),
    (10000,  7.0),
    (5000,   5.0),
    (0,      0.0),
]

# -------------------------------------------------
# PERSISTENCE HELPERS
# -------------------------------------------------
def load_inventory() -> pd.DataFrame:
    if os.path.exists(INVENTORY_FILE):
        return pd.read_csv(INVENTORY_FILE)
    if os.path.exists(SEED_CSV):
        df = pd.read_csv(SEED_CSV)
        df.to_csv(INVENTORY_FILE, index=False)
        return df
    df = pd.DataFrame(columns=["Product_ID", "Product_Name", "Category", "Price", "Stock"])
    df.to_csv(INVENTORY_FILE, index=False)
    return df

def save_inventory(df: pd.DataFrame):
    df.to_csv(INVENTORY_FILE, index=False)

def save_members(df: pd.DataFrame):
    df.to_csv(MEMBERS_FILE, index=False)

def load_members() -> pd.DataFrame:
    if os.path.exists(MEMBERS_FILE):
        df = pd.read_csv(MEMBERS_FILE)
        if "member" in df.columns: # Migration from old format
            df = df.rename(columns={"member": "Name"})
            df["Name"] = df["Name"].str.title()
            df["Customer_ID"] = [f"RC{str(i+1).zfill(4)}" for i in range(len(df))]
            df["Points"] = 0
            df["Join_Date"] = datetime.now().strftime("%Y-%m-%d")
            df = df[["Customer_ID", "Name", "Points", "Join_Date"]]
            save_members(df)
        if df.empty or "Join_Date" not in df.columns:
            df = pd.DataFrame([
                {"Customer_ID": "RC0001", "Name": "Alice Smith",  "Points": 0, "Join_Date": "2023-01-15"},
                {"Customer_ID": "RC0002", "Name": "John Doe",     "Points": 0, "Join_Date": "2023-05-20"},
                {"Customer_ID": "RC0003", "Name": "Rahul Sharma", "Points": 0, "Join_Date": "2023-11-01"},
                {"Customer_ID": "RC0004", "Name": "Sarah Jenkins","Points": 0, "Join_Date": "2024-02-10"},
            ])
            save_members(df)
        return df
        
    df = pd.DataFrame([
        {"Customer_ID": "RC0001", "Name": "Alice Smith",  "Points": 0, "Join_Date": "2023-01-15"},
        {"Customer_ID": "RC0002", "Name": "John Doe",     "Points": 0, "Join_Date": "2023-05-20"},
        {"Customer_ID": "RC0003", "Name": "Rahul Sharma", "Points": 0, "Join_Date": "2023-11-01"},
        {"Customer_ID": "RC0004", "Name": "Sarah Jenkins","Points": 0, "Join_Date": "2024-02-10"},
    ])
    save_members(df)
    return df

def next_customer_id(df: pd.DataFrame) -> str:
    if df.empty:
        return "RC0001"
    nums = df["Customer_ID"].str.extract(r"RC(\d+)")[0].astype(int)
    return f"RC{int(nums.max()) + 1:04d}"

def load_sales() -> pd.DataFrame:
    if os.path.exists(SALES_FILE):
        return pd.read_csv(SALES_FILE)
    return pd.DataFrame(columns=[
        "Date", "Bill_ID", "Customer_ID", "Customer", "Is_Member",
        "Product_ID", "Product", "Category", "Qty",
        "Unit_Price", "Offer", "Offer_Disc_%", "Offer_Disc_Amt", "Line_Total",
        "Loyalty_Disc_%", "Loyalty_Disc_Amt", "Bill_Total", "Points_Earned",
    ])

def save_sales(df: pd.DataFrame):
    df.to_csv(SALES_FILE, index=False)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "inventory_df" not in st.session_state:
    st.session_state.inventory_df = load_inventory()
if "members_df" not in st.session_state:
    st.session_state.members_df = load_members()
if "sales_df" not in st.session_state:
    st.session_state.sales_df = load_sales()
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "member_confirmed" not in st.session_state:
    st.session_state.member_confirmed = None
if "offer_name" not in st.session_state:
    st.session_state.offer_name = "None (0%)"

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def member_lookup(name: str):
    df = st.session_state.members_df
    if df.empty or "Name" not in df.columns:
        return None
    m = df[df["Name"].str.strip().str.title() == name.strip().title()]
    return None if m.empty else m.iloc[0].to_dict()

def offer_category_rate(offer: str, category: str) -> float:
    rules = DISCOUNT_OFFERS.get(offer, {"default": 0})
    return float(rules.get(category, rules.get("default", 0)))

def loyalty_rate(subtotal: float, is_member: bool) -> float:
    if not is_member:
        return 0.0
    for threshold, rate in LOYALTY_TIERS:
        if subtotal >= threshold:
            return rate
    return 0.0

def recalc_cart_discounts(offer: str):
    inv = st.session_state.inventory_df
    for pid, d in st.session_state.cart.items():
        row = inv[inv["Product_ID"] == pid]
        cat = d.get("category", row.iloc[0]["Category"] if not row.empty else "")
        d["offer_disc"] = offer_category_rate(offer, cat)

# -------------------------------------------------
# HEADER & NAVIGATION
# -------------------------------------------------
st.title("🛒 RetailPro | Dynamic Discounts, Billing & Inventory")

app_mode = st.sidebar.radio(
    "Go to",
    [
        "🛒 POS & Billing",
        "📦 Inventory Manager",
        "📊 Revenue Analytics",
        "📦 Stock Analytics",
        "⭐ Reward Program",
    ],
)

# =================================================
# MODULE 1 : POS & BILLING
# =================================================
if app_mode == "🛒 POS & Billing":
    st.header("Point of Sale — Build a Bill")

    inv = st.session_state.inventory_df

    # ---------- Discount Selector (Moved Above) ----------
    st.subheader("🎁 Active Discount Offer")
    offer_name = st.selectbox(
        "Select a discount offer (applies per item as you add to cart)",
        list(DISCOUNT_OFFERS.keys()),
        index=list(DISCOUNT_OFFERS.keys()).index(st.session_state.offer_name)
              if st.session_state.offer_name in DISCOUNT_OFFERS else 0,
    )
    if offer_name != st.session_state.offer_name:
        st.session_state.offer_name = offer_name
        recalc_cart_discounts(offer_name)
        st.rerun()

    rules = DISCOUNT_OFFERS[offer_name]
    rule_txt = ", ".join(f"{k}: {v}%" for k, v in rules.items() if k != "default")
    st.caption(f"Default: {rules['default']}% • {rule_txt or 'no category overrides'}")

    st.markdown("---")

    # ---------- Customer Panel ----------
    st.subheader("👤 Customer Details")
    c1, c2 = st.columns([3, 2])
    with c1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name...")

    with c2:
        existing = member_lookup(customer_name) if customer_name.strip() else None
        if not customer_name.strip():
            st.info("Type a name to check membership.")
        elif existing:
            st.success(f"⭐ Member {existing['Customer_ID']} — {existing['Name']} ({int(existing['Points'])} pts)")
            st.session_state.member_confirmed = existing
        else:
            st.warning("Not a reward member.")
            with st.expander("💡 Enroll in Reward Program?", expanded=True):
                st.write("Get tiered discounts, 5%+ on big carts, and 2 reward points per ₹100 spent.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Add to Program", use_container_width=True):
                        new_id = next_customer_id(st.session_state.members_df)
                        new_row = pd.DataFrame([{
                            "Customer_ID": new_id, 
                            "Name": customer_name.strip().title(), 
                            "Points": 0,
                            "Join_Date": datetime.now().strftime("%Y-%m-%d")
                        }])
                        st.session_state.members_df = pd.concat(
                            [st.session_state.members_df, new_row], ignore_index=True
                        )
                        save_members(st.session_state.members_df)
                        st.success(f"Enrolled! Customer ID: {new_id}")
                        st.session_state.member_confirmed = member_lookup(customer_name)
                        st.rerun()
                with col_no:
                    if st.button("➡️ Proceed Without Program", use_container_width=True):
                        st.session_state.member_confirmed = {"Customer_ID": "GUEST", "Name": customer_name.strip().title(), "Points": 0}
                        st.rerun()

    confirmed = st.session_state.member_confirmed
    is_member = bool(confirmed and confirmed.get("Customer_ID") != "GUEST")

    st.markdown("---")

    # ---------- Search & add products ----------
    st.subheader("🔍 Search Products")
    s1, s2 = st.columns([2, 1])
    with s1:
        search_q = st.text_input("Search by name, ID, or category", placeholder="e.g. mouse, audio, E001")
    with s2:
        category_filter = st.selectbox(
            "Filter category",
            ["All"] + sorted(inv["Category"].dropna().unique().tolist())
            if "Category" in inv.columns else ["All"],
        )

    if search_q or category_filter != "All":
        filtered = inv.copy()
        if search_q:
            mask = (
                filtered["Product_Name"].str.contains(search_q, case=False, na=False)
                | filtered["Product_ID"].str.contains(search_q, case=False, na=False)
                | (filtered["Category"].str.contains(search_q, case=False, na=False)
                   if "Category" in filtered.columns else False)
            )
            filtered = filtered[mask]
        if category_filter != "All" and "Category" in filtered.columns:
            filtered = filtered[filtered["Category"] == category_filter]
        filtered = filtered[filtered["Stock"] > 0]

        if filtered.empty:
            st.warning("No matching in-stock products.")
        else:
            disp = filtered.copy()
            disp["Offer_Disc_%"] = disp["Category"].apply(lambda c: offer_category_rate(offer_name, c)) \
                                   if "Category" in disp.columns else 0
            disp["Effective_Price"] = disp["Price"] * (1 - disp["Offer_Disc_%"] / 100)
            st.dataframe(
                disp[["Product_ID", "Product_Name", "Category", "Price",
                      "Offer_Disc_%", "Effective_Price", "Stock"]]
                if "Category" in disp.columns else
                disp[["Product_ID", "Product_Name", "Price", "Offer_Disc_%",
                      "Effective_Price", "Stock"]],
                use_container_width=True, hide_index=True,
            )

            colA, colB, colC, colD = st.columns([3, 1, 1, 1])
            with colA:
                options = {f"{r['Product_Name']} [{r['Product_ID']}]": r["Product_ID"]
                           for _, r in disp.iterrows()}
                chosen_label = st.selectbox("Select product", list(options.keys()), key="bill_select")
                chosen_id = options[chosen_label]
                prod = disp[disp["Product_ID"] == chosen_id].iloc[0]
            with colB:
                st.metric("List Price", f"₹{prod['Price']:,.2f}")
            with colC:
                disc = offer_category_rate(offer_name, prod.get("Category", ""))
                st.metric("Offer Disc", f"{disc:.0f}%")
            with colD:
                st.metric("Effective", f"₹{prod['Price'] * (1 - disc / 100):,.2f}")

            qc1, qc2 = st.columns([1, 3])
            with qc1:
                qty = st.number_input("Quantity", min_value=1, max_value=int(prod["Stock"]), value=1)
            with qc2:
                st.write("")
                st.write("")
                if st.button("🛒 Add to Cart", type="primary", use_container_width=True):
                    pid = chosen_id
                    if pid in st.session_state.cart:
                        new_qty = st.session_state.cart[pid]["qty"] + qty
                        if new_qty > int(prod["Stock"]):
                            st.error(f"Only {int(prod['Stock'])} units available.")
                        else:
                            st.session_state.cart[pid]["qty"] = new_qty
                            st.success(f"Updated cart: {new_qty} × {prod['Product_Name']}")
                    else:
                        st.session_state.cart[pid] = {
                            "name": prod["Product_Name"],
                            "category": prod.get("Category", ""),
                            "price": float(prod["Price"]),
                            "qty": int(qty),
                            "offer_disc": offer_category_rate(offer_name, prod.get("Category", "")),
                        }
                        st.success(f"Added {qty} × {prod['Product_Name']}")
                    st.rerun()
    else:
        st.info("🔎 Start typing a search term or pick a category to see products.")

    st.markdown("---")

    # ---------- Cart ----------
    st.subheader("🧾 Cart")

    if not st.session_state.cart:
        st.info("Cart is empty.")
    else:
        cart_rows = []
        subtotal = 0.0
        for pid, d in st.session_state.cart.items():
            unit_net = d["price"] * (1 - d["offer_disc"] / 100)
            line_total = unit_net * d["qty"]
            subtotal += line_total
            cart_rows.append({
                "Product_ID": pid,
                "Product": d["name"],
                "Qty": d["qty"],
                "List ₹": round(d["price"], 2),
                "Offer %": d["offer_disc"],
                "Net Unit ₹": round(unit_net, 2),
                "Line Total ₹": round(line_total, 2),
            })
        cart_df = pd.DataFrame(cart_rows)
        st.dataframe(cart_df, use_container_width=True, hide_index=True)

        e1, e2, e3 = st.columns([2, 1, 1])
        with e1:
            edit_pid = st.selectbox(
                "Edit which item?",
                options=["—"] + [f"{d['name']} [{pid}]" for pid, d in st.session_state.cart.items()],
                key="edit_cart_item",
            )
        with e2:
            if edit_pid != "—":
                sel_pid = edit_pid.split("[")[-1].rstrip("]")
                current_qty = st.session_state.cart[sel_pid]["qty"]
                new_qty = st.number_input(
                    "New quantity", min_value=0, value=int(current_qty), step=1, key=f"qty_{sel_pid}"
                )
            else:
                sel_pid, new_qty = None, None
        with e3:
            st.write("")
            st.write("")
            if sel_pid and st.button("💾 Update Qty", use_container_width=True):
                if new_qty == 0:
                    del st.session_state.cart[sel_pid]
                else:
                    st.session_state.cart[sel_pid]["qty"] = int(new_qty)
                st.rerun()
            if sel_pid and st.button("🗑️ Remove Item", use_container_width=True):
                del st.session_state.cart[sel_pid]
                st.rerun()

        loy_rate = loyalty_rate(subtotal, is_member)
        loy_amt = subtotal * loy_rate / 100
        grand = subtotal - loy_amt

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Subtotal (after offers)", f"₹{subtotal:,.2f}")
        m2.metric(f"Loyalty Disc ({loy_rate:.0f}%)", f"- ₹{loy_amt:,.2f}")
        m3.metric("Grand Total", f"₹{grand:,.2f}")
        m4.metric("Points to Earn", f"+{int(grand // 100 * 2)} pts" if is_member else "0 pts")

        st.markdown("**Loyalty tiers (members only):** ₹5k→5% • ₹10k→7% • ₹20k→10% • ₹50k→12%")

        b1, b2 = st.columns([2, 1])
        with b1:
            if st.button("✅ Complete Checkout", type="primary", use_container_width=True):
                if not customer_name.strip():
                    st.error("Enter a customer name before checkout.")
                elif not st.session_state.member_confirmed:
                    st.error("Choose whether to enroll the customer in the reward program.")
                else:
                    conf = st.session_state.member_confirmed
                    pts = int(grand // 100 * 2) if is_member else 0
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    bill_id = f"B{datetime.now().strftime('%y%m%d%H%M%S')}"

                    inv2 = st.session_state.inventory_df.copy()
                    lines = []
                    
                    for pid, d in st.session_state.cart.items():
                        idx = inv2.index[inv2["Product_ID"] == pid][0]
                        inv2.at[idx, "Stock"] = int(inv2.at[idx, "Stock"]) - d["qty"]
                        
                        unit_net = d["price"] * (1 - d["offer_disc"] / 100)
                        line_tot = unit_net * d["qty"]
                        offer_amt = (d["price"] * d["qty"]) - line_tot
                        
                        lines.append({
                            "Date": now,
                            "Bill_ID": bill_id,
                            "Customer_ID": conf.get("Customer_ID", "GUEST"),
                            "Customer": conf.get("Name", customer_name),
                            "Is_Member": is_member,
                            "Product_ID": pid,
                            "Product": d["name"],
                            "Category": d.get("category", ""),
                            "Qty": d["qty"],
                            "Unit_Price": round(unit_net, 2),
                            "Offer": offer_name,
                            "Offer_Disc_%": d["offer_disc"],
                            "Offer_Disc_Amt": round(offer_amt, 2),
                            "Line_Total": round(line_tot, 2),
                            "Loyalty_Disc_%": loy_rate,
                            "Loyalty_Disc_Amt": round(loy_amt / max(1, len(st.session_state.cart)), 2),
                            "Bill_Total": round(grand, 2),
                            "Points_Earned": pts,
                        })
                    st.session_state.inventory_df = inv2
                    save_inventory(inv2)

                    st.session_state.sales_df = pd.concat(
                        [st.session_state.sales_df, pd.DataFrame(lines)], ignore_index=True
                    )
                    save_sales(st.session_state.sales_df)

                    if is_member and pts:
                        mem = st.session_state.members_df
                        mask = mem["Customer_ID"] == conf["Customer_ID"]
                        mem.loc[mask, "Points"] = mem.loc[mask, "Points"].astype(int) + pts
                        st.session_state.members_df = mem
                        save_members(mem)

                    # Reset page state completely after successful checkout
                    st.session_state.cart = {}
                    st.session_state.member_confirmed = None
                    st.session_state.offer_name = "None (0%)"
                    
                    st.success(f"🎉 Checkout complete. ₹{grand:,.2f} collected. "
                               f"{'+ ' + str(pts) + ' pts to member' if is_member else ''}")
                    st.rerun()
        with b2:
            if st.button("❌ Clear Cart", use_container_width=True):
                st.session_state.cart = {}
                st.rerun()

# =================================================
# MODULE 2 : INVENTORY MANAGER
# =================================================
elif app_mode == "📦 Inventory Manager":
    st.header("Inventory Manager")
    inv = st.session_state.inventory_df
    t1, t2, t3 = st.tabs(["📋 View & Edit", "➕ Add Product", "🔄 Bulk / Reset"])

    with t1:
        search_q = st.text_input("🔍 Search inventory", key="inv_search")
        view = inv.copy()
        if search_q:
            view = view[
                view["Product_Name"].str.contains(search_q, case=False, na=False)
                | view["Product_ID"].str.contains(search_q, case=False, na=False)
                | (view["Category"].str.contains(search_q, case=False, na=False)
                   if "Category" in view.columns else False)
            ]
        st.dataframe(view, use_container_width=True, hide_index=True)

        st.markdown("##### ✏️ Quick-edit a product")
        edit_options = {f"{r['Product_Name']} [{r['Product_ID']}]": r["Product_ID"] for _, r in inv.iterrows()}
        if edit_options:
            chosen = st.selectbox("Select product to edit", list(edit_options.keys()), key="edit_prod")
            pid = edit_options[chosen]
            row = inv[inv["Product_ID"] == pid].iloc[0]
            e1, e2, e3 = st.columns(3)
            with e1:
                new_price = st.number_input("Price (₹)", value=float(row["Price"]), min_value=0.0)
            with e2:
                new_stock = st.number_input("Stock", value=int(row["Stock"]), min_value=0)
            with e3:
                st.write("")
                st.write("")
                if st.button("💾 Save changes"):
                    inv.loc[inv["Product_ID"] == pid, "Price"] = new_price
                    inv.loc[inv["Product_ID"] == pid, "Stock"] = new_stock
                    st.session_state.inventory_df = inv
                    save_inventory(inv)
                    st.success("Updated.")
                    st.rerun()
            if st.button("🗑️ Delete this product"):
                st.session_state.inventory_df = inv[inv["Product_ID"] != pid].reset_index(drop=True)
                save_inventory(st.session_state.inventory_df)
                st.success("Deleted.")
                st.rerun()

    with t2:
        with st.form("add_product_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                new_id = st.text_input("Product ID *", placeholder="E101")
                new_name = st.text_input("Product Name *")
                new_cat = st.text_input("Category", placeholder="Accessories")
            with f2:
                new_price = st.number_input("Price (₹) *", min_value=0.0, value=499.0)
                new_stock = st.number_input("Initial Stock *", min_value=0, value=10)
            if st.form_submit_button("➕ Add Product"):
                if not new_id or not new_name:
                    st.error("ID and Name required.")
                elif new_id in st.session_state.inventory_df["Product_ID"].values:
                    st.error(f"ID {new_id} exists.")
                else:
                    new_row = pd.DataFrame([{
                        "Product_ID": new_id, "Product_Name": new_name,
                        "Category": new_cat or "Uncategorized",
                        "Price": new_price, "Stock": new_stock,
                    }])
                    st.session_state.inventory_df = pd.concat(
                        [st.session_state.inventory_df, new_row], ignore_index=True
                    )
                    save_inventory(st.session_state.inventory_df)
                    st.success("Added.")
                    st.rerun()

    with t3:
        st.markdown("#### Restock all zero-stock items")
        rq = st.number_input("Add units to every out-of-stock SKU", 1, 1000, 10)
        if st.button("♻️ Restock Zero-Stock"):
            inv.loc[inv["Stock"] == 0, "Stock"] = rq
            st.session_state.inventory_df = inv
            save_inventory(inv)
            st.success("Restocked.")
            st.rerun()

# =================================================
# MODULE 3 : REVENUE ANALYTICS
# =================================================
elif app_mode == "📊 Revenue Analytics":
    st.header("Revenue & Sales Analytics")
    sales = st.session_state.sales_df

    if sales.empty:
        st.info("No sales yet. Complete a checkout in POS & Billing first.")
    else:
        sales["Date_dt"] = pd.to_datetime(sales["Date"])
        bills = sales.drop_duplicates(subset=["Bill_ID"])
        total_rev = bills["Bill_Total"].sum()
        total_bills = len(bills)
        total_units = int(sales["Qty"].sum())
        avg_bill = total_rev / total_bills if total_bills else 0

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("💰 Total Revenue", f"₹{total_rev:,.2f}")
        k2.metric("🧾 Bills", total_bills)
        k3.metric("📦 Units Sold", total_units)
        k4.metric("📈 Avg Bill", f"₹{avg_bill:,.2f}")

        st.markdown("---")
        ch1, ch2 = st.columns(2)
        with ch1:
            st.subheader("Revenue by Day")
            daily = bills.groupby(bills["Date_dt"].dt.date)["Bill_Total"].sum()
            st.bar_chart(daily)
        with ch2:
            st.subheader("Top 10 Products by Revenue")
            top = sales.groupby("Product")["Line_Total"].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top)

        st.markdown("---")
        st.subheader("👥 Per-Customer Bills Breakdown")
        
        # Format Is_Member for summary
        cust_summary = (
            sales.groupby(["Customer_ID", "Customer", "Is_Member"])
            .agg(Bills=("Bill_ID", "nunique"),
                 Revenue=("Bill_Total", lambda x: sales.loc[x.index].drop_duplicates(subset=["Bill_ID"])["Bill_Total"].sum()),
                 Units=("Qty", "sum"))
            .reset_index()
        )
        cust_summary["Is_Member"] = cust_summary["Is_Member"].map({True: "Yes", False: "No"})
        
        st.dataframe(cust_summary, use_container_width=True, hide_index=True)

        # Detailed Dropdown for Customer Bills
        st.markdown("#### 🔍 Drill-down: Customer Bill Details")
        cust_options = ["— Select a Customer —"] + [f"{r['Customer']} ({r['Customer_ID']})" for _, r in cust_summary.iterrows()]
        selected_cust = st.selectbox("Select Customer to view history", cust_options)
        
        if selected_cust != "— Select a Customer —":
            cid = selected_cust.split("(")[-1].rstrip(")")
            cust_bills = sales[sales["Customer_ID"] == cid].sort_values("Date", ascending=False)
            
            for bill_id in cust_bills["Bill_ID"].unique():
                bill_data = cust_bills[cust_bills["Bill_ID"] == bill_id]
                first_row = bill_data.iloc[0]
                date_str = first_row["Date"]
                tot = first_row["Bill_Total"]
                pts = first_row["Points_Earned"]
                
                with st.expander(f"📄 Bill {bill_id} — {date_str} | Total: ₹{tot:,.2f} | Points: {pts}"):
                    display_cols = ["Product", "Category", "Qty", "Unit_Price", "Offer_Disc_%", "Offer_Disc_Amt", "Loyalty_Disc_Amt", "Line_Total"]
                    st.dataframe(bill_data[display_cols], use_container_width=True, hide_index=True)

        st.subheader("Full Transaction History")
        st.dataframe(sales.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

        st.download_button(
            "📥 Download Sales Report (CSV)",
            data=sales.to_csv(index=False).encode("utf-8"),
            file_name=f"retail_sales_{datetime.now():%Y%m%d_%H%M}.csv",
            mime="text/csv",
        )

# =================================================
# MODULE 4 : STOCK ANALYTICS
# =================================================
elif app_mode == "📦 Stock Analytics":
    st.header("Stock Analytics")
    inv = st.session_state.inventory_df

    if inv.empty:
        st.info("Inventory is empty. Add or upload products first.")
    else:
        total_units = int(inv["Stock"].sum())
        skus = len(inv)
        zero_skus = int((inv["Stock"] == 0).sum())
        inv_value = float((inv["Price"] * inv["Stock"]).sum())
        low_stock = int(((inv["Stock"] > 0) & (inv["Stock"] <= 10)).sum())

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("SKUs", skus)
        k2.metric("Units in stock", total_units)
        k3.metric("Out-of-stock SKUs", zero_skus)
        k4.metric("Low stock (1–10)", low_stock)
        k5.metric("Inventory value", f"₹{inv_value:,.0f}")

        st.markdown("---")
        ch1, ch2 = st.columns(2)

        with ch1:
            st.subheader("Stock by Category")
            cat_stock = inv.groupby("Category")["Stock"].sum().sort_values(ascending=False) \
                if "Category" in inv.columns else inv.groupby("Product_Name")["Stock"].sum()
            st.bar_chart(cat_stock)

        with ch2:
            st.subheader("Inventory Value by Category")
            if "Category" in inv.columns:
                inv["Value"] = inv["Price"] * inv["Stock"]
                cat_val = inv.groupby("Category")["Value"].sum().sort_values(ascending=False)
                st.bar_chart(cat_val)

        st.subheader("🚨 Reorder Alert (stock ≤ 10)")
        reorder = inv[inv["Stock"] <= 10].sort_values("Stock")
        if reorder.empty:
            st.success("All products above reorder threshold.")
        else:
            st.dataframe(
                reorder[["Product_ID", "Product_Name", "Category", "Stock", "Price"]]
                if "Category" in reorder.columns
                else reorder[["Product_ID", "Product_Name", "Stock", "Price"]],
                use_container_width=True, hide_index=True,
            )

# =================================================
# MODULE 5 : REWARD PROGRAM
# =================================================
elif app_mode == "⭐ Reward Program":
    st.header("Reward Program")
    
    mem = st.session_state.members_df
    sales = st.session_state.sales_df
    
    rp1, rp2 = st.tabs(["👥 Member Directory & Details", "📊 Reward Analytics"])
    
    # --- TAB 1: Directory & Drill-down ---
    with rp1:
        st.subheader("Member Directory")
        
        # Merge member data with sales data for details
        if not sales.empty:
            member_spend = sales.groupby("Customer_ID").agg(
                Total_Bills=("Bill_ID", "nunique"),
                Total_Spend=("Bill_Total", lambda x: sales.loc[x.index].drop_duplicates(subset=["Bill_ID"])["Bill_Total"].sum()),
                Total_Units=("Qty", "sum")
            ).reset_index()
            # Get favourite category
            fav_cat = sales.groupby(["Customer_ID", "Category"])["Qty"].sum().reset_index()
            fav_cat = fav_cat.sort_values(["Customer_ID", "Qty"], ascending=[True, False]).drop_duplicates("Customer_ID")
            fav_cat = fav_cat.rename(columns={"Category": "Fav_Category"})[["Customer_ID", "Fav_Category"]]
            
            mem_merged = pd.merge(mem, member_spend, on="Customer_ID", how="left").fillna(0)
            mem_merged = pd.merge(mem_merged, fav_cat, on="Customer_ID", how="left").fillna({"Fav_Category": "—"})
        else:
            mem_merged = mem.copy()
            mem_merged["Total_Bills"] = 0
            mem_merged["Total_Spend"] = 0.0
            mem_merged["Total_Units"] = 0
            mem_merged["Fav_Category"] = "—"

        # Render a nice grid of expanders
        for _, row in mem_merged.iterrows():
            header_text = f"👤 {row['Name']} ({row['Customer_ID']}) — {int(row['Points'])} pts"
            with st.expander(header_text):
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("Join Date", row["Join_Date"])
                e2.metric("Total Spend", f"₹{row['Total_Spend']:,.2f}")
                e3.metric("Total Bills", int(row["Total_Bills"]))
                e4.metric("Fav Category", row["Fav_Category"])
                
                if row["Total_Bills"] > 0:
                    st.write(f"**Frequent Shopper Status:** {'⭐ Frequent' if row['Total_Bills'] > 2 else 'Occasional'}")
                    st.write(f"**Avg Bill Value:** ₹{(row['Total_Spend'] / row['Total_Bills']):,.2f}")
                else:
                    st.info("No purchases made yet.")

        st.markdown("---")
        st.subheader("Register New Member")
        col1, col2 = st.columns([3, 1])
        with col1:
            new_member = st.text_input("Name", key="new_member_input")
        with col2:
            st.write("")
            st.write("")
            if st.button("Register", use_container_width=True):
                clean = new_member.strip().title()
                if not clean:
                    st.error("Enter a valid name.")
                elif (mem["Name"].str.lower() == clean.lower()).any():
                    st.warning("Already registered.")
                else:
                    new_id = next_customer_id(mem)
                    new_row = pd.DataFrame([{
                        "Customer_ID": new_id, "Name": clean, "Points": 0, 
                        "Join_Date": datetime.now().strftime("%Y-%m-%d")
                    }])
                    st.session_state.members_df = pd.concat([mem, new_row], ignore_index=True)
                    save_members(st.session_state.members_df)
                    st.success(f"Registered {clean} as {new_id}.")
                    st.rerun()

    # --- TAB 2: Reward Analytics ---
    with rp2:
        st.subheader("Program Analytics")
        
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("**Points Leaderboard**")
            top_pts = mem.sort_values("Points", ascending=False).head(10)
            st.bar_chart(top_pts.set_index("Name")["Points"])
            
        with a2:
            st.markdown("**Top Spenders (Revenue)**")
            if not sales.empty:
                top_spenders = mem_merged.sort_values("Total_Spend", ascending=False).head(10)
                st.bar_chart(top_spenders.set_index("Name")["Total_Spend"])
            else:
                st.info("No sales data to plot yet.")
                
        st.markdown("---")
        st.markdown("**Member Activity Levels**")
        if not sales.empty:
            active = len(mem_merged[mem_merged["Total_Bills"] > 0])
            inactive = len(mem_merged[mem_merged["Total_Bills"] == 0])
            st.write(f"Active Buyers: **{active}** | No Purchases Yet: **{inactive}**")
            
            # Category preference chart
            st.markdown("**Overall Member Category Preferences**")
            member_sales = sales[sales["Is_Member"] == True]
            if not member_sales.empty:
                cat_prefs = member_sales.groupby("Category")["Qty"].sum().sort_values(ascending=False)
                st.bar_chart(cat_prefs)
        else:
            st.info("Enroll members and make sales to see analytics.")