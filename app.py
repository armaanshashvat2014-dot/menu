import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from datetime import datetime

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="PNB Luxury Salon & Spa",
    page_icon="💎",
    layout="wide"
)

# ======================================================
# FIREBASE
# ======================================================

if not firebase_admin._apps:

    firebase_dict = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url":
            st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url":
            st.secrets["client_x509_cert_url"]
    }

    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred)

db = firestore.client()

# ======================================================
# AI CONFIG
# ======================================================

AI_API_URL = st.secrets["AI_API_URL"]
AI_API_KEY = st.secrets["AI_API_KEY"]

# ======================================================
# AI TASK GENERATOR
# ======================================================

def generate_ai_tasks(service, customer_name):

    prompt = f"""
    Customer booked: {service}
    Customer Name: {customer_name}

    Generate:
    - worker role
    - preparation steps
    - estimated time
    - materials required

    Keep it professional.
    """

    try:

        response = requests.post(
            AI_API_URL,
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages":[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            }
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        if "response" in data:
            return data["response"]

        if "result" in data:
            return data["result"]

        return str(data)

    except Exception as e:

        return f"AI Error: {e}"

# ======================================================
# ROLE MATCHING
# ======================================================

def get_role(service):

    if "Massage" in service:
        return "Massage Expert"

    if "Makeup" in service:
        return "Makeup Artist"

    if (
        "Hair" in service
        or "Keratin" in service
        or "Smoothening" in service
        or "Straightening" in service
        or "Rebonding" in service
    ):
        return "Hair Stylist"

    if (
        "Pedicure" in service
        or "Manicure" in service
        or "Nail" in service
    ):
        return "Nail Technician"

    return "Salon Staff"

# ======================================================
# SERVICES
# ======================================================

services = {

    "Massage & Spa":[
        ("Ayurvedic Massage","45 mins","₹1500"),
        ("Ayurvedic Massage","60 mins","₹1800"),
        ("Aroma Therapy","45 mins","₹2000"),
        ("Aroma Therapy","60 mins","₹2500"),
        ("Deep Tissue Massage","60 mins","₹3000"),
        ("Body Polish","Luxury","₹3500"),
    ],

    "Piercing & Beauty":[
        ("Wart Removal","","₹200"),
        ("Nose Piercing","","₹600"),
        ("Single Ear Piercing","","₹800"),
        ("Double Ear Piercing","","₹1200"),
        ("Mehandi","","₹500"),
        ("Fashion Plait","","₹500"),
        ("Flower Plait Fixing","","₹800"),
    ],

    "Makeup":[
        ("Light Makeup","","₹2500"),
        ("Party Makeup","","₹3500"),
        ("Bridal Trial Makeup","","₹2500"),
        ("Bridal Makeup","","₹7500"),
        ("Reception Makeup","","₹5000"),
    ],

    "Pedicure":[
        ("Basic Pedicure","","₹500"),
        ("Spa Pedicure","","₹600"),
        ("Crystal Pedicure","","₹900"),
        ("Aromatic Pedicure","","₹1200"),
        ("Heel Peel Pedicure","","₹1300"),
        ("PNB Signature Pedicure","","₹1600"),
        ("Bomb Pedicure","","₹2000"),
    ],

    "Hair Treatments":[
        ("Keratin Treatment","","₹5000"),
        ("Express Keratin Treatment","","₹4500"),
        ("Deep Conditioning","","₹3000"),
        ("Hair Scrub","","₹800"),
        ("Smoothening","","₹4000"),
        ("Rebonding","","₹4500"),
        ("Straightening","","₹4500"),
    ]
}

# ======================================================
# CUSTOM CSS
# ======================================================

st.markdown("""
<style>

.stApp{
    background:linear-gradient(135deg,#0f0f0f,#181818);
    color:white;
}

h1,h2,h3{
    color:#d4af37 !important;
}

.service-card{
    background:#1b1b1b;
    padding:25px;
    border-radius:20px;
    margin-bottom:20px;
    border:1px solid rgba(255,255,255,0.08);
    box-shadow:0 10px 25px rgba(0,0,0,0.3);
}

.price{
    color:#d4af37;
    font-size:28px;
    font-weight:bold;
}

.duration{
    color:#aaa;
}

.dashboard-card{
    background:#1b1b1b;
    padding:25px;
    border-radius:20px;
    margin-bottom:20px;
    border:1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.markdown("""
<div style='text-align:center;padding:30px;'>

<h1 style='font-size:60px;'>
💎 PNB Luxury Salon & Spa
</h1>

<p style='color:#bbb;font-size:20px;'>
Beauty • Wellness • Luxury
</p>

</div>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR
# ======================================================

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Salon Menu",
        "Worker Dashboard",
        "Analytics"
    ]
)

# ======================================================
# MENU PAGE
# ======================================================

if page == "Salon Menu":

    st.title("Luxury Services")

    for category, items in services.items():

        st.subheader(category)

        cols = st.columns(3)

        for i, item in enumerate(items):

            service, duration, price = item

            with cols[i % 3]:

                st.markdown(f"""
                <div class='service-card'>
                    <h3>{service}</h3>
                    <div class='duration'>{duration}</div>
                    <div class='price'>{price}</div>
                </div>
                """, unsafe_allow_html=True)

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
                        f"Confirm Booking",
                        key=f"btn_{service}_{i}"
                    ):

                        if customer_name and phone:

                            try:

                                role = get_role(service)

                                ai_tasks = generate_ai_tasks(
                                    service,
                                    customer_name
                                )

                                db.collection("bookings").add({

                                    "customer_name":
                                        customer_name,

                                    "phone":
                                        phone,

                                    "service":
                                        service,

                                    "category":
                                        category,

                                    "assigned_role":
                                        role,

                                    "ai_tasks":
                                        ai_tasks,

                                    "status":
                                        "Pending",

                                    "created_at":
                                        str(datetime.now())

                                })

                                st.success(
                                    "Booking saved to Firebase!"
                                )

                                st.info(
                                    f"Assigned Role: {role}"
                                )

                                st.code(ai_tasks)

                            except Exception as e:

                                st.error(
                                    f"Firebase Error: {e}"
                                )

                        else:

                            st.error(
                                "Please fill all fields"
                            )

# ======================================================
# WORKER DASHBOARD
# ======================================================

elif page == "Worker Dashboard":

    st.title("👩‍💼 Worker Dashboard")

    search = st.text_input(
        "Search Customer or Service"
    )

    bookings_ref = db.collection(
        "bookings"
    ).stream()

    bookings = []

    for doc in bookings_ref:

        data = doc.to_dict()
        data["doc_id"] = doc.id

        bookings.append(data)

    for booking in bookings:

        booking_text = str(booking).lower()

        if (
            search.lower() not in booking_text
            and search != ""
        ):
            continue

        st.markdown(f"""
        <div class='dashboard-card'>

            <h2>{booking.get('service')}</h2>

            <p>
            <b>Customer:</b>
            {booking.get('customer_name')}
            </p>

            <p>
            <b>Phone:</b>
            {booking.get('phone')}
            </p>

            <p>
            <b>Role:</b>
            {booking.get('assigned_role')}
            </p>

            <p>
            <b>Status:</b>
            {booking.get('status')}
            </p>

        </div>
        """, unsafe_allow_html=True)

        st.subheader("🤖 AI Instructions")

        st.code(booking.get("ai_tasks"))

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                f"Accept #{booking.get('doc_id')}",
                key=f"a_{booking.get('doc_id')}"
            ):

                db.collection(
                    "bookings"
                ).document(
                    booking.get("doc_id")
                ).update({
                    "status":"Accepted"
                })

                st.rerun()

        with col2:

            if st.button(
                f"Complete #{booking.get('doc_id')}",
                key=f"c_{booking.get('doc_id')}"
            ):

                db.collection(
                    "bookings"
                ).document(
                    booking.get("doc_id")
                ).update({
                    "status":"Completed"
                })

                st.rerun()

        with col3:

            if st.button(
                f"Delete #{booking.get('doc_id')}",
                key=f"d_{booking.get('doc_id')}"
            ):

                db.collection(
                    "bookings"
                ).document(
                    booking.get("doc_id")
                ).delete()

                st.rerun()

        st.divider()

# ======================================================
# ANALYTICS
# ======================================================

elif page == "Analytics":

    st.title("📊 Salon Analytics")

    docs = list(
        db.collection("bookings").stream()
    )

    total = len(docs)

    pending = len([
        d for d in docs
        if d.to_dict().get("status") == "Pending"
    ])

    accepted = len([
        d for d in docs
        if d.to_dict().get("status") == "Accepted"
    ])

    completed = len([
        d for d in docs
        if d.to_dict().get("status") == "Completed"
    ])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", total)
    col2.metric("Pending", pending)
    col3.metric("Accepted", accepted)
    col4.metric("Completed", completed)

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<hr style='margin-top:50px;'>

<div style='
text-align:center;
padding:25px;
color:#888;
font-size:18px;
'>

Powered by
<span style='color:#d4af37;font-weight:bold;'>
MentorLoop EDU
</span>
and
<span style='color:#d4af37;font-weight:bold;'>
PNB
</span>

</div>
""", unsafe_allow_html=True)
