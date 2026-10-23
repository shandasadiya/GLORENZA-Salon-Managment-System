"""
GLORENZA SALON AHMEDABAD - Owner Management Suite
Complete POS billing workflow with persistent cart, multi-tax engine, sound,
WhatsApp dispatch, backbar auto-deduction, and database backup manager.
"""

from datetime import date, datetime
import os
import streamlit as st
import pandas as pd

from database.connection import fetch_all, fetch_one, execute_query, DB_PATH
from modules.session import get_current_user, logout_user
from modules.customers import get_all_customers, register_customer
from modules.staff import get_all_staff
from modules.services import get_all_services
from modules.chairs import get_all_chairs
from modules.products import get_all_products
from modules.billing import create_bill
from modules.payments import record_payment
from modules.expenses import add_expense
from modules.reviews import get_all_reviews
from modules.support import get_all_tickets
from modules.whatsapp import generate_invoice_whatsapp_link
from utils.export import export_to_excel
from ui.common import render_header


def play_payment_success_chime():
    sound_js = """
    <script>
    (function() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const now = ctx.currentTime;
            const osc1 = ctx.createOscillator();
            const gain1 = ctx.createGain();
            osc1.type = 'sine';
            osc1.frequency.setValueAtTime(587.33, now);
            osc1.frequency.exponentialRampToValueAtTime(880, now + 0.15);
            gain1.gain.setValueAtTime(0.3, now);
            gain1.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
            osc1.connect(gain1);
            gain1.connect(ctx.destination);
            osc1.start(now);
            osc1.stop(now + 0.6);

            const osc2 = ctx.createOscillator();
            const gain2 = ctx.createGain();
            osc2.type = 'triangle';
            osc2.frequency.setValueAtTime(1174.66, now + 0.12);
            gain2.gain.setValueAtTime(0.4, now + 0.12);
            gain2.gain.exponentialRampToValueAtTime(0.01, now + 0.8);
            osc2.connect(gain2);
            gain2.connect(ctx.destination);
            osc2.start(now + 0.12);
            osc2.stop(now + 0.8);
        } catch(e) {}
    })();
    </script>
    """
    st.components.v1.html(sound_js, height=0, width=0)


def auto_deduct_backbar_inventory(service_name: str, service_category: str):
    """Automatically reduces salon backbar consumable stock when chemical/spa services are billed."""
    name_lower = service_name.lower()
    cat_lower = service_category.lower()
    
    search_keyword = None
    if "color" in name_lower or "balayage" in name_lower or "highlight" in name_lower:
        search_keyword = "Color"
    elif "keratin" in name_lower or "botox" in name_lower or "straight" in name_lower:
        search_keyword = "Keratin"
    elif "facial" in name_lower or "clean" in name_lower or "hydra" in name_lower or "skin" in cat_lower:
        search_keyword = "Facial"
    elif "spa" in name_lower or "massage" in name_lower:
        search_keyword = "Shampoo"

    if search_keyword:
        matched_prod = fetch_one(
            "SELECT id, name, stock_quantity FROM products WHERE (name LIKE ? OR category LIKE ?) AND stock_quantity > 0 LIMIT 1;",
            (f"%{search_keyword}%", f"%{search_keyword}%")
        )
        if matched_prod:
            execute_query("UPDATE products SET stock_quantity = MAX(0, stock_quantity - 1) WHERE id = ?;", (matched_prod["id"],))


def get_service_margin_data(category: str, price: float) -> tuple:
    cat = category.lower()
    if "hair" in cat:
        pct = 65.0
    elif "skin" in cat or "facial" in cat:
        pct = 55.0
    elif "hand" in cat or "feet" in cat or "nail" in cat or "spa" in cat:
        pct = 60.0
    elif "bridal" in cat or "makeup" in cat:
        pct = 70.0
    elif "beard" in cat:
        pct = 60.0
    else:
        pct = 60.0
    profit = (price * pct) / 100.0
    return pct, profit


def render_owner_panel():
    render_header()
    user = get_current_user()

    if "owner_active_tab" not in st.session_state:
        st.session_state.owner_active_tab = "POS Multi-Item Billing"
    if "pos_cart" not in st.session_state:
        st.session_state.pos_cart = []
    if "last_receipt" not in st.session_state:
        st.session_state.last_receipt = None

    # Top Bar
    col_t1, col_t2 = st.columns([5, 1.2])
    with col_t1:
        st.markdown(f"**Executive Salon Portal** &mdash; Administrator: **{user.get('full_name')}**")
    with col_t2:
        if st.button("🚪 LOGOUT", key="owner_logout", use_container_width=True):
            logout_user()
            st.rerun()

    # Sidebar Navigation
    st.sidebar.markdown('<div class="sidebar-brand-title">SALON MANAGEMENT</div>', unsafe_allow_html=True)
    
    menu_items = [
        ("Financial Dashboard", "Financial Dashboard"),
        ("Styling Stations", "Styling Stations (6 Units)"),
        ("POS Multi-Item Billing", "POS Multi-Item Billing"),
        ("Client Directory", "Client Directory"),
        ("Staff Specialists", "Staff Specialists & Payroll"),
        ("Service Menu & Pricing", "Service Menu & Pricing"),
        ("Inventory & Supplies", "Inventory (50 Items)"),
        ("Operating Expenses", "Operating Expenses"),
        ("Client Reviews", "Client Reviews"),
        ("Support Concierge", "Support Concierge"),
        ("System Database Backup", "Database Backup & Safety"),
        ("Excel Reports Export", "Excel Reports Export")
    ]

    for key_name, label_text in menu_items:
        if st.sidebar.button(label_text, key=f"nav_{key_name}", use_container_width=True):
            st.session_state.owner_active_tab = key_name
            st.rerun()

    menu = st.session_state.owner_active_tab

    # ---------------- 1. FINANCIAL DASHBOARD ----------------
    if menu == "Financial Dashboard":
        st.markdown("#### Real-Time Financial Performance")
        tab_day, tab_month = st.tabs(["Daily Performance View", "Monthly Aggregate View"])

        with tab_day:
            day_selected = st.date_input("Select Date", value=date.today(), key="analytics_day_select")
            day_str = str(day_selected)

            rev_row = fetch_one("SELECT SUM(grand_total) as total FROM bills WHERE DATE(created_at, 'localtime') = ?;", (day_str,))
            day_revenue = rev_row["total"] if rev_row and rev_row["total"] else 0.0

            exp_row = fetch_one("SELECT SUM(amount) as total FROM expenses WHERE expense_date = ? AND (notes IS NULL OR notes NOT LIKE '%deduct:no%');", (day_str,))
            day_expenses = exp_row["total"] if exp_row and exp_row["total"] else 0.0

            apts_row = fetch_one("SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ?;", (day_str,))
            day_apts = apts_row["count"] if apts_row else 0

            srv_items = fetch_all(
                """
                SELECT bi.total_price, s.category
                FROM bill_items bi
                JOIN bills b ON bi.bill_id = b.id
                JOIN services s ON bi.item_id = s.id
                WHERE bi.item_type = 'SERVICE' AND DATE(b.created_at, 'localtime') = ?;
                """,
                (day_str,)
            )
            service_revenue = sum(it["total_price"] for it in srv_items)
            service_profit = sum(get_service_margin_data(it["category"], it["total_price"])[1] for it in srv_items)

            prod_items = fetch_all(
                """
                SELECT bi.total_price, (bi.total_price - (p.purchase_price * bi.quantity)) as item_profit
                FROM bill_items bi
                JOIN bills b ON bi.bill_id = b.id
                JOIN products p ON bi.item_id = p.id
                WHERE bi.item_type = 'PRODUCT' AND DATE(b.created_at, 'localtime') = ?;
                """,
                (day_str,)
            )
            product_revenue = sum(it["total_price"] for it in prod_items)
            product_profit = sum(it["item_profit"] for it in prod_items)

            day_net_profit = max(0.0, (service_profit + product_profit) - day_expenses) if day_revenue > 0 else 0.0

            kpi_html = (
                "<div class='kpi-row-container'>"
                f"<div class='kpi-single-card'><div class='card-title'>Gross Revenue</div><div class='card-value'>₹{day_revenue:,.2f}</div></div>"
                f"<div class='kpi-single-card'><div class='card-title'>Operating Expenses</div><div class='card-value'>₹{day_expenses:,.2f}</div></div>"
                f"<div class='kpi-single-card'><div class='card-title'>Net Operating Profit</div><div class='card-value'>₹{day_net_profit:,.2f}</div></div>"
                f"<div class='kpi-single-card'><div class='card-title'>Appointments</div><div class='card-value'>{day_apts}</div></div>"
                "</div>"
            )
            st.markdown(kpi_html, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.info(f"💆‍♀️ **Services:** Revenue ₹{service_revenue:,.2f} | Est. Net Margin ₹{service_profit:,.2f}")
            with c2:
                st.info(f"🛍️ **Retail Products:** Sales ₹{product_revenue:,.2f} | Gross Margin ₹{product_profit:,.2f}")

        with tab_month:
            m_selected = st.date_input("Select Month Reference", value=date.today(), key="analytics_month_select")
            month_str = m_selected.strftime('%Y-%m')

            m_rev_row = fetch_one("SELECT SUM(grand_total) as total FROM bills WHERE strftime('%Y-%m', created_at, 'localtime') = ?;", (month_str,))
            m_revenue = m_rev_row["total"] if m_rev_row and m_rev_row["total"] else 0.0

            m_exp_row = fetch_one("SELECT SUM(amount) as total FROM expenses WHERE strftime('%Y-%m', expense_date) = ? AND (notes IS NULL OR notes NOT LIKE '%deduct:no%');", (month_str,))
            m_expenses = m_exp_row["total"] if m_exp_row and m_exp_row["total"] else 0.0

            m_apts_row = fetch_one("SELECT COUNT(*) as count FROM appointments WHERE strftime('%Y-%m', appointment_date) = ?;", (month_str,))
            m_apts = m_apts_row["count"] if m_apts_row else 0

            m_net_profit = max(0.0, m_revenue - m_expenses) if m_revenue > 0 else 0.0

            m_kpi_html = (
                "<div class='kpi-row-container'>"
                f"<div class='kpi-single-card'><div class='card-title'>Month Revenue</div><div class='card-value'>₹{m_revenue:,.2f}</div></div>"
                f"<div class='kpi-single-card'><div class='card-title'>Month Expenses</div><div class='card-value'>₹{m_expenses:,.2f}</div></div>"
                f"<div class='kpi-single-card'><div class='card-title'>Month Net Profit</div><div class='card-value'>₹{m_net_profit:,.2f}</div></div>"
                f"<div class='kpi-single-card'><div class='card-title'>Month Bookings</div><div class='card-value'>{m_apts}</div></div>"
                "</div>"
            )
            st.markdown(m_kpi_html, unsafe_allow_html=True)

    # ---------------- 2. STATIONS ----------------
    elif menu == "Styling Stations":
        st.markdown("#### Salon Station Occupancy")
        chairs = get_all_chairs()
        if chairs:
            cols = st.columns(3)
            for idx, chair in enumerate(chairs):
                col = cols[idx % 3]
                badge_bg = "#E8F5E9" if chair["status"] == "Available" else "#FCE4EC"
                badge_color = "#2E7D32" if chair["status"] == "Available" else "#C2185B"
                with col:
                    st.markdown(
                        f"""
                        <div style="background:#FFF; border:1.5px solid #EEE; border-radius:8px; padding:14px; text-align:center; margin-bottom:10px;">
                            <h4 style="margin:0; font-size:15px; color:#111;">{chair['chair_name']}</h4>
                            <p style="margin:3px 0 8px 0; font-size:12px; color:#666;">Type: {chair['chair_type']}</p>
                            <span style="background:{badge_bg}; color:{badge_color}; font-size:11px; font-weight:700; padding:4px 10px; border-radius:12px;">
                                {chair['status']}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    new_st = "Occupied" if chair["status"] == "Available" else "Available"
                    if st.button(f"Set {new_st}", key=f"tgl_{chair['id']}"):
                        execute_query("UPDATE chairs SET status = ? WHERE id = ?;", (new_st, chair["id"]))
                        st.rerun()

    # ---------------- 3. POS MULTI-ITEM BILLING (WITH WHATSAPP DISPATCH) ----------------
    elif menu == "POS Multi-Item Billing":
        st.markdown("#### Point of Sale & Invoicing")
        pos_tab1, pos_tab2 = st.tabs(["Create New Bill", "Past Billing History"])

        with pos_tab1:
            all_cust_list = get_all_customers()
            services = get_all_services(active_only=True)
            staff_list = get_all_staff()
            retail_products = fetch_all("SELECT * FROM products WHERE selling_price > 0 AND status = 'active';")

            c_top1, c_top2 = st.columns([3, 2])
            with c_top1:
                search_client = st.text_input("🔍 Search Client (Name / Mobile / Code)", placeholder="Type client name or mobile...", key="pos_client_search")
            with c_top2:
                with st.expander("➕ Quick Register New Client"):
                    qc_name = st.text_input("Full Name *", key="qc_name")
                    qc_phone = st.text_input("Mobile Number (10 Digits) *", key="qc_phone")
                    qc_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="qc_gender")
                    if st.button("Save & Register Client", key="btn_quick_save_client"):
                        if qc_name and qc_phone:
                            ok, msg, _ = register_customer(qc_name, qc_phone, "Client@123", gender=qc_gender)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

            filtered_customers = get_all_customers(search_query=search_client.strip() if search_client else None)
            cust_pool = filtered_customers if filtered_customers else all_cust_list

            if not cust_pool:
                st.warning("No client found in system. Register a new client above to begin billing.")
            else:
                cust_options = {f"{c['full_name']} ({c['phone']}) - [{c['customer_code']}]": c for c in cust_pool}
                selected_cust_label = st.selectbox("Select Billed Client *", list(cust_options.keys()))
                selected_cust = cust_options[selected_cust_label]

                st.divider()

                cart_col1, cart_col2 = st.columns(2)

                with cart_col1:
                    st.markdown("##### 💆‍♀️ Add Services to Cart")
                    if services:
                        srv_options = {f"{s['name']} — ₹{s['price']:.0f}": s for s in services}
                        chosen_srv_key = st.selectbox("Select Service", list(srv_options.keys()), key="pos_srv_picker")
                        chosen_srv = srv_options[chosen_srv_key]

                        stf_options = {f"{stf['full_name']} ({stf['role']})": stf for stf in staff_list} if staff_list else {"General Specialist": {"id": 1, "full_name": "General Specialist"}}
                        chosen_stf_name = st.selectbox("Specialist Stylist", list(stf_options.keys()), key="pos_stf_picker")
                        chosen_stf = stf_options[chosen_stf_name]

                        if st.button("➕ ADD SERVICE TO CART", key="btn_add_srv"):
                            st.session_state.pos_cart.append({
                                "type": "SERVICE",
                                "id": chosen_srv["id"],
                                "staff_id": chosen_stf["id"],
                                "staff_name": chosen_stf["full_name"],
                                "name": chosen_srv["name"],
                                "category": chosen_srv["category"],
                                "price": float(chosen_srv["price"]),
                                "qty": 1
                            })
                            st.rerun()

                with cart_col2:
                    st.markdown("##### 🛍️ Add Retail Products to Cart")
                    if retail_products:
                        prod_options = {f"{p['name']} — ₹{p['selling_price']:.0f} (Stock: {p['stock_quantity']})": p for p in retail_products}
                        chosen_prod_key = st.selectbox("Select Product", list(prod_options.keys()), key="pos_prd_picker")
                        chosen_prod = prod_options[chosen_prod_key]
                        p_qty = st.number_input("Quantity", min_value=1, max_value=max(1, chosen_prod["stock_quantity"]), value=1, key="pos_prd_qty")

                        if st.button("➕ ADD PRODUCT TO CART", key="btn_add_prd"):
                            st.session_state.pos_cart.append({
                                "type": "PRODUCT",
                                "id": chosen_prod["id"],
                                "staff_id": chosen_stf["id"] if staff_list else 1,
                                "staff_name": chosen_stf["full_name"] if staff_list else "Retail Counter",
                                "name": chosen_prod["name"],
                                "category": chosen_prod["category"],
                                "price": float(chosen_prod["selling_price"]),
                                "qty": int(p_qty)
                            })
                            st.rerun()
                    else:
                        st.info("No retail products available.")

                st.divider()

                st.markdown(f"#### 🛒 Current Bill Items ({len(st.session_state.pos_cart)} Items Added)")

                if not st.session_state.pos_cart:
                    st.info("Billing cart is empty. Choose a service or product above and click '➕ ADD'.")
                else:
                    cart_rows = []
                    for idx, item in enumerate(st.session_state.pos_cart):
                        line_total = item["price"] * item["qty"]
                        cart_rows.append({
                            "Item #": idx + 1,
                            "Category": item["type"],
                            "Description": item["name"],
                            "Specialist": item.get("staff_name", "N/A"),
                            "Unit Price (₹)": f"₹{item['price']:,.2f}",
                            "Quantity": item["qty"],
                            "Total (₹)": f"₹{line_total:,.2f}"
                        })
                    st.table(pd.DataFrame(cart_rows))

                    if st.button("🗑️ CLEAR CART", key="btn_clear_cart"):
                        st.session_state.pos_cart = []
                        st.rerun()

                raw_subtotal = sum(item["price"] * item["qty"] for item in st.session_state.pos_cart)

                st.markdown("##### 🧾 Taxes & Adjustments")
                m_tax1, m_tax2, m_tax3, m_tax4 = st.columns(4)

                with m_tax1:
                    gst_choice = st.selectbox("GST Tax Mode", ["18% Standard GST", "5% Composition", "0% Exempted"], key="tax_gst_mode")
                    gst_pct = 18.0 if "18%" in gst_choice else (5.0 if "5%" in gst_choice else 0.0)
                with m_tax2:
                    apply_svc_charge = st.checkbox("Service Charge (5%)", value=False, key="cb_svc_charge")
                    svc_charge_val = (raw_subtotal * 0.05) if apply_svc_charge else 0.0
                with m_tax3:
                    staff_tip_val = st.number_input("Specialist Tip (₹)", min_value=0.0, value=0.0, step=50.0, key="inp_staff_tip")
                with m_tax4:
                    discount_val = st.number_input("Discount Voucher (₹)", min_value=0.0, value=0.0, step=100.0, key="inp_discount")

                taxable_amt = max(0.0, raw_subtotal - discount_val)
                gst_amount = (taxable_amt * gst_pct) / 100.0
                final_grand_total = taxable_amt + gst_amount + svc_charge_val + staff_tip_val

                st.markdown(
                    f"""
                    <div style="background:#FFF5F8; border:2px solid #C2185B; border-radius:8px; padding:16px; margin:15px 0;">
                        <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:4px;">
                            <span><b>Cart Subtotal ({len(st.session_state.pos_cart)} items):</b></span>
                            <span>₹{raw_subtotal:,.2f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:4px;">
                            <span><b>Discount Voucher:</b></span>
                            <span>-₹{discount_val:,.2f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:4px;">
                            <span><b>GST ({gst_pct}%):</b></span>
                            <span>+₹{gst_amount:,.2f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:4px;">
                            <span><b>Service Charge & Tip:</b></span>
                            <span>+₹{(svc_charge_val + staff_tip_val):,.2f}</span>
                        </div>
                        <hr style="border:1px dashed #C2185B; margin:8px 0;"/>
                        <div style="display:flex; justify-content:space-between; font-size:22px; font-weight:800; color:#C2185B;">
                            <span>LIVE PAYABLE TOTAL:</span>
                            <span>₹{final_grand_total:,.2f}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_pay1, col_pay2 = st.columns(2)
                with col_pay1:
                    pay_method = st.selectbox("Payment Mode", ["UPI", "Cash", "Credit Card", "Debit Card", "Mixed"], key="sel_pay_method")
                with col_pay2:
                    st.write("")
                    st.write("")
                    process_btn = st.button("🔥 GENERATE INVOICE & PRINT RECEIPT", use_container_width=True, disabled=(len(st.session_state.pos_cart) == 0), key="btn_gen_invoice")

                if process_btn and st.session_state.pos_cart:
                    # Auto-deduct backbar consumable inventory for services billed
                    for item in st.session_state.pos_cart:
                        if item["type"] == "SERVICE":
                            auto_deduct_backbar_inventory(item["name"], item.get("category", "General"))

                    ok, msg, data = create_bill(
                        customer_id=selected_cust["id"],
                        items=st.session_state.pos_cart,
                        discount_amount=discount_val,
                        tax_amount=gst_amount + svc_charge_val + staff_tip_val
                    )
                    if ok and data:
                        record_payment(bill_id=data["bill_id"], amount=data["total"], payment_method=pay_method)
                        
                        st.session_state.last_receipt = {
                            "invoice_no": data["bill_number"],
                            "client_code": selected_cust["customer_code"],
                            "client_name": selected_cust["full_name"],
                            "client_phone": selected_cust["phone"],
                            "items": list(st.session_state.pos_cart),
                            "subtotal": raw_subtotal,
                            "discount": discount_val,
                            "gst_pct": gst_pct,
                            "gst_amount": gst_amount,
                            "svc_charge": svc_charge_val,
                            "staff_tip": staff_tip_val,
                            "grand_total": final_grand_total,
                            "pay_method": pay_method,
                            "date": datetime.now().strftime('%d-%b-%Y %H:%M')
                        }
                        st.session_state.pos_cart = []
                        st.session_state.trigger_success_anim = True
                        st.rerun()

                # RECEIPT CARD + WHATSAPP INSTANT TRIGGER
                if st.session_state.last_receipt:
                    r = st.session_state.last_receipt
                    
                    if st.session_state.get("trigger_success_anim", False):
                        play_payment_success_chime()
                        st.balloons()
                        st.session_state.trigger_success_anim = False

                    st.success(f"Invoice {r['invoice_no']} Settled Successfully!")

                    # Instant WhatsApp Dispatch Link
                    wa_url = generate_invoice_whatsapp_link(r)
                    st.markdown(
                        f"""
                        <div style="text-align:center; margin:10px 0 16px 0;">
                            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                                <div style="background:#25D366; color:#FFF; font-weight:700; font-size:14px; padding:11px 20px; border-radius:6px; display:inline-block; box-shadow:0 3px 8px rgba(37,211,102,0.3);">
                                    💬 SEND INVOICE TO CLIENT ON WHATSAPP (+91 {r['client_phone']})
                                </div>
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    items_html_list = []
                    for idx, it in enumerate(r["items"], 1):
                        stf_tag = f" <span style='color:#666;'>[By: {it.get('staff_name', 'General')}]</span>" if it.get('staff_name') else ""
                        items_html_list.append(
                            f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span>{idx}. {it['name']} (x{it['qty']}){stf_tag}</span><span>₹{(it['price'] * it['qty']):,.2f}</span></div>"
                        )
                    items_rendered = "".join(items_html_list)

                    charges_html = ""
                    if r.get("svc_charge", 0.0) > 0:
                        charges_html += f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span>Service Charge (5%):</span><span>+₹{r['svc_charge']:,.2f}</span></div>"
                    if r.get("staff_tip", 0.0) > 0:
                        charges_html += f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span>Specialist Tip:</span><span>+₹{r['staff_tip']:,.2f}</span></div>"

                    full_receipt_html = (
                        "<div style='background:#FFF; border:2px dashed #C2185B; border-radius:8px; padding:22px; max-width:540px; margin:15px auto; font-family:monospace; color:#111;'>"
                        "<div style='text-align:center; font-size:22px; font-weight:800; color:#C2185B; letter-spacing:2px; margin-bottom:2px;'>GLORENZA SALON</div>"
                        "<div style='text-align:center; font-size:11px; color:#555; margin-bottom:10px;'>Navrangpura, Ahmedabad &bull; GSTIN: 24AAAAA0000A1Z5 &bull; +91 9825012345</div>"
                        "<hr style='border:none; border-top:1px dashed #C2185B; margin:8px 0;'/>"
                        f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span><b>Invoice:</b> {r['invoice_no']}</span><span><b>Date:</b> {r['date']}</span></div>"
                        f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span><b>Client:</b> {r['client_name']} ({r['client_code']})</span><span><b>Phone:</b> {r['client_phone']}</span></div>"
                        f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span><b>Payment Mode:</b> {r['pay_method']}</span><span><b>Status:</b> <span style='color:#2E7D32; font-weight:bold;'>PAID</span></span></div>"
                        "<hr style='border:none; border-top:1px dashed #C2185B; margin:8px 0;'/>"
                        "<div style='font-weight:bold; margin-bottom:8px; font-size:12px; letter-spacing:1px;'>ITEMIZED SERVICES & PRODUCTS</div>"
                        f"{items_rendered}"
                        "<hr style='border:none; border-top:1px dashed #C2185B; margin:8px 0;'/>"
                        f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span>Gross Subtotal:</span><span>₹{r['subtotal']:,.2f}</span></div>"
                        f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span>Discount Voucher:</span><span>-₹{r['discount']:,.2f}</span></div>"
                        f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'><span>GST ({r.get('gst_pct', 18)}%):</span><span>+₹{r.get('gst_amount', 0.0):,.2f}</span></div>"
                        f"{charges_html}"
                        "<hr style='border:none; border-top:1px dashed #C2185B; margin:8px 0;'/>"
                        f"<div style='display:flex; justify-content:space-between; font-size:17px; font-weight:800; color:#C2185B; margin-top:6px;'><span>FINAL SETTLED TOTAL:</span><span>₹{r['grand_total']:,.2f}</span></div>"
                        "<hr style='border:none; border-top:1px dashed #C2185B; margin:8px 0;'/>"
                        "<div style='text-align:center; font-size:11px; color:#555; margin-top:8px;'>Thank you for choosing GLORENZA Salon! Visit Again.</div>"
                        "</div>"
                    )

                    st.markdown(full_receipt_html, unsafe_allow_html=True)

        with pos_tab2:
            st.markdown("#### All Settled Invoices")
            all_bills = fetch_all(
                """
                SELECT b.bill_number as 'Invoice No', c.full_name as 'Client', c.phone as 'Phone',
                       b.subtotal as 'Subtotal (₹)', b.discount_amount as 'Discount (₹)',
                       b.tax_amount as 'Taxes (₹)', b.grand_total as 'Grand Total (₹)',
                       b.payment_status as 'Status', b.created_at as 'Date & Time'
                FROM bills b
                JOIN customers c ON b.customer_id = c.id
                ORDER BY b.id DESC;
                """
            )
            if all_bills:
                st.dataframe(pd.DataFrame(all_bills), use_container_width=True)
            else:
                st.info("No bills generated yet.")

    # ---------------- 4. CLIENT DIRECTORY ----------------
    elif menu == "Client Directory":
        st.markdown("#### Client Directory & Lifetime Spend")
        customers = get_all_customers()
        if not customers:
            st.info("No registered clients.")
        else:
            for c in customers:
                c_bills = fetch_all("SELECT * FROM bills WHERE customer_id = ? ORDER BY id DESC;", (c["id"],))
                total_spent = sum(b["grand_total"] for b in c_bills)
                total_visits = len(c_bills)

                with st.expander(f"👤 {c['full_name']} ({c['phone']}) — [{c['customer_code']}] | Total Spent: ₹{total_spent:,.2f} ({total_visits} Visits)"):
                    st.write(f"**Gender:** {c.get('gender', 'N/A')} | **Type:** `{c['customer_type']}` | **Joined:** {c['created_at']}")
                    if c_bills:
                        st.markdown("##### Invoices Issued:")
                        st.dataframe(pd.DataFrame(c_bills)[["bill_number", "subtotal", "discount_amount", "tax_amount", "grand_total", "payment_status", "created_at"]], use_container_width=True)

    # ---------------- 5. STAFF SPECIALISTS & PAYROLL ----------------
    elif menu == "Staff Specialists":
        st.markdown("#### Salon Specialists & Comprehensive Payroll Desk")
        stf_tab1, stf_tab2, stf_tab3, stf_tab4 = st.tabs(["Directory & Profiles", "Monthly Payroll & Commissions", "Daily Attendance Logs", "Leave Requests Approval"])

        with stf_tab1:
            staff_members = get_all_staff(status_filter=None)
            if staff_members:
                st.dataframe(pd.DataFrame(staff_members)[["staff_code", "full_name", "phone", "role", "specialization", "salary", "service_commission_percent", "status"]], use_container_width=True)

        with stf_tab2:
            st.markdown("##### 💼 Monthly Salary & Commission Payouts")
            pay_month = st.date_input("Payroll Month Reference", value=date.today(), key="payroll_month_ref")
            month_str = pay_month.strftime('%Y-%m')

            all_stf = get_all_staff(status_filter="active")
            if all_stf:
                payroll_data = []
                for s in all_stf:
                    s_id = s["id"]
                    base_sal = float(s.get("salary", 50000.0))
                    comm_pct = float(s.get("service_commission_percent", 10.0))

                    srv_billed = fetch_all(
                        """
                        SELECT bi.total_price 
                        FROM bill_items bi
                        JOIN bills b ON bi.bill_id = b.id
                        WHERE bi.staff_id = ? AND strftime('%Y-%m', b.created_at, 'localtime') = ?;
                        """,
                        (s_id, month_str)
                    )
                    billed_total = sum(float(it["total_price"]) for it in srv_billed)
                    comm_earned = (billed_total * comm_pct) / 100.0
                    total_payout = base_sal + comm_earned

                    payroll_data.append({
                        "Staff Code": s["staff_code"],
                        "Name": s["full_name"],
                        "Role": s["role"],
                        "Base Salary (₹)": f"₹{base_sal:,.2f}",
                        "Billed Services (₹)": f"₹{billed_total:,.2f}",
                        "Commission Rate": f"{comm_pct:.0f}%",
                        "Commission (₹)": f"₹{comm_earned:,.2f}",
                        "Final Monthly Payout (₹)": f"₹{total_payout:,.2f}"
                    })
                st.dataframe(pd.DataFrame(payroll_data), use_container_width=True)

        with stf_tab3:
            st.markdown("##### ⏱️ Salon Attendance History")
            att_date_sel = st.date_input("Filter Attendance Date", value=date.today(), key="att_date_filter")
            att_logs = fetch_all(
                """
                SELECT a.id, s.staff_code, s.full_name as 'Specialist', s.role,
                       a.attendance_date as 'Date', a.check_in as 'Punch In',
                       a.check_out as 'Punch Out', a.status as 'Status'
                FROM attendance a
                JOIN staff s ON a.staff_id = s.id
                WHERE a.attendance_date = ?
                ORDER BY a.id DESC;
                """,
                (str(att_date_sel),)
            )
            if att_logs:
                st.dataframe(pd.DataFrame(att_logs), use_container_width=True)
            else:
                st.info(f"No attendance logs registered for {att_date_sel}.")

        with stf_tab4:
            st.markdown("##### 🏖️ Staff Leave Requests Approval")
            leave_reqs = fetch_all(
                """
                SELECT sl.id, s.full_name as 'Specialist', sl.leave_type, sl.start_date,
                       sl.end_date, sl.reason, sl.status, sl.created_at
                FROM staff_leaves sl
                JOIN staff s ON sl.staff_id = s.id
                ORDER BY sl.id DESC;
                """
            )
            if not leave_reqs:
                st.info("No leave requests submitted.")
            else:
                for l in leave_reqs:
                    st_col1, st_col2 = st.columns([4, 2])
                    with st_col1:
                        st.markdown(
                            f"""
                            <div style="background:#FFF; border:1px solid #EEE; border-left:4px solid #C2185B; border-radius:6px; padding:10px 14px; margin-bottom:8px;">
                                <b>{l['Specialist']}</b> &mdash; <i>{l['leave_type']}</i> ({l['start_date']} to {l['end_date']})<br>
                                <span style="font-size:12px; color:#555;">Reason: {l['reason']} | Status: <b>{l['status']}</b></span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with st_col2:
                        if l["status"] == "Pending":
                            c_a, c_r = st.columns(2)
                            with c_a:
                                if st.button("Approve", key=f"app_{l['id']}"):
                                    execute_query("UPDATE staff_leaves SET status = 'Approved' WHERE id = ?;", (l["id"],))
                                    st.success("Approved!")
                                    st.rerun()
                            with c_r:
                                if st.button("Reject", key=f"rej_{l['id']}"):
                                    execute_query("UPDATE staff_leaves SET status = 'Rejected' WHERE id = ?;", (l["id"],))
                                    st.warning("Rejected!")
                                    st.rerun()

    # ---------------- 6. SERVICES ----------------
    elif menu == "Service Menu & Pricing":
        st.markdown("#### Salon Service Catalog")
        services = get_all_services(active_only=False)
        if services:
            services_table = []
            for s in services:
                margin_pct, net_profit = get_service_margin_data(s["category"], s["price"])
                services_table.append({
                    "Code": s["service_code"],
                    "Service Name": s["name"],
                    "Category": s["category"],
                    "Duration (Mins)": s["duration_minutes"],
                    "Customer Price (₹)": f"₹{s['price']:,.2f}",
                    "Profit Margin (%)": f"{margin_pct:.0f}%",
                    "Net Profit per Service (₹)": f"₹{net_profit:,.2f}"
                })
            st.dataframe(pd.DataFrame(services_table), use_container_width=True)

    # ---------------- 7. INVENTORY ----------------
    elif menu == "Inventory & Supplies":
        st.markdown("#### Inventory & Supplies")
        products = get_all_products(active_only=False)
        if products:
            inv_table = []
            for p in products:
                cost = p["purchase_price"]
                sell = p["selling_price"]
                profit = max(0.0, sell - cost) if sell > 0 else 0.0
                margin_pct = ((profit / sell) * 100.0) if sell > 0 else 0.0

                inv_table.append({
                    "Code": p["product_code"],
                    "Product Name": p["name"],
                    "Category": p["category"],
                    "Purchase Cost (₹)": f"₹{cost:,.2f}",
                    "Selling Price (₹)": f"₹{sell:,.2f}" if sell > 0 else "In-Salon Use",
                    "Net Profit / Unit (₹)": f"₹{profit:,.2f}" if sell > 0 else "N/A",
                    "Margin (%)": f"{margin_pct:.1f}%" if sell > 0 else "N/A",
                    "Stock": p["stock_quantity"]
                })
            st.dataframe(pd.DataFrame(inv_table), use_container_width=True)

    # ---------------- 8. SALON EXPENSES ----------------
    elif menu == "Operating Expenses":
        st.markdown("#### Salon Operational Cost Tracker")
        c1, c2 = st.columns(2)
        with c1:
            e_cat = st.selectbox("Category", ["Rent", "Electricity", "Water", "Internet", "Maintenance", "Supplies", "Marketing", "Staff Welfare", "Other"], key="in_exp_cat")
            e_amt = st.number_input("Amount (₹) *", min_value=10.0, value=1500.0, step=100.0, key="in_exp_amt")
            deduct_profit = st.checkbox("Deduct this Expense from Salon Net Profit?", value=True, key="in_exp_deduct")
        with c2:
            e_dt = st.date_input("Expense Date", value=date.today(), key="in_exp_date")
            e_pay = st.selectbox("Payment Mode", ["UPI", "Cash", "Bank Transfer", "Card"], key="in_exp_pay")
            e_desc = st.text_input("Expense Description / Vendor *", placeholder="e.g. Electricity Bill", key="in_exp_desc")

        if st.button("Record Operational Expense", key="btn_save_expense"):
            if e_desc.strip():
                note_tag = "deduct:yes" if deduct_profit else "deduct:no"
                ok, msg = add_expense(
                    category=e_cat,
                    description=e_desc,
                    amount=float(e_amt),
                    expense_date=str(e_dt),
                    payment_method=e_pay,
                    notes=note_tag
                )
                if ok:
                    st.success("Expense recorded successfully!")
                    st.rerun()
                else:
                    st.error(msg)

        st.divider()
        all_expenses = fetch_all("SELECT * FROM expenses ORDER BY expense_date DESC, id DESC;")
        if all_expenses:
            st.dataframe(pd.DataFrame(all_expenses)[["expense_code", "category", "description", "amount", "expense_date", "payment_method"]], use_container_width=True)

    # ---------------- 9. REVIEWS ----------------
    elif menu == "Client Reviews":
        st.markdown("#### Client Reviews & Ratings")
        revs = get_all_reviews()
        if revs:
            st.dataframe(pd.DataFrame(revs)[["customer_name", "staff_name", "rating", "review_text", "created_at"]], use_container_width=True)

    # ---------------- 10. SUPPORT ----------------
    elif menu == "Support Concierge":
        st.markdown("#### Support Tickets")
        tickets = get_all_tickets()
        if tickets:
            st.dataframe(pd.DataFrame(tickets)[["customer_name", "customer_phone", "subject", "message", "status", "created_at"]], use_container_width=True)

    # ---------------- 11. DATABASE BACKUP & SAFETY ----------------
    elif menu == "System Database Backup":
        st.markdown("#### Salon Database Backup & Data Protection")
        st.info("Download a snapshot of your salon database (`glorenza.db`) containing all client records, bills, expenses, staff salaries, and appointments.")
        
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "rb") as db_file:
                db_bytes = db_file.read()

            st.download_button(
                label="📦 DOWNLOAD FULL DATABASE BACKUP (.DB)",
                data=db_bytes,
                file_name=f"GLORENZA_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                mime="application/x-sqlite3",
                use_container_width=True
            )
        else:
            st.error("Database file path not found.")

    # ---------------- 12. EXCEL EXPORTS ----------------
    elif menu == "Excel Reports Export":
        st.markdown("#### Export Operational Data to Excel")
        rep = st.selectbox("Select Report", ["Billing & Revenue", "Appointments", "Staff Directory", "Inventory", "Expenses", "Clients"], key="sel_excel_rep")
        if st.button("Download Excel Report", key="btn_download_excel", use_container_width=True):
            if rep == "Billing & Revenue":
                data = fetch_all("SELECT * FROM bills ORDER BY id DESC;")
            elif rep == "Appointments":
                data = fetch_all("SELECT * FROM appointments ORDER BY id DESC;")
            elif rep == "Staff Directory":
                data = get_all_staff(status_filter=None)
            elif rep == "Inventory":
                data = get_all_products(active_only=False)
            elif rep == "Clients":
                data = get_all_customers()
            else:
                data = fetch_all("SELECT * FROM expenses ORDER BY id DESC;")

            excel_bytes = export_to_excel(data, sheet_name=rep)
            st.download_button(
                label=f"Download {rep}.xlsx",
                data=excel_bytes,
                file_name=f"GLORENZA_{rep.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )