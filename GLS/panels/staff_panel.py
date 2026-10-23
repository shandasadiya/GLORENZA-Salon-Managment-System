"""
GLORENZA SALON AHMEDABAD - Staff Specialist Panel
Live commission tracking, attendance punch clock, treatment consultation notes,
client reviews scoreboard, leave application system, and daily appointment roster.
"""

from datetime import date, datetime
import streamlit as st
import pandas as pd

from database.connection import fetch_all, fetch_one, execute_query
from modules.session import get_current_user, logout_user
from ui.common import render_header


def render_staff_panel():
    render_header()
    user = get_current_user()

    # Link logged-in user with staff database profile
    staff_record = fetch_one(
        "SELECT * FROM staff WHERE user_id = ? OR phone = ?;",
        (user.get("id"), user.get("phone"))
    )
    if not staff_record:
        st.error("Staff profile not linked with your login account. Contact the salon administrator.")
        if st.button("Logout"):
            logout_user()
            st.rerun()
        return

    staff_id = staff_record["id"]
    staff_name = staff_record["full_name"]
    staff_role = staff_record["role"]
    comm_rate = float(staff_record.get("service_commission_percent", 10.0))
    base_salary = float(staff_record.get("salary", 50000.0))

    if "staff_active_tab" not in st.session_state:
        st.session_state.staff_active_tab = "My Daily Roster"

    # Top Bar with Luxury Specialist Role Badge
    col_t1, col_t2 = st.columns([5, 1.2])
    with col_t1:
        st.markdown(
            f"""
            <div style="font-size:15px; font-weight:600; color:#111; padding-top:4px;">
                Specialist Workstation &mdash; Stylist: <b>{staff_name}</b> 
                <span style="background:#FCE4EC; color:#C2185B; padding:3px 10px; border-radius:4px; font-size:12px; font-weight:700; margin-left:8px; border:1px solid #F8BBD0;">
                    {staff_role}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_t2:
        if st.button("🚪 LOGOUT", key="staff_logout", use_container_width=True):
            logout_user()
            st.rerun()

    # Sidebar Navigation
    st.sidebar.markdown('<div class="sidebar-brand-title">SPECIALIST DESK</div>', unsafe_allow_html=True)
    
    menu_items = [
        ("My Daily Roster", "📅 My Daily Roster"),
        ("Live Earnings & Commission", "💰 Live Earnings & Commission"),
        ("Attendance & Punch Clock", "⏱️ Attendance & Punch Clock"),
        ("Client Consultation Notes", "📝 Client Consultation Notes"),
        ("My Performance & Reviews", "⭐ My Performance & Reviews"),
        ("Leave Application", "🏖️ Leave Application")
    ]

    for key_name, label_text in menu_items:
        if st.sidebar.button(label_text, key=f"staff_nav_{key_name}", use_container_width=True):
            st.session_state.staff_active_tab = key_name
            st.rerun()

    menu = st.session_state.staff_active_tab

    # ---------------- 1. MY DAILY ROSTER & APPOINTMENTS ----------------
    if menu == "My Daily Roster":
        st.markdown("#### Today's Appointment Queue & Assigned Services")
        today_str = str(date.today())

        # Today's billed services processed by this staff
        today_services = fetch_all(
            """
            SELECT bi.id as item_id, b.bill_number, c.full_name as client_name, c.phone as client_phone,
                   bi.item_type, s.name as service_name, bi.total_price, b.created_at
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            JOIN customers c ON b.customer_id = c.id
            LEFT JOIN services s ON bi.item_id = s.id
            WHERE bi.staff_id = ? AND DATE(b.created_at, 'localtime') = ?
            ORDER BY bi.id DESC;
            """,
            (staff_id, today_str)
        )

        # Today's booked appointments assigned to this staff
        today_apts = fetch_all(
            """
            SELECT a.id, a.appointment_code, c.full_name as client_name, c.phone as client_phone,
                   s.name as service_name, a.start_time, ch.chair_name, a.status
            FROM appointments a
            JOIN customers c ON a.customer_id = c.id
            JOIN services s ON a.service_id = s.id
            LEFT JOIN chairs ch ON a.chair_id = ch.id
            WHERE a.staff_id = ? AND a.appointment_date = ?
            ORDER BY a.start_time ASC;
            """,
            (staff_id, today_str)
        )

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("##### 📌 Scheduled Bookings Today")
            if not today_apts:
                st.info("No advance appointments scheduled for today.")
            else:
                for apt in today_apts:
                    st.markdown(
                        f"""
                        <div style="background:#FFF; border:1.5px solid #FCE4EC; border-left:4px solid #C2185B; border-radius:6px; padding:12px 14px; margin-bottom:8px; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                            <div style="display:flex; justify-content:space-between;">
                                <b>{apt['client_name']} ({apt['client_phone']})</b>
                                <span style="color:#C2185B; font-weight:700;">{apt.get('start_time', 'N/A')}</span>
                            </div>
                            <div style="font-size:12px; color:#555; margin:3px 0;">Service: <b>{apt['service_name']}</b> | Station: <b>{apt.get('chair_name') or 'General'}</b></div>
                            <div style="font-size:11px; color:#777;">Booking Ref: <code>{apt['appointment_code']}</code> | Status: <b>{apt['status']}</b></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        with col_r2:
            st.markdown("##### 💆‍♀️ Completed / Billed Services Today")
            if not today_services:
                st.info("No billed services processed yet today.")
            else:
                for srv in today_services:
                    comm_earned = (float(srv["total_price"]) * comm_rate) / 100.0
                    st.markdown(
                        f"""
                        <div style="background:#FFF; border:1.5px solid #EBEBEB; border-left:4px solid #2E7D32; border-radius:6px; padding:12px 14px; margin-bottom:8px; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                            <div style="display:flex; justify-content:space-between;">
                                <b>{srv['service_name']}</b>
                                <span style="color:#2E7D32; font-weight:700;">+₹{comm_earned:,.2f} Comm</span>
                            </div>
                            <div style="font-size:12px; color:#555; margin:2px 0;">Client: <b>{srv['client_name']}</b> | Bill: <code>{srv['bill_number']}</code></div>
                            <div style="font-size:11px; color:#777;">Billed Value: ₹{srv['total_price']:,.2f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # ---------------- 2. LIVE EARNINGS & COMMISSION ----------------
    elif menu == "Live Earnings & Commission":
        st.markdown("#### Specialist Earnings & Commission Breakdown")
        
        m_ref = st.date_input("Select Month Reference", value=date.today(), key="staff_comm_month")
        month_str = m_ref.strftime('%Y-%m')

        month_billed = fetch_all(
            """
            SELECT bi.total_price, b.created_at, s.name as service_name, c.full_name as client_name
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            JOIN customers c ON b.customer_id = c.id
            LEFT JOIN services s ON bi.item_id = s.id
            WHERE bi.staff_id = ? AND strftime('%Y-%m', b.created_at, 'localtime') = ?;
            """,
            (staff_id, month_str)
        )

        total_service_sales = sum(float(it["total_price"]) for it in month_billed)
        total_commissions = (total_service_sales * comm_rate) / 100.0
        projected_payout = base_salary + total_commissions

        kpi_earn = (
            "<div class='kpi-row-container'>"
            f"<div class='kpi-single-card'><div class='card-title'>Base Fixed Salary</div><div class='card-value'>₹{base_salary:,.2f}</div></div>"
            f"<div class='kpi-single-card'><div class='card-title'>Commission Rate</div><div class='card-value'>{comm_rate:.0f}%</div></div>"
            f"<div class='kpi-single-card'><div class='card-title'>Month Commission</div><div class='card-value'>₹{total_commissions:,.2f}</div></div>"
            f"<div class='kpi-single-card'><div class='card-title'>Total Estimated Payout</div><div class='card-value'>₹{projected_payout:,.2f}</div></div>"
            "</div>"
        )
        st.markdown(kpi_earn, unsafe_allow_html=True)

        st.divider()
        st.markdown("##### Detailed Billed Items for Selected Month")
        if month_billed:
            report_rows = []
            for it in month_billed:
                it_comm = (float(it["total_price"]) * comm_rate) / 100.0
                report_rows.append({
                    "Date & Time": it["created_at"],
                    "Client": it["client_name"],
                    "Service": it["service_name"] or "Product Sale",
                    "Service Price (₹)": f"₹{it['total_price']:,.2f}",
                    "My Commission (₹)": f"₹{it_comm:,.2f}"
                })
            st.dataframe(pd.DataFrame(report_rows), use_container_width=True)
        else:
            st.info("No service transactions registered for this month.")

    # ---------------- 3. ATTENDANCE & PUNCH CLOCK ----------------
    elif menu == "Attendance & Punch Clock":
        st.markdown("#### Daily Digital Punch Attendance")
        today_str = str(date.today())

        att_row = fetch_one(
            "SELECT * FROM attendance WHERE staff_id = ? AND attendance_date = ?;",
            (staff_id, today_str)
        )

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"**Date:** `{today_str}`")
            status_curr = att_row["status"] if att_row else "Not Marked"
            st.markdown(f"**Current Attendance Status:** `{status_curr}`")
            if att_row and att_row.get("check_in"):
                st.markdown(f"**Punch-In Time:** `{att_row['check_in']}`")
            if att_row and att_row.get("check_out"):
                st.markdown(f"**Punch-Out Time:** `{att_row['check_out']}`")

        with col_p2:
            now_time = datetime.now().strftime("%H:%M:%S")
            if not att_row:
                if st.button("🟢 PUNCH IN (START SHIFT)", use_container_width=True, key="btn_punch_in"):
                    execute_query(
                        """
                        INSERT INTO attendance (staff_id, attendance_date, check_in, status)
                        VALUES (?, ?, ?, 'Present');
                        """,
                        (staff_id, today_str, now_time)
                    )
                    st.success(f"Punched in successfully at {now_time}!")
                    st.rerun()
            elif att_row and not att_row.get("check_out"):
                if st.button("🔴 PUNCH OUT (END SHIFT)", use_container_width=True, key="btn_punch_out"):
                    execute_query(
                        "UPDATE attendance SET check_out = ? WHERE id = ?;",
                        (now_time, att_row["id"])
                    )
                    st.success(f"Punched out successfully at {now_time}!")
                    st.rerun()
            else:
                st.info("Shift completed for today. Thank you!")

        st.divider()
        st.markdown("##### Past Attendance History")
        past_att = fetch_all(
            "SELECT attendance_date, check_in, check_out, status FROM attendance WHERE staff_id = ? ORDER BY attendance_date DESC LIMIT 30;",
            (staff_id,)
        )
        if past_att:
            st.dataframe(pd.DataFrame(past_att), use_container_width=True)

    # ---------------- 4. CLIENT CONSULTATION NOTES ----------------
    elif menu == "Client Consultation Notes":
        st.markdown("#### Specialist Consultation & Treatment Records")
        
        all_clients = fetch_all("SELECT id, customer_code, full_name, phone FROM customers ORDER BY full_name ASC;")
        if not all_clients:
            st.info("No clients registered.")
        else:
            client_dict = {f"{c['full_name']} ({c['phone']}) - [{c['customer_code']}]": c for c in all_clients}
            chosen_c_label = st.selectbox("Select Client", list(client_dict.keys()), key="consult_cust_select")
            chosen_c = client_dict[chosen_c_label]

            with st.form("form_consult_note"):
                st.markdown(f"**Add Formula / Consultation Note for:** `{chosen_c['full_name']}`")
                note_category = st.selectbox("Treatment Category", ["Hair Color Formula", "Skin & Facial Sensitivity", "Scalp Condition", "General Preferences"])
                note_text = st.text_area("Detailed Formulation / Observation Notes *", placeholder="e.g. Majirel 3 (40g) + 20 Vol (60g). Sensitive skin, avoid eucalyptus masks.")
                submit_note = st.form_submit_button("SAVE CONSULTATION NOTE", use_container_width=True)

                if submit_note:
                    if note_text.strip():
                        formatted_note = f"[{note_category}] {note_text.strip()} (Logged By: {staff_name})"
                        execute_query(
                            "INSERT INTO customer_notes (customer_id, staff_id, note) VALUES (?, ?, ?);",
                            (chosen_c["id"], staff_id, formatted_note)
                        )
                        st.success("Consultation note recorded!")
                        st.rerun()
                    else:
                        st.error("Please enter observation details.")

            st.divider()
            st.markdown("##### Previous Treatment Notes for this Client")
            prev_notes = fetch_all(
                """
                SELECT cn.note, cn.created_at, s.full_name as stylist_name
                FROM customer_notes cn
                JOIN staff s ON cn.staff_id = s.id
                WHERE cn.customer_id = ?
                ORDER BY cn.id DESC;
                """,
                (chosen_c["id"],)
            )
            if prev_notes:
                for n in prev_notes:
                    st.markdown(
                        f"""
                        <div style="background:#FFF9FA; border:1px solid #F8BBD0; border-radius:6px; padding:10px 14px; margin-bottom:6px;">
                            <div style="font-size:13px; color:#111;">{n['note']}</div>
                            <div style="font-size:11px; color:#777; margin-top:3px;">Logged by: <b>{n['stylist_name']}</b> | {n['created_at']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No prior treatment notes logged for this client.")

    # ---------------- 5. MY REVIEWS & PERFORMANCE ----------------
    elif menu == "My Performance & Reviews":
        st.markdown("#### Client Feedback & Performance Scorecard")
        reviews = fetch_all(
            """
            SELECT r.rating, r.review_text, r.created_at, c.full_name as client_name
            FROM reviews r
            JOIN customers c ON r.customer_id = c.id
            WHERE r.staff_id = ?
            ORDER BY r.id DESC;
            """,
            (staff_id,)
        )

        if reviews:
            avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
            st.markdown(
                f"""
                <div class="kpi-single-card" style="max-width:320px; margin-bottom:15px;">
                    <div class="card-title">Average Rating Score</div>
                    <div class="card-value">⭐ {avg_rating:.1f} / 5.0 ({len(reviews)} Reviews)</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            for r in reviews:
                st.markdown(
                    f"""
                    <div style="background:#FFF; border:1.5px solid #EEE; border-radius:6px; padding:12px 16px; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                        <div style="display:flex; justify-content:space-between;">
                            <b>{r['client_name']}</b>
                            <span style="color:#C2185B; font-weight:bold;">{'★' * r['rating']}{'☆' * (5 - r['rating'])}</span>
                        </div>
                        <p style="margin:4px 0 2px 0; font-size:13px; color:#333;">"{r['review_text']}"</p>
                        <span style="font-size:11px; color:#888;">{r['created_at']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No customer reviews received yet.")

    # ---------------- 6. LEAVE APPLICATION ----------------
    elif menu == "Leave Application":
        st.markdown("#### Request Leave / Shift Off")
        with st.form("form_leave_request"):
            c1, c2 = st.columns(2)
            with c1:
                leave_start = st.date_input("Start Date", value=date.today(), key="in_leave_start")
                leave_type = st.selectbox("Leave Type", ["Casual Leave", "Sick Leave", "Paid Time Off", "Emergency"], key="in_leave_type")
            with c2:
                leave_end = st.date_input("End Date", value=date.today(), key="in_leave_end")
                leave_reason = st.text_input("Reason *", placeholder="e.g. Family Function / Medical", key="in_leave_reason")

            submit_leave = st.form_submit_button("SUBMIT LEAVE APPLICATION", use_container_width=True)
            if submit_leave:
                if leave_reason.strip():
                    execute_query(
                        """
                        INSERT INTO staff_leaves (staff_id, leave_type, start_date, end_date, reason, status)
                        VALUES (?, ?, ?, ?, ?, 'Pending');
                        """,
                        (staff_id, leave_type, str(leave_start), str(leave_end), leave_reason.strip())
                    )
                    st.success("Leave application submitted to salon administrator!")
                    st.rerun()
                else:
                    st.error("Please provide a reason for leave.")

        st.divider()
        st.markdown("##### My Leave Application History")
        my_leaves = fetch_all(
            "SELECT leave_type, start_date, end_date, reason, status, created_at FROM staff_leaves WHERE staff_id = ? ORDER BY id DESC;",
            (staff_id,)
        )
        if my_leaves:
            st.dataframe(pd.DataFrame(my_leaves), use_container_width=True)
        else:
            st.info("No past leave applications.")