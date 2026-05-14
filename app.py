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
# API CONFIG
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
# HUGE FULL MENU
# ======================================================

services = [

    # MASSAGES

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
        "name":"Aroma Therapy 45 mins",
        "duration":"45 mins",
        "price":2000,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Luxury aroma therapy massage.",
        "image":"https://images.unsplash.com/photo-1515377905703-c4788e51af15"
    },

    {
        "name":"Aroma Therapy 60 mins",
        "duration":"60 mins",
        "price":2500,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Extended aroma therapy session.",
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
        "name":"Body Polish",
        "duration":"60 mins",
        "price":3500,
        "role":"Massage Expert",
        "category":"Spa",
        "description":"Luxury skin polishing treatment.",
        "image":"https://images.unsplash.com/photo-1515377905703-c4788e51af15"
    },

    {
        "name":"Hand Massage",
        "duration":"20 mins",
        "price":250,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Relaxing hand massage.",
        "image":"https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },

    {
        "name":"Foot Work Massage",
        "duration":"30 mins",
        "price":300,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Luxury foot massage therapy.",
        "image":"https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },

    {
        "name":"Back Energy Massage",
        "duration":"30 mins",
        "price":400,
        "role":"Massage Expert",
        "category":"Massage",
        "description":"Back muscle recovery therapy.",
        "image":"https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },

    # PIERCINGS

    {
        "name":"Wart Removal",
        "duration":"20 mins",
        "price":200,
        "role":"Salon Staff",
        "category":"Piercing",
        "description":"Professional wart removal.",
        "image":"https://images.unsplash.com/photo-1519824145371-296894a0daa9"
    },

    {
        "name":"Nose Piercing",
        "duration":"20 mins",
        "price":600,
        "role":"Salon Staff",
        "category":"Piercing",
        "description":"Safe nose piercing service.",
        "image":"https://images.unsplash.com/photo-1521572267360-ee0c2909d518"
    },

    {
        "name":"Ear Piercing Single",
        "duration":"20 mins",
        "price":800,
        "role":"Salon Staff",
        "category":"Piercing",
        "description":"Single ear piercing.",
        "image":"https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },

    {
        "name":"Double Ear Piercing",
        "duration":"25 mins",
        "price":1200,
        "role":"Salon Staff",
        "category":"Piercing",
        "description":"Double ear piercing styling.",
        "image":"https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },

    # MAKEUP

    {
        "name":"Mehandi",
        "duration":"45 mins",
        "price":500,
        "role":"Makeup Artist",
        "category":"Makeup",
        "description":"Traditional mehandi designs.",
        "image":"https://images.unsplash.com/photo-1596704017254-9758d0f1a8db"
    },

    {
        "name":"Light Makeup",
        "duration":"45 mins",
        "price":2500,
        "role":"Makeup Artist",
        "category":"Makeup",
        "description":"Elegant light makeup.",
        "image":"https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"
    },

    {
        "name":"Party Makeup",
        "duration":"60 mins",
        "price":3500,
        "role":"Makeup Artist",
        "category":"Makeup",
        "description":"Party glam makeup.",
        "image":"https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"
    },

    {
        "name":"Bridal Trial Makeup",
        "duration":"60 mins",
        "price":2500,
        "role":"Makeup Artist",
        "category":"Makeup",
        "description":"Trial bridal makeup.",
        "image":"https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },

    {
        "name":"Bridal Makeup",
        "duration":"120 mins",
        "price":7500,
        "role":"Makeup Artist",
        "category":"Makeup",
        "description":"Premium bridal package.",
        "image":"https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },

    {
        "name":"Reception Makeup",
        "duration":"90 mins",
        "price":5000,
        "role":"Makeup Artist",
        "category":"Makeup",
        "description":"Reception glam makeover.",
        "image":"https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },

    # SAREE

    {
        "name":"Half Saree Draping",
        "duration":"30 mins",
        "price":300,
        "role":"Salon Staff",
        "category":"Saree",
        "description":"Half saree styling.",
        "image":"https://images.unsplash.com/photo-1610030469983-98e550d6193c"
    },

    {
        "name":"Saree Draping",
        "duration":"45 mins",
        "price":500,
        "role":"Salon Staff",
        "category":"Saree",
        "description":"Luxury saree draping.",
        "image":"https://images.unsplash.com/photo-1610030469983-98e550d6193c"
    },

    {
        "name":"Saree Preplating",
        "duration":"45 mins",
        "price":700,
        "role":"Salon Staff",
        "category":"Saree",
        "description":"Professional saree preplating.",
        "image":"https://images.unsplash.com/photo-1610030469983-98e550d6193c"
    },

    # PEDICURE

    {
        "name":"Basic Pedicure",
        "duration":"45 mins",
        "price":500,
        "role":"Nail Technician",
        "category":"Pedicure",
        "description":"Basic foot care.",
        "image":"https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },

    {
        "name":"Spa Pedicure",
        "duration":"60 mins",
        "price":600,
        "role":"Nail Technician",
        "category":"Pedicure",
        "description":"Relaxing spa pedicure.",
        "image":"https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },

    {
        "name":"Crystal Pedicure",
        "duration":"60 mins",
        "price":900,
        "role":"Nail Technician",
        "category":"Pedicure",
        "description":"Crystal spa pedicure.",
        "image":"https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },

    {
        "name":"Bomb Pedicure",
        "duration":"90 mins",
        "price":2000,
        "role":"Nail Technician",
        "category":"Pedicure",
        "description":"Premium bomb pedicure.",
        "image":"https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    }

]

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

.service-card:hover{
    transform:translateY(-5px);
}

.price{
    color:#d4af37;
    font-size:24px;
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

    search = st.text_input(
        "Search Services"
    )

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

    selected_category = st.selectbox(
        "Filter Category",
        ["All"] + categories
    )

    cols = st.columns(3)

    filtered = []

    for s in services:

        if (
            selected_category != "All"
            and
            s["category"] != selected_category
        ):
            continue

        if (
            search.lower()
            not in s["name"].lower()
        ):
            continue

        filtered.append(s)

    for i, service in enumerate(filtered):

        with cols[i % 3]:

            st.image(
                service["image"]
            )

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
                    "selected_service"
                ] = service

    # ==================================================
    # POPUP
    # ==================================================

    if "selected_service" in st.session_state:

        selected = st.session_state[
            "selected_service"
        ]

        @st.dialog(selected["name"])

        def popup():

            st.image(
                selected["image"]
            )

            st.write(
                selected["description"]
            )

            st.write(
                f"Duration: "
                f"{selected['duration']}"
            )

            st.write(
                f"Price: "
                f"₹{selected['price']}"
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
                        "Slot occupied"
                    )

                else:

                    prompt = f"""
                    Explain
                    {selected['name']}
                    briefly.
                    """

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
                                        "content":prompt
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

                        st.error(
                            str(e)
                        )

        popup()

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
                    booking.get("booking_date")
                )

                st.write(
                    booking.get("time_slot")
                )

                st.write(
                    booking.get("status")
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
                        "Customer earned "
                        "5 points!"
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
MentorLoop EDU
</span>

and

<span style='color:#d4af37;font-weight:bold;'>
PNB
</span>

</div>

""", unsafe_allow_html=True)
