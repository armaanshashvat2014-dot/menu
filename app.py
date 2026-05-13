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
# WORKER PASSWORD
# ======================================================

WORKER_PASSWORD = "PNBWORKER123"

# ======================================================
# TIME SLOTS
# ======================================================

time_slots = [
    "10:00 AM",
    "11:00 AM",
    "12:00 PM",
    "1:00 PM",
    "2:00 PM",
    "3:00 PM",
    "4:00 PM",
    "5:00 PM",
    "6:00 PM",
    "7:00 PM",
    "8:00 PM",
    "9:00 PM"
]

# ======================================================
# AI TASK GENERATOR
# ======================================================

def generate_ai_tasks(service, customer_name):

    prompt = f"""
    Customer booked: {service}
    Customer name: {customer_name}

    In ONE SHORT PARAGRAPH ONLY:
    - explain the service
    - give quick preparation advice
    - mention duration briefly

    Keep it luxurious, concise, and friendly.
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

    "Makeup":[
        ("Light Makeup","","₹2500"),
        ("Party Makeup","","₹3500"),
        ("Bridal Makeup","","₹7500"),
        ("Reception Makeup","","₹5000"),
    ],

    "Pedicure":[
        ("Basic Pedicure","","₹500"),
        ("Spa Pedicure","","₹600"),
        ("Crystal Pedicure","","₹900"),
        ("Bomb Pedicure","","₹2000"),
    ],

    "Hair Treatments":[
        ("Keratin Treatment","","₹5000"),
        ("Express Keratin Treatment","","₹4500"),
        ("Deep Conditioning","","₹3000"),
        ("Smoothening","","₹4000"),
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

.slot-box{
    padding:10px;
    border-radius:10px;
    background:#232323;
    margin-bottom:10px;
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

mode = st.sidebar.radio(
    "Select Mode",
    [
        "Customer",
        "Worker Login"
    ]
)

# ======================================================
# CUSTOMER
# ======================================================

if mode == "Customer":

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

                    booking_date = st.date_input(
                        "Select Booking Date",
                        key=f"date_{service}_{i}"
                    )

                    time_slot = st.selectbox(
                        "Choose Time Slot",
                        time_slots,
                        key=f"time_{service}_{i}"
                    )

                    slot_docs = db.collection("bookings") \
                        .where(
                            "booking_date",
                            "==",
                            str(booking_date)
                        ) \
                        .where(
                            "time_slot",
                            "==",
                            time_slot
                        ) \
                        .stream()

                    slot_count = len(list(slot_docs))

                    remaining = 4 - slot_count

                    if remaining <= 0:

                        st.error(
                            "This slot is fully occupied."
                        )

                    else:

                        st.success(
                            f"{remaining} slots remaining"
                        )

                    if st.button(
                        "Confirm Booking",
                        key=f"btn_{service}_{i}"
                    ):

                        if remaining <= 0:

                            st.error(
                                "Cannot book occupied slot."
                            )

                        elif customer_name and phone:

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

                                    "booking_date":
                                        str(booking_date),

                                    "time_slot":
                                        time_slot,

                                    "created_at":
                                        str(datetime.now())

                                })

                                st.success(
                                    "Booking Confirmed!"
                                )

                                st.info(ai_tasks)

                            except Exception as e:

                                st.error(
                                    f"Error: {e}"
                                )

                        else:

                            st.error(
                                "Please fill all fields"
                            )

# ======================================================
# WORKER LOGIN
# ======================================================

elif mode == "Worker Login":

    st.title("🔒 Worker Access")

    password = st.text_input(
        "Enter Worker Password",
        type="password"
    )

    if password == WORKER_PASSWORD:

        worker_role = st.selectbox(
            "Select Your Role",
            [
                "Massage Expert",
                "Makeup Artist",
                "Hair Stylist",
                "Nail Technician",
                "Salon Staff"
            ]
        )

        st.success("Access Granted")

        bookings_ref = db.collection(
            "bookings"
        ).stream()

        bookings = []

        for doc in bookings_ref:

            data = doc.to_dict()
            data["doc_id"] = doc.id

            bookings.append(data)

        for booking in bookings:

            if (
                booking.get("assigned_role")
                != worker_role
            ):
                continue

            if booking.get("status") == "Completed":
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
                <b>Date:</b>
                {booking.get('booking_date')}
                </p>

                <p>
                <b>Time:</b>
                {booking.get('time_slot')}
                </p>

                <p>
                <b>Status:</b>
                {booking.get('status')}
                </p>

            </div>
            """, unsafe_allow_html=True)

            st.info(
                booking.get("ai_tasks")
            )

            col1, col2 = st.columns(2)

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
                        "status":
                            "Awaiting Customer Confirmation"
                    })

                    st.rerun()

        st.divider()

        st.title("✅ Customer Confirmations")

        customer_name_confirm = st.text_input(
            "Customer Name"
        )

        customer_phone_confirm = st.text_input(
            "Customer Phone"
        )

        if st.button("Load My Bookings"):

            confirm_docs = db.collection(
                "bookings"
            ).stream()

            for doc in confirm_docs:

                booking = doc.to_dict()

                if (
                    booking.get("customer_name")
                    == customer_name_confirm
                    and
                    booking.get("phone")
                    == customer_phone_confirm
                    and
                    booking.get("status")
                    ==
                    "Awaiting Customer Confirmation"
                ):

                    st.success(
                        f"""
                        {booking.get('service')}
                        completed successfully?
                        """
                    )

                    if st.button(
                        f"YES Complete "
                        f"{doc.id}"
                    ):

                        booking["status"] = "Completed"

                        db.collection(
                            "completed_bookings"
                        ).add(booking)

                        db.collection(
                            "bookings"
                        ).document(
                            doc.id
                        ).delete()

                        st.success(
                            "Booking Completed!"
                        )

                        st.rerun()

    elif password != "":

        st.error("Wrong Password")

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
