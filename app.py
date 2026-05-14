import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from datetime import datetime

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="SalonSmart",
    page_icon="✨",
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
# API
# ======================================================

AI_API_URL = st.secrets["AI_API_URL"]
AI_API_KEY = st.secrets["AI_API_KEY"]

# ======================================================
# PASSWORD
# ======================================================

WORKER_PASSWORD = "SALONSMART123"

# ======================================================
# SESSION STATE
# ======================================================

if "selected_service" not in st.session_state:
    st.session_state["selected_service"] = None

if "open_ai" not in st.session_state:
    st.session_state["open_ai"] = False

# ======================================================
# TIME SLOTS
# ======================================================

TIME_SLOTS = [
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
# SERVICES
# ======================================================

services = [

    {
        "name":"Ayurvedic Massage 45 mins",
        "duration":"45 mins",
        "price":1500,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Traditional Ayurvedic herbal massage.",
        "image":"https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },

    {
        "name":"Ayurvedic Massage 60 mins",
        "duration":"60 mins",
        "price":1800,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Extended Ayurvedic rejuvenation massage.",
        "image":"https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },

    {
        "name":"Aroma Therapy",
        "duration":"45 mins",
        "price":2000,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Luxury aroma therapy session.",
        "image":"https://images.unsplash.com/photo-1515377905703-c4788e51af15"
    },

    {
        "name":"Deep Tissue Massage",
        "duration":"60 mins",
        "price":3000,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Deep muscle recovery massage.",
        "image":"https://images.unsplash.com/photo-1519823551278-64ac92734fb1"
    },

    {
        "name":"Bridal Makeup",
        "duration":"120 mins",
        "price":7500,
        "role":"Makeup Artist",
        "category":"Makeup",
        "description":"Luxury bridal makeover package.",
        "image":"https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },

    {
        "name":"Party Makeup",
        "duration":"60 mins",
        "price":3500,
        "role":"Makeup Artist",
        "category":"Makeup",
        "description":"Elegant glam party makeup.",
        "image":"https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"
    },

    {
        "name":"Keratin Treatment",
        "duration":"2 Hours",
        "price":5000,
        "role":"Hair Stylist",
        "category":"Hair",
        "description":"Premium keratin treatment.",
        "image":"https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"
    },

    {
        "name":"Bomb Pedicure",
        "duration":"90 mins",
        "price":2000,
        "role":"Nail Technician",
        "category":"Nails",
        "description":"Luxury bomb pedicure.",
        "image":"https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    }

]

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>

.stApp{
    background:linear-gradient(135deg,#0f0f0f,#1b1b1b);
    color:white;
}

.service-card{
    background:#1e1e1e;
    padding:20px;
    border-radius:20px;
    border:1px solid rgba(255,255,255,0.08);
    margin-bottom:20px;
}

.price{
    color:#d4af37;
    font-size:24px;
    font-weight:bold;
}

.ai-circle button{
    border-radius:50% !important;
    height:60px !important;
    width:60px !important;
    font-size:28px !important;
    background:#d4af37 !important;
    color:black !important;
    border:none !important;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.markdown("""

<div style='text-align:center;padding:20px;'>

<h1 style='font-size:60px;color:#d4af37;'>
✨ SalonSmart
</h1>

<p style='color:#bbb;font-size:20px;'>
AI Powered Luxury Salon Platform
</p>

</div>

""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR
# ======================================================

mode = st.sidebar.radio(
    "Choose",
    [
        "Customer",
        "My Bookings",
        "Worker Login"
    ]
)

# ======================================================
# CUSTOMER
# ======================================================

if mode == "Customer":

    st.title("Luxury Services")

    # ==================================================
    # SEARCH + AI BUTTON
    # ==================================================

    col1, col2 = st.columns([10,1])

    with col1:

        search = st.text_input(
            "Search Services"
        )

    with col2:

        st.markdown(
            "<div class='ai-circle'>",
            unsafe_allow_html=True
        )

        if st.button("✨"):

            st.session_state[
                "selected_service"
            ] = None

            st.session_state[
                "open_ai"
            ] = True

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # ==================================================
    # FILTER
    # ==================================================

    categories = sorted(
        list(
            set(
                [
                    s["category"]
                    for s in services
                ]
            )
        )
    )

    category = st.selectbox(
        "Filter Category",
        ["All"] + categories
    )

    # ==================================================
    # SERVICES
    # ==================================================

    filtered = []

    for s in services:

        if (
            category != "All"
            and
            s["category"] != category
        ):
            continue

        if (
            search.lower()
            not in s["name"].lower()
        ):
            continue

        filtered.append(s)

    cols = st.columns(3)

    for i, service in enumerate(filtered):

        with cols[i % 3]:

            st.markdown(
                "<div class='service-card'>",
                unsafe_allow_html=True
            )

            st.image(service["image"])

            st.markdown(
                f"### {service['name']}"
            )

            st.write(
                service["description"]
            )

            st.write(
                f"⏱ {service['duration']}"
            )

            st.markdown(
                f"<div class='price'>₹{service['price']}</div>",
                unsafe_allow_html=True
            )

            if st.button(
                f"Open {service['name']}",
                key=f"open_{i}"
            ):

                st.session_state[
                    "open_ai"
                ] = False

                st.session_state[
                    "selected_service"
                ] = service

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

    # ==================================================
    # SERVICE POPUP
    # ==================================================

    if st.session_state[
        "selected_service"
    ] is not None:

        selected = st.session_state[
            "selected_service"
        ]

        @st.dialog(selected["name"])

        def service_popup():

            st.image(
                selected["image"]
            )

            st.write(
                selected["description"]
            )

            st.write(
                f"⏱ {selected['duration']}"
            )

            st.write(
                f"💰 ₹{selected['price']}"
            )

            booking_date = st.date_input(
                "Booking Date"
            )

            time_slot = st.selectbox(
                "Time Slot",
                TIME_SLOTS
            )

            customer_name = st.text_input(
                "Customer Name"
            )

            customer_phone = st.text_input(
                "Phone Number"
            )

            if st.button(
                "Confirm Booking"
            ):

                slot_docs = db.collection(
                    "bookings"
                ).where(
                    "booking_date",
                    "==",
                    str(booking_date)
                ).where(
                    "time_slot",
                    "==",
                    time_slot
                ).stream()

                slot_count = len(
                    list(slot_docs)
                )

                if slot_count >= 4:

                    st.error(
                        "Slot occupied."
                    )

                else:

                    try:

                        response = requests.post(

                            AI_API_URL,

                            headers={
                                "Authorization":
                                f"Bearer {AI_API_KEY}",

                                "Content-Type":
                                "application/json"
                            },

                            json={

                                "messages":[
                                    {
                                        "role":"user",
                                        "content":
                                        f"Explain {selected['name']} briefly."
                                    }
                                ],

                                "generateImage": True
                            }
                        )

                        db.collection(
                            "bookings"
                        ).add({

                            "customer_name":
                            customer_name,

                            "phone":
                            customer_phone,

                            "service":
                            selected["name"],

                            "booking_date":
                            str(booking_date),

                            "time_slot":
                            time_slot,

                            "status":
                            "Pending",

                            "assigned_role":
                            selected["role"],

                            "created_at":
                            str(datetime.now())
                        })

                        st.success(
                            "Booking confirmed!"
                        )

                        st.write(
                            response.json()
                        )

                    except Exception as e:

                        st.error(str(e))

            if st.button(
                "Close"
            ):

                st.session_state[
                    "selected_service"
                ] = None

                st.rerun()

        service_popup()

    # ==================================================
    # AI POPUP
    # ==================================================

    if st.session_state["open_ai"]:

        @st.dialog("✨ SalonSmart AI")

        def ai_popup():

            st.write(
                "Ask about beauty, hair, makeup or skincare."
            )

            user_question = st.text_input(
                "Your Question"
            )

            if st.button(
                "Ask AI"
            ):

                if user_question.strip() != "":

                    try:

                        response = requests.post(

                            AI_API_URL,

                            headers={

                                "Authorization":
                                f"Bearer {AI_API_KEY}",

                                "Content-Type":
                                "application/json"
                            },

                            json={

                                "messages":[
                                    {
                                        "role":"user",
                                        "content":
                                        user_question
                                    }
                                ]
                            }
                        )

                        st.success(
                            "SalonSmart AI"
                        )

                        st.write(
                            response.json()
                        )

                    except Exception as e:

                        st.error(str(e))

            if st.button(
                "Close AI"
            ):

                st.session_state[
                    "open_ai"
                ] = False

                st.rerun()

        ai_popup()

# ======================================================
# MY BOOKINGS
# ======================================================

elif mode == "My Bookings":

    st.title("📅 My Bookings")

    phone = st.text_input(
        "Phone Number"
    )

    if st.button(
        "Load Bookings"
    ):

        docs = db.collection(
            "bookings"
        ).stream()

        found = False

        for doc in docs:

            booking = doc.to_dict()

            if booking.get("phone") == phone:

                found = True

                st.subheader(
                    booking.get("service")
                )

                st.write(
                    booking.get(
                        "booking_date"
                    )
                )

                st.write(
                    booking.get(
                        "time_slot"
                    )
                )

                st.write(
                    booking.get(
                        "status"
                    )
                )

                if st.button(
                    f"Cancel {doc.id}",
                    key=f"cancel_{doc.id}"
                ):

                    db.collection(
                        "bookings"
                    ).document(
                        doc.id
                    ).delete()

                    st.success(
                        "Booking cancelled."
                    )

                    st.rerun()

        if not found:

            st.warning(
                "No bookings found."
            )

# ======================================================
# WORKER LOGIN
# ======================================================

elif mode == "Worker Login":

    st.title(
        "🔒 Worker Dashboard"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if password == WORKER_PASSWORD:

        role = st.selectbox(
            "Select Role",
            [
                "Massage Expert",
                "Makeup Artist",
                "Hair Stylist",
                "Nail Technician"
            ]
        )

        docs = db.collection(
            "bookings"
        ).stream()

        for doc in docs:

            booking = doc.to_dict()

            if (
                booking.get(
                    "assigned_role"
                )
                != role
            ):
                continue

            st.subheader(
                booking.get("service")
            )

            st.write(
                booking.get(
                    "customer_name"
                )
            )

            st.write(
                booking.get(
                    "booking_date"
                )
            )

            st.write(
                booking.get(
                    "time_slot"
                )
            )

            st.write(
                booking.get(
                    "status"
                )
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    f"Accept {doc.id}",
                    key=f"a_{doc.id}"
                ):

                    db.collection(
                        "bookings"
                    ).document(
                        doc.id
                    ).update({
                        "status":"Accepted"
                    })

                    st.rerun()

            with col2:

                if st.button(
                    f"Complete {doc.id}",
                    key=f"c_{doc.id}"
                ):

                    booking["status"] = (
                        "Completed"
                    )

                    db.collection(
                        "completed_bookings"
                    ).document(
                        doc.id
                    ).set(booking)

                    db.collection(
                        "bookings"
                    ).document(
                        doc.id
                    ).delete()

                    customer_ref = db.collection(
                        "loyalty_points"
                    ).document(
                        booking["phone"]
                    )

                    customer_doc = (
                        customer_ref.get()
                    )

                    current_points = 0

                    if customer_doc.exists:

                        current_points = (
                            customer_doc
                            .to_dict()
                            .get(
                                "points",
                                0
                            )
                        )

                    customer_ref.set({

                        "customer_name":
                        booking[
                            "customer_name"
                        ],

                        "phone":
                        booking["phone"],

                        "points":
                        current_points + 5
                    })

                    st.success(
                        "Completed!"
                    )

                    st.success(
                        "Customer earned 5 points!"
                    )

                    st.rerun()

# ======================================================
# FOOTER
# ======================================================

st.markdown("""

<hr>

<div style='text-align:center;padding:20px;'>

Powered by

<span style='color:#d4af37;font-weight:bold;'>
SalonSmart
</span>

</div>

""", unsafe_allow_html=True)
