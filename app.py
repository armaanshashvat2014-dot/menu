# streamlit_app.py

```python
import streamlit as st
import sqlite3
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="PNB Luxury Salon & Spa",
    page_icon="💎",
    layout="wide"
)

# =========================
# FIREBASE DATABASE
# =========================

import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:

    firebase_credentials = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace('\n', '
'),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }

    cred = credentials.Certificate(firebase_credentials)

    firebase_admin.initialize_app(cred)


db = firestore.client()

# =========================
# AI CONFIG
# =========================

AI_API_URL = st.secrets["AI_API_URL"]
AI_API_KEY = st.secrets["AI_API_KEY"]

# =========================
# SERVICES
# =========================

services = {

    "Massage & Spa": [
        ("Ayurvedic Massage", "45 mins", 1500),
        ("Ayurvedic Massage", "60 mins", 1800),
        ("Aroma Therapy", "45 mins", 2000),
        ("Aroma Therapy", "60 mins", 2500),
        ("Deep Tissue Massage", "60 mins", 3000),
        ("Body Polish", "Luxury", 3500),
    ],

    "Piercing & Beauty": [
        ("Wart Removal", "Quick", 200),
        ("Nose Piercing", "Quick", 600),
        ("Single Ear Piercing", "Quick", 800),
        ("Double Ear Piercing", "Quick", 1200),
        ("Mehandi", "Standard", 500),
        ("Fashion Plait", "Standard", 500),
        ("Flower Plait Fixing", "Premium", 800),
    ],

    "Makeup": [
        ("Light Makeup", "Basic", 2500),
        ("Party Makeup", "Party", 3500),
        ("Bridal Trial Makeup", "Trial", 2500),
        ("Bridal Makeup", "Premium", 7500),
        ("Reception Makeup", "Reception", 5000),
    ],

    "Pedicure": [
        ("Basic Pedicure", "Basic", 500),
        ("Spa Pedicure", "Spa", 600),
        ("Crystal Pedicure", "Luxury", 900),
        ("Aromatic Pedicure", "Luxury", 1200),
        ("Heel Peel Pedicure", "Premium", 1300),
        ("PNB Signature Pedicure", "Signature", 1600),
        ("Bomb Pedicure", "Luxury", 2000),
    ],

    "Manicure & Nails": [
        ("Basic Manicure", "Basic", 300),
        ("Spa Manicure", "Spa", 500),
        ("Crystal Spa Manicure", "Luxury", 750),
        ("Bomb Manicure", "Premium", 1800),
        ("French Polish", "Luxury", 250),
        ("Gel Polish", "Premium", 500),
    ],

    "Hair Treatments": [
        ("Keratin Treatment", "Premium", 5000),
        ("Express Keratin Treatment", "Express", 4500),
        ("Deep Conditioning", "Luxury", 3000),
        ("Hair Scrub", "Basic", 800),
        ("Smoothening", "Premium", 4000),
        ("Rebonding", "Premium", 4500),
        ("Straightening", "Premium", 4500),
    ],

    "Haircuts": [
        ("Haircut Below 8 Years", "Kids", 200),
        ("Basic Haircut", "Basic", 250),
        ("Split Ends Haircut", "Advanced", 400),
        ("Advanced Haircut", "Premium", 500),
    ],

    "Face Packs": [
        ("Young Face Pack", "Basic", 300),
        ("White Face Pack", "Basic", 300),
        ("Charcoal Pack", "Luxury", 350),
        ("Gold Facial", "Premium", 800),
    ]
}

# =========================
# CUSTOM CSS
# =========================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(135deg,#0f0f0f,#171717);
        color:white;
    }

    h1,h2,h3 {
        color:#d4af37 !important;
    }

    .service-card {
        background:#1b1b1b;
        padding:25px;
        border-radius:22px;
        border:1px solid rgba(255,255,255,0.08);
        margin-bottom:20px;
        transition:0.3s;
        box-shadow:0 10px 30px rgba(0,0,0,0.3);
    }

    .service-card:hover {
        transform:translateY(-4px);
        box-shadow:0 15px 35px rgba(212,175,55,0.2);
    }

    .price {
        font-size:24px;
        color:#d4af37;
        font-weight:bold;
    }

    .duration {
        color:#aaa;
        margin-top:5px;
    }

    .dashboard-card {
        background:#1a1a1a;
        padding:20px;
        border-radius:18px;
        margin-bottom:20px;
        border:1px solid rgba(255,255,255,0.08);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# AI TASK GENERATOR
# =========================

def generate_ai_tasks(service, customer_name):

    prompt = f"""
    Customer booked: {service}
    Customer Name: {customer_name}

    Generate:
    - Best worker role
    - Priority
    - Estimated time
    - Preparation tasks

    Return valid JSON only.
    """

    try:

        response = requests.post(
            AI_API_URL,
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt
            }
        )

        data = response.json()

        if "response" in data:
            return data["response"]

        if "result" in data:
            return data["result"]

        return json.dumps(data, indent=2)

    except Exception as e:

        return f"AI generation failed: {e}"

# =========================
# ROLE MATCHING
# =========================

def get_role(service):

    if "Massage" in service:
        return "Massage Expert"

    if "Makeup" in service:
        return "Makeup Artist"

    if "Hair" in service or "Keratin" in service:
        return "Hair Stylist"

    if "Pedicure" in service or "Manicure" in service:
        return "Nail Technician"

    return "Salon Staff"

# =========================
# HEADER
# =========================

st.markdown(
    """
    <div style='text-align:center;padding:20px;'>
        <h1 style='font-size:60px;'>💎 PNB Luxury Salon & Spa</h1>
        <p style='color:#bbb;font-size:20px;'>Beauty • Wellness • Luxury</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# SIDEBAR
# =========================

page = st.sidebar.selectbox(
    "Choose Section",
    [
        "Salon Menu",
        "Worker Dashboard",
        "Analytics"
    ]
)

# =========================
# MENU PAGE
# =========================

if page == "Salon Menu":

    st.title("Luxury Services")

    for category, items in services.items():

        st.subheader(category)

        cols = st.columns(3)

        for i, item in enumerate(items):

            service, duration, price = item

            with cols[i % 3]:

                st.markdown(
                    f"""
                    <div class='service-card'>
                        <h3>{service}</h3>
                        <div class='duration'>{duration}</div>
                        <div class='price'>₹{price}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.expander(f"Book {service}"):

                    customer_name = st.text_input(
                        "Customer Name",
                        key=f"name_{service}_{i}"
                    )

                    phone = st.text_input(
                        "Phone Number",
                        key=f"phone_{service}_{i}"
                    )

                    if st.button(
                        f"Confirm Booking - {service}",
                        key=f"btn_{service}_{i}"
                    ):

                        if customer_name and phone:

                            role = get_role(service)

                            with st.spinner("AI assigning worker tasks..."):
                                ai_tasks = generate_ai_tasks(
                                    service,
                                    customer_name
                                )

                            db.collection("bookings").add({
                                    "customer_name": customer_name,
                                    "phone": phone,
                                    "service": service,
                                    "category": category,
                                    "assigned_role": role,
                                    "ai_tasks": ai_tasks,
                                    "status": "Pending",
                                    "created_at": str(datetime.now())
                                })

                            st.success("Booking Confirmed Successfully!")

                            st.info(f"Assigned Role: {role}")

                            st.code(ai_tasks)

                        else:
                            st.error("Please fill all fields")

# =========================
# WORKER DASHBOARD
# =========================

elif page == "Worker Dashboard":

    st.title("👩‍💼 Worker Dashboard")

    search = st.text_input("Search Customer or Service")

    bookings_ref = db.collection("bookings").stream()

    bookings = []

    for doc in bookings_ref:
        data = doc.to_dict()
        data["doc_id"] = doc.id
        bookings.append(data)

    filtered = []

    for booking in bookings:

        if (
            search.lower() in str(booking).lower()
            or search == ""
        ):
            filtered.append(booking)

    for booking in filtered:

        booking_id = booking.get("doc_id")
        customer_name = booking.get("customer_name")
        phone = booking.get("phone")
        service = booking.get("service")
        category = booking.get("category")
        role = booking.get("assigned_role")
        ai_tasks = booking.get("ai_tasks")
        status = booking.get("status")
        created_at = booking.get("created_at")

        st.markdown(
            f"""
            <div class='dashboard-card'>
                <h2>{service}</h2>
                <p><b>Customer:</b> {customer_name}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Category:</b> {category}</p>
                <p><b>Assigned Role:</b> {role}</p>
                <p><b>Status:</b> {status}</p>
                <p><b>Created:</b> {created_at}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("🤖 AI Instructions")
        st.code(ai_tasks)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                f"Accept #{booking_id}",
                key=f"accept_{booking_id}"
            ):

                db.collection("bookings").document(booking_id).update({
                    "status":"Accepted"
                })

                st.rerun()

        with col2:
            if st.button(
                f"Complete #{booking_id}",
                key=f"complete_{booking_id}"
            ):

                db.collection("bookings").document(booking_id).update({
                    "status":"Completed"
                })

                st.rerun()

        with col3:
            if st.button(
                f"Delete #{booking_id}",
                key=f"delete_{booking_id}"
            ):

                db.collection("bookings").document(booking_id).delete()

                st.rerun()

        st.divider()

# =========================
# ANALYTICS
# =========================

elif page == "Analytics":

    st.title("📊 Salon Analytics")

    all_docs = list(db.collection("bookings").stream())

    total_bookings = len(all_docs)

    completed = len([
        d for d in all_docs
        if d.to_dict().get("status") == "Completed"
    ])

    pending = len([
        d for d in all_docs
        if d.to_dict().get("status") == "Pending"
    ])

    accepted = len([
        d for d in all_docs
        if d.to_dict().get("status") == "Accepted"
    ])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Bookings", total_bookings)
    col2.metric("Pending", pending)
    col3.metric("Accepted", accepted)
    col4.metric("Completed", completed)

    st.subheader("Recent Bookings")

    recent_docs = db.collection("bookings").stream()

    recent = []

    for d in recent_docs:
        data = d.to_dict()
        recent.append((
            data.get("customer_name"),
            data.get("service"),
            data.get("status")
        ))

    for r in recent:
        st.write(r)
