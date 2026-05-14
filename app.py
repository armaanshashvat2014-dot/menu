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
# PASSWORD
# ======================================================

WORKER_PASSWORD = "PNBWORKER123"

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

services = {

    "Ayurvedic Massage": {
        "duration": "45 / 60 mins",
        "price": 1500,
        "image":
        "https://images.unsplash.com/photo-1544161515-4ab6ce6db874",
        "description":
        "Relaxing Ayurvedic therapy using herbal oils.",
        "role":
        "Massage Expert"
    },

    "Aroma Therapy": {
        "duration": "45 / 60 mins",
        "price": 2000,
        "image":
        "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
        "description":
        "Luxury aroma oil therapy for stress relief.",
        "role":
        "Massage Expert"
    },

    "Deep Tissue Massage": {
        "duration": "60 mins",
        "price": 3000,
        "image":
        "https://images.unsplash.com/photo-1519823551278-64ac92734fb1",
        "description":
        "Deep muscle pressure therapy.",
        "role":
        "Massage Expert"
    },

    "Bridal Makeup": {
        "duration": "2 Hours",
        "price": 7500,
        "image":
        "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",
        "description":
        "Luxury bridal makeover package.",
        "role":
        "Makeup Artist"
    },

    "Keratin Treatment": {
        "duration": "2 Hours",
        "price": 5000,
        "image":
        "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f",
        "description":
        "Advanced keratin smoothing treatment.",
        "role":
        "Hair Stylist"
    },

    "Bomb Pedicure": {
        "duration": "1 Hour",
        "price": 2000,
        "image":
        "https://images.unsplash.com/photo-1519014816548-bf5fe059798b",
        "description":
        "Luxury spa pedicure experience.",
        "role":
        "Nail Technician"
    }
}

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>

.stApp{
    background:linear-gradient(135deg,#0f0f0f,#1c1c1c);
    color:white;
}

.service-card{
    background:#1b1b1b;
    padding:20px;
    border-radius:20px;
    margin-bottom:20px;
    border:1px solid rgba(255,255,255,0.08);
}

.service-image{
    width:100%;
    border-radius:15px;
}

.price{
    color:#d4af37;
    font-size:26px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.markdown("""
<div style='text-align:center;padding:20px;'>

<h1 style='font-size:60px;color:#d4af37;'>
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
    # LOYALTY POINTS
    # ==================================================

    st.subheader("🎁 Loyalty Points")

    check_phone = st.text_input(
        "Enter Phone Number"
    )

    if st.button("Load Points"):

        if check_phone.strip() == "":

            st.error(
                "Please enter phone number."
            )

        else:

            points_doc = db.collection(
                "loyalty_points"
            ).document(
                check_phone
            ).get()

            if points_doc.exists:

                points = points_doc.to_dict().get(
                    "points",
                    0
                )

                st.success(
                    f"You have {points} points!"
                )

            else:

                st.warning(
                    "No points yet."
                )

    # ==================================================
    # SERVICE CARDS
    # ==================================================

    cols = st.columns(3)

    for i, (service, data) in enumerate(services.items()):

        with cols[i % 3]:

            st.markdown(f"""
            <div class='service-card'>

            <img src='{data["image"]}'
            class='service-image'>

            <h2 style='color:#d4af37;'>
            {service}
            </h2>

            <p>{data["description"]}</p>

            <p>
            <b>Duration:</b>
            {data["duration"]}
            </p>

            <div class='price'>
            ₹{data["price"]}
            </div>

            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"✨ Open {service}",
                key=f"open_{service}"
            ):

                st.session_state[
                    "selected_service"
                ] = service

    # ==================================================
    # SERVICE DETAILS
    # ==================================================

    if "selected_service" in st.session_state:

        selected = st.session_state[
            "selected_service"
        ]

        data = services[selected]

        st.divider()

        st.title(selected)

        st.image(data["image"])

        st.write(data["description"])

        st.write(
            f"Duration: {data['duration']}"
        )

        st.write(
            f"Price: ₹{data['price']}"
        )

        booking_date = st.date_input(
            "Select Date"
        )

        time_slot = st.selectbox(
            "Select Time Slot",
            TIME_SLOTS
        )

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

        slot_count = len(list(slot_docs))

        remaining = 4 - slot_count

        if remaining <= 0:

            st.error("Slot occupied")

        else:

            st.success(
                f"{remaining} slots remaining"
            )

        customer_name = st.text_input(
            "Customer Name"
        )

        customer_phone = st.text_input(
            "Phone Number"
        )

        if st.button("Confirm Booking"):

            if remaining <= 0:

                st.error(
                    "Cannot book occupied slot."
                )

            elif customer_name and customer_phone:

                try:

                    prompt = f"""
                    Explain {selected}
                    briefly and luxuriously.
                    """

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
                                    "content":prompt
                                }
                            ],

                            "generateImage": True
                        }
                    )

                    ai_response = response.json()

                    ai_text = str(ai_response)

                    db.collection(
                        "bookings"
                    ).add({

                        "customer_name":
                        customer_name,

                        "phone":
                        customer_phone,

                        "service":
                        selected,

                        "price":
                        data["price"],

                        "booking_date":
                        str(booking_date),

                        "time_slot":
                        time_slot,

                        "status":
                        "Pending",

                        "assigned_role":
                        data["role"],

                        "ai_response":
                        ai_text,

                        "created_at":
                        str(datetime.now())
                    })

                    st.success(
                        "Booking Confirmed!"
                    )

                    st.info(ai_text)

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )

# ======================================================
# MY BOOKINGS
# ======================================================

elif mode == "My Bookings":

    st.title("📅 My Bookings")

    customer_name = st.text_input(
        "Customer Name"
    )

    customer_phone = st.text_input(
        "Phone Number"
    )

    if st.button("Load Bookings"):

        docs = db.collection(
            "bookings"
        ).stream()

        found = False

        for doc in docs:

            booking = doc.to_dict()

            if (
                booking.get("customer_name")
                == customer_name
                and
                booking.get("phone")
                == customer_phone
            ):

                found = True

                st.subheader(
                    booking.get("service")
                )

                st.write(
                    f"Date: "
                    f"{booking.get('booking_date')}"
                )

                st.write(
                    f"Time: "
                    f"{booking.get('time_slot')}"
                )

                st.write(
                    f"Status: "
                    f"{booking.get('status')}"
                )

                if st.button(
                    f"Cancel {doc.id}",
                    key=f"cancel_{doc.id}"
                ):

                    db.collection(
                        "bookings"
                    ).document(doc.id).delete()

                    st.success(
                        "Booking cancelled"
                    )

                    st.rerun()

        if not found:

            st.warning(
                "No bookings found"
            )

# ======================================================
# WORKER LOGIN
# ======================================================

elif mode == "Worker Login":

    st.title("🔒 Worker Dashboard")

    password = st.text_input(
        "Enter Worker Password",
        type="password"
    )

    if password == WORKER_PASSWORD:

        worker_role = st.selectbox(
            "Select Role",
            [
                "Massage Expert",
                "Makeup Artist",
                "Hair Stylist",
                "Nail Technician",
                "Salon Staff"
            ]
        )

        docs = db.collection(
            "bookings"
        ).stream()

        for doc in docs:

            booking = doc.to_dict()

            if (
                booking.get("assigned_role")
                != worker_role
            ):
                continue

            st.subheader(
                booking.get("service")
            )

            st.write(
                booking.get("customer_name")
            )

            st.write(
                booking.get("booking_date")
            )

            st.write(
                booking.get("time_slot")
            )

            st.write(
                booking.get("status")
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    f"Accept {doc.id}",
                    key=f"accept_{doc.id}"
                ):

                    db.collection(
                        "bookings"
                    ).document(doc.id).update({
                        "status":"Accepted"
                    })

                    st.rerun()

            with col2:

                if st.button(
                    f"Complete {doc.id}",
                    key=f"complete_{doc.id}"
                ):

                    try:

                        customer_ref = db.collection(
                            "loyalty_points"
                        ).document(
                            booking["phone"]
                        )

                        customer_doc = customer_ref.get()

                        current_points = 0

                        if customer_doc.exists:

                            current_points = (
                                customer_doc
                                .to_dict()
                                .get("points",0)
                            )

                        customer_ref.set({

                            "customer_name":
                            booking["customer_name"],

                            "phone":
                            booking["phone"],

                            "points":
                            current_points + 5
                        })

                        booking["status"] = (
                            "Completed"
                        )

                        booking["earned_points"] = 5

                        db.collection(
                            "completed_bookings"
                        ).document(doc.id).set(
                            booking
                        )

                        db.collection(
                            "bookings"
                        ).document(doc.id).delete()

                        st.success(
                            "Completed!"
                        )

                        st.success(
                            "Customer earned "
                            "5 loyalty points!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )

    elif password != "":

        st.error("Wrong password")

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<hr>

<div style='text-align:center;padding:20px;'>

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
