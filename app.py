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
# WORKER NUMBERED IDs
# Each role has up to 3 numbered workers
# ======================================================

WORKER_ROLES = [
    "Massage Expert",
    "Makeup Artist",
    "Hair Stylist",
    "Nail Technician",
    "Skin Specialist",
    "Mehandi Artist",
    "Styling Expert"
]

WORKER_OPTIONS = []
for role in WORKER_ROLES:
    for n in range(1, 4):
        WORKER_OPTIONS.append(f"{role} #{n}")

# ======================================================
# DIGITAL PETS SHOP
# ======================================================

DIGITAL_PETS = [
    {
        "name": "Golden Kitty",
        "emoji": "🐱",
        "cost": 10,
        "rarity": "Common",
        "description": "A cheerful golden kitten who loves head scratches and warm laps."
    },
    {
        "name": "Pearl Bunny",
        "emoji": "🐰",
        "cost": 15,
        "rarity": "Common",
        "description": "A soft pearl-white bunny with dreamy eyes. Hops around your profile."
    },
    {
        "name": "Sapphire Pup",
        "emoji": "🐶",
        "cost": 20,
        "rarity": "Uncommon",
        "description": "A loyal sapphire-eyed puppy that never leaves your side."
    },
    {
        "name": "Rose Parrot",
        "emoji": "🦜",
        "cost": 25,
        "rarity": "Uncommon",
        "description": "A vibrant rose-feathered parrot that whispers beauty tips."
    },
    {
        "name": "Velvet Fox",
        "emoji": "🦊",
        "cost": 35,
        "rarity": "Rare",
        "description": "A mysterious velvet fox with a tail that shimmers like gold."
    },
    {
        "name": "Crystal Deer",
        "emoji": "🦌",
        "cost": 45,
        "rarity": "Rare",
        "description": "An ethereal crystal deer that glows under moonlight."
    },
    {
        "name": "Midnight Owl",
        "emoji": "🦉",
        "cost": 55,
        "rarity": "Epic",
        "description": "A wise midnight owl with ancient knowledge of beauty secrets."
    },
    {
        "name": "Aurora Dragon",
        "emoji": "🐉",
        "cost": 80,
        "rarity": "Legendary",
        "description": "The rarest of all — an aurora dragon who breathes golden light."
    },
    {
        "name": "Diamond Unicorn",
        "emoji": "🦄",
        "cost": 100,
        "rarity": "Mythic",
        "description": "A mythic diamond unicorn. The crown jewel of the PNB pet collection."
    },
]

RARITY_COLORS = {
    "Common": "#888",
    "Uncommon": "#3ab26e",
    "Rare": "#4a9eff",
    "Epic": "#a855f7",
    "Legendary": "#f97316",
    "Mythic": "#c9a84c"
}

# ======================================================
# SESSION STATE
# ======================================================

if "selected_service" not in st.session_state:
    st.session_state["selected_service"] = None
if "open_ai" not in st.session_state:
    st.session_state["open_ai"] = False
if "active_category" not in st.session_state:
    st.session_state["active_category"] = "All"
if "bookings_phone" not in st.session_state:
    st.session_state["bookings_phone"] = ""

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

.stTextInput input{
    color:#f5f0e8 !important;
    background:#1a1610 !important;
}

.stTextInput input::placeholder{
    color:#6a5e42 !important;
    opacity:1 !important;
}

.stTextInput input::-webkit-input-placeholder{ color:#6a5e42 !important; }
.stTextInput input::-moz-placeholder{ color:#6a5e42 !important; }
.stTextInput input:-ms-input-placeholder{ color:#6a5e42 !important; }

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
    ["💎 Services", "📅 My Bookings", "🐾 Pet Shop", "🏆 Leaderboard", "🔒 Worker Login"]
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
                    ).where("time_slot", "==", time_slot).where(
                        "service", "==", selected["name"]
                    ).stream()

                    if len(list(slot_docs)) >= 4:
                        st.error("⚠️ This service is fully booked for that slot (max 4). Please choose another time.")
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
    st.markdown("<p style='color:#666;margin-bottom:24px'>Enter your phone number to view and cancel your bookings.</p>", unsafe_allow_html=True)

    phone = st.text_input("📱 Phone Number")

    if st.button("Load My Bookings"):
        if not phone.strip():
            st.warning("Please enter your phone number.")
        else:
            st.session_state["bookings_phone"] = phone.strip()

    # Keep bookings visible after cancel rerun
    lookup_phone = st.session_state.get("bookings_phone", "")

    if lookup_phone:
        # Show loyalty points — always, even if 0
        loyalty_doc = db.collection("loyalty_points").document(lookup_phone).get()
        if loyalty_doc.exists:
            pts = loyalty_doc.to_dict().get("points", 0)
            cname = loyalty_doc.to_dict().get("customer_name", "Guest")
        else:
            pts = 0
            # Try to get name from a booking
            sample_docs = [d.to_dict() for d in db.collection("bookings").stream() if d.to_dict().get("phone") == lookup_phone]
            cname = sample_docs[0].get("customer_name", "Guest") if sample_docs else "Guest"

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(201,168,76,0.12),rgba(201,168,76,0.04));
            border:1px solid rgba(201,168,76,0.35);border-radius:16px;padding:20px 28px;
            margin-bottom:28px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;'>
            <div style='font-size:48px'>💎</div>
            <div>
                <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:26px'>{cname}</div>
                <div style='color:#888;font-size:12px;letter-spacing:1px;text-transform:uppercase;margin-top:4px'>Loyalty Points</div>
                <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:38px;font-weight:600'>{pts} pts</div>
                <div style='color:#666;font-size:12px;margin-top:4px'>🐾 Spend your points in the Pet Shop!</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        docs = list(db.collection("bookings").stream())
        my_bookings = [(doc.id, doc.to_dict()) for doc in docs if doc.to_dict().get("phone") == lookup_phone]

        if not my_bookings:
            st.markdown("""
            <div style='text-align:center;padding:40px;color:#555'>
                <div style='font-size:48px;margin-bottom:16px'>🔍</div>
                <p>No active bookings found for this phone number.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for doc_id, booking in my_bookings:
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
                        <span>👤 {booking.get('assigned_role','')}</span>
                    </div>
                    <span class='{status_class}'>● {status}</span>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"❌ Cancel this booking", key=f"cancel_{doc_id}"):
                    # Delete from bookings (removes from worker view too)
                    db.collection("bookings").document(doc_id).delete()
                    # Also clean up completed_bookings if it somehow ended up there
                    db.collection("completed_bookings").document(doc_id).delete()
                    st.success(f"✅ '{booking.get('service')}' booking cancelled successfully.")
                    st.rerun()

# ======================================================
# LEADERBOARD
# ======================================================

elif mode == "🏆 Leaderboard":
    st.markdown("<h1 class='section-heading'>🏆 Loyalty Leaderboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666;margin-bottom:28px'>Rankings by total wealth — current points plus the value of all owned pets.</p>", unsafe_allow_html=True)

    loyalty_docs = list(db.collection("loyalty_points").stream())
    leaderboard = []

    for doc in loyalty_docs:
        d = doc.to_dict()
        phone = d.get("phone", doc.id)
        name  = d.get("customer_name", "Guest")
        pts   = d.get("points", 0)

        # Add pet costs to wealth
        pet_doc = db.collection("owned_pets").document(phone).get()
        pet_names = pet_doc.to_dict().get("pets", []) if pet_doc.exists else []
        pet_wealth = sum(p["cost"] for p in DIGITAL_PETS if p["name"] in pet_names)
        pet_emojis = "".join(p["emoji"] for p in DIGITAL_PETS if p["name"] in pet_names)

        leaderboard.append({
            "name": name,
            "points": pts,
            "pet_wealth": pet_wealth,
            "total": pts + pet_wealth,
            "pets": pet_emojis,
            "pet_count": len(pet_names)
        })

    leaderboard.sort(key=lambda x: x["total"], reverse=True)

    MEDALS = ["🥇","🥈","🥉"]
    if not leaderboard:
        st.markdown("<div style='text-align:center;padding:60px;color:#555;font-size:18px'>No loyalty members yet. Complete a service to earn points!</div>", unsafe_allow_html=True)
    else:
        for rank, entry in enumerate(leaderboard):
            medal = MEDALS[rank] if rank < 3 else f"#{rank+1}"
            bg = "rgba(201,168,76,0.12)" if rank == 0 else ("rgba(180,180,180,0.07)" if rank == 1 else ("rgba(180,120,60,0.07)" if rank == 2 else "rgba(255,255,255,0.02)"))
            border = "#c9a84c" if rank == 0 else ("#aaa" if rank == 1 else ("#a06030" if rank == 2 else "rgba(255,255,255,0.06)"))
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {border};border-radius:16px;
                padding:18px 24px;margin-bottom:12px;
                display:flex;align-items:center;gap:20px;flex-wrap:wrap;'>
                <div style='font-size:32px;min-width:40px;text-align:center'>{medal}</div>
                <div style='flex:1;min-width:150px'>
                    <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:22px;font-weight:600'>{entry["name"]}</div>
                    <div style='color:#666;font-size:12px;margin-top:2px'>
                        💎 {entry["points"]} pts &nbsp;+&nbsp; 🐾 {entry["pet_wealth"]} pet value
                        {"&nbsp;&nbsp;" + entry["pets"] if entry["pets"] else ""}
                    </div>
                </div>
                <div style='text-align:right'>
                    <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:36px;font-weight:600;line-height:1'>{entry["total"]}</div>
                    <div style='color:#666;font-size:11px;letter-spacing:1px;text-transform:uppercase'>total wealth</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ======================================================
# PET SHOP
# ======================================================

elif mode == "🐾 Pet Shop":
    import streamlit.components.v1 as components
    import time as time_module

    st.markdown("<h1 class='section-heading'>🐾 Digital Pet Shop</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#888;margin-bottom:8px;line-height:1.7'>
    Earn <span style='color:#c9a84c;font-weight:600'>5 loyalty points</span> every time you complete a salon service.
    Spend them here to adopt a digital pet — then <b style='color:#c9a84c'>play with it in 3D!</b> 🌟
    </p>
    """, unsafe_allow_html=True)

    shop_phone = st.text_input("📱 Enter your phone number", key="shop_phone")

    if st.button("Check My Points & Shop"):
        if not shop_phone.strip():
            st.warning("Please enter your phone number.")
        else:
            st.session_state["shop_phone_verified"] = shop_phone.strip()
            st.session_state["playing_pet"] = None

    shop_phone_verified = st.session_state.get("shop_phone_verified", "")
    if "playing_pet" not in st.session_state:
        st.session_state["playing_pet"] = None

    if shop_phone_verified:
        loyalty_ref = db.collection("loyalty_points").document(shop_phone_verified)
        loyalty_doc = loyalty_ref.get()

        if loyalty_doc.exists:
            loyalty_data = loyalty_doc.to_dict()
            current_points = loyalty_data.get("points", 0)
            customer_name = loyalty_data.get("customer_name", "Guest")
        else:
            current_points = 0
            customer_name = "Guest"

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(201,168,76,0.15),rgba(201,168,76,0.04));
            border:1px solid rgba(201,168,76,0.4);border-radius:20px;padding:24px 32px;
            margin:20px 0 32px;display:flex;align-items:center;gap:24px;flex-wrap:wrap;'>
            <div style='font-size:56px'>💎</div>
            <div>
                <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:28px;margin-bottom:2px'>{customer_name}</div>
                <div style='color:#666;font-size:12px;letter-spacing:2px;text-transform:uppercase'>Your Balance</div>
                <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:52px;font-weight:600;line-height:1'>{current_points}</div>
                <div style='color:#888;font-size:13px'>loyalty points</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Load owned pets + their needs state
        owned_doc = db.collection("owned_pets").document(shop_phone_verified).get()
        owned_pets_data = owned_doc.to_dict() if owned_doc.exists else {}
        owned_pets = owned_pets_data.get("pets", [])
        pet_needs_all = owned_pets_data.get("needs", {})

        # Decay needs based on time since last save
        now_ts = time_module.time()
        last_saved_ts = owned_pets_data.get("last_saved", now_ts)
        hours_elapsed = min((now_ts - last_saved_ts) / 3600.0, 12)  # cap at 12h decay
        DECAY_PER_HOUR = 4  # each need drops 4 pts/hour

        for pname in owned_pets:
            if pname not in pet_needs_all:
                pet_needs_all[pname] = {"hunger": 80, "happiness": 80, "energy": 80, "cleanliness": 80}
            needs = pet_needs_all[pname]
            for k in ["hunger", "happiness", "energy", "cleanliness"]:
                needs[k] = max(0, needs[k] - DECAY_PER_HOUR * hours_elapsed)
            pet_needs_all[pname] = needs

        # ── PLAY MODE ──────────────────────────────────────────────
        playing = st.session_state["playing_pet"]

        if playing and playing in owned_pets:
            pet_info = next((p for p in DIGITAL_PETS if p["name"] == playing), None)
            needs = pet_needs_all.get(playing, {"hunger": 80, "happiness": 80, "energy": 80, "cleanliness": 80})

            rarity_color = RARITY_COLORS.get(pet_info["rarity"], "#888") if pet_info else "#c9a84c"

            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:16px;margin-bottom:24px'>
                <div style='font-size:42px'>{pet_info["emoji"] if pet_info else "🐾"}</div>
                <div>
                    <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:30px'>{playing}</div>
                    <div style='color:{rarity_color};font-size:11px;letter-spacing:2px;text-transform:uppercase'>
                        ✦ {pet_info["rarity"] if pet_info else ""} ✦
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Build needs color
            def needs_color(v):
                if v >= 60: return "#3ab26e"
                if v >= 30: return "#e0a030"
                return "#e05050"

            def needs_emoji(k, v):
                icons = {"hunger": "🍖", "happiness": "😊", "energy": "⚡", "cleanliness": "🛁"}
                if v < 20:
                    sad = {"hunger": "😵", "happiness": "😢", "energy": "😴", "cleanliness": "🤢"}
                    return sad[k]
                return icons[k]

            # Need bars
            h = int(needs["hunger"]); ha = int(needs["happiness"])
            e = int(needs["energy"]); c = int(needs["cleanliness"])

            st.markdown(f"""
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px'>
                {"".join([
                    f"""<div style='background:#161410;border:1px solid rgba(201,168,76,0.2);border-radius:14px;padding:16px'>
                        <div style='display:flex;justify-content:space-between;margin-bottom:8px'>
                            <span style='color:#aaa;font-size:13px;text-transform:uppercase;letter-spacing:1px'>
                                {needs_emoji(k,v)} {k.title()}
                            </span>
                            <span style='color:{needs_color(v)};font-weight:600;font-size:13px'>{int(v)}/100</span>
                        </div>
                        <div style='background:#0a0a0a;border-radius:8px;height:10px;overflow:hidden'>
                            <div style='width:{v}%;height:100%;background:{needs_color(v)};
                                border-radius:8px;transition:width 0.4s'></div>
                        </div>
                    </div>"""
                    for k, v in [("hunger", h), ("happiness", ha), ("energy", e), ("cleanliness", c)]
                ])}
            </div>
            """, unsafe_allow_html=True)

            # ── 3D THREE.JS PET SCENE ──────────────────────────────
            # Map pet to a color palette for its 3D body
            pet_colors = {
                "Golden Kitty":   {"body": "#f5c842", "eye": "#222", "accent": "#e0a020"},
                "Pearl Bunny":    {"body": "#f0eae0", "eye": "#ffb3c6", "accent": "#ddd0c8"},
                "Sapphire Pup":   {"body": "#5b8dd9", "eye": "#1a1a6e", "accent": "#3a6abf"},
                "Rose Parrot":    {"body": "#e8607a", "eye": "#222", "accent": "#c9a84c"},
                "Velvet Fox":     {"body": "#c0623a", "eye": "#1a0a00", "accent": "#8b3a1a"},
                "Crystal Deer":   {"body": "#b8e0f7", "eye": "#2255aa", "accent": "#7ec8e3"},
                "Midnight Owl":   {"body": "#2a2040", "eye": "#f0c040", "accent": "#4a3870"},
                "Aurora Dragon":  {"body": "#7b4fc4", "eye": "#00ffcc", "accent": "#c9a84c"},
                "Diamond Unicorn":{"body": "#f0f8ff", "eye": "#c9a84c", "accent": "#e8c0ff"},
            }
            pc = pet_colors.get(playing, {"body": "#c9a84c", "eye": "#222", "accent": "#a08030"})

            mood = "happy" if ha >= 50 else ("sad" if ha < 25 else "neutral")
            is_hungry = h < 30
            is_sleepy = e < 25
            is_dirty  = c < 25
            energy_zero = e == 0

            if energy_zero:   bubble_text = "😵 Too tired! Feed me!"
            elif is_sleepy:   bubble_text = "💤 Sleepy..."
            elif is_hungry:   bubble_text = "🍖 Hungry!"
            elif is_dirty:    bubble_text = "🛁 Need a bath!"
            elif mood == "happy": bubble_text = "😊 So happy!"
            elif mood == "sad":   bubble_text = "😢 Play with me!"
            else:             bubble_text = "👋 Hello!"

            # Pass energy state so JS can disable play
            three_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:linear-gradient(160deg,#0a0808,#130f0a); overflow:hidden; font-family:'Segoe UI',sans-serif; }}
  #c {{ display:block; width:100%; height:400px; }}
  #bubble {{
    position:absolute; top:14px; left:50%; transform:translateX(-50%);
    background:rgba(20,16,10,0.95); border:1.5px solid {pc['accent']};
    border-radius:24px; padding:8px 20px; color:#f5f0e8;
    font-size:14px; white-space:nowrap; pointer-events:none;
    box-shadow:0 4px 20px rgba(0,0,0,0.6);
  }}
  #ui {{
    position:absolute; bottom:0; left:0; right:0;
    background:linear-gradient(0deg,rgba(8,6,4,0.98),transparent);
    padding:12px 16px 16px;
    display:flex; gap:8px; justify-content:center; flex-wrap:wrap;
  }}
  .btn {{
    background:linear-gradient(135deg,#1e1a12,#2a2218);
    border:1px solid {pc['accent']}88;
    color:#c9a84c; border-radius:30px;
    padding:8px 18px; font-size:12px;
    cursor:pointer; letter-spacing:1px; text-transform:uppercase;
    transition:all 0.2s; font-weight:700;
  }}
  .btn:hover:not(:disabled) {{ background:{pc['accent']}22; border-color:{pc['accent']}; transform:translateY(-2px); }}
  .btn:active:not(:disabled) {{ transform:scale(0.95); }}
  .btn:disabled {{ opacity:0.3; cursor:not-allowed; }}
  #fb {{
    position:absolute; top:52px; left:50%; transform:translateX(-50%);
    color:#3ab26e; font-size:12px; font-weight:700; letter-spacing:1px;
    opacity:0; transition:opacity 0.3s; white-space:nowrap;
    text-shadow:0 0 8px #3ab26e88; pointer-events:none;
  }}
  #needs {{
    position:absolute; top:14px; right:14px;
    display:flex; flex-direction:column; gap:4px;
    background:rgba(10,8,6,0.85); border:1px solid rgba(201,168,76,0.2);
    border-radius:12px; padding:10px 12px; min-width:120px;
  }}
  .nb {{ display:flex; align-items:center; gap:6px; }}
  .nb-label {{ font-size:10px; color:#888; width:20px; text-align:center; }}
  .nb-track {{ flex:1; background:#0a0a0a; border-radius:4px; height:6px; overflow:hidden; }}
  .nb-fill {{ height:6px; border-radius:4px; transition:width 0.5s; }}
</style>
</head>
<body>
<div id="bubble">{bubble_text}</div>
<div id="fb"></div>
<div id="needs">
  <div class="nb"><span class="nb-label">🍖</span><div class="nb-track"><div class="nb-fill" id="b-hunger" style="width:{h}%;background:{('#3ab26e' if h>=60 else '#e0a030' if h>=30 else '#e05050')}"></div></div></div>
  <div class="nb"><span class="nb-label">⚡</span><div class="nb-track"><div class="nb-fill" id="b-energy" style="width:{e}%;background:{('#3ab26e' if e>=60 else '#e0a030' if e>=30 else '#e05050')}"></div></div></div>
  <div class="nb"><span class="nb-label">😊</span><div class="nb-track"><div class="nb-fill" id="b-happy" style="width:{ha}%;background:{('#3ab26e' if ha>=60 else '#e0a030' if ha>=30 else '#e05050')}"></div></div></div>
  <div class="nb"><span class="nb-label">🛁</span><div class="nb-track"><div class="nb-fill" id="b-clean" style="width:{c}%;background:{('#3ab26e' if c>=60 else '#e0a030' if c>=30 else '#e05050')}"></div></div></div>
</div>
<canvas id="c"></canvas>
<div id="ui">
  <button class="btn" id="btn-feed"  onclick="doAction('feed')">🍖 Feed</button>
  <button class="btn" id="btn-play"  onclick="doAction('play')"  {'disabled' if energy_zero else ''}>🎾 Play</button>
  <button class="btn" id="btn-sleep" onclick="doAction('sleep')">💤 Rest</button>
  <button class="btn" id="btn-bathe" onclick="doAction('bathe')">🛁 Bathe</button>
  <button class="btn" id="btn-pet"   onclick="doAction('pet')">✋ Pet</button>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const BODY_COLOR = "{pc['body']}";
const EYE_COLOR  = "{pc['eye']}";
const ACCENT     = "{pc['accent']}";
const MOOD       = "{mood}";

// Live need values (updated on action)
const needs = {{ hunger:{h}, energy:{e}, happiness:{ha}, cleanliness:{c} }};

function nc(v) {{ return v>=60?'#3ab26e':v>=30?'#e0a030':'#e05050'; }}
function updateBars() {{
  document.getElementById('b-hunger').style.width = needs.hunger+'%';
  document.getElementById('b-hunger').style.background = nc(needs.hunger);
  document.getElementById('b-energy').style.width = needs.energy+'%';
  document.getElementById('b-energy').style.background = nc(needs.energy);
  document.getElementById('b-happy').style.width  = needs.happiness+'%';
  document.getElementById('b-happy').style.background = nc(needs.happiness);
  document.getElementById('b-clean').style.width  = needs.cleanliness+'%';
  document.getElementById('b-clean').style.background = nc(needs.cleanliness);
  // Disable play if energy=0
  document.getElementById('btn-play').disabled = needs.energy <= 0;
  // Update bubble
  let txt = '👋 Hello!';
  if(needs.energy<=0)    txt='😵 Too tired! Feed me!';
  else if(needs.energy<25) txt='💤 Sleepy...';
  else if(needs.hunger<30) txt='🍖 Hungry!';
  else if(needs.cleanliness<25) txt='🛁 Need a bath!';
  else if(needs.happiness>=50) txt='😊 So happy!';
  else if(needs.happiness<25)  txt='😢 Play with me!';
  document.getElementById('bubble').textContent = txt;
}}

// ── Scene ─────────────────────────────────────────────────────
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({{canvas, antialias:true, alpha:true}});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

function resize() {{
  const w = canvas.parentElement.clientWidth;
  renderer.setSize(w, 400);
  camera.aspect = w/400; camera.updateProjectionMatrix();
}}

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x0a0808, 8, 22);
const camera = new THREE.PerspectiveCamera(50,1,0.1,100);
camera.position.set(0,2.2,6); camera.lookAt(0,0.8,0);

scene.add(new THREE.AmbientLight(0xfff5e0, 0.5));
const sun = new THREE.DirectionalLight(0xffe8b0, 1.4);
sun.position.set(4,8,5); sun.castShadow=true; sun.shadow.mapSize.set(1024,1024);
scene.add(sun);
const fill = new THREE.PointLight(parseInt(ACCENT.replace('#','0x')),0.6,12);
fill.position.set(-3,2,2); scene.add(fill);
scene.add(Object.assign(new THREE.DirectionalLight(0x8888ff,0.3),{{position:new THREE.Vector3(-4,3,-4)}}));

// Floor
const floor = new THREE.Mesh(new THREE.CircleGeometry(4,64), new THREE.MeshStandardMaterial({{color:0x1a1410,roughness:0.9}}));
floor.rotation.x=-Math.PI/2; floor.receiveShadow=true; scene.add(floor);
const ring = new THREE.Mesh(new THREE.RingGeometry(1.3,1.45,64), new THREE.MeshBasicMaterial({{color:parseInt(ACCENT.replace('#','0x')),side:THREE.DoubleSide}}));
ring.rotation.x=-Math.PI/2; ring.position.y=0.002; scene.add(ring);

// Materials
const bodyMat  = new THREE.MeshStandardMaterial({{color:parseInt(BODY_COLOR.replace('#','0x')),roughness:0.5,metalness:0.08}});
const accentMat= new THREE.MeshStandardMaterial({{color:parseInt(ACCENT.replace('#','0x')),roughness:0.4,metalness:0.3}});
const eyeMat   = new THREE.MeshStandardMaterial({{color:parseInt(EYE_COLOR.replace('#','0x')),roughness:0.2,metalness:0.5,emissive:parseInt(EYE_COLOR.replace('#','0x')),emissiveIntensity:0.4}});
const noseMat  = new THREE.MeshStandardMaterial({{color:0x1a1010,roughness:0.3}});
const whiteMat = new THREE.MeshStandardMaterial({{color:0xffffff,roughness:0.3}});

function mk(geo,mat,x,y,z,rx=0,ry=0,rz=0) {{
  const m=new THREE.Mesh(geo,mat);
  m.position.set(x,y,z); m.rotation.set(rx,ry,rz);
  m.castShadow=true; m.receiveShadow=true; return m;
}}

// ── Build pet body ────────────────────────────────────────────
const pet=new THREE.Group(); scene.add(pet);
const body  = mk(new THREE.SphereGeometry(0.72,32,32),bodyMat,0,0.75,0);
const belly = mk(new THREE.SphereGeometry(0.42,24,24),whiteMat,0,0.68,0.52);
belly.scale.set(1,1.1,0.5);
const head  = mk(new THREE.SphereGeometry(0.55,32,32),bodyMat,0,1.7,0);
const earL  = mk(new THREE.ConeGeometry(0.2,0.5,16),bodyMat,-0.35,2.32,0,0,0,-0.3);
const earR  = mk(new THREE.ConeGeometry(0.2,0.5,16),bodyMat, 0.35,2.32,0,0,0, 0.3);
const earIL = mk(new THREE.ConeGeometry(0.1,0.3,12),accentMat,-0.35,2.3,0.06,0,0,-0.3);
const earIR = mk(new THREE.ConeGeometry(0.1,0.3,12),accentMat, 0.35,2.3,0.06,0,0, 0.3);
const eyeL  = mk(new THREE.SphereGeometry(0.1,16,16),eyeMat,-0.2,1.78,0.46);
const eyeR  = mk(new THREE.SphereGeometry(0.1,16,16),eyeMat, 0.2,1.78,0.46);
const shL   = mk(new THREE.SphereGeometry(0.035,8,8),whiteMat,-0.17,1.8,0.54);
const shR   = mk(new THREE.SphereGeometry(0.035,8,8),whiteMat, 0.23,1.8,0.54);
const nose  = mk(new THREE.SphereGeometry(0.07,12,12),noseMat,0,1.62,0.52);
nose.scale.set(1.2,0.8,0.8);
const mouthGeo = new THREE.TorusGeometry(0.13,0.025,8,20,Math.PI);
const mouth = mk(mouthGeo,noseMat,0,1.48,0.5);
if(MOOD==='sad') {{ mouth.rotation.set(Math.PI,0,0); mouth.position.y=1.54; }}
const tailC = new THREE.CatmullRomCurve3([new THREE.Vector3(0,0.6,-0.6),new THREE.Vector3(-0.4,1.1,-0.9),new THREE.Vector3(-0.6,1.6,-0.5)]);
const tail  = new THREE.Mesh(new THREE.TubeGeometry(tailC,20,0.09,8,false),bodyMat);
tail.castShadow=true;
const tailTip = mk(new THREE.SphereGeometry(0.15,12,12),accentMat,-0.6,1.6,-0.5);
const legGeo  = new THREE.CylinderGeometry(0.12,0.1,0.5,14);
const legL = mk(legGeo,bodyMat,-0.32,0.3,0.42,0.3,0,0);
const legR = mk(legGeo,bodyMat, 0.32,0.3,0.42,0.3,0,0);
const pawL = mk(new THREE.SphereGeometry(0.14,12,12),accentMat,-0.38,0.08,0.6);
const pawR = mk(new THREE.SphereGeometry(0.14,12,12),accentMat, 0.38,0.08,0.6);
const blL  = mk(legGeo,bodyMat,-0.38,0.26,-0.35,-0.2,0, 0.1);
const blR  = mk(legGeo,bodyMat, 0.38,0.26,-0.35,-0.2,0,-0.1);
const collar = new THREE.Mesh(new THREE.TorusGeometry(0.38,0.055,12,40),accentMat);
collar.position.set(0,1.22,0); collar.rotation.x=Math.PI/6; collar.castShadow=true;
pet.add(body,belly,head,earL,earR,earIL,earIR,eyeL,eyeR,shL,shR,nose,mouth,tail,tailTip,legL,legR,pawL,pawR,blL,blR,collar);

// Sparkles
const sparkles=[];
for(let i=0;i<16;i++) {{
  const sp=new THREE.Mesh(new THREE.SphereGeometry(0.025,6,6),new THREE.MeshBasicMaterial({{color:parseInt(ACCENT.replace('#','0x')),transparent:true,opacity:0.8}}));
  sp.userData={{angle:Math.random()*Math.PI*2,radius:1.1+Math.random()*0.5,speed:0.4+Math.random()*0.6,yBase:0.5+Math.random()*1.5,yAmp:0.2+Math.random()*0.3,yPhase:Math.random()*Math.PI*2}};
  scene.add(sp); sparkles.push(sp);
}}

// Sleep Z
const zMeshes=[];
for(let i=0;i<3;i++) {{
  const z=new THREE.Mesh(new THREE.SphereGeometry(0.08,6,6),new THREE.MeshBasicMaterial({{color:0xaaaacc,transparent:true,opacity:0}}));
  z.userData={{delay:i*0.8,life:0}}; scene.add(z); zMeshes.push(z);
}}

// ── Actions ───────────────────────────────────────────────────
let anim='idle', animT=0, petY=0, tailSwing=0, eyeBlinkT=0, msgTimer=0;
const fbEl=document.getElementById('fb');
const MSGS={{
  feed: ["Yum yum! 🍖","So tasty!","More please!"],
  play: ["Wheee! 🎾","So fun!","Catch me!"],
  sleep:["Zzz... 💤","So cozy...","Night night!"],
  bathe:["Splish splash! 🛁","Squeaky clean!","Ahh, fresh!"],
  pet:  ["Purrrr... 💕","*happy wiggle*","Love you! 💖"]
}};

function showFb(t) {{ fbEl.textContent=t; fbEl.style.opacity='1'; msgTimer=2.5; }}

function doAction(type) {{
  // Energy=0: only feed works
  if(needs.energy<=0 && type!=='feed') {{
    showFb('😵 No energy! Feed first!'); return;
  }}
  anim = type==='feed'?'shake':type==='play'?'jump':type==='sleep'?'sleep':type==='bathe'?'spin':'wave';
  animT=0;
  const msgs=MSGS[type]; showFb(msgs[Math.floor(Math.random()*msgs.length)]);
  // Update local needs
  const boosts={{feed:{{hunger:25,happiness:5}},play:{{happiness:20,energy:-8}},sleep:{{energy:30,happiness:5}},bathe:{{cleanliness:25}},pet:{{happiness:10}}}};
  const b=boosts[type]||{{}};
  for(const [k,v] of Object.entries(b)) {{ needs[k]=Math.min(100,Math.max(0,(needs[k]||0)+v)); }}
  updateBars();
  // Tell Streamlit
  window.parent.postMessage({{type:'pet_action',action:type,needs:{{...needs}}}}, '*');
}}

// ── Render loop ───────────────────────────────────────────────
const clock=new THREE.Clock();
function animate() {{
  requestAnimationFrame(animate);
  const dt=clock.getDelta(), t=clock.getElapsedTime();
  animT+=dt;
  let bodyY=petY, bodyRot=0, headTilt=0;

  if(anim==='idle') {{ bodyY=Math.sin(t*1.8)*0.06; tailSwing=Math.sin(t*3)*0.35; headTilt=Math.sin(t*1.2)*0.08; }}
  if(anim==='jump') {{
    if(animT<0.35) petY+=4*dt; else petY=Math.max(0,petY-6*dt);
    if(petY<=0&&animT>0.5&&animT>1.2) {{ petY=0; anim='idle'; }}
    bodyY=petY; tailSwing=Math.sin(animT*10)*0.5;
  }}
  if(anim==='spin') {{ bodyRot=animT*6; tailSwing=0.6; if(animT>1.5){{anim='idle';pet.rotation.y=0;}} }}
  if(anim==='wave') {{ legL.rotation.z=Math.sin(animT*8)*0.8-0.5; tailSwing=Math.sin(animT*5)*0.5; if(animT>1.4){{legL.rotation.z=0;anim='idle';}} }}
  if(anim==='shake') {{ pet.position.x=Math.sin(animT*20)*0.12; tailSwing=Math.sin(animT*8)*0.5; if(animT>0.8){{pet.position.x=0;anim='idle';}} }}
  if(anim==='sleep') {{
    bodyY=Math.sin(animT*1.2)*0.05-0.1; headTilt=-0.3; eyeL.scale.y=0.2; eyeR.scale.y=0.2;
    zMeshes.forEach((z,i)=>{{ z.userData.life+=dt; const l=z.userData.life-z.userData.delay; if(l>0){{ z.position.set(-0.3+i*0.15,2.1+l*0.5,0.5); z.material.opacity=Math.max(0,0.8-l*0.6); z.scale.setScalar(1+l*0.5); if(l>1.4)z.userData.life=0; }} }});
    if(animT>2.2){{ anim='idle'; eyeL.scale.y=1; eyeR.scale.y=1; zMeshes.forEach(z=>z.material.opacity=0); }}
  }}

  pet.position.y=bodyY;
  if(anim==='spin') pet.rotation.y=bodyRot;
  else if(anim!=='shake') pet.rotation.y=Math.sin(t*0.5)*0.12;
  head.rotation.z=headTilt; tail.rotation.y=tailSwing;
  tailTip.position.x=-0.6+Math.sin(tailSwing)*0.2;

  eyeBlinkT-=dt; if(eyeBlinkT<=0) eyeBlinkT=2.5+Math.random()*3;
  const blink=eyeBlinkT<0.12?0.1:1;
  if(anim!=='sleep') {{ eyeL.scale.y=blink; eyeR.scale.y=blink; }}

  sparkles.forEach(sp=>{{ const d=sp.userData; d.angle+=d.speed*dt; sp.position.set(Math.cos(d.angle)*d.radius,d.yBase+Math.sin(t*1.5+d.yPhase)*d.yAmp,Math.sin(d.angle)*d.radius); sp.material.opacity=0.5+0.3*Math.sin(t*2+d.yPhase); }});

  if(msgTimer>0){{ msgTimer-=dt; if(msgTimer<=0) fbEl.style.opacity='0'; }}
  renderer.render(scene,camera);
}}
window.addEventListener('resize',resize); resize(); animate();
</script>
</body>
</html>
"""
            components.html(three_html, height=430, scrolling=False)

            # ── Single save-back button row ──────────────────────────
            # (Visual actions are in the 3D canvas; this just saves state)
            st.markdown("<p style='color:#555;font-size:12px;text-align:center;margin-top:4px'>👆 Use the buttons inside the 3D view to interact with your pet</p>", unsafe_allow_html=True)

            bcol1, bcol2 = st.columns(2)
            with bcol1:
                if st.button("💾 Save Pet State", key="save_needs"):
                    db.collection("owned_pets").document(shop_phone_verified).set({
                        "phone": shop_phone_verified,
                        "pets": owned_pets,
                        "needs": pet_needs_all,
                        "last_saved": time_module.time()
                    })
                    st.success("✅ Saved!")
                    st.rerun()
            with bcol2:
                if st.button("⬅ Back to My Pets", key="back_pets"):
                    st.session_state["playing_pet"] = None
                    st.rerun()

        # ── PET ROSTER (not playing) ───────────────────────────────
        else:
            if owned_pets:
                st.markdown("<h3 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:26px;margin-bottom:16px'>🏡 Your Pets</h3>", unsafe_allow_html=True)
                pet_cols = st.columns(min(len(owned_pets), 3))
                for pi, pname in enumerate(owned_pets):
                    pet_data = next((p for p in DIGITAL_PETS if p["name"] == pname), None)
                    if not pet_data: continue
                    rarity_color = RARITY_COLORS.get(pet_data["rarity"], "#888")
                    needs = pet_needs_all.get(pname, {"hunger":80,"happiness":80,"energy":80,"cleanliness":80})

                    # Save decayed needs back
                    pet_needs_all[pname] = needs

                    def bar(v, color):
                        return f"<div style='background:#0a0a0a;border-radius:4px;height:6px;width:100%;margin:3px 0'><div style='width:{int(v)}%;height:6px;background:{color};border-radius:4px'></div></div>"

                    nc = lambda v: "#3ab26e" if v>=60 else ("#e0a030" if v>=30 else "#e05050")

                    with pet_cols[pi % 3]:
                        st.markdown(f"""
                        <div style='background:linear-gradient(145deg,#161410,#1e1a12);
                            border:1px solid {rarity_color}55;border-radius:20px;padding:22px;
                            text-align:center;margin-bottom:8px;'>
                            <div style='font-size:56px;margin-bottom:10px'>{pet_data["emoji"]}</div>
                            <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:20px;margin-bottom:4px'>{pname}</div>
                            <div style='color:{rarity_color};font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px'>✦ {pet_data["rarity"]} ✦</div>
                            <div style='text-align:left;font-size:11px;color:#777;letter-spacing:0.5px'>
                                🍖 Hunger
                                {bar(needs['hunger'], nc(needs['hunger']))}
                                😊 Happiness
                                {bar(needs['happiness'], nc(needs['happiness']))}
                                ⚡ Energy
                                {bar(needs['energy'], nc(needs['energy']))}
                                🛁 Cleanliness
                                {bar(needs['cleanliness'], nc(needs['cleanliness']))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"▶ Play with {pname}", key=f"play_{pi}"):
                            # Save decayed needs before entering play
                            db.collection("owned_pets").document(shop_phone_verified).set({
                                "phone": shop_phone_verified,
                                "pets": owned_pets,
                                "needs": pet_needs_all,
                                "last_saved": time_module.time()
                            })
                            st.session_state["playing_pet"] = pname
                            st.rerun()

            # ── PET SHOP ──────────────────────────────────────────
            st.markdown("<h3 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:26px;margin:28px 0 16px'>🛒 Adopt a Pet</h3>", unsafe_allow_html=True)

            pet_cols = st.columns(3)
            for pi, pet in enumerate(DIGITAL_PETS):
                rarity_color = RARITY_COLORS.get(pet["rarity"], "#888")
                already_owned = pet["name"] in owned_pets
                can_afford = current_points >= pet["cost"]

                with pet_cols[pi % 3]:
                    st.markdown(f"""
                    <div style='background:linear-gradient(145deg,#161410,#1e1a12);
                        border:1px solid {rarity_color}55;border-radius:20px;padding:24px;
                        text-align:center;margin-bottom:8px;
                        {"opacity:0.45;" if already_owned else ""}'>
                        <div style='font-size:60px;margin-bottom:10px'>{pet["emoji"]}</div>
                        <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:22px;margin-bottom:4px'>{pet["name"]}</div>
                        <div style='color:{rarity_color};font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px'>✦ {pet["rarity"]} ✦</div>
                        <div style='color:#888;font-size:13px;line-height:1.5;margin-bottom:14px'>{pet["description"]}</div>
                        <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:28px;font-weight:600'>{pet["cost"]} pts</div>
                        {"<div style='color:#3ab26e;font-size:12px;margin-top:8px;letter-spacing:1px'>✅ OWNED</div>" if already_owned else ""}
                        {"<div style='color:#555;font-size:12px;margin-top:8px'>Not enough points</div>" if not can_afford and not already_owned else ""}
                    </div>
                    """, unsafe_allow_html=True)

                    if not already_owned:
                        if st.button(f"🐾 Adopt", key=f"adopt_{pi}", disabled=not can_afford):
                            new_points = current_points - pet["cost"]
                            loyalty_ref.set({
                                "customer_name": customer_name,
                                "phone": shop_phone_verified,
                                "points": new_points
                            })
                            new_owned = owned_pets + [pet["name"]]
                            pet_needs_all[pet["name"]] = {"hunger":80,"happiness":80,"energy":80,"cleanliness":80}
                            db.collection("owned_pets").document(shop_phone_verified).set({
                                "phone": shop_phone_verified,
                                "pets": new_owned,
                                "needs": pet_needs_all,
                                "last_saved": time_module.time()
                            })
                            st.success(f"🎉 You adopted {pet['emoji']} {pet['name']}!")
                            st.rerun()

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
        <span>PNB Smart &amp; Luxurious Salon</span>
        &nbsp;·&nbsp; AI-Powered Beauty Experience
    </p>
</div>
""", unsafe_allow_html=True)
