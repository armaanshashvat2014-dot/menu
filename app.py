import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from datetime import datetime

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="PNB Smart & Luxurious Salon",
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
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
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

WORKER_PASSWORD = "PNB2024"

# ======================================================
# SESSION STATE
# ======================================================

if "selected_service" not in st.session_state:
    st.session_state["selected_service"] = None
if "open_ai" not in st.session_state:
    st.session_state["open_ai"] = False
if "active_category" not in st.session_state:
    st.session_state["active_category"] = "All"

# ======================================================
# TIME SLOTS
# ======================================================

TIME_SLOTS = [
    "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM",
    "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM",
    "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM"
]

# ======================================================
# FULL SERVICES MENU
# ======================================================

services = [

    # ---------- MASSAGE ----------
    {
        "name": "Ayurvedic Massage (45 mins)",
        "duration": "45 mins",
        "price": 1500,
        "role": "Massage Expert",
        "category": "Massage",
        "description": "Traditional Ayurvedic herbal massage using warm medicated oils to balance doshas, relieve stress and revitalize the body.",
        "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },
    {
        "name": "Ayurvedic Massage (60 mins)",
        "duration": "60 mins",
        "price": 1800,
        "role": "Massage Expert",
        "category": "Massage",
        "description": "Extended traditional Ayurvedic herbal massage for deep relaxation, improved circulation, and holistic wellness.",
        "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },
    {
        "name": "Aroma Therapy (45 mins)",
        "duration": "45 mins",
        "price": 2000,
        "role": "Massage Expert",
        "category": "Massage",
        "description": "Luxury aromatherapy session with premium essential oils to calm the mind and refresh the senses.",
        "image": "https://images.unsplash.com/photo-1515377905703-c4788e51af15"
    },
    {
        "name": "Aroma Therapy (60 mins)",
        "duration": "60 mins",
        "price": 2500,
        "role": "Massage Expert",
        "category": "Massage",
        "description": "Extended luxury aromatherapy session for deep stress relief and full body relaxation using curated essential oil blends.",
        "image": "https://images.unsplash.com/photo-1515377905703-c4788e51af15"
    },
    {
        "name": "Deep Tissue Massage",
        "duration": "60 mins",
        "price": 3000,
        "role": "Massage Expert",
        "category": "Massage",
        "description": "Therapeutic deep muscle recovery massage targeting chronic tension, knots, and muscle fatigue.",
        "image": "https://images.unsplash.com/photo-1519823551278-64ac92734fb1"
    },
    {
        "name": "Body Polish",
        "duration": "60 mins",
        "price": 3500,
        "role": "Massage Expert",
        "category": "Massage",
        "description": "Full body exfoliation and polishing treatment to reveal radiant, smooth and glowing skin.",
        "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"
    },

    # ---------- SKIN / SPECIALTY ----------
    {
        "name": "Wart Removal",
        "duration": "20 mins",
        "price": 200,
        "role": "Skin Specialist",
        "category": "Skin",
        "description": "Safe and precise wart removal treatment performed by trained skin specialists using advanced techniques.",
        "image": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908"
    },
    {
        "name": "Nose Piercing",
        "duration": "15 mins",
        "price": 600,
        "role": "Skin Specialist",
        "category": "Skin",
        "description": "Professional nose piercing with hygienic, sterilized equipment and premium jewelry options.",
        "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"
    },
    {
        "name": "Ear Piercing (Single)",
        "duration": "10 mins",
        "price": 800,
        "role": "Skin Specialist",
        "category": "Skin",
        "description": "Single ear piercing with sterilized tools, safe and quick procedure with aftercare guidance.",
        "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"
    },
    {
        "name": "Ear Piercing (Double)",
        "duration": "15 mins",
        "price": 1200,
        "role": "Skin Specialist",
        "category": "Skin",
        "description": "Double ear piercing for both ears with premium sterilized equipment and stylish jewelry.",
        "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"
    },

    # ---------- MEHANDI / HAIR STYLING ----------
    {
        "name": "Mehandi",
        "duration": "30 mins",
        "price": 500,
        "role": "Mehandi Artist",
        "category": "Mehandi & Styling",
        "description": "Beautiful intricate henna mehandi designs crafted by skilled artists for festive and bridal occasions.",
        "image": "https://images.unsplash.com/photo-1532030543767-ea4b0f5aa7a5"
    },
    {
        "name": "Fashion Plait",
        "duration": "20 mins",
        "price": 500,
        "role": "Hair Stylist",
        "category": "Mehandi & Styling",
        "description": "Trendy and elegant fashion plait hairstyle crafted to complement any look or occasion.",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e"
    },
    {
        "name": "Flower Plait Fixing",
        "duration": "25 mins",
        "price": 800,
        "role": "Hair Stylist",
        "category": "Mehandi & Styling",
        "description": "Gorgeous flower plait adorned with fresh or artificial flowers for weddings and celebrations.",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e"
    },

    # ---------- MAKEUP ----------
    {
        "name": "Light Makeup",
        "duration": "45 mins",
        "price": 2500,
        "role": "Makeup Artist",
        "category": "Makeup",
        "description": "Fresh, natural light makeup look perfect for daytime events and casual outings.",
        "image": "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"
    },
    {
        "name": "Party Makeup",
        "duration": "60 mins",
        "price": 3500,
        "role": "Makeup Artist",
        "category": "Makeup",
        "description": "Bold and glamorous party makeup for an unforgettable evening look.",
        "image": "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"
    },
    {
        "name": "Bridal Trial Makeup",
        "duration": "90 mins",
        "price": 2500,
        "role": "Makeup Artist",
        "category": "Makeup",
        "description": "Pre-wedding trial session to perfect your bridal look and ensure flawless results on the big day.",
        "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },
    {
        "name": "Bridal Makeup",
        "duration": "120 mins",
        "price": 7500,
        "role": "Makeup Artist",
        "category": "Makeup",
        "description": "Complete luxury bridal makeover package — because your wedding day deserves nothing less than perfection.",
        "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },
    {
        "name": "Reception Makeup",
        "duration": "90 mins",
        "price": 5000,
        "role": "Makeup Artist",
        "category": "Makeup",
        "description": "Elegant and radiant reception makeup designed to glow under lights and cameras.",
        "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
    },

    # ---------- SAREE ----------
    {
        "name": "Half Saree Draping",
        "duration": "20 mins",
        "price": 300,
        "role": "Styling Expert",
        "category": "Saree & Draping",
        "description": "Neat and graceful half-saree draping for a traditional and elegant look.",
        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"
    },
    {
        "name": "Saree Draping",
        "duration": "25 mins",
        "price": 500,
        "role": "Styling Expert",
        "category": "Saree & Draping",
        "description": "Perfect saree draping by skilled experts to ensure you look flawless and feel confident.",
        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"
    },
    {
        "name": "Saree Pre-Plating",
        "duration": "30 mins",
        "price": 700,
        "role": "Styling Expert",
        "category": "Saree & Draping",
        "description": "Professional saree pre-plating and pinning for a crisp, well-structured drape that lasts all day.",
        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"
    },

    # ---------- PEDICURE ----------
    {
        "name": "Basic Pedicure",
        "duration": "30 mins",
        "price": 500,
        "role": "Nail Technician",
        "category": "Pedicure",
        "description": "Classic pedicure with soaking, scrubbing, nail shaping and a fresh coat of colour.",
        "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },
    {
        "name": "Spa Pedicure",
        "duration": "45 mins",
        "price": 600,
        "role": "Nail Technician",
        "category": "Pedicure",
        "description": "Relaxing spa pedicure with moisturizing treatment and gentle massage for soft, happy feet.",
        "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },
    {
        "name": "Crystal Pedicure",
        "duration": "50 mins",
        "price": 900,
        "role": "Nail Technician",
        "category": "Pedicure",
        "description": "Luxurious crystal pedicure for deeply nourished, glowing skin and beautifully shaped nails.",
        "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },
    {
        "name": "Aromatic Pedicure",
        "duration": "55 mins",
        "price": 1200,
        "role": "Nail Technician",
        "category": "Pedicure",
        "description": "Aromatic pedicure infused with essential oils for a sensory treat and deeply refreshed feet.",
        "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },
    {
        "name": "Heel Peel Pedicure",
        "duration": "60 mins",
        "price": 1300,
        "role": "Nail Technician",
        "category": "Pedicure",
        "description": "Specialized heel peel treatment to eliminate rough, cracked heels leaving feet baby soft.",
        "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },
    {
        "name": "PNB Signature Pedicure",
        "duration": "75 mins",
        "price": 1600,
        "role": "Nail Technician",
        "category": "Pedicure",
        "description": "Our exclusive signature pedicure — a premium full-care ritual designed for ultimate indulgence.",
        "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },
    {
        "name": "Nail Cut & Colouring",
        "duration": "20 mins",
        "price": 200,
        "role": "Nail Technician",
        "category": "Pedicure",
        "description": "Neat nail cutting and a vibrant colour application for a polished, put-together look.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Bomb Pedicure",
        "duration": "90 mins",
        "price": 2000,
        "role": "Nail Technician",
        "category": "Pedicure",
        "description": "The ultimate luxury bomb pedicure — an explosive combination of exfoliation, massage and glamour.",
        "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"
    },

    # ---------- MANICURE ----------
    {
        "name": "Basic Manicure",
        "duration": "30 mins",
        "price": 300,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Classic manicure with soaking, cuticle care, nail shaping and colour application.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Spa Manicure",
        "duration": "45 mins",
        "price": 500,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Relaxing spa manicure with moisturizing treatment and a soothing hand massage.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Crystal Spa Manicure",
        "duration": "50 mins",
        "price": 750,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Luxury crystal spa manicure for beautifully nourished hands and flawless nails.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Nail Filing & Colouring",
        "duration": "15 mins",
        "price": 200,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Quick nail filing and colour application for a neat and stylish finish.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Colouring Only",
        "duration": "10 mins",
        "price": 100,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Simple and quick nail colour application in your choice of shade.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Nail Filing Only",
        "duration": "10 mins",
        "price": 50,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Precise nail shaping and filing for a clean, well-groomed look.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "French Polish",
        "duration": "20 mins",
        "price": 250,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Classic French polish for timeless, elegant nails with a white tip and nude base.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Gel Polish",
        "duration": "30 mins",
        "price": 500,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Long-lasting gel polish for chip-free, glossy nails that stay perfect for weeks.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Gel Polish Removal",
        "duration": "20 mins",
        "price": 200,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Safe and gentle gel polish removal without damaging the natural nail.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },
    {
        "name": "Bomb Manicure",
        "duration": "75 mins",
        "price": 1800,
        "role": "Nail Technician",
        "category": "Manicure",
        "description": "Our ultimate bomb manicure — a complete luxury hand ritual for beautifully pampered hands.",
        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"
    },

    # ---------- HAIR TREATMENTS ----------
    {
        "name": "Perming (Small)",
        "duration": "90 mins",
        "price": 2000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Create bouncy, beautiful curls with professional perming treatment for short/small sections.",
        "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"
    },
    {
        "name": "Perming (Medium)",
        "duration": "120 mins",
        "price": 3000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Professional perming for medium-length hair with long-lasting, voluminous curls.",
        "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"
    },
    {
        "name": "Perming (Large)",
        "duration": "150 mins",
        "price": 4000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Full perming treatment for long or thick hair with stunning, defined curls.",
        "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"
    },
    {
        "name": "Smoothening (Small)",
        "duration": "90 mins",
        "price": 3000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Hair smoothening treatment for short hair — eliminate frizz and add shine.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Smoothening (Medium)",
        "duration": "120 mins",
        "price": 4000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Smoothening treatment for medium hair — silky, manageable, frizz-free results.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Smoothening (Large)",
        "duration": "150 mins",
        "price": 5000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Smoothening treatment for long/thick hair — dramatically smoother, shinier tresses.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Rebonding (Small)",
        "duration": "120 mins",
        "price": 4000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Rebonding for short hair — permanently straighten and restructure for ultra-sleek results.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Rebonding (Medium)",
        "duration": "150 mins",
        "price": 5000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Rebonding for medium hair — salon-perfect straight hair with long-lasting effects.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Rebonding (Large)",
        "duration": "180 mins",
        "price": 6000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Rebonding for long or thick hair — complete transformation to glass-smooth straight hair.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Straightening (Small)",
        "duration": "90 mins",
        "price": 5000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Professional straightening for short hair with premium products for lasting sleekness.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Straightening (Medium)",
        "duration": "120 mins",
        "price": 6000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Professional straightening for medium hair — smooth, glossy, and beautifully managed.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Straightening (Large)",
        "duration": "150 mins",
        "price": 7000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Professional straightening for long/thick hair — perfectly straight, mirror-shiny results.",
        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"
    },
    {
        "name": "Keratin Treatment",
        "duration": "120 mins",
        "price": 5000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Premium keratin treatment to deeply nourish, smoothen and add brilliant shine to your hair.",
        "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"
    },
    {
        "name": "Express Keratin Treatment",
        "duration": "90 mins",
        "price": 4500,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Quick express keratin treatment for a faster dose of frizz-free, glossy hair.",
        "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"
    },
    {
        "name": "Deep Conditioning",
        "duration": "60 mins",
        "price": 3000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Intensive deep conditioning treatment to restore moisture, strength, and brilliance to damaged hair.",
        "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"
    },
    {
        "name": "Hair Scrub",
        "duration": "30 mins",
        "price": 800,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Scalp purifying hair scrub to remove buildup, unclog follicles and promote healthy hair growth.",
        "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"
    },
    {
        "name": "Metal DK Treatment",
        "duration": "45 mins",
        "price": 1000,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Metal DK bond-rebuilding treatment to repair chemical damage and restore hair integrity.",
        "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"
    },
    {
        "name": "Hair Treatment",
        "duration": "45 mins",
        "price": 1300,
        "role": "Hair Stylist",
        "category": "Hair Treatments",
        "description": "Targeted professional hair treatment customized to your hair type and concern.",
        "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"
    },

    # ---------- HAIR COLOUR ----------
    {
        "name": "Colour Application Only",
        "duration": "40 mins",
        "price": 300,
        "role": "Hair Stylist",
        "category": "Hair Colour",
        "description": "Professional colour application to achieve rich, vibrant hair colour.",
        "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"
    },
    {
        "name": "Colour Application + Wash (Basic)",
        "duration": "60 mins",
        "price": 550,
        "role": "Hair Stylist",
        "category": "Hair Colour",
        "description": "Colour application followed by a professional wash and blow-dry for a finished look.",
        "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"
    },
    {
        "name": "Colour Application (Full)",
        "duration": "60 mins",
        "price": 500,
        "role": "Hair Stylist",
        "category": "Hair Colour",
        "description": "Full head colour application for complete colour coverage and transformation.",
        "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"
    },
    {
        "name": "Colour Application + Wash (Premium)",
        "duration": "75 mins",
        "price": 800,
        "role": "Hair Stylist",
        "category": "Hair Colour",
        "description": "Premium full colour application with professional wash and conditioning treatment.",
        "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"
    },
    {
        "name": "Touch Up",
        "duration": "45 mins",
        "price": 1000,
        "role": "Hair Stylist",
        "category": "Hair Colour",
        "description": "Precise root touch-up to refresh your colour and keep it looking salon-fresh.",
        "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"
    },

    # ---------- HAIRCUT ----------
    {
        "name": "Haircut (Below 8 yrs)",
        "duration": "20 mins",
        "price": 200,
        "role": "Hair Stylist",
        "category": "Haircut",
        "description": "Gentle and fun haircut designed specially for children below 8 years.",
        "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"
    },
    {
        "name": "Basic Haircut",
        "duration": "30 mins",
        "price": 250,
        "role": "Hair Stylist",
        "category": "Haircut",
        "description": "Classic stylish haircut shaped to flatter your features and suit your style.",
        "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"
    },
    {
        "name": "Split Ends Trim",
        "duration": "25 mins",
        "price": 400,
        "role": "Hair Stylist",
        "category": "Haircut",
        "description": "Precision split-end removal to restore healthy, smooth hair ends without losing length.",
        "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"
    },
    {
        "name": "Advanced Haircut",
        "duration": "45 mins",
        "price": 500,
        "role": "Hair Stylist",
        "category": "Haircut",
        "description": "Expert advanced haircut with precision layering and styling tailored to your hair type.",
        "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"
    },

    # ---------- HAIR WASH ----------
    {
        "name": "Hair Wash + Conditioner (Til/Coconut Oil Massage)",
        "duration": "30 mins",
        "price": 300,
        "role": "Hair Stylist",
        "category": "Hair Wash",
        "description": "Nourishing hair wash with conditioner, preceded by a relaxing traditional oil head massage.",
        "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"
    },
    {
        "name": "Hair Wash + Conditioner (Olive/Aroma/Cooling Oil Massage)",
        "duration": "35 mins",
        "price": 350,
        "role": "Hair Stylist",
        "category": "Hair Wash",
        "description": "Revitalizing hair wash with conditioner after an indulgent premium oil head massage.",
        "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"
    },

    # ---------- FACE TREATMENTS ----------
    {
        "name": "Young Face Pack",
        "duration": "30 mins",
        "price": 300,
        "role": "Skin Specialist",
        "category": "Face Treatments",
        "description": "Hydrating and brightening face pack to give your skin a youthful, dewy glow.",
        "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"
    },
    {
        "name": "White Face Pack",
        "duration": "30 mins",
        "price": 300,
        "role": "Skin Specialist",
        "category": "Face Treatments",
        "description": "Brightening white face pack for a luminous, even-toned and radiant complexion.",
        "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"
    },
    {
        "name": "Charcoal Pack",
        "duration": "35 mins",
        "price": 350,
        "role": "Skin Specialist",
        "category": "Face Treatments",
        "description": "Deep-cleansing activated charcoal face pack to purify pores and detox the skin.",
        "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"
    },
    {
        "name": "Tan Pack",
        "duration": "45 mins",
        "price": 600,
        "role": "Skin Specialist",
        "category": "Face Treatments",
        "description": "Effective de-tan face pack to reverse sun damage and restore skin's natural brightness.",
        "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"
    },
    {
        "name": "Charcoal Face Mask",
        "duration": "40 mins",
        "price": 750,
        "role": "Skin Specialist",
        "category": "Face Treatments",
        "description": "Premium activated charcoal face mask for deep pore purification and skin detox.",
        "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"
    },
    {
        "name": "Gold Face Mask",
        "duration": "45 mins",
        "price": 800,
        "role": "Skin Specialist",
        "category": "Face Treatments",
        "description": "Luxury 24k gold face mask to boost radiance, reduce fine lines and illuminate your skin.",
        "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"
    },

    # ---------- MASSAGE (HANDS / FOOT / BACK) ----------
    {
        "name": "Hand Massage",
        "duration": "20 mins",
        "price": 250,
        "role": "Massage Expert",
        "category": "Quick Massages",
        "description": "Soothing hand massage to relieve tension and leave your hands feeling soft and revitalized.",
        "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },
    {
        "name": "Foot Work Massage",
        "duration": "25 mins",
        "price": 300,
        "role": "Massage Expert",
        "category": "Quick Massages",
        "description": "Revitalizing foot massage targeting pressure points to relieve fatigue and improve circulation.",
        "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },
    {
        "name": "Back Energy Massage",
        "duration": "30 mins",
        "price": 400,
        "role": "Massage Expert",
        "category": "Quick Massages",
        "description": "Energizing back massage to release muscle knots, reduce tension and restore vitality.",
        "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"
    },
]

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap');

*{font-family:'Jost',sans-serif;}

.stApp{
    background:linear-gradient(160deg,#0a0a0a 0%,#111010 40%,#130f0a 100%);
    color:#f5f0e8;
}

h1,h2,h3{font-family:'Cormorant Garamond',serif !important; color:#c9a84c !important;}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0d0b08,#1a1208) !important;
    border-right:1px solid rgba(201,168,76,0.2) !important;
}

section[data-testid="stSidebar"] *{color:#e8d5a3 !important;}

/* Category pills */
.cat-pill{
    display:inline-block;
    padding:6px 18px;
    margin:4px;
    border-radius:30px;
    border:1px solid rgba(201,168,76,0.4);
    color:#c9a84c;
    font-size:13px;
    letter-spacing:1px;
    cursor:pointer;
    text-transform:uppercase;
    background:transparent;
    transition:all 0.3s;
}

.cat-pill:hover{
    background:rgba(201,168,76,0.12);
}

/* Service card */
.service-link-card{
    background:linear-gradient(145deg,#161410,#1e1a12);
    border:1px solid rgba(201,168,76,0.15);
    border-radius:16px;
    padding:0;
    overflow:hidden;
    margin-bottom:24px;
    transition:transform 0.3s, border-color 0.3s, box-shadow 0.3s;
    cursor:pointer;
}

.service-link-card:hover{
    transform:translateY(-4px);
    border-color:rgba(201,168,76,0.5);
    box-shadow:0 12px 40px rgba(201,168,76,0.12);
}

.service-card-body{
    padding:16px;
}

.service-name{
    font-family:'Cormorant Garamond',serif;
    font-size:20px;
    color:#c9a84c;
    margin:0 0 6px 0;
    line-height:1.3;
}

.service-desc{
    color:#999;
    font-size:13px;
    line-height:1.5;
    margin-bottom:10px;
}

.service-meta{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.service-price{
    font-family:'Cormorant Garamond',serif;
    font-size:26px;
    font-weight:600;
    color:#c9a84c;
}

.service-duration{
    color:#666;
    font-size:12px;
    letter-spacing:1px;
    text-transform:uppercase;
}

/* Header */
.salon-header{
    text-align:center;
    padding:48px 20px 32px;
    position:relative;
}

.salon-title{
    font-family:'Cormorant Garamond',serif;
    font-size:72px;
    font-weight:300;
    color:#c9a84c;
    letter-spacing:6px;
    line-height:1.1;
    margin:0;
}

.salon-sub{
    color:#7a6640;
    font-size:13px;
    letter-spacing:4px;
    text-transform:uppercase;
    margin-top:10px;
}

.gold-divider{
    width:120px;
    height:1px;
    background:linear-gradient(90deg,transparent,#c9a84c,transparent);
    margin:16px auto;
}

/* Section heading */
.section-heading{
    font-family:'Cormorant Garamond',serif;
    font-size:38px;
    color:#c9a84c;
    margin:8px 0 24px;
    letter-spacing:2px;
}

/* Booking form styling */
.stTextInput>div>div{
    background:#1a1610 !important;
    border-color:rgba(201,168,76,0.3) !important;
    color:#f5f0e8 !important;
    border-radius:8px !important;
}

.stSelectbox>div>div{
    background:#1a1610 !important;
    border-color:rgba(201,168,76,0.3) !important;
    color:#f5f0e8 !important;
    border-radius:8px !important;
}

.stDateInput>div>div{
    background:#1a1610 !important;
    border-color:rgba(201,168,76,0.3) !important;
    border-radius:8px !important;
}

/* Buttons */
.stButton>button{
    background:linear-gradient(135deg,#b8922a,#c9a84c) !important;
    color:#0a0a0a !important;
    border:none !important;
    border-radius:8px !important;
    font-family:'Jost',sans-serif !important;
    font-weight:600 !important;
    letter-spacing:1px !important;
    text-transform:uppercase !important;
    font-size:12px !important;
    padding:10px 28px !important;
    transition:opacity 0.2s !important;
}

.stButton>button:hover{
    opacity:0.85 !important;
}

/* AI button */
.ai-circle .stButton>button{
    border-radius:50% !important;
    height:52px !important;
    width:52px !important;
    font-size:20px !important;
    padding:0 !important;
}

/* Worker badge */
.worker-badge{
    display:inline-block;
    background:rgba(201,168,76,0.1);
    border:1px solid rgba(201,168,76,0.3);
    border-radius:20px;
    padding:4px 14px;
    font-size:12px;
    color:#c9a84c;
    letter-spacing:1px;
    text-transform:uppercase;
    margin-bottom:8px;
}

/* Booking card in my bookings */
.booking-card{
    background:#161410;
    border:1px solid rgba(201,168,76,0.2);
    border-radius:12px;
    padding:20px;
    margin-bottom:16px;
}

.status-pending{color:#e0a030; font-weight:600;}
.status-accepted{color:#3ab26e; font-weight:600;}
.status-completed{color:#aaa; font-weight:600;}

/* Footer */
.salon-footer{
    text-align:center;
    padding:32px 20px;
    margin-top:40px;
    border-top:1px solid rgba(201,168,76,0.1);
    color:#4a3e28;
    font-size:12px;
    letter-spacing:2px;
    text-transform:uppercase;
}

.salon-footer span{color:#c9a84c;}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.markdown("""
<div class='salon-header'>
    <p class='salon-sub'>Welcome to</p>
    <h1 class='salon-title'>PNB Smart &amp; Luxurious Salon</h1>
    <div class='gold-divider'></div>
    <p style='color:#7a6640;font-size:14px;letter-spacing:2px;'>AI-POWERED BEAUTY &amp; WELLNESS EXPERIENCE</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR
# ======================================================

mode = st.sidebar.radio(
    "Navigation",
    ["💎 Services", "📅 My Bookings", "🔒 Worker Login"]
)

# ======================================================
# SERVICES MODE
# ======================================================

if mode == "💎 Services":

    # Search + AI button
    col1, col2 = st.columns([10, 1])
    with col1:
        search = st.text_input("🔍 Search services...", placeholder="e.g. keratin, bridal, pedicure")
    with col2:
        st.markdown("<div class='ai-circle'>", unsafe_allow_html=True)
        if st.button("✨"):
            st.session_state["selected_service"] = None
            st.session_state["open_ai"] = True
        st.markdown("</div>", unsafe_allow_html=True)

    # Category filter
    categories = sorted(list(set([s["category"] for s in services])))
    category = st.selectbox("Filter by Category", ["All"] + categories)

    # Filter services
    filtered = [
        s for s in services
        if (category == "All" or s["category"] == category)
        and search.lower() in s["name"].lower()
    ]

    if filtered:
        st.markdown(f"""
        <div class='section-heading'>
            {category if category != 'All' else 'All Services'}
            <span style='font-size:18px;color:#555;margin-left:12px;font-family:Jost;'>
                {len(filtered)} services
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Display service cards as clickable links
    cols = st.columns(3)
    for i, service in enumerate(filtered):
        with cols[i % 3]:
            st.image(service["image"], use_container_width=True)
            st.markdown(f"""
            <div class='service-card-body' style='background:linear-gradient(145deg,#161410,#1e1a12);
                border:1px solid rgba(201,168,76,0.15);border-radius:0 0 16px 16px;padding:16px;
                margin-bottom:4px;'>
                <div class='service-name'>{service['name']}</div>
                <div class='service-desc'>{service['description'][:80]}...</div>
                <div class='service-meta'>
                    <div class='service-price'>₹{service['price']:,}</div>
                    <div class='service-duration'>⏱ {service['duration']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"View & Book", key=f"open_{i}"):
                st.session_state["open_ai"] = False
                st.session_state["selected_service"] = service

    # ======================================================
    # SERVICE DETAIL POPUP / DIALOG
    # ======================================================

    if st.session_state["selected_service"] is not None:
        selected = st.session_state["selected_service"]

        @st.dialog(f"✨ {selected['name']}", width="large")
        def service_popup():
            col_img, col_info = st.columns([1, 1])
            with col_img:
                st.image(selected["image"], use_container_width=True)
            with col_info:
                st.markdown(f"<h2 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:32px'>{selected['name']}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#aaa;line-height:1.7'>{selected['description']}</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='margin:16px 0;'>
                    <span style='background:rgba(201,168,76,0.1);border:1px solid rgba(201,168,76,0.3);
                        border-radius:20px;padding:4px 14px;font-size:12px;color:#c9a84c;
                        letter-spacing:1px;text-transform:uppercase;margin-right:8px'>
                        ⏱ {selected['duration']}
                    </span>
                    <span style='background:rgba(201,168,76,0.1);border:1px solid rgba(201,168,76,0.3);
                        border-radius:20px;padding:4px 14px;font-size:12px;color:#c9a84c;
                        letter-spacing:1px;text-transform:uppercase'>
                        👤 {selected['role']}
                    </span>
                </div>
                <div style='font-family:Cormorant Garamond;font-size:42px;color:#c9a84c;font-weight:600;margin:12px 0'>
                    ₹{selected['price']:,}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<hr style='border-color:rgba(201,168,76,0.15);margin:20px 0'>", unsafe_allow_html=True)
            st.markdown("<h3 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:24px;margin-bottom:16px'>📋 Book This Service</h3>", unsafe_allow_html=True)

            bcol1, bcol2 = st.columns(2)
            with bcol1:
                booking_date = st.date_input("📅 Booking Date")
                customer_name = st.text_input("👤 Your Name")
            with bcol2:
                time_slot = st.selectbox("🕐 Time Slot", TIME_SLOTS)
                customer_phone = st.text_input("📱 Phone Number")

            if st.button("💎 Confirm Booking", use_container_width=True):
                if not customer_name.strip() or not customer_phone.strip():
                    st.error("Please fill in your name and phone number.")
                else:
                    slot_docs = db.collection("bookings").where(
                        "booking_date", "==", str(booking_date)
                    ).where("time_slot", "==", time_slot).stream()

                    if len(list(slot_docs)) >= 4:
                        st.error("⚠️ This time slot is fully booked. Please choose another.")
                    else:
                        try:
                            response = requests.post(
                                AI_API_URL,
                                headers={
                                    "Authorization": f"Bearer {AI_API_KEY}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "messages": [{
                                        "role": "user",
                                        "content": f"In 2-3 sentences, give a warm, luxurious, welcoming tip or insight about the salon service: {selected['name']}."
                                    }]
                                }
                            )
                            data = response.json()
                            ai_reply = data["choices"][0]["message"]["content"]
                        except Exception:
                            ai_reply = f"Thank you for booking {selected['name']}. We look forward to pampering you!"

                        db.collection("bookings").add({
                            "customer_name": customer_name,
                            "phone": customer_phone,
                            "service": selected["name"],
                            "booking_date": str(booking_date),
                            "time_slot": time_slot,
                            "status": "Pending",
                            "assigned_role": selected["role"],
                            "price": selected["price"],
                            "created_at": str(datetime.now())
                        })

                        st.success("✅ Booking confirmed!")
                        st.markdown(f"""
                        <div style='background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.25);
                            border-radius:12px;padding:16px;margin-top:12px;color:#c9a84c;
                            font-style:italic;line-height:1.7;'>
                            ✨ {ai_reply}
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()

            if st.button("✕ Close", use_container_width=False):
                st.session_state["selected_service"] = None
                st.rerun()

        service_popup()

    # ======================================================
    # AI POPUP
    # ======================================================

    if st.session_state["open_ai"]:

        @st.dialog("✨ PNB Beauty AI Assistant", width="large")
        def ai_popup():
            st.markdown("""
            <p style='color:#aaa;line-height:1.7;margin-bottom:16px'>
            Ask anything about beauty, skincare, haircare, makeup, wellness or our services.
            Our AI beauty consultant is here to guide you.
            </p>
            """, unsafe_allow_html=True)

            user_question = st.text_input("💬 Your Question", placeholder="e.g. What treatment is best for frizzy hair?")

            if st.button("✨ Ask AI", use_container_width=True):
                if user_question.strip():
                    with st.spinner("Consulting our beauty expert..."):
                        try:
                            response = requests.post(
                                AI_API_URL,
                                headers={
                                    "Authorization": f"Bearer {AI_API_KEY}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "messages": [{
                                        "role": "user",
                                        "content": f"You are a luxury salon AI beauty consultant for PNB Smart & Luxurious Salon. Answer this customer question helpfully and warmly: {user_question}"
                                    }]
                                }
                            )
                            data = response.json()
                            ai_reply = data["choices"][0]["message"]["content"]
                            st.markdown(f"""
                            <div style='background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.25);
                                border-radius:12px;padding:20px;color:#e8d5a3;line-height:1.8;'>
                                {ai_reply}
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(str(e))

            if st.button("✕ Close AI", use_container_width=False):
                st.session_state["open_ai"] = False
                st.rerun()

        ai_popup()

# ======================================================
# MY BOOKINGS
# ======================================================

elif mode == "📅 My Bookings":
    st.markdown("<h1 class='section-heading'>📅 My Bookings</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666;margin-bottom:24px'>Enter your phone number to view and manage your bookings.</p>", unsafe_allow_html=True)

    phone = st.text_input("📱 Phone Number")

    if st.button("Load My Bookings"):
        if not phone.strip():
            st.warning("Please enter your phone number.")
        else:
            docs = db.collection("bookings").stream()
            found = False

            for doc in docs:
                booking = doc.to_dict()
                if booking.get("phone") == phone.strip():
                    found = True
                    status = booking.get("status", "Pending")
                    status_class = f"status-{status.lower()}"
                    st.markdown(f"""
                    <div class='booking-card'>
                        <div style='font-family:Cormorant Garamond;font-size:24px;color:#c9a84c;margin-bottom:8px'>
                            {booking.get('service')}
                        </div>
                        <div style='display:flex;gap:24px;flex-wrap:wrap;color:#888;font-size:13px;margin-bottom:12px'>
                            <span>📅 {booking.get('booking_date')}</span>
                            <span>🕐 {booking.get('time_slot')}</span>
                            <span>💰 ₹{booking.get('price', '—')}</span>
                        </div>
                        <span class='{status_class}'>{status}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"❌ Cancel Booking", key=f"cancel_{doc.id}"):
                        db.collection("bookings").document(doc.id).delete()
                        st.success("Booking cancelled.")
                        st.rerun()

            if not found:
                st.markdown("""
                <div style='text-align:center;padding:40px;color:#555'>
                    <div style='font-size:48px;margin-bottom:16px'>🔍</div>
                    <p>No bookings found for this phone number.</p>
                </div>
                """, unsafe_allow_html=True)

# ======================================================
# WORKER LOGIN
# ======================================================

elif mode == "🔒 Worker Login":
    st.markdown("<h1 class='section-heading'>🔒 Worker Dashboard</h1>", unsafe_allow_html=True)

    password = st.text_input("Password", type="password")

    if password == WORKER_PASSWORD:
        st.markdown("<div style='color:#3ab26e;margin-bottom:16px'>✅ Access Granted</div>", unsafe_allow_html=True)

        role = st.selectbox("Your Role", [
            "Massage Expert",
            "Makeup Artist",
            "Hair Stylist",
            "Nail Technician",
            "Skin Specialist",
            "Mehandi Artist",
            "Styling Expert"
        ])

        docs = db.collection("bookings").stream()
        bookings_for_role = [
            (doc.id, doc.to_dict()) for doc in docs
            if doc.to_dict().get("assigned_role") == role
        ]

        if not bookings_for_role:
            st.markdown("""
            <div style='text-align:center;padding:40px;color:#555'>
                <div style='font-size:48px;margin-bottom:12px'>🎉</div>
                <p>No pending bookings for your role.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:#888;margin-bottom:20px'>{len(bookings_for_role)} booking(s) assigned to you</p>", unsafe_allow_html=True)

        for doc_id, booking in bookings_for_role:
            status = booking.get("status", "Pending")
            st.markdown(f"""
            <div class='booking-card'>
                <div class='worker-badge'>{booking.get('assigned_role')}</div>
                <div style='font-family:Cormorant Garamond;font-size:26px;color:#c9a84c;margin-bottom:8px'>
                    {booking.get('service')}
                </div>
                <div style='color:#aaa;font-size:14px;margin-bottom:4px'>👤 {booking.get('customer_name')}</div>
                <div style='display:flex;gap:24px;flex-wrap:wrap;color:#666;font-size:13px;margin-bottom:12px'>
                    <span>📅 {booking.get('booking_date')}</span>
                    <span>🕐 {booking.get('time_slot')}</span>
                    <span>💰 ₹{booking.get('price','—')}</span>
                </div>
                <span class='status-{status.lower()}'>{status}</span>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Accept", key=f"a_{doc_id}"):
                    db.collection("bookings").document(doc_id).update({"status": "Accepted"})
                    st.rerun()
            with col2:
                if st.button("🏆 Complete", key=f"c_{doc_id}"):
                    booking["status"] = "Completed"
                    db.collection("completed_bookings").document(doc_id).set(booking)
                    db.collection("bookings").document(doc_id).delete()

                    customer_ref = db.collection("loyalty_points").document(booking["phone"])
                    customer_doc = customer_ref.get()
                    current_points = 0
                    if customer_doc.exists:
                        current_points = customer_doc.to_dict().get("points", 0)
                    customer_ref.set({
                        "customer_name": booking["customer_name"],
                        "phone": booking["phone"],
                        "points": current_points + 5
                    })

                    st.success("✅ Service completed! Customer earned 5 loyalty points. 💎")
                    st.rerun()

    elif password != "":
        st.error("Incorrect password.")

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class='salon-footer'>
    <div class='gold-divider'></div>
    <p>
        Crafted with elegance by
        <span>PNB Smart &amp; Luxurious Salon and MentorLoop EDU</span>
        &nbsp;·&nbsp; AI-Powered Beauty Experience
    </p>
</div>
""", unsafe_allow_html=True)
