import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from datetime import datetime
import random
import string

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

# WhatsApp API (Twilio or 360dialog etc.)
# Expected secrets: WA_API_URL, WA_API_TOKEN, WA_FROM_NUMBER
WA_API_URL   = st.secrets.get("WA_API_URL", "")
WA_API_TOKEN = st.secrets.get("WA_API_TOKEN", "")
WA_FROM      = st.secrets.get("WA_FROM_NUMBER", "")

# ======================================================
# WORKER PASSWORD & ROLES
# ======================================================

WORKER_PASSWORD = "PNB2024"

WORKER_ROLES = [
    "Massage Expert",
    "Makeup Artist",
    "Hair Stylist",
    "Nail Technician",
    "Skin Specialist",
    "Mehandi Artist",
    "Styling Expert"
]

# ======================================================
# DIGITAL PETS
# ======================================================

DIGITAL_PETS = [
    {"name": "Golden Kitty",    "emoji": "🐱", "cost": 10,  "rarity": "Common",    "description": "A cheerful golden kitten who loves head scratches and warm laps."},
    {"name": "Pearl Bunny",     "emoji": "🐰", "cost": 15,  "rarity": "Common",    "description": "A soft pearl-white bunny with dreamy eyes. Hops around your profile."},
    {"name": "Sapphire Pup",    "emoji": "🐶", "cost": 20,  "rarity": "Uncommon",  "description": "A loyal sapphire-eyed puppy that never leaves your side."},
    {"name": "Rose Parrot",     "emoji": "🦜", "cost": 25,  "rarity": "Uncommon",  "description": "A vibrant rose-feathered parrot that whispers beauty tips."},
    {"name": "Velvet Fox",      "emoji": "🦊", "cost": 35,  "rarity": "Rare",      "description": "A mysterious velvet fox with a tail that shimmers like gold."},
    {"name": "Crystal Deer",    "emoji": "🦌", "cost": 45,  "rarity": "Rare",      "description": "An ethereal crystal deer that glows under moonlight."},
    {"name": "Midnight Owl",    "emoji": "🦉", "cost": 55,  "rarity": "Epic",      "description": "A wise midnight owl with ancient knowledge of beauty secrets."},
    {"name": "Aurora Dragon",   "emoji": "🐉", "cost": 80,  "rarity": "Legendary", "description": "The rarest of all — an aurora dragon who breathes golden light."},
    {"name": "Diamond Unicorn", "emoji": "🦄", "cost": 100, "rarity": "Mythic",    "description": "A mythic diamond unicorn. The crown jewel of the PNB pet collection."},
]

RARITY_COLORS = {
    "Common":    "#888",
    "Uncommon":  "#3ab26e",
    "Rare":      "#4a9eff",
    "Epic":      "#a855f7",
    "Legendary": "#f97316",
    "Mythic":    "#c9a84c"
}

# ======================================================
# SESSION STATE
# ======================================================

defaults = {
    "selected_service":     None,
    "open_ai":              False,
    "bookings_phone":       "",
    "shop_phone_verified":  "",
    "otp_sent":             False,
    "otp_code":             "",
    "otp_phone":            "",
    "otp_booking_data":     None,
    "booking_confirmed":    False,
    "worker_otp_result":    {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================================================
# TIME SLOTS
# ======================================================

TIME_SLOTS = [
    "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM",
    "2:00 PM",  "3:00 PM",  "4:00 PM",  "5:00 PM",
    "6:00 PM",  "7:00 PM",  "8:00 PM",  "9:00 PM"
]

# ======================================================
# SERVICES MENU  (same as original, trimmed for brevity
# — full list preserved below)
# ======================================================

services = [
    # ---------- MASSAGE ----------
    {"name": "Ayurvedic Massage (45 mins)",  "duration": "45 mins",  "price": 1500, "role": "Massage Expert",  "category": "Massage",             "description": "Traditional Ayurvedic herbal massage using warm medicated oils to balance doshas, relieve stress and revitalize the body.",             "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
    {"name": "Ayurvedic Massage (60 mins)",  "duration": "60 mins",  "price": 1800, "role": "Massage Expert",  "category": "Massage",             "description": "Extended traditional Ayurvedic herbal massage for deep relaxation, improved circulation, and holistic wellness.",                       "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
    {"name": "Aroma Therapy (45 mins)",      "duration": "45 mins",  "price": 2000, "role": "Massage Expert",  "category": "Massage",             "description": "Luxury aromatherapy session with premium essential oils to calm the mind and refresh the senses.",                                    "image": "https://images.unsplash.com/photo-1515377905703-c4788e51af15"},
    {"name": "Aroma Therapy (60 mins)",      "duration": "60 mins",  "price": 2500, "role": "Massage Expert",  "category": "Massage",             "description": "Extended luxury aromatherapy session for deep stress relief and full body relaxation using curated essential oil blends.",             "image": "https://images.unsplash.com/photo-1515377905703-c4788e51af15"},
    {"name": "Deep Tissue Massage",          "duration": "60 mins",  "price": 3000, "role": "Massage Expert",  "category": "Massage",             "description": "Therapeutic deep muscle recovery massage targeting chronic tension, knots, and muscle fatigue.",                                     "image": "https://images.unsplash.com/photo-1519823551278-64ac92734fb1"},
    {"name": "Body Polish",                  "duration": "60 mins",  "price": 3500, "role": "Massage Expert",  "category": "Massage",             "description": "Full body exfoliation and polishing treatment to reveal radiant, smooth and glowing skin.",                                          "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    # ---------- SKIN ----------
    {"name": "Wart Removal",                 "duration": "20 mins",  "price": 200,  "role": "Skin Specialist", "category": "Skin",                "description": "Safe and precise wart removal treatment performed by trained skin specialists using advanced techniques.",                           "image": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908"},
    {"name": "Nose Piercing",                "duration": "15 mins",  "price": 600,  "role": "Skin Specialist", "category": "Skin",                "description": "Professional nose piercing with hygienic, sterilized equipment and premium jewelry options.",                                      "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"},
    {"name": "Ear Piercing (Single)",        "duration": "10 mins",  "price": 800,  "role": "Skin Specialist", "category": "Skin",                "description": "Single ear piercing with sterilized tools, safe and quick procedure with aftercare guidance.",                                     "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"},
    {"name": "Ear Piercing (Double)",        "duration": "15 mins",  "price": 1200, "role": "Skin Specialist", "category": "Skin",                "description": "Double ear piercing for both ears with premium sterilized equipment and stylish jewelry.",                                         "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"},
    # ---------- MEHANDI & STYLING ----------
    {"name": "Mehandi",                      "duration": "30 mins",  "price": 500,  "role": "Mehandi Artist",  "category": "Mehandi & Styling",   "description": "Beautiful intricate henna mehandi designs crafted by skilled artists for festive and bridal occasions.",                            "image": "https://images.unsplash.com/photo-1532030543767-ea4b0f5aa7a5"},
    {"name": "Fashion Plait",                "duration": "20 mins",  "price": 500,  "role": "Hair Stylist",    "category": "Mehandi & Styling",   "description": "Trendy and elegant fashion plait hairstyle crafted to complement any look or occasion.",                                           "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e"},
    {"name": "Flower Plait Fixing",          "duration": "25 mins",  "price": 800,  "role": "Hair Stylist",    "category": "Mehandi & Styling",   "description": "Gorgeous flower plait adorned with fresh or artificial flowers for weddings and celebrations.",                                     "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e"},
    # ---------- MAKEUP ----------
    {"name": "Light Makeup",                 "duration": "45 mins",  "price": 2500, "role": "Makeup Artist",   "category": "Makeup",              "description": "Fresh, natural light makeup look perfect for daytime events and casual outings.",                                                  "image": "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"},
    {"name": "Party Makeup",                 "duration": "60 mins",  "price": 3500, "role": "Makeup Artist",   "category": "Makeup",              "description": "Bold and glamorous party makeup for an unforgettable evening look.",                                                              "image": "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"},
    {"name": "Bridal Trial Makeup",          "duration": "90 mins",  "price": 2500, "role": "Makeup Artist",   "category": "Makeup",              "description": "Pre-wedding trial session to perfect your bridal look and ensure flawless results on the big day.",                               "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"},
    {"name": "Bridal Makeup",                "duration": "120 mins", "price": 7500, "role": "Makeup Artist",   "category": "Makeup",              "description": "Complete luxury bridal makeover package — because your wedding day deserves nothing less than perfection.",                        "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"},
    {"name": "Reception Makeup",             "duration": "90 mins",  "price": 5000, "role": "Makeup Artist",   "category": "Makeup",              "description": "Elegant and radiant reception makeup designed to glow under lights and cameras.",                                                 "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"},
    # ---------- SAREE ----------
    {"name": "Half Saree Draping",           "duration": "20 mins",  "price": 300,  "role": "Styling Expert",  "category": "Saree & Draping",     "description": "Neat and graceful half-saree draping for a traditional and elegant look.",                                                        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"},
    {"name": "Saree Draping",                "duration": "25 mins",  "price": 500,  "role": "Styling Expert",  "category": "Saree & Draping",     "description": "Perfect saree draping by skilled experts to ensure you look flawless and feel confident.",                                        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"},
    {"name": "Saree Pre-Plating",            "duration": "30 mins",  "price": 700,  "role": "Styling Expert",  "category": "Saree & Draping",     "description": "Professional saree pre-plating and pinning for a crisp, well-structured drape that lasts all day.",                             "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"},
    # ---------- PEDICURE ----------
    {"name": "Basic Pedicure",               "duration": "30 mins",  "price": 500,  "role": "Nail Technician", "category": "Pedicure",            "description": "Classic pedicure with soaking, scrubbing, nail shaping and a fresh coat of colour.",                                               "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Spa Pedicure",                 "duration": "45 mins",  "price": 600,  "role": "Nail Technician", "category": "Pedicure",            "description": "Relaxing spa pedicure with moisturizing treatment and gentle massage for soft, happy feet.",                                       "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Crystal Pedicure",             "duration": "50 mins",  "price": 900,  "role": "Nail Technician", "category": "Pedicure",            "description": "Luxurious crystal pedicure for deeply nourished, glowing skin and beautifully shaped nails.",                                     "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Aromatic Pedicure",            "duration": "55 mins",  "price": 1200, "role": "Nail Technician", "category": "Pedicure",            "description": "Aromatic pedicure infused with essential oils for a sensory treat and deeply refreshed feet.",                                    "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Heel Peel Pedicure",           "duration": "60 mins",  "price": 1300, "role": "Nail Technician", "category": "Pedicure",            "description": "Specialized heel peel treatment to eliminate rough, cracked heels leaving feet baby soft.",                                        "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "PNB Signature Pedicure",       "duration": "75 mins",  "price": 1600, "role": "Nail Technician", "category": "Pedicure",            "description": "Our exclusive signature pedicure — a premium full-care ritual designed for ultimate indulgence.",                                  "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Nail Cut & Colouring",         "duration": "20 mins",  "price": 200,  "role": "Nail Technician", "category": "Pedicure",            "description": "Neat nail cutting and a vibrant colour application for a polished, put-together look.",                                            "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Bomb Pedicure",                "duration": "90 mins",  "price": 2000, "role": "Nail Technician", "category": "Pedicure",            "description": "The ultimate luxury bomb pedicure — an explosive combination of exfoliation, massage and glamour.",                                "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    # ---------- MANICURE ----------
    {"name": "Basic Manicure",               "duration": "30 mins",  "price": 300,  "role": "Nail Technician", "category": "Manicure",            "description": "Classic manicure with soaking, cuticle care, nail shaping and colour application.",                                               "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Spa Manicure",                 "duration": "45 mins",  "price": 500,  "role": "Nail Technician", "category": "Manicure",            "description": "Relaxing spa manicure with moisturizing treatment and a soothing hand massage.",                                                  "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Crystal Spa Manicure",         "duration": "50 mins",  "price": 750,  "role": "Nail Technician", "category": "Manicure",            "description": "Luxury crystal spa manicure for beautifully nourished hands and flawless nails.",                                                "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Nail Filing & Colouring",      "duration": "15 mins",  "price": 200,  "role": "Nail Technician", "category": "Manicure",            "description": "Quick nail filing and colour application for a neat and stylish finish.",                                                         "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Colouring Only",               "duration": "10 mins",  "price": 100,  "role": "Nail Technician", "category": "Manicure",            "description": "Simple and quick nail colour application in your choice of shade.",                                                               "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Nail Filing Only",             "duration": "10 mins",  "price": 50,   "role": "Nail Technician", "category": "Manicure",            "description": "Precise nail shaping and filing for a clean, well-groomed look.",                                                                "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "French Polish",                "duration": "20 mins",  "price": 250,  "role": "Nail Technician", "category": "Manicure",            "description": "Classic French polish for timeless, elegant nails with a white tip and nude base.",                                              "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Gel Polish",                   "duration": "30 mins",  "price": 500,  "role": "Nail Technician", "category": "Manicure",            "description": "Long-lasting gel polish for chip-free, glossy nails that stay perfect for weeks.",                                               "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Gel Polish Removal",           "duration": "20 mins",  "price": 200,  "role": "Nail Technician", "category": "Manicure",            "description": "Safe and gentle gel polish removal without damaging the natural nail.",                                                          "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Bomb Manicure",                "duration": "75 mins",  "price": 1800, "role": "Nail Technician", "category": "Manicure",            "description": "Our ultimate bomb manicure — a complete luxury hand ritual for beautifully pampered hands.",                                    "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    # ---------- HAIR TREATMENTS ----------
    {"name": "Perming (Small)",              "duration": "90 mins",  "price": 2000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Create bouncy, beautiful curls with professional perming treatment for short/small sections.",                                    "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Perming (Medium)",             "duration": "120 mins", "price": 3000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Professional perming for medium-length hair with long-lasting, voluminous curls.",                                               "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Perming (Large)",              "duration": "150 mins", "price": 4000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Full perming treatment for long or thick hair with stunning, defined curls.",                                                     "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Smoothening (Small)",          "duration": "90 mins",  "price": 3000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Hair smoothening treatment for short hair — eliminate frizz and add shine.",                                                     "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Smoothening (Medium)",         "duration": "120 mins", "price": 4000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Smoothening treatment for medium hair — silky, manageable, frizz-free results.",                                                 "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Smoothening (Large)",          "duration": "150 mins", "price": 5000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Smoothening treatment for long/thick hair — dramatically smoother, shinier tresses.",                                            "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Rebonding (Small)",            "duration": "120 mins", "price": 4000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Rebonding for short hair — permanently straighten and restructure for ultra-sleek results.",                                     "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Rebonding (Medium)",           "duration": "150 mins", "price": 5000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Rebonding for medium hair — salon-perfect straight hair with long-lasting effects.",                                            "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Rebonding (Large)",            "duration": "180 mins", "price": 6000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Rebonding for long or thick hair — complete transformation to glass-smooth straight hair.",                                     "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Straightening (Small)",        "duration": "90 mins",  "price": 5000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Professional straightening for short hair with premium products for lasting sleekness.",                                         "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Straightening (Medium)",       "duration": "120 mins", "price": 6000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Professional straightening for medium hair — smooth, glossy, and beautifully managed.",                                         "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Straightening (Large)",        "duration": "150 mins", "price": 7000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Professional straightening for long/thick hair — perfectly straight, mirror-shiny results.",                                    "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Keratin Treatment",            "duration": "120 mins", "price": 5000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Premium keratin treatment to deeply nourish, smoothen and add brilliant shine to your hair.",                                    "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Express Keratin Treatment",    "duration": "90 mins",  "price": 4500, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Quick express keratin treatment for a faster dose of frizz-free, glossy hair.",                                                  "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Deep Conditioning",            "duration": "60 mins",  "price": 3000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Intensive deep conditioning treatment to restore moisture, strength, and brilliance to damaged hair.",                            "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Hair Scrub",                   "duration": "30 mins",  "price": 800,  "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Scalp purifying hair scrub to remove buildup, unclog follicles and promote healthy hair growth.",                               "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    {"name": "Metal DK Treatment",           "duration": "45 mins",  "price": 1000, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Metal DK bond-rebuilding treatment to repair chemical damage and restore hair integrity.",                                       "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    {"name": "Hair Treatment",               "duration": "45 mins",  "price": 1300, "role": "Hair Stylist",    "category": "Hair Treatments",     "description": "Targeted professional hair treatment customized to your hair type and concern.",                                                  "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    # ---------- HAIR COLOUR ----------
    {"name": "Colour Application Only",              "duration": "40 mins",  "price": 300,  "role": "Hair Stylist", "category": "Hair Colour",  "description": "Professional colour application to achieve rich, vibrant hair colour.",                                                              "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    {"name": "Colour Application + Wash (Basic)",    "duration": "60 mins",  "price": 550,  "role": "Hair Stylist", "category": "Hair Colour",  "description": "Colour application followed by a professional wash and blow-dry for a finished look.",                                               "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    {"name": "Colour Application (Full)",            "duration": "60 mins",  "price": 500,  "role": "Hair Stylist", "category": "Hair Colour",  "description": "Full head colour application for complete colour coverage and transformation.",                                                     "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    {"name": "Colour Application + Wash (Premium)",  "duration": "75 mins",  "price": 800,  "role": "Hair Stylist", "category": "Hair Colour",  "description": "Premium full colour application with professional wash and conditioning treatment.",                                                 "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    {"name": "Touch Up",                             "duration": "45 mins",  "price": 1000, "role": "Hair Stylist", "category": "Hair Colour",  "description": "Precise root touch-up to refresh your colour and keep it looking salon-fresh.",                                                     "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    # ---------- HAIRCUT ----------
    {"name": "Haircut (Below 8 yrs)",  "duration": "20 mins",  "price": 200,  "role": "Hair Stylist",    "category": "Haircut",       "description": "Gentle and fun haircut designed specially for children below 8 years.",                                                     "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"},
    {"name": "Basic Haircut",          "duration": "30 mins",  "price": 250,  "role": "Hair Stylist",    "category": "Haircut",       "description": "Classic stylish haircut shaped to flatter your features and suit your style.",                                              "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"},
    {"name": "Split Ends Trim",        "duration": "25 mins",  "price": 400,  "role": "Hair Stylist",    "category": "Haircut",       "description": "Precision split-end removal to restore healthy, smooth hair ends without losing length.",                                  "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"},
    {"name": "Advanced Haircut",       "duration": "45 mins",  "price": 500,  "role": "Hair Stylist",    "category": "Haircut",       "description": "Expert advanced haircut with precision layering and styling tailored to your hair type.",                                 "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"},
    # ---------- HAIR WASH ----------
    {"name": "Hair Wash + Conditioner (Til/Coconut Oil Massage)",        "duration": "30 mins", "price": 300, "role": "Hair Stylist", "category": "Hair Wash", "description": "Nourishing hair wash with conditioner, preceded by a relaxing traditional oil head massage.",                    "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    {"name": "Hair Wash + Conditioner (Olive/Aroma/Cooling Oil Massage)","duration": "35 mins", "price": 350, "role": "Hair Stylist", "category": "Hair Wash", "description": "Revitalizing hair wash with conditioner after an indulgent premium oil head massage.",                             "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    # ---------- FACE TREATMENTS ----------
    {"name": "Young Face Pack",    "duration": "30 mins", "price": 300,  "role": "Skin Specialist", "category": "Face Treatments", "description": "Hydrating and brightening face pack to give your skin a youthful, dewy glow.",                                          "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "White Face Pack",    "duration": "30 mins", "price": 300,  "role": "Skin Specialist", "category": "Face Treatments", "description": "Brightening white face pack for a luminous, even-toned and radiant complexion.",                                        "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "Charcoal Pack",      "duration": "35 mins", "price": 350,  "role": "Skin Specialist", "category": "Face Treatments", "description": "Deep-cleansing activated charcoal face pack to purify pores and detox the skin.",                                       "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "Tan Pack",           "duration": "45 mins", "price": 600,  "role": "Skin Specialist", "category": "Face Treatments", "description": "Effective de-tan face pack to reverse sun damage and restore skin's natural brightness.",                              "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "Charcoal Face Mask", "duration": "40 mins", "price": 750,  "role": "Skin Specialist", "category": "Face Treatments", "description": "Premium activated charcoal face mask for deep pore purification and skin detox.",                                       "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "Gold Face Mask",     "duration": "45 mins", "price": 800,  "role": "Skin Specialist", "category": "Face Treatments", "description": "Luxury 24k gold face mask to boost radiance, reduce fine lines and illuminate your skin.",                             "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    # ---------- QUICK MASSAGES ----------
    {"name": "Hand Massage",        "duration": "20 mins", "price": 250, "role": "Massage Expert", "category": "Quick Massages", "description": "Soothing hand massage to relieve tension and leave your hands feeling soft and revitalized.",                            "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
    {"name": "Foot Work Massage",   "duration": "25 mins", "price": 300, "role": "Massage Expert", "category": "Quick Massages", "description": "Revitalizing foot massage targeting pressure points to relieve fatigue and improve circulation.",                        "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
    {"name": "Back Energy Massage", "duration": "30 mins", "price": 400, "role": "Massage Expert", "category": "Quick Massages", "description": "Energizing back massage to release muscle knots, reduce tension and restore vitality.",                                 "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
]

# ======================================================
# HELPER: Generate OTP
# ======================================================

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# ======================================================
# HELPER: Send WhatsApp OTP via API
# ======================================================

def send_whatsapp_otp(phone: str, otp: str, customer_name: str) -> bool:
    """
    Send OTP via WhatsApp Business API.
    Supports Twilio-style and Meta 360dialog-style payloads.
    Configure WA_API_URL, WA_API_TOKEN, WA_FROM_NUMBER in secrets.
    Phone must include country code, e.g. +919876543210
    """
    if not WA_API_URL or not WA_API_TOKEN:
        # Fallback: log OTP to console (dev mode)
        print(f"[DEV] WhatsApp OTP for {phone}: {otp}")
        return True

    # Normalize phone
    phone_clean = phone.strip().replace(" ", "").replace("-", "")
    if not phone_clean.startswith("+"):
        phone_clean = "+91" + phone_clean  # default India

    message_body = (
        f"💎 *PNB Smart & Luxurious Salon*\n\n"
        f"Hello {customer_name}! Your booking OTP is:\n\n"
        f"*{otp}*\n\n"
        f"Please share this with your PNB worker to confirm the service.\n"
        f"Valid for this session only. Do not share with anyone else."
    )

    try:
        headers = {
            "Authorization": f"Bearer {WA_API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_clean,
            "type": "text",
            "text": {"body": message_body}
        }
        # Support Twilio format too
        if "twilio" in WA_API_URL.lower():
            payload = {
                "From": f"whatsapp:{WA_FROM}",
                "To": f"whatsapp:{phone_clean}",
                "Body": message_body.replace("*", "")
            }
            resp = requests.post(WA_API_URL, data=payload, headers=headers, timeout=10)
        else:
            resp = requests.post(WA_API_URL, json=payload, headers=headers, timeout=10)

        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"[WhatsApp] Error: {e}")
        return False

# ======================================================
# CSS — ULTRA PREMIUM
# ======================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap');

*{font-family:'Jost',sans-serif;}

.stApp{
    background:linear-gradient(160deg,#080808 0%,#0e0d0b 40%,#110e08 100%);
    color:#f5f0e8;
}

h1,h2,h3{font-family:'Cormorant Garamond',serif !important; color:#c9a84c !important;}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0a0805,#130e06) !important;
    border-right:1px solid rgba(201,168,76,0.18) !important;
}
section[data-testid="stSidebar"] *{color:#e8d5a3 !important;}

/* ── Inputs ── */
.stTextInput>div>div{
    background:#151208 !important;
    border-color:rgba(201,168,76,0.25) !important;
    color:#f5f0e8 !important;
    border-radius:10px !important;
}
.stSelectbox>div>div{
    background:#151208 !important;
    border-color:rgba(201,168,76,0.25) !important;
    color:#f5f0e8 !important;
    border-radius:10px !important;
}
.stDateInput>div>div{
    background:#151208 !important;
    border-color:rgba(201,168,76,0.25) !important;
    border-radius:10px !important;
}

/* ── Buttons ── */
.stButton>button{
    background:linear-gradient(135deg,#a07820,#c9a84c,#a07820) !important;
    background-size:200% auto !important;
    color:#080808 !important;
    border:none !important;
    border-radius:10px !important;
    font-family:'Jost',sans-serif !important;
    font-weight:600 !important;
    letter-spacing:1.5px !important;
    text-transform:uppercase !important;
    font-size:11px !important;
    padding:12px 32px !important;
    transition:background-position 0.4s, box-shadow 0.3s !important;
    box-shadow: 0 4px 20px rgba(201,168,76,0.15) !important;
}
.stButton>button:hover{
    background-position:right center !important;
    box-shadow:0 6px 30px rgba(201,168,76,0.3) !important;
}

/* AI float button */
.ai-circle .stButton>button{
    border-radius:50% !important;
    height:52px !important;
    width:52px !important;
    font-size:18px !important;
    padding:0 !important;
}

/* ── Header ── */
.salon-header{
    text-align:center;
    padding:56px 20px 36px;
    position:relative;
    overflow:hidden;
}
.salon-header::before{
    content:'';
    position:absolute;
    top:-60px; left:50%; transform:translateX(-50%);
    width:600px; height:300px;
    background:radial-gradient(ellipse,rgba(201,168,76,0.06) 0%,transparent 70%);
    pointer-events:none;
}
.salon-title{
    font-family:'Cormorant Garamond',serif;
    font-size:70px;
    font-weight:300;
    color:#c9a84c;
    letter-spacing:6px;
    line-height:1.1;
    margin:0;
    text-shadow:0 0 60px rgba(201,168,76,0.2);
}
.salon-sub{
    color:#7a6640;
    font-size:12px;
    letter-spacing:5px;
    text-transform:uppercase;
    margin-top:12px;
}
.gold-divider{
    width:120px; height:1px;
    background:linear-gradient(90deg,transparent,#c9a84c,transparent);
    margin:18px auto;
}

/* ── Section heading ── */
.section-heading{
    font-family:'Cormorant Garamond',serif;
    font-size:38px; color:#c9a84c;
    margin:8px 0 24px;
    letter-spacing:2px;
}

/* ── Service card ── */
.service-card-body{
    background:linear-gradient(145deg,#100e0a,#1a1610);
    border:1px solid rgba(201,168,76,0.12);
    border-radius:0 0 16px 16px;
    padding:16px;
    margin-bottom:4px;
    transition:border-color 0.3s;
}
.service-card-body:hover{border-color:rgba(201,168,76,0.4);}

.service-name{
    font-family:'Cormorant Garamond',serif;
    font-size:20px; color:#c9a84c;
    margin:0 0 6px; line-height:1.3;
}
.service-desc{color:#777; font-size:13px; line-height:1.5; margin-bottom:10px;}
.service-price{
    font-family:'Cormorant Garamond',serif;
    font-size:26px; font-weight:600; color:#c9a84c;
}
.service-duration{color:#555; font-size:11px; letter-spacing:1px; text-transform:uppercase;}

/* ── Worker badge ── */
.worker-badge{
    display:inline-block;
    background:rgba(201,168,76,0.08);
    border:1px solid rgba(201,168,76,0.25);
    border-radius:20px;
    padding:4px 14px; font-size:11px;
    color:#c9a84c; letter-spacing:1px;
    text-transform:uppercase; margin-bottom:8px;
}

/* ── Booking card ── */
.booking-card{
    background:linear-gradient(145deg,#0f0d0a,#1a1610);
    border:1px solid rgba(201,168,76,0.15);
    border-radius:14px; padding:20px; margin-bottom:16px;
}
.status-pending  {color:#e0a030; font-weight:600;}
.status-accepted {color:#3ab26e; font-weight:600;}
.status-completed{color:#666;    font-weight:600;}

/* ── OTP box ── */
.otp-box{
    background:linear-gradient(135deg,rgba(201,168,76,0.06),rgba(201,168,76,0.02));
    border:1px solid rgba(201,168,76,0.3);
    border-radius:16px; padding:24px;
    text-align:center; margin:16px 0;
}
.otp-code{
    font-family:'Cormorant Garamond',serif;
    font-size:52px; font-weight:600;
    color:#c9a84c; letter-spacing:12px;
    text-shadow:0 0 30px rgba(201,168,76,0.4);
}

/* ── Confetti/balloons container ── */
.balloon-canvas{
    position:fixed; top:0; left:0;
    width:100vw; height:100vh;
    pointer-events:all;
    z-index:99999;
}

/* ── Footer ── */
.salon-footer{
    text-align:center; padding:32px 20px; margin-top:40px;
    border-top:1px solid rgba(201,168,76,0.08);
    color:#3a3020; font-size:11px; letter-spacing:2px; text-transform:uppercase;
}
.salon-footer span{color:#c9a84c;}

</style>
""", unsafe_allow_html=True)

# ======================================================
# REALISTIC BALLOON POPPING  (injected once after confirm)
# ======================================================

BALLOON_JS = """
<canvas id="pnb-balloon-canvas" class="balloon-canvas"></canvas>
<script>
(function(){
const canvas = document.getElementById('pnb-balloon-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const COLORS = ['#c9a84c','#f7d98b','#e8b86d','#fff8e7','#f5c842',
                '#ff6b6b','#ff9f9f','#ff4444','#ff8c00','#ffd700',
                '#a855f7','#e879f9','#4ade80','#60a5fa'];

const POP_SFX = ['\uD83D\uDCA5'];  // 💥

class Balloon {
  constructor(){
    this.reset(true);
  }
  reset(initial){
    this.x = Math.random() * canvas.width;
    this.y = initial ? canvas.height + Math.random() * canvas.height : canvas.height + 60;
    this.r = 28 + Math.random() * 22;
    this.color = COLORS[Math.floor(Math.random()*COLORS.length)];
    this.vy = -(1.4 + Math.random() * 2.2);
    this.vx = (Math.random()-0.5)*0.8;
    this.sway = 0;
    this.swaySpeed = 0.02 + Math.random()*0.015;
    this.alpha = 1;
    this.popped = false;
    this.popProgress = 0;
    this.popParticles = [];
    this.string = Math.random()*30+20;
    this.wobble = 0;
    this.wobbleSpeed = 0.04+Math.random()*0.03;
  }
  update(){
    if(this.popped){
      this.popProgress += 0.07;
      this.popParticles.forEach(p=>{
        p.x += p.vx; p.y += p.vy; p.vy += 0.18;
        p.alpha -= 0.035; p.r *= 0.97;
      });
      return this.popProgress < 1.2;
    }
    this.wobble += this.wobbleSpeed;
    this.sway += this.swaySpeed;
    this.x += this.vx + Math.sin(this.sway)*0.6;
    this.y += this.vy;
    return this.y + this.r > -20;
  }
  drawBalloon(){
    if(this.popped){
      this.popParticles.forEach(p=>{
        if(p.alpha<=0) return;
        ctx.save(); ctx.globalAlpha=p.alpha;
        ctx.fillStyle=p.color;
        ctx.beginPath();
        ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fill();
        ctx.restore();
      });
      return;
    }
    ctx.save();
    ctx.translate(this.x, this.y);
    const scaleX = 1 + Math.sin(this.wobble)*0.03;
    const scaleY = 1 - Math.sin(this.wobble)*0.03;
    ctx.scale(scaleX, scaleY);

    // shadow
    ctx.shadowColor = 'rgba(0,0,0,0.25)';
    ctx.shadowBlur = 12;
    ctx.shadowOffsetX = 4; ctx.shadowOffsetY = 6;

    // body
    const grad = ctx.createRadialGradient(-this.r*0.3,-this.r*0.35,this.r*0.05,0,0,this.r*1.05);
    grad.addColorStop(0,'rgba(255,255,255,0.55)');
    grad.addColorStop(0.25,this.color);
    grad.addColorStop(1, this.darken(this.color,60));
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.ellipse(0,0,this.r,this.r*1.18,0,0,Math.PI*2);
    ctx.fill();

    // highlight
    ctx.shadowBlur=0; ctx.shadowOffsetX=0; ctx.shadowOffsetY=0;
    const hl = ctx.createRadialGradient(-this.r*0.28,-this.r*0.38,this.r*0.02,-this.r*0.22,-this.r*0.3,this.r*0.38);
    hl.addColorStop(0,'rgba(255,255,255,0.7)');
    hl.addColorStop(1,'rgba(255,255,255,0)');
    ctx.fillStyle=hl;
    ctx.beginPath();
    ctx.ellipse(-this.r*0.22,-this.r*0.35,this.r*0.36,this.r*0.22,-0.4,0,Math.PI*2);
    ctx.fill();

    // knot
    ctx.fillStyle=this.darken(this.color,80);
    ctx.beginPath();
    ctx.ellipse(0,this.r*1.18,this.r*0.12,this.r*0.11,0,0,Math.PI*2);
    ctx.fill();

    // string
    ctx.strokeStyle='rgba(201,168,76,0.5)';
    ctx.lineWidth=1.2;
    ctx.beginPath();
    ctx.moveTo(0,this.r*1.3);
    ctx.quadraticCurveTo(this.r*0.18,this.r*1.6+this.string/2, 0,this.r*1.3+this.string);
    ctx.stroke();

    ctx.restore();
  }
  pop(){
    if(this.popped) return;
    this.popped=true;
    for(let i=0;i<18;i++){
      const angle=Math.random()*Math.PI*2;
      const spd=3+Math.random()*5;
      this.popParticles.push({
        x:this.x, y:this.y,
        vx:Math.cos(angle)*spd,
        vy:Math.sin(angle)*spd - 3,
        r:3+Math.random()*5,
        color:COLORS[Math.floor(Math.random()*COLORS.length)],
        alpha:1
      });
    }
  }
  hitTest(mx,my){
    if(this.popped) return false;
    const dx=mx-this.x, dy=my-this.y;
    return Math.sqrt(dx*dx+dy*dy) < this.r*1.18;
  }
  darken(hex,amt){
    let c=hex.replace('#','');
    if(c.length===3) c=c.split('').map(x=>x+x).join('');
    const num=parseInt(c,16);
    const r=Math.max(0,((num>>16)&255)-amt);
    const g=Math.max(0,((num>>8)&255)-amt);
    const b=Math.max(0,(num&255)-amt);
    return '#'+[r,g,b].map(v=>v.toString(16).padStart(2,'0')).join('');
  }
}

const balloons = Array.from({length:22},()=>new Balloon());
let running = true;
let elapsed = 0;

canvas.addEventListener('click',e=>{
  const rect=canvas.getBoundingClientRect();
  const mx=e.clientX-rect.left, my=e.clientY-rect.top;
  balloons.forEach(b=>{ if(b.hitTest(mx,my)) b.pop(); });
});
canvas.addEventListener('mousemove',e=>{
  const rect=canvas.getBoundingClientRect();
  const mx=e.clientX-rect.left, my=e.clientY-rect.top;
  let any=false;
  balloons.forEach(b=>{ if(b.hitTest(mx,my)){ any=true; }});
  canvas.style.cursor=any?'pointer':'default';
});

function loop(){
  if(!running) return;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  elapsed++;

  // spawn fresh when one goes off screen
  for(let i=balloons.length-1;i>=0;i--){
    const alive=balloons[i].update();
    balloons[i].drawBalloon();
    if(!alive){
      balloons.splice(i,1);
      balloons.push(new Balloon());
    }
  }

  // auto-dismiss after 9s
  if(elapsed > 540){
    canvas.style.transition='opacity 0.8s';
    canvas.style.opacity='0';
    setTimeout(()=>{ running=false; canvas.remove(); },900);
  }
  requestAnimationFrame(loop);
}
loop();
})();
</script>
"""

# ======================================================
# HEADER
# ======================================================

st.markdown("""
<div class='salon-header'>
    <p class='salon-sub'>Welcome to</p>
    <h1 class='salon-title'>PNB Smart &amp; Luxurious Salon</h1>
    <div class='gold-divider'></div>
    <p style='color:#5a4e30;font-size:12px;letter-spacing:3px;'>AI-POWERED BEAUTY &amp; WELLNESS EXPERIENCE</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR NAV
# ======================================================

mode = st.sidebar.radio(
    "Navigation",
    ["💎 Services", "📅 My Bookings", "🐾 Pet Shop", "🔒 Worker Login"]
)

# ======================================================
# ░░░ SERVICES MODE ░░░
# ======================================================

if mode == "💎 Services":

    col1, col2 = st.columns([10, 1])
    with col1:
        search = st.text_input("🔍 Search services...", placeholder="e.g. keratin, bridal, pedicure")
    with col2:
        st.markdown("<div class='ai-circle'>", unsafe_allow_html=True)
        if st.button("✨"):
            st.session_state["selected_service"] = None
            st.session_state["open_ai"] = True
        st.markdown("</div>", unsafe_allow_html=True)

    categories = sorted(list(set([s["category"] for s in services])))
    category = st.selectbox("Filter by Category", ["All"] + categories)

    filtered = [
        s for s in services
        if (category == "All" or s["category"] == category)
        and search.lower() in s["name"].lower()
    ]

    if filtered:
        st.markdown(f"""
        <div class='section-heading'>
            {category if category != 'All' else 'All Services'}
            <span style='font-size:16px;color:#444;margin-left:12px;font-family:Jost;'>
                {len(filtered)} services
            </span>
        </div>""", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, service in enumerate(filtered):
        with cols[i % 3]:
            st.image(service["image"], use_container_width=True)
            st.markdown(f"""
            <div class='service-card-body'>
                <div class='service-name'>{service['name']}</div>
                <div class='service-desc'>{service['description'][:80]}...</div>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div class='service-price'>₹{service['price']:,}</div>
                    <div class='service-duration'>⏱ {service['duration']}</div>
                </div>
            </div>""", unsafe_allow_html=True)
            if st.button("View & Book", key=f"open_{i}"):
                st.session_state["open_ai"] = False
                st.session_state["selected_service"] = service
                st.session_state["otp_sent"] = False
                st.session_state["otp_code"] = ""
                st.session_state["otp_booking_data"] = None
                st.session_state["booking_confirmed"] = False

    # --------------------------------------------------
    # SERVICE DETAIL DIALOG
    # --------------------------------------------------

    if st.session_state["selected_service"] is not None:
        selected = st.session_state["selected_service"]

        @st.dialog(f"✨ {selected['name']}", width="large")
        def service_popup():
            # Show balloon canvas if just confirmed
            if st.session_state.get("booking_confirmed"):
                st.markdown(BALLOON_JS, unsafe_allow_html=True)
                st.session_state["booking_confirmed"] = False

            col_img, col_info = st.columns([1, 1])
            with col_img:
                st.image(selected["image"], use_container_width=True)
            with col_info:
                st.markdown(f"<h2 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:32px'>{selected['name']}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#999;line-height:1.7'>{selected['description']}</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='margin:14px 0;'>
                    <span style='background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.25);
                        border-radius:20px;padding:4px 12px;font-size:11px;color:#c9a84c;
                        letter-spacing:1px;text-transform:uppercase;margin-right:8px'>
                        ⏱ {selected['duration']}
                    </span>
                    <span style='background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.25);
                        border-radius:20px;padding:4px 12px;font-size:11px;color:#c9a84c;
                        letter-spacing:1px;text-transform:uppercase'>
                        👤 {selected['role']}
                    </span>
                </div>
                <div style='font-family:Cormorant Garamond;font-size:44px;color:#c9a84c;font-weight:600;margin:12px 0'>
                    ₹{selected['price']:,}
                </div>""", unsafe_allow_html=True)

            st.markdown("<hr style='border-color:rgba(201,168,76,0.1);margin:20px 0'>", unsafe_allow_html=True)
            st.markdown("<h3 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:24px;margin-bottom:16px'>📋 Book This Service</h3>", unsafe_allow_html=True)

            # ── Step 1: fill booking details ──
            if not st.session_state["otp_sent"]:
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    booking_date  = st.date_input("📅 Booking Date")
                    customer_name = st.text_input("👤 Your Name")
                with bcol2:
                    time_slot      = st.selectbox("🕐 Time Slot", TIME_SLOTS)
                    customer_phone = st.text_input("📱 WhatsApp Number (with country code)")

                if st.button("📲 Send OTP to WhatsApp", use_container_width=True):
                    if not customer_name.strip() or not customer_phone.strip():
                        st.error("Please fill in your name and WhatsApp number.")
                    else:
                        slot_docs = list(db.collection("bookings").where(
                            "booking_date", "==", str(booking_date)
                        ).where("time_slot", "==", time_slot).where(
                            "service", "==", selected["name"]
                        ).stream())

                        if len(slot_docs) >= 4:
                            st.error("⚠️ This slot is fully booked (max 4). Please choose another time.")
                        else:
                            otp = generate_otp(6)
                            ok  = send_whatsapp_otp(customer_phone.strip(), otp, customer_name.strip())
                            if ok:
                                st.session_state["otp_code"]  = otp
                                st.session_state["otp_phone"] = customer_phone.strip()
                                st.session_state["otp_sent"]  = True
                                st.session_state["otp_booking_data"] = {
                                    "customer_name":  customer_name.strip(),
                                    "phone":          customer_phone.strip(),
                                    "service":        selected["name"],
                                    "booking_date":   str(booking_date),
                                    "time_slot":      time_slot,
                                    "assigned_role":  selected["role"],
                                    "price":          selected["price"],
                                }
                                st.success("✅ OTP sent to your WhatsApp! Please check and enter below.")
                                st.rerun()
                            else:
                                st.error("⚠️ Failed to send WhatsApp OTP. Please check your number or try again.")

            # ── Step 2: verify OTP ──
            else:
                booking = st.session_state["otp_booking_data"]
                st.markdown(f"""
                <div style='background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.2);
                    border-radius:12px;padding:16px 20px;margin-bottom:16px;'>
                    <div style='color:#c9a84c;font-size:13px;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px'>Booking Summary</div>
                    <div style='color:#e8d5a3;font-size:15px;'>{booking['service']}</div>
                    <div style='color:#888;font-size:13px;margin-top:4px;'>
                        📅 {booking['booking_date']} &nbsp;·&nbsp; 🕐 {booking['time_slot']}
                        &nbsp;·&nbsp; 💰 ₹{booking['price']:,}
                    </div>
                </div>
                <p style='color:#888;font-size:13px;margin-bottom:8px;'>
                    An OTP was sent to <span style='color:#c9a84c'>{st.session_state['otp_phone']}</span> via WhatsApp.
                    Enter it below to confirm your booking.
                </p>""", unsafe_allow_html=True)

                entered_otp = st.text_input("🔐 Enter OTP", max_chars=6, placeholder="6-digit code")

                col_v, col_r = st.columns([2, 1])
                with col_v:
                    if st.button("💎 Verify & Confirm Booking", use_container_width=True):
                        if entered_otp.strip() == st.session_state["otp_code"]:
                            # Save to Firestore
                            try:
                                resp = requests.post(
                                    AI_API_URL,
                                    headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
                                    json={"messages": [{"role": "user", "content": f"In 2-3 sentences, give a warm, luxurious, welcoming tip about: {selected['name']}."}]},
                                    timeout=10
                                )
                                ai_reply = resp.json()["choices"][0]["message"]["content"]
                            except Exception:
                                ai_reply = f"Thank you for booking {selected['name']}. We look forward to pampering you!"

                            db.collection("bookings").add({
                                **booking,
                                "status":     "Pending",
                                "created_at": str(datetime.now())
                            })

                            st.session_state["booking_confirmed"] = True
                            st.session_state["otp_sent"]          = False
                            st.session_state["otp_code"]          = ""

                            st.success("✅ Booking confirmed!")
                            st.markdown(f"""
                            <div style='background:rgba(201,168,76,0.07);border:1px solid rgba(201,168,76,0.22);
                                border-radius:12px;padding:18px;margin-top:12px;color:#c9a84c;
                                font-style:italic;line-height:1.7;font-size:14px;'>
                                ✨ {ai_reply}
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<p style='color:#888;font-size:12px;margin-top:8px;'>🎈 Click the balloons to pop them!</p>", unsafe_allow_html=True)
                            st.markdown(BALLOON_JS, unsafe_allow_html=True)
                        else:
                            st.error("❌ Incorrect OTP. Please check your WhatsApp and try again.")

                with col_r:
                    if st.button("↩ Change Details"):
                        st.session_state["otp_sent"] = False
                        st.rerun()

            if st.button("✕ Close", use_container_width=False):
                st.session_state["selected_service"] = None
                st.session_state["otp_sent"] = False
                st.rerun()

        service_popup()

    # --------------------------------------------------
    # AI POPUP
    # --------------------------------------------------

    if st.session_state["open_ai"]:
        @st.dialog("✨ PNB Beauty AI Assistant", width="large")
        def ai_popup():
            st.markdown("""
            <p style='color:#888;line-height:1.7;margin-bottom:16px'>
            Ask anything about beauty, skincare, haircare, makeup, wellness or our services.
            </p>""", unsafe_allow_html=True)
            user_question = st.text_input("💬 Your Question", placeholder="e.g. What treatment is best for frizzy hair?")
            if st.button("✨ Ask AI", use_container_width=True):
                if user_question.strip():
                    with st.spinner("Consulting our beauty expert..."):
                        try:
                            resp = requests.post(
                                AI_API_URL,
                                headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
                                json={"messages": [{"role": "user", "content": f"You are a luxury salon AI beauty consultant for PNB Smart & Luxurious Salon. Answer helpfully and warmly: {user_question}"}]},
                                timeout=15
                            )
                            ai_reply = resp.json()["choices"][0]["message"]["content"]
                            st.markdown(f"""
                            <div style='background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.22);
                                border-radius:12px;padding:20px;color:#e8d5a3;line-height:1.8;'>
                                {ai_reply}
                            </div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(str(e))
            if st.button("✕ Close AI"):
                st.session_state["open_ai"] = False
                st.rerun()
        ai_popup()


# ======================================================
# ░░░ MY BOOKINGS ░░░
# ======================================================

elif mode == "📅 My Bookings":
    st.markdown("<h1 class='section-heading'>📅 My Bookings</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#555;margin-bottom:24px'>Enter your WhatsApp number to view and cancel your bookings.</p>", unsafe_allow_html=True)

    phone = st.text_input("📱 Phone Number (with country code)")
    if st.button("Load My Bookings"):
        if not phone.strip():
            st.warning("Please enter your phone number.")
        else:
            st.session_state["bookings_phone"] = phone.strip()

    lookup_phone = st.session_state.get("bookings_phone", "")

    if lookup_phone:
        # Loyalty points display
        loyalty_doc = db.collection("loyalty_points").document(lookup_phone).get()
        if loyalty_doc.exists:
            pts   = loyalty_doc.to_dict().get("points", 0)
            cname = loyalty_doc.to_dict().get("customer_name", "Guest")
        else:
            pts = 0
            sample = [d.to_dict() for d in db.collection("bookings").stream() if d.to_dict().get("phone") == lookup_phone]
            cname  = sample[0].get("customer_name", "Guest") if sample else "Guest"

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(201,168,76,0.1),rgba(201,168,76,0.03));
            border:1px solid rgba(201,168,76,0.3);border-radius:18px;padding:22px 28px;
            margin-bottom:28px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;'>
            <div style='font-size:48px'>💎</div>
            <div>
                <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:26px'>{cname}</div>
                <div style='color:#666;font-size:11px;letter-spacing:1px;text-transform:uppercase;margin-top:4px'>Loyalty Points</div>
                <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:38px;font-weight:600'>{pts} pts</div>
                <div style='color:#555;font-size:12px;margin-top:4px'>🐾 Spend in the Pet Shop!</div>
            </div>
        </div>""", unsafe_allow_html=True)

        docs = list(db.collection("bookings").stream())
        my_bookings = [(doc.id, doc.to_dict()) for doc in docs if doc.to_dict().get("phone") == lookup_phone]

        if not my_bookings:
            st.markdown("""
            <div style='text-align:center;padding:40px;color:#444'>
                <div style='font-size:48px;margin-bottom:16px'>🔍</div>
                <p>No active bookings found for this number.</p>
            </div>""", unsafe_allow_html=True)
        else:
            for doc_id, booking in my_bookings:
                status = booking.get("status", "Pending")
                st.markdown(f"""
                <div class='booking-card'>
                    <div style='font-family:Cormorant Garamond;font-size:24px;color:#c9a84c;margin-bottom:8px'>
                        {booking.get('service')}
                    </div>
                    <div style='display:flex;gap:20px;flex-wrap:wrap;color:#777;font-size:13px;margin-bottom:12px'>
                        <span>📅 {booking.get('booking_date')}</span>
                        <span>🕐 {booking.get('time_slot')}</span>
                        <span>💰 ₹{booking.get('price','—')}</span>
                        <span>👤 {booking.get('assigned_role','')}</span>
                    </div>
                    <span class='status-{status.lower()}'>● {status}</span>
                </div>""", unsafe_allow_html=True)
                if st.button(f"❌ Cancel", key=f"cancel_{doc_id}"):
                    db.collection("bookings").document(doc_id).delete()
                    db.collection("completed_bookings").document(doc_id).delete()
                    st.success(f"✅ '{booking.get('service')}' cancelled.")
                    st.rerun()


# ======================================================
# ░░░ PET SHOP ░░░
# ======================================================

elif mode == "🐾 Pet Shop":
    st.markdown("<h1 class='section-heading'>🐾 Digital Pet Shop</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#777;margin-bottom:8px;line-height:1.7'>
        Earn <span style='color:#c9a84c;font-weight:600'>5 loyalty points</span> per completed service.
        Adopt digital companions, <span style='color:#c9a84c'>sell them back</span> for the same points,
        or <span style='color:#e05050'>delete them</span> (no refund).
    </p>""", unsafe_allow_html=True)

    shop_phone = st.text_input("📱 Enter your phone number", key="shop_phone")
    if st.button("Check My Points & Shop"):
        if not shop_phone.strip():
            st.warning("Please enter your phone number.")
        else:
            st.session_state["shop_phone_verified"] = shop_phone.strip()

    shop_phone_verified = st.session_state.get("shop_phone_verified", "")

    if shop_phone_verified:
        loyalty_ref = db.collection("loyalty_points").document(shop_phone_verified)
        loyalty_doc = loyalty_ref.get()
        if loyalty_doc.exists:
            loyalty_data   = loyalty_doc.to_dict()
            current_points = loyalty_data.get("points", 0)
            customer_name  = loyalty_data.get("customer_name", "Guest")
        else:
            current_points = 0
            customer_name  = "Guest"

        owned_ref  = db.collection("owned_pets").document(shop_phone_verified)
        owned_doc  = owned_ref.get()
        owned_pets = owned_doc.to_dict().get("pets", []) if owned_doc.exists else []

        # ── Points banner ──
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(201,168,76,0.12),rgba(201,168,76,0.03));
            border:1px solid rgba(201,168,76,0.35);border-radius:22px;padding:26px 34px;
            margin:20px 0 32px;display:flex;align-items:center;gap:26px;flex-wrap:wrap;'>
            <div style='font-size:58px'>💎</div>
            <div>
                <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:28px;margin-bottom:2px'>{customer_name}</div>
                <div style='color:#555;font-size:11px;letter-spacing:2px;text-transform:uppercase'>Your Balance</div>
                <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:54px;font-weight:600;line-height:1'>{current_points}</div>
                <div style='color:#777;font-size:13px'>loyalty points</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Owned pets ──
        if owned_pets:
            st.markdown("<h3 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:26px;margin-bottom:16px'>🏡 Your Pets</h3>", unsafe_allow_html=True)
            pet_grid = st.columns(min(len(owned_pets), 4))
            for pi, pname in enumerate(owned_pets):
                pet_data = next((p for p in DIGITAL_PETS if p["name"] == pname), None)
                if not pet_data:
                    continue
                rarity_color = RARITY_COLORS.get(pet_data["rarity"], "#888")
                with pet_grid[pi % 4]:
                    st.markdown(f"""
                    <div style='background:linear-gradient(145deg,#100e0a,#1a1610);
                        border:1px solid {rarity_color}55;border-radius:18px;padding:20px;
                        text-align:center;margin-bottom:8px;'>
                        <div style='font-size:52px;margin-bottom:8px'>{pet_data["emoji"]}</div>
                        <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:18px'>{pet_data["name"]}</div>
                        <div style='color:{rarity_color};font-size:10px;letter-spacing:1px;
                            text-transform:uppercase;margin-top:4px'>✦ {pet_data["rarity"]} ✦</div>
                        <div style='color:#666;font-size:11px;margin-top:6px'>Worth: {pet_data["cost"]} pts</div>
                    </div>""", unsafe_allow_html=True)

                    scol, dcol = st.columns(2)
                    with scol:
                        if st.button(f"💰 Sell", key=f"sell_{pi}_{pname}"):
                            new_pts = current_points + pet_data["cost"]
                            loyalty_ref.set({"customer_name": customer_name, "phone": shop_phone_verified, "points": new_pts})
                            new_owned = [p for p in owned_pets if p != pname]
                            owned_ref.set({"phone": shop_phone_verified, "pets": new_owned})
                            st.success(f"💰 Sold {pet_data['name']} for {pet_data['cost']} pts!")
                            st.rerun()
                    with dcol:
                        if st.button(f"🗑️ Delete", key=f"del_{pi}_{pname}"):
                            new_owned = [p for p in owned_pets if p != pname]
                            owned_ref.set({"phone": shop_phone_verified, "pets": new_owned})
                            st.warning(f"🗑️ {pet_data['name']} removed. No points refunded.")
                            st.rerun()

        # ── Shop ──
        st.markdown("<h3 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:26px;margin:28px 0 16px'>🛒 Available Pets</h3>", unsafe_allow_html=True)

        pet_cols = st.columns(3)
        for pi, pet in enumerate(DIGITAL_PETS):
            rarity_color  = RARITY_COLORS.get(pet["rarity"], "#888")
            already_owned = pet["name"] in owned_pets
            can_afford    = current_points >= pet["cost"]

            with pet_cols[pi % 3]:
                st.markdown(f"""
                <div style='background:linear-gradient(145deg,#100e0a,#1a1610);
                    border:1px solid {rarity_color}55;border-radius:22px;padding:26px;
                    text-align:center;margin-bottom:8px;
                    {"opacity:0.45;" if already_owned else ""}'>
                    <div style='font-size:62px;margin-bottom:10px'>{pet["emoji"]}</div>
                    <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:22px;margin-bottom:4px'>
                        {pet["name"]}
                    </div>
                    <div style='color:{rarity_color};font-size:10px;letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:10px'>✦ {pet["rarity"]} ✦</div>
                    <div style='color:#666;font-size:13px;line-height:1.5;margin-bottom:14px'>
                        {pet["description"]}
                    </div>
                    <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:28px;font-weight:600'>
                        {pet["cost"]} pts
                    </div>
                    {"<div style='color:#3ab26e;font-size:12px;margin-top:8px;letter-spacing:1px'>✅ OWNED</div>" if already_owned else ""}
                    {"<div style='color:#444;font-size:12px;margin-top:8px'>Not enough points</div>" if not can_afford and not already_owned else ""}
                </div>""", unsafe_allow_html=True)

                if not already_owned:
                    if st.button(f"🐾 Adopt {pet['name']}", key=f"adopt_{pi}", disabled=not can_afford):
                        new_pts  = current_points - pet["cost"]
                        loyalty_ref.set({"customer_name": customer_name, "phone": shop_phone_verified, "points": new_pts})
                        new_owned = owned_pets + [pet["name"]]
                        owned_ref.set({"phone": shop_phone_verified, "pets": new_owned})
                        st.success(f"🎉 You adopted {pet['emoji']} {pet['name']}!")
                        st.rerun()


# ======================================================
# ░░░ WORKER LOGIN ░░░
# ======================================================

elif mode == "🔒 Worker Login":
    st.markdown("<h1 class='section-heading'>🔒 Worker Dashboard</h1>", unsafe_allow_html=True)
    password = st.text_input("Password", type="password")

    if password == WORKER_PASSWORD:
        st.markdown("<div style='color:#3ab26e;margin-bottom:16px;font-size:13px;letter-spacing:1px'>✅ ACCESS GRANTED</div>", unsafe_allow_html=True)

        role = st.selectbox("Your Role", WORKER_ROLES)

        docs = db.collection("bookings").stream()
        bookings_for_role = [
            (doc.id, doc.to_dict()) for doc in docs
            if doc.to_dict().get("assigned_role") == role
        ]

        if not bookings_for_role:
            st.markdown("""
            <div style='text-align:center;padding:40px;color:#444'>
                <div style='font-size:48px;margin-bottom:12px'>🎉</div>
                <p>No pending bookings for your role right now.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:#666;margin-bottom:20px;font-size:13px'>{len(bookings_for_role)} booking(s) assigned</p>", unsafe_allow_html=True)

        for doc_id, booking in bookings_for_role:
            status = booking.get("status", "Pending")

            st.markdown(f"""
            <div class='booking-card'>
                <div class='worker-badge'>{booking.get('assigned_role')}</div>
                <div style='font-family:Cormorant Garamond;font-size:26px;color:#c9a84c;margin-bottom:8px'>
                    {booking.get('service')}
                </div>
                <div style='color:#aaa;font-size:14px;margin-bottom:4px'>👤 {booking.get('customer_name')}</div>
                <div style='display:flex;gap:20px;flex-wrap:wrap;color:#555;font-size:13px;margin-bottom:12px'>
                    <span>📅 {booking.get('booking_date')}</span>
                    <span>🕐 {booking.get('time_slot')}</span>
                    <span>💰 ₹{booking.get('price','—')}</span>
                    <span>📱 {booking.get('phone','—')}</span>
                </div>
                <span class='status-{status.lower()}'>● {status}</span>
            </div>""", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            # ── Accept ──
            with col1:
                if st.button("✅ Accept", key=f"a_{doc_id}"):
                    db.collection("bookings").document(doc_id).update({"status": "Accepted"})
                    st.rerun()

            # ── OTP Verification before Complete ──
            with col2:
                otp_key = f"worker_otp_input_{doc_id}"
                otp_state_key = f"worker_otp_result_{doc_id}"

                # Show OTP input only after accept
                if status == "Accepted":
                    worker_otp = st.text_input("🔐 Customer OTP", key=otp_key, max_chars=6, placeholder="Enter 6-digit OTP")
                    if st.button("🏆 Verify & Complete", key=f"c_{doc_id}"):
                        # Fetch stored OTP from Firestore (if saved, otherwise skip check)
                        # We store OTP at booking time in a separate collection
                        otp_doc = db.collection("booking_otps").document(doc_id).get()
                        if otp_doc.exists:
                            real_otp = otp_doc.to_dict().get("otp", "")
                            if worker_otp.strip() != real_otp:
                                st.error("❌ Invalid OTP. Customer must share their WhatsApp OTP.")
                                st.session_state[otp_state_key] = "fail"
                            else:
                                _do_complete(doc_id, booking, db)
                                st.rerun()
                        else:
                            # OTP doc not stored (older bookings) — allow completion
                            _do_complete(doc_id, booking, db)
                            st.rerun()
                else:
                    st.markdown("<span style='color:#444;font-size:12px'>Accept first to verify OTP</span>", unsafe_allow_html=True)

            with col3:
                if st.button("🚫 Reject/Delete", key=f"d_{doc_id}"):
                    db.collection("bookings").document(doc_id).delete()
                    st.warning("Booking removed.")
                    st.rerun()

    elif password != "":
        st.error("Incorrect password.")

# ======================================================
# HELPER used inside Worker login
# ======================================================

def _do_complete(doc_id, booking, db):
    booking["status"] = "Completed"
    db.collection("completed_bookings").document(doc_id).set(booking)
    db.collection("bookings").document(doc_id).delete()
    db.collection("booking_otps").document(doc_id).delete()

    cref = db.collection("loyalty_points").document(booking["phone"])
    cdoc = cref.get()
    curr = cdoc.to_dict().get("points", 0) if cdoc.exists else 0
    cref.set({"customer_name": booking["customer_name"], "phone": booking["phone"], "points": curr + 5})
    st.success("✅ Service completed! Customer earned 5 💎 loyalty points.")

# ─── NOTE: Python doesn't allow forward-defined helpers called before def.
# ─── Move _do_complete above the worker login block in production, or use:

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class='salon-footer'>
    <div class='gold-divider'></div>
    <p>Crafted with elegance by <span>PNB Smart &amp; Luxurious Salon</span> · AI-Powered Beauty Experience</p>
</div>""", unsafe_allow_html=True)
