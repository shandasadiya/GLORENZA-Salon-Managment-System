
"""
GLORENZA SALON AHMEDABAD - Luxury Client Portal
Includes booking error handling, WhatsApp confirmations,
loyalty points, invoice history, reviews and support tickets.
"""

import random
from datetime import date, datetime

import streamlit as st

from database.connection import fetch_all, fetch_one, execute_query
from modules.session import get_current_user, logout_user
from modules.services import get_all_services
from modules.staff import get_all_staff
from modules.chairs import get_all_chairs
from modules.whatsapp import generate_appointment_whatsapp_link
from ui.common import render_header


def safe_execute(query, params=()):
    """Execute a database write without exposing raw database errors."""
    try:
        execute_query(query, params)
        return True
    except Exception:
        return False


def get_client_vip_tier(total_spent: float) -> tuple:
    if total_spent >= 50000:
        return "DIAMOND VIP", "#4A148C", "#F3E5F5", 15.0
    elif total_spent >= 20000:
        return "GOLD PRIVILEGE", "#C2185B", "#FCE4EC", 10.0
    elif total_spent >= 5000:
        return "SILVER MEMBER", "#1565C0", "#E3F2FD", 5.0
    return "CLASSIC CLIENT", "#37474F", "#ECEFF1", 0.0


def render_customer_panel():
    try:
        render_header()
        user = get_current_user()

        if not user:
            st.warning("Please log in to continue.")
            return

        cust_record = fetch_one(
            "SELECT * FROM customers WHERE user_id = ? OR phone = ?;",
            (user.get("id"), user.get("phone"))
        )

        if not cust_record:
            st.error(
                "Customer profile not found. "
                "Please contact salon reception."
            )
            if st.button("Logout", key="cust_missing_logout"):
                logout_user()
                st.rerun()
            return

        cust_id = cust_record["id"]
        cust_name = cust_record["full_name"]
        cust_code = cust_record["customer_code"]
        cust_phone = cust_record["phone"]

        all_bills = fetch_all(
            "SELECT * FROM bills WHERE customer_id = ? ORDER BY id DESC;",
            (cust_id,)
        ) or []

        total_spent = sum(float(b["grand_total"] or 0) for b in all_bills)
        loyalty_points = int(total_spent * 0.05)

        tier_name, tier_color, tier_bg, tier_disc = (
            get_client_vip_tier(total_spent)
        )

        if "cust_active_tab" not in st.session_state:
            st.session_state.cust_active_tab = "Book Appointment"

        if "last_booking_wa" not in st.session_state:
            st.session_state.last_booking_wa = None

        # Customer header
        col_t1, col_t2 = st.columns([5, 1.2])

        with col_t1:
            st.markdown(
                f"""
                <div style="font-size:15px;font-weight:600;color:#111;padding-top:4px;">
                    Welcome, <b>{cust_name}</b>
                    <span style="color:#777;">({cust_code})</span>
                    <span style="background:{tier_bg};color:{tier_color};
                    padding:3px 10px;border-radius:4px;font-size:12px;
                    font-weight:800;margin-left:8px;
                    border:1px solid {tier_color}40;">
                        {tier_name}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_t2:
            if st.button(
                "🚪 LOGOUT",
                key="cust_logout",
                use_container_width=True
            ):
                logout_user()
                st.rerun()

        # Navigation
        st.sidebar.markdown(
            '<div class="sidebar-brand-title">CLIENT CONCIERGE</div>',
            unsafe_allow_html=True
        )

        menu_items = [
            ("Book Appointment", "📅 Book Appointment"),
            ("My Active Bookings", "📌 My Active Bookings"),
            ("Loyalty Wallet & VIP Tier", "💎 Loyalty Wallet & VIP Tier"),
            ("Invoice History & Receipts", "🧾 Invoices & Receipts"),
            ("My Hair & Skin Profile", "💆 Hair & Skin Profile"),
            ("Rate & Review Stylist", "⭐ Rate Specialist"),
            ("Support Concierge", "💬 Support Concierge"),
        ]

        for key_name, label_text in menu_items:
            if st.sidebar.button(
                label_text,
                key=f"cust_nav_{key_name}",
                use_container_width=True
            ):
                st.session_state.cust_active_tab = key_name
                st.rerun()

        menu = st.session_state.cust_active_tab

        # --------------------------------------------------
        # 1. BOOK APPOINTMENT
        # --------------------------------------------------
        if menu == "Book Appointment":
            st.markdown("#### Schedule a Luxury Salon Experience")

            services = get_all_services(active_only=True) or []
            staff_list = get_all_staff(status_filter="active") or []
            chairs = get_all_chairs() or []

            if not services:
                st.warning("No services are currently available.")
                return

            if not staff_list:
                st.warning("No active stylists are currently available.")
                return

            with st.form("form_book_appointment"):
                col1, col2 = st.columns(2)

                with col1:
                    srv_dict = {
                        f"{s['name']} — ₹{s['price']:.0f} "
                        f"({s['duration_minutes']} Mins)": s
                        for s in services
                    }

                    chosen_srv_label = st.selectbox(
                        "Select Desired Service *",
                        list(srv_dict.keys())
                    )
                    chosen_srv = srv_dict[chosen_srv_label]

                    apt_date = st.date_input(
                        "Appointment Date *",
                        min_value=date.today(),
                        value=date.today()
                    )

                with col2:
                    stf_dict = {
                        f"{s['full_name']} ({s['role']})": s
                        for s in staff_list
                    }

                    chosen_stf_label = st.selectbox(
                        "Preferred Specialist Stylist *",
                        list(stf_dict.keys())
                    )
                    chosen_stf = stf_dict[chosen_stf_label]

                    apt_time = st.selectbox(
                        "Preferred Time Slot *",
                        [
                            "10:00 AM", "11:00 AM", "12:00 PM",
                            "01:00 PM", "02:00 PM", "03:00 PM",
                            "04:00 PM", "05:00 PM", "06:00 PM",
                            "07:00 PM", "08:00 PM",
                        ]
                    )

                notes = st.text_input(
                    "Special Requests / Allergies / Hair Length notes",
                    placeholder="e.g. Sensitive scalp, prefer quiet service"
                )

                book_btn = st.form_submit_button(
                    "CONFIRM LUXURY BOOKING",
                    use_container_width=True
                )

            if book_btn:
                try:
                    conflict_apt = fetch_one(
                        """
                        SELECT id FROM appointments
                        WHERE staff_id = ?
                          AND appointment_date = ?
                          AND start_time = ?
                          AND status != 'Cancelled';
                        """,
                        (
                            chosen_stf["id"],
                            str(apt_date),
                            apt_time
                        )
                    )

                    if conflict_apt:
                        st.error(
                            f"Stylist {chosen_stf['full_name']} is already "
                            f"booked at {apt_time} on {apt_date}. "
                            "Please choose another time or stylist."
                        )
                    else:
                        avail_chair = (
                            chairs[0]["id"] if chairs else 1
                        )

                        apt_code = (
                            f"GLZ-APT-"
                            f"{int(datetime.now().timestamp()) % 10000:04d}"
                            f"{random.randint(10, 99)}"
                        )

                        cols_info = fetch_all(
                            "PRAGMA table_info(appointments);"
                        )
                        col_names = [c["name"] for c in cols_info]

                        insert_data = {
                            "appointment_code": apt_code,
                            "customer_id": cust_id,
                            "service_id": chosen_srv["id"],
                            "staff_id": chosen_stf["id"],
                            "chair_id": avail_chair,
                            "appointment_date": str(apt_date),
                            "start_time": apt_time,
                            "end_time": apt_time,
                            "status": "Confirmed",
                            "payment_status": "Pending",
                            "notes": notes or "",
                        }

                        valid_cols = [
                            k for k in insert_data if k in col_names
                        ]

                        # Preserve the original schema compatibility logic.
                        # If an insert still violates a database constraint,
                        # show a friendly message rather than a traceback.
                        for col in cols_info:
                            name = col["name"]

                            if (
                                col["notnull"] == 1
                                and col["dflt_value"] is None
                                and col["pk"] == 0
                                and name not in valid_cols
                            ):
                                valid_cols.append(name)
                                col_type = (col["type"] or "").upper()

                                insert_data[name] = (
                                    0 if (
                                        "INT" in col_type
                                        or "REAL" in col_type
                                    ) else ""
                                )

                        placeholders = ", ".join(
                            ["?"] * len(valid_cols)
                        )
                        columns_sql = ", ".join(valid_cols)
                        values_tuple = tuple(
                            insert_data[k] for k in valid_cols
                        )

                        insert_query = (
                            f"INSERT INTO appointments "
                            f"({columns_sql}) VALUES ({placeholders});"
                        )

                        execute_query(insert_query, values_tuple)

                        st.session_state.last_booking_wa = {
                            "client_name": cust_name,
                            "client_phone": cust_phone,
                            "appointment_code": apt_code,
                            "service_name": chosen_srv["name"],
                            "stylist_name": chosen_stf["full_name"],
                            "date": str(apt_date),
                            "time": apt_time,
                            "station": (
                                chairs[0]["chair_name"]
                                if chairs else "Studio"
                            ),
                        }

                        st.success(
                            f"Appointment {apt_code} booked successfully "
                            f"for {apt_date} at {apt_time}!"
                        )
                        st.balloons()
                        st.rerun()

                except Exception:
                    st.error(
                        "We could not complete this booking right now. "
                        "Please try another slot or contact salon reception."
                    )

            # WhatsApp confirmation
            if st.session_state.last_booking_wa:
                try:
                    wa_url = generate_appointment_whatsapp_link(
                        st.session_state.last_booking_wa
                    )

                    st.markdown(
                        f"""
                        <div style="text-align:center;margin:16px 0;">
                            <a href="{wa_url}" target="_blank"
                            style="text-decoration:none;">
                                <div style="background:#25D366;color:#FFF;
                                font-weight:700;font-size:14px;
                                padding:12px 24px;border-radius:6px;
                                display:inline-block;">
                                    💬 SEND BOOKING CONFIRMATION TO WHATSAPP
                                </div>
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception:
                    st.info("WhatsApp confirmation is temporarily unavailable.")

        # --------------------------------------------------
        # 2. ACTIVE BOOKINGS
        # --------------------------------------------------
        elif menu == "My Active Bookings":
            st.markdown("#### Upcoming Appointments & Live Queue")

            try:
                my_apts = fetch_all(
                    """
                    SELECT a.id, a.appointment_code, s.name AS service_name,
                           s.price, stf.full_name AS stylist_name,
                           a.appointment_date, a.start_time, a.status,
                           ch.chair_name
                    FROM appointments a
                    JOIN services s ON a.service_id = s.id
                    JOIN staff stf ON a.staff_id = stf.id
                    LEFT JOIN chairs ch ON a.chair_id = ch.id
                    WHERE a.customer_id = ?
                    ORDER BY a.appointment_date DESC, a.id DESC;
                    """,
                    (cust_id,)
                ) or []

                if not my_apts:
                    st.info("No bookings found. Book your first salon service.")

                for apt in my_apts:
                    status = apt["status"]
                    status_color = (
                        "#2E7D32" if status == "Confirmed"
                        else "#C2185B" if status == "Completed"
                        else "#757575"
                    )

                    st.markdown(
                        f"""
                        <div style="background:#FFF;border:1.5px solid #FCE4EC;
                        border-left:5px solid #C2185B;border-radius:8px;
                        padding:16px;margin-bottom:12px;">
                            <h4 style="margin:0;color:#111;">
                                {apt['service_name']}
                            </h4>
                            <span style="color:{status_color};
                            font-weight:800;font-size:12px;">
                                {status.upper()}
                            </span>
                            <div style="font-size:13px;color:#444;margin-top:8px;">
                                📅 <b>Date:</b> {apt['appointment_date']}
                                &nbsp;|&nbsp; ⏰ <b>Time:</b>
                                {apt['start_time']}
                                &nbsp;|&nbsp; ✂️ <b>Stylist:</b>
                                {apt['stylist_name']}
                            </div>
                            <div style="font-size:12px;color:#777;">
                                Station: {apt['chair_name'] or 'Styling Studio'}
                                &nbsp;|&nbsp; Ref Code:
                                <code>{apt['appointment_code']}</code>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            except Exception:
                st.error("Unable to load appointments right now.")

        # --------------------------------------------------
        # 3. LOYALTY WALLET
        # --------------------------------------------------
        elif menu == "Loyalty Wallet & VIP Tier":
            st.markdown("#### Privilege Rewards & Membership Tier")

            st.markdown(
                f"""
                <div class="kpi-row-container">
                    <div class="kpi-single-card">
                        <div class="card-title">Reward Points</div>
                        <div class="card-value">🪙 {loyalty_points} Pts</div>
                    </div>
                    <div class="kpi-single-card">
                        <div class="card-title">Wallet Cash Value</div>
                        <div class="card-value">₹{loyalty_points:,.2f}</div>
                    </div>
                    <div class="kpi-single-card">
                        <div class="card-title">Lifetime Salon Spend</div>
                        <div class="card-value">₹{total_spent:,.2f}</div>
                    </div>
                    <div class="kpi-single-card">
                        <div class="card-title">VIP Tier Discount</div>
                        <div class="card-value">{tier_disc:.0f}% OFF</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.divider()
            st.markdown(
                """
                ##### 🌟 Glorenza Elite Tier Milestones

                * **Classic Client (₹0 - ₹4,999):** 5% Reward Points.
                * **Silver Member (₹5,000 - ₹19,999):** 5% Discount.
                * **Gold Privilege (₹20,000 - ₹49,999):** 10% Discount.
                * **Diamond VIP (₹50,000+):** 15% VIP Discount.
                """
            )

        # --------------------------------------------------
        # 4. INVOICES & RECEIPTS
        # --------------------------------------------------
        elif menu == "Invoice History & Receipts":
            st.markdown("#### Settled Invoices & Thermal Receipts")

            if not all_bills:
                st.info("No past invoices recorded.")

            for bill in all_bills:
                try:
                    items = fetch_all(
                        """
                        SELECT bi.item_type, bi.total_price, bi.quantity,
                               COALESCE(s.name, p.name) AS item_name
                        FROM bill_items bi
                        LEFT JOIN services s
                            ON bi.item_type = 'SERVICE' AND bi.item_id = s.id
                        LEFT JOIN products p
                            ON bi.item_type = 'PRODUCT' AND bi.item_id = p.id
                        WHERE bi.bill_id = ?;
                        """,
                        (bill["id"],)
                    ) or []

                    with st.expander(
                        f"Invoice {bill['bill_number']} — "
                        f"{bill['created_at']} | "
                        f"Grand Total: ₹{bill['grand_total']:,.2f}"
                    ):
                        item_rows = "".join(
                            f"<div style='display:flex;justify-content:space-between;'>"
                            f"<span>{item['item_name']} (x{item['quantity']})</span>"
                            f"<span>₹{item['total_price']:,.2f}</span></div>"
                            for item in items
                        )

                        st.markdown(
                            f"""
                            <div style="background:#FFF;border:2px dashed #C2185B;
                            border-radius:8px;padding:18px;font-family:monospace;
                            max-width:480px;margin:auto;">
                                <div style="text-align:center;font-size:18px;
                                font-weight:800;color:#C2185B;">
                                    GLORENZA SALON
                                </div>
                                <div style="text-align:center;font-size:11px;color:#666;">
                                    Navrangpura, Ahmedabad
                                </div>
                                <hr>
                                <div>Invoice: {bill['bill_number']}</div>
                                <div>Date: {bill['created_at']}</div>
                                <div>Client: {cust_name} ({cust_code})</div>
                                <hr>
                                {item_rows}
                                <hr>
                                <div>Subtotal: ₹{bill['subtotal']:,.2f}</div>
                                <div>Discount: -₹{bill['discount_amount']:,.2f}</div>
                                <div>Taxes: +₹{bill['tax_amount']:,.2f}</div>
                                <hr>
                                <div style="font-size:16px;font-weight:bold;color:#C2185B;">
                                    PAID TOTAL: ₹{bill['grand_total']:,.2f}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                except Exception:
                    st.warning("One invoice could not be displayed.")

        # --------------------------------------------------
        # 5. HAIR & SKIN PROFILE
        # --------------------------------------------------
        elif menu == "My Hair & Skin Profile":
            st.markdown(
                "#### Specialist Consultation & Aftercare Treatment History"
            )

            try:
                notes = fetch_all(
                    """
                    SELECT cn.note, cn.created_at,
                           s.full_name AS stylist_name, s.role
                    FROM customer_notes cn
                    JOIN staff s ON cn.staff_id = s.id
                    WHERE cn.customer_id = ?
                    ORDER BY cn.id DESC;
                    """,
                    (cust_id,)
                ) or []

                if not notes:
                    st.info("No personalized treatment notes recorded yet.")

                for note in notes:
                    st.markdown(
                        f"""
                        <div style="background:#FFF9FA;border:1.5px solid #F8BBD0;
                        border-radius:8px;padding:14px;margin-bottom:10px;">
                            <div style="font-size:14px;font-weight:600;color:#111;">
                                {note['note']}
                            </div>
                            <div style="font-size:11px;color:#C2185B;margin-top:6px;">
                                Prescribed By: <b>{note['stylist_name']}</b>
                                ({note['role']}) &bull; {note['created_at']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            except Exception:
                st.info("Treatment history is temporarily unavailable.")

        # --------------------------------------------------
        # 6. RATE & REVIEW STYLIST
        # --------------------------------------------------
        elif menu == "Rate & Review Stylist":
            st.markdown("#### Share Your Salon Experience")

            try:
                staff_list = get_all_staff() or []

                if not staff_list:
                    st.info("No stylists are available for review.")
                else:
                    staff_map = {
                        f"{s['full_name']} ({s['role']})": s["id"]
                        for s in staff_list
                    }

                    with st.form("form_submit_review"):
                        selected_staff = st.selectbox(
                            "Select Specialist Stylist",
                            list(staff_map.keys())
                        )
                        rating = st.slider(
                            "Rating (Stars)", 1, 5, 5
                        )
                        review_text = st.text_area(
                            "Your Review & Feedback *",
                            placeholder="How was your salon experience?"
                        )

                        submit_review = st.form_submit_button(
                            "SUBMIT FEEDBACK & RATING",
                            use_container_width=True
                        )

                    if submit_review:
                        if review_text.strip():
                            success = safe_execute(
                                """
                                INSERT INTO reviews
                                    (customer_id, staff_id, rating, review_text)
                                VALUES (?, ?, ?, ?);
                                """,
                                (
                                    cust_id,
                                    staff_map[selected_staff],
                                    rating,
                                    review_text.strip()
                                )
                            )

                            if success:
                                st.success("Thank you for your valuable feedback!")
                                st.rerun()
                            else:
                                st.error("Review could not be saved right now.")
                        else:
                            st.error("Please enter a review message.")

            except Exception:
                st.error("Review section is temporarily unavailable.")

        # --------------------------------------------------
        # 7. SUPPORT CONCIERGE
        # --------------------------------------------------
        elif menu == "Support Concierge":
            st.markdown("#### Client Helpdesk & Direct Concierge")

            with st.form("form_cust_ticket"):
                subject = st.text_input(
                    "Subject / Inquiry *",
                    placeholder="e.g. Reschedule request / Product query"
                )
                message = st.text_area(
                    "Message Details *",
                    placeholder="Describe your query..."
                )

                submit_ticket = st.form_submit_button(
                    "SUBMIT TICKET TO RECEPTION",
                    use_container_width=True
                )

            if submit_ticket:
                if subject.strip() and message.strip():
                    success = safe_execute(
                        """
                        INSERT INTO support_tickets
                            (customer_name, customer_phone, subject, message, status)
                        VALUES (?, ?, ?, ?, 'Open');
                        """,
                        (
                            cust_name,
                            cust_phone,
                            subject.strip(),
                            message.strip()
                        )
                    )

                    if success:
                        st.success(
                            "Your ticket has been sent to our Salon Concierge desk!"
                        )
                        st.rerun()
                    else:
                        st.error(
                            "Your ticket could not be saved right now. "
                            "Please contact salon reception."
                        )
                else:
                    st.error("Please fill in both subject and message.")

    except Exception:
        # Final safety net: don't expose internal database tracebacks to clients.
        st.error(
            "The customer portal is temporarily unavailable. "
            "Please refresh the page or contact salon reception."
        )
