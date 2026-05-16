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
        "type":                        st.secrets["type"],
        "project_id":                  st.secrets["project_id"],
        "private_key_id":              st.secrets["private_key_id"],
        "private_key":                 st.secrets["private_key"],
        "client_email":                st.secrets["client_email"],
        "client_id":                   st.secrets["client_id"],
        "auth_uri":                    st.secrets["auth_uri"],
        "token_uri":                   st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url":        st.secrets["client_x509_cert_url"],
    }
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ======================================================
# AI API CONFIG
# ======================================================

AI_API_URL = st.secrets["AI_API_URL"]
AI_API_KEY = st.secrets["AI_API_KEY"]

# ======================================================
# CONSTANTS
# ======================================================

WORKER_PASSWORD = "PNB2024"

WORKER_ROLES = [
    "Massage Expert",
    "Makeup Artist",
    "Hair Stylist",
    "Nail Technician",
    "Skin Specialist",
    "Mehandi Artist",
    "Styling Expert",
]

TIME_SLOTS = [
    "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM",
    "2:00 PM",  "3:00 PM",  "4:00 PM",  "5:00 PM",
    "6:00 PM",  "7:00 PM",  "8:00 PM",  "9:00 PM",
]

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
    "Common":    "#888888",
    "Uncommon":  "#3ab26e",
    "Rare":      "#4a9eff",
    "Epic":      "#a855f7",
    "Legendary": "#f97316",
    "Mythic":    "#c9a84c",
}

# ======================================================
# SESSION STATE DEFAULTS
# ======================================================

_defaults = {
    "selected_service": None,
    "open_ai":          False,
    "bookings_phone":   "",
    "shop_phone":       "",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ======================================================
# HELPERS
# ======================================================

def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def complete_booking(doc_id: str, booking: dict):
    """Move booking to completed, award 5 loyalty points."""
    booking["status"] = "Completed"
    db.collection("completed_bookings").document(doc_id).set(booking)
    db.collection("bookings").document(doc_id).delete()

    phone = booking.get("phone", "")
    cref  = db.collection("loyalty_points").document(phone)
    cdoc  = cref.get()
    pts   = cdoc.to_dict().get("points", 0) if cdoc.exists else 0
    cref.set({
        "customer_name": booking.get("customer_name", ""),
        "phone":         phone,
        "points":        pts + 5,
    })

# ======================================================
# SERVICES LIST
# ======================================================

services = [
    # MASSAGE
    {"name": "Ayurvedic Massage (45 mins)",   "duration": "45 mins",  "price": 1500, "role": "Massage Expert",  "category": "Massage",           "description": "Traditional Ayurvedic herbal massage using warm medicated oils to balance doshas, relieve stress and revitalize the body.",            "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
    {"name": "Ayurvedic Massage (60 mins)",   "duration": "60 mins",  "price": 1800, "role": "Massage Expert",  "category": "Massage",           "description": "Extended traditional Ayurvedic herbal massage for deep relaxation, improved circulation, and holistic wellness.",                      "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
    {"name": "Aroma Therapy (45 mins)",       "duration": "45 mins",  "price": 2000, "role": "Massage Expert",  "category": "Massage",           "description": "Luxury aromatherapy session with premium essential oils to calm the mind and refresh the senses.",                                   "image": "https://images.unsplash.com/photo-1515377905703-c4788e51af15"},
    {"name": "Aroma Therapy (60 mins)",       "duration": "60 mins",  "price": 2500, "role": "Massage Expert",  "category": "Massage",           "description": "Extended luxury aromatherapy session for deep stress relief and full body relaxation using curated essential oil blends.",            "image": "https://images.unsplash.com/photo-1515377905703-c4788e51af15"},
    {"name": "Deep Tissue Massage",           "duration": "60 mins",  "price": 3000, "role": "Massage Expert",  "category": "Massage",           "description": "Therapeutic deep muscle recovery massage targeting chronic tension, knots, and muscle fatigue.",                                    "image": "https://images.unsplash.com/photo-1519823551278-64ac92734fb1"},
    {"name": "Body Polish",                   "duration": "60 mins",  "price": 3500, "role": "Massage Expert",  "category": "Massage",           "description": "Full body exfoliation and polishing treatment to reveal radiant, smooth and glowing skin.",                                         "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    # SKIN
    {"name": "Wart Removal",                  "duration": "20 mins",  "price": 200,  "role": "Skin Specialist", "category": "Skin",              "description": "Safe and precise wart removal treatment performed by trained skin specialists using advanced techniques.",                          "image": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908"},
    {"name": "Nose Piercing",                 "duration": "15 mins",  "price": 600,  "role": "Skin Specialist", "category": "Skin",              "description": "Professional nose piercing with hygienic, sterilized equipment and premium jewelry options.",                                     "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"},
    {"name": "Ear Piercing (Single)",         "duration": "10 mins",  "price": 800,  "role": "Skin Specialist", "category": "Skin",              "description": "Single ear piercing with sterilized tools, safe and quick procedure with aftercare guidance.",                                    "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"},
    {"name": "Ear Piercing (Double)",         "duration": "15 mins",  "price": 1200, "role": "Skin Specialist", "category": "Skin",              "description": "Double ear piercing for both ears with premium sterilized equipment and stylish jewelry.",                                        "image": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c"},
    # MEHANDI & STYLING
    {"name": "Mehandi",                       "duration": "30 mins",  "price": 500,  "role": "Mehandi Artist",  "category": "Mehandi & Styling", "description": "Beautiful intricate henna mehandi designs crafted by skilled artists for festive and bridal occasions.",                           "image": "https://images.unsplash.com/photo-1532030543767-ea4b0f5aa7a5"},
    {"name": "Fashion Plait",                 "duration": "20 mins",  "price": 500,  "role": "Hair Stylist",    "category": "Mehandi & Styling", "description": "Trendy and elegant fashion plait hairstyle crafted to complement any look or occasion.",                                          "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e"},
    {"name": "Flower Plait Fixing",           "duration": "25 mins",  "price": 800,  "role": "Hair Stylist",    "category": "Mehandi & Styling", "description": "Gorgeous flower plait adorned with fresh or artificial flowers for weddings and celebrations.",                                    "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e"},
    # MAKEUP
    {"name": "Light Makeup",                  "duration": "45 mins",  "price": 2500, "role": "Makeup Artist",   "category": "Makeup",            "description": "Fresh, natural light makeup look perfect for daytime events and casual outings.",                                                 "image": "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"},
    {"name": "Party Makeup",                  "duration": "60 mins",  "price": 3500, "role": "Makeup Artist",   "category": "Makeup",            "description": "Bold and glamorous party makeup for an unforgettable evening look.",                                                             "image": "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2"},
    {"name": "Bridal Trial Makeup",           "duration": "90 mins",  "price": 2500, "role": "Makeup Artist",   "category": "Makeup",            "description": "Pre-wedding trial session to perfect your bridal look and ensure flawless results on the big day.",                              "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"},
    {"name": "Bridal Makeup",                 "duration": "120 mins", "price": 7500, "role": "Makeup Artist",   "category": "Makeup",            "description": "Complete luxury bridal makeover package — because your wedding day deserves nothing less than perfection.",                       "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"},
    {"name": "Reception Makeup",              "duration": "90 mins",  "price": 5000, "role": "Makeup Artist",   "category": "Makeup",            "description": "Elegant and radiant reception makeup designed to glow under lights and cameras.",                                                "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"},
    # SAREE
    {"name": "Half Saree Draping",            "duration": "20 mins",  "price": 300,  "role": "Styling Expert",  "category": "Saree & Draping",   "description": "Neat and graceful half-saree draping for a traditional and elegant look.",                                                       "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"},
    {"name": "Saree Draping",                 "duration": "25 mins",  "price": 500,  "role": "Styling Expert",  "category": "Saree & Draping",   "description": "Perfect saree draping by skilled experts to ensure you look flawless and feel confident.",                                       "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"},
    {"name": "Saree Pre-Plating",             "duration": "30 mins",  "price": 700,  "role": "Styling Expert",  "category": "Saree & Draping",   "description": "Professional saree pre-plating and pinning for a crisp, well-structured drape that lasts all day.",                            "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b"},
    # PEDICURE
    {"name": "Basic Pedicure",                "duration": "30 mins",  "price": 500,  "role": "Nail Technician", "category": "Pedicure",          "description": "Classic pedicure with soaking, scrubbing, nail shaping and a fresh coat of colour.",                                              "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Spa Pedicure",                  "duration": "45 mins",  "price": 600,  "role": "Nail Technician", "category": "Pedicure",          "description": "Relaxing spa pedicure with moisturizing treatment and gentle massage for soft, happy feet.",                                      "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Crystal Pedicure",              "duration": "50 mins",  "price": 900,  "role": "Nail Technician", "category": "Pedicure",          "description": "Luxurious crystal pedicure for deeply nourished, glowing skin and beautifully shaped nails.",                                    "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Aromatic Pedicure",             "duration": "55 mins",  "price": 1200, "role": "Nail Technician", "category": "Pedicure",          "description": "Aromatic pedicure infused with essential oils for a sensory treat and deeply refreshed feet.",                                   "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Heel Peel Pedicure",            "duration": "60 mins",  "price": 1300, "role": "Nail Technician", "category": "Pedicure",          "description": "Specialized heel peel treatment to eliminate rough, cracked heels leaving feet baby soft.",                                       "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "PNB Signature Pedicure",        "duration": "75 mins",  "price": 1600, "role": "Nail Technician", "category": "Pedicure",          "description": "Our exclusive signature pedicure — a premium full-care ritual designed for ultimate indulgence.",                                 "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    {"name": "Nail Cut & Colouring",          "duration": "20 mins",  "price": 200,  "role": "Nail Technician", "category": "Pedicure",          "description": "Neat nail cutting and a vibrant colour application for a polished, put-together look.",                                           "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Bomb Pedicure",                 "duration": "90 mins",  "price": 2000, "role": "Nail Technician", "category": "Pedicure",          "description": "The ultimate luxury bomb pedicure — an explosive combination of exfoliation, massage and glamour.",                               "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b"},
    # MANICURE
    {"name": "Basic Manicure",                "duration": "30 mins",  "price": 300,  "role": "Nail Technician", "category": "Manicure",          "description": "Classic manicure with soaking, cuticle care, nail shaping and colour application.",                                              "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Spa Manicure",                  "duration": "45 mins",  "price": 500,  "role": "Nail Technician", "category": "Manicure",          "description": "Relaxing spa manicure with moisturizing treatment and a soothing hand massage.",                                                 "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Crystal Spa Manicure",          "duration": "50 mins",  "price": 750,  "role": "Nail Technician", "category": "Manicure",          "description": "Luxury crystal spa manicure for beautifully nourished hands and flawless nails.",                                               "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Nail Filing & Colouring",       "duration": "15 mins",  "price": 200,  "role": "Nail Technician", "category": "Manicure",          "description": "Quick nail filing and colour application for a neat and stylish finish.",                                                        "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Colouring Only",                "duration": "10 mins",  "price": 100,  "role": "Nail Technician", "category": "Manicure",          "description": "Simple and quick nail colour application in your choice of shade.",                                                              "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Nail Filing Only",              "duration": "10 mins",  "price": 50,   "role": "Nail Technician", "category": "Manicure",          "description": "Precise nail shaping and filing for a clean, well-groomed look.",                                                               "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "French Polish",                 "duration": "20 mins",  "price": 250,  "role": "Nail Technician", "category": "Manicure",          "description": "Classic French polish for timeless, elegant nails with a white tip and nude base.",                                             "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Gel Polish",                    "duration": "30 mins",  "price": 500,  "role": "Nail Technician", "category": "Manicure",          "description": "Long-lasting gel polish for chip-free, glossy nails that stay perfect for weeks.",                                              "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Gel Polish Removal",            "duration": "20 mins",  "price": 200,  "role": "Nail Technician", "category": "Manicure",          "description": "Safe and gentle gel polish removal without damaging the natural nail.",                                                         "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    {"name": "Bomb Manicure",                 "duration": "75 mins",  "price": 1800, "role": "Nail Technician", "category": "Manicure",          "description": "Our ultimate bomb manicure — a complete luxury hand ritual for beautifully pampered hands.",                                   "image": "https://images.unsplash.com/photo-1604654894610-df63bc536371"},
    # HAIR TREATMENTS
    {"name": "Perming (Small)",               "duration": "90 mins",  "price": 2000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Create bouncy, beautiful curls with professional perming treatment for short/small sections.",                                   "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Perming (Medium)",              "duration": "120 mins", "price": 3000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Professional perming for medium-length hair with long-lasting, voluminous curls.",                                              "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Perming (Large)",               "duration": "150 mins", "price": 4000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Full perming treatment for long or thick hair with stunning, defined curls.",                                                    "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Smoothening (Small)",           "duration": "90 mins",  "price": 3000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Hair smoothening treatment for short hair — eliminate frizz and add shine.",                                                    "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Smoothening (Medium)",          "duration": "120 mins", "price": 4000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Smoothening treatment for medium hair — silky, manageable, frizz-free results.",                                               "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Smoothening (Large)",           "duration": "150 mins", "price": 5000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Smoothening treatment for long/thick hair — dramatically smoother, shinier tresses.",                                           "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Rebonding (Small)",             "duration": "120 mins", "price": 4000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Rebonding for short hair — permanently straighten and restructure for ultra-sleek results.",                                    "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Rebonding (Medium)",            "duration": "150 mins", "price": 5000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Rebonding for medium hair — salon-perfect straight hair with long-lasting effects.",                                           "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Rebonding (Large)",             "duration": "180 mins", "price": 6000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Rebonding for long or thick hair — complete transformation to glass-smooth straight hair.",                                    "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Straightening (Small)",         "duration": "90 mins",  "price": 5000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Professional straightening for short hair with premium products for lasting sleekness.",                                        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Straightening (Medium)",        "duration": "120 mins", "price": 6000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Professional straightening for medium hair — smooth, glossy, and beautifully managed.",                                        "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Straightening (Large)",         "duration": "150 mins", "price": 7000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Professional straightening for long/thick hair — perfectly straight, mirror-shiny results.",                                   "image": "https://images.unsplash.com/photo-1522337660859-02fbefca4702"},
    {"name": "Keratin Treatment",             "duration": "120 mins", "price": 5000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Premium keratin treatment to deeply nourish, smoothen and add brilliant shine to your hair.",                                   "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Express Keratin Treatment",     "duration": "90 mins",  "price": 4500, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Quick express keratin treatment for a faster dose of frizz-free, glossy hair.",                                                 "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Deep Conditioning",             "duration": "60 mins",  "price": 3000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Intensive deep conditioning treatment to restore moisture, strength, and brilliance to damaged hair.",                           "image": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"},
    {"name": "Hair Scrub",                    "duration": "30 mins",  "price": 800,  "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Scalp purifying hair scrub to remove buildup, unclog follicles and promote healthy hair growth.",                              "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    {"name": "Metal DK Treatment",            "duration": "45 mins",  "price": 1000, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Metal DK bond-rebuilding treatment to repair chemical damage and restore hair integrity.",                                      "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    {"name": "Hair Treatment",                "duration": "45 mins",  "price": 1300, "role": "Hair Stylist",    "category": "Hair Treatments",   "description": "Targeted professional hair treatment customized to your hair type and concern.",                                                 "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    # HAIR COLOUR
    {"name": "Colour Application Only",              "duration": "40 mins", "price": 300,  "role": "Hair Stylist", "category": "Hair Colour",   "description": "Professional colour application to achieve rich, vibrant hair colour.",                                                             "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    {"name": "Colour Application + Wash (Basic)",    "duration": "60 mins", "price": 550,  "role": "Hair Stylist", "category": "Hair Colour",   "description": "Colour application followed by a professional wash and blow-dry for a finished look.",                                              "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    {"name": "Colour Application (Full)",            "duration": "60 mins", "price": 500,  "role": "Hair Stylist", "category": "Hair Colour",   "description": "Full head colour application for complete colour coverage and transformation.",                                                    "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    {"name": "Colour Application + Wash (Premium)",  "duration": "75 mins", "price": 800,  "role": "Hair Stylist", "category": "Hair Colour",   "description": "Premium full colour application with professional wash and conditioning treatment.",                                                "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    {"name": "Touch Up",                             "duration": "45 mins", "price": 1000, "role": "Hair Stylist", "category": "Hair Colour",   "description": "Precise root touch-up to refresh your colour and keep it looking salon-fresh.",                                                    "image": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11"},
    # HAIRCUT
    {"name": "Haircut (Below 8 yrs)",  "duration": "20 mins", "price": 200, "role": "Hair Stylist", "category": "Haircut",    "description": "Gentle and fun haircut designed specially for children below 8 years.",                                                    "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"},
    {"name": "Basic Haircut",          "duration": "30 mins", "price": 250, "role": "Hair Stylist", "category": "Haircut",    "description": "Classic stylish haircut shaped to flatter your features and suit your style.",                                             "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"},
    {"name": "Split Ends Trim",        "duration": "25 mins", "price": 400, "role": "Hair Stylist", "category": "Haircut",    "description": "Precision split-end removal to restore healthy, smooth hair ends without losing length.",                                 "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"},
    {"name": "Advanced Haircut",       "duration": "45 mins", "price": 500, "role": "Hair Stylist", "category": "Haircut",    "description": "Expert advanced haircut with precision layering and styling tailored to your hair type.",                                "image": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186"},
    # HAIR WASH
    {"name": "Hair Wash + Conditioner (Til/Coconut Oil Massage)",         "duration": "30 mins", "price": 300, "role": "Hair Stylist", "category": "Hair Wash", "description": "Nourishing hair wash with conditioner, preceded by a relaxing traditional oil head massage.",    "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    {"name": "Hair Wash + Conditioner (Olive/Aroma/Cooling Oil Massage)", "duration": "35 mins", "price": 350, "role": "Hair Stylist", "category": "Hair Wash", "description": "Revitalizing hair wash with conditioner after an indulgent premium oil head massage.",             "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1"},
    # FACE TREATMENTS
    {"name": "Young Face Pack",    "duration": "30 mins", "price": 300, "role": "Skin Specialist", "category": "Face Treatments", "description": "Hydrating and brightening face pack to give your skin a youthful, dewy glow.",                                         "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "White Face Pack",    "duration": "30 mins", "price": 300, "role": "Skin Specialist", "category": "Face Treatments", "description": "Brightening white face pack for a luminous, even-toned and radiant complexion.",                                       "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "Charcoal Pack",      "duration": "35 mins", "price": 350, "role": "Skin Specialist", "category": "Face Treatments", "description": "Deep-cleansing activated charcoal face pack to purify pores and detox the skin.",                                      "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "Tan Pack",           "duration": "45 mins", "price": 600, "role": "Skin Specialist", "category": "Face Treatments", "description": "Effective de-tan face pack to reverse sun damage and restore skin's natural brightness.",                             "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "Charcoal Face Mask", "duration": "40 mins", "price": 750, "role": "Skin Specialist", "category": "Face Treatments", "description": "Premium activated charcoal face mask for deep pore purification and skin detox.",                                      "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    {"name": "Gold Face Mask",     "duration": "45 mins", "price": 800, "role": "Skin Specialist", "category": "Face Treatments", "description": "Luxury 24k gold face mask to boost radiance, reduce fine lines and illuminate your skin.",                            "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881"},
    # QUICK MASSAGES
    {"name": "Hand Massage",        "duration": "20 mins", "price": 250, "role": "Massage Expert", "category": "Quick Massages", "description": "Soothing hand massage to relieve tension and leave your hands feeling soft and revitalized.",   "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
    {"name": "Foot Work Massage",   "duration": "25 mins", "price": 300, "role": "Massage Expert", "category": "Quick Massages", "description": "Revitalizing foot massage targeting pressure points to relieve fatigue and improve circulation.", "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
    {"name": "Back Energy Massage", "duration": "30 mins", "price": 400, "role": "Massage Expert", "category": "Quick Massages", "description": "Energizing back massage to release muscle knots, reduce tension and restore vitality.",          "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874"},
]

# ======================================================
# REALISTIC BALLOON CANVAS  (click / hover to pop)
# ======================================================

BALLOON_HTML = """
<canvas id="pnb-bc" style="position:fixed;top:0;left:0;width:100vw;height:100vh;
  pointer-events:all;z-index:99999;"></canvas>
<script>
(function(){
  var C=document.getElementById('pnb-bc');
  var X=C.getContext('2d');
  C.width=window.innerWidth; C.height=window.innerHeight;
  var PAL=['#c9a84c','#f7d98b','#ff6b6b','#ff9f9f','#a855f7',
           '#e879f9','#4ade80','#60a5fa','#ffd700','#ff8c00',
           '#e8b86d','#fff8e7','#ff4444','#f5c842'];
  function dk(h,a){
    h=h.replace('#','');
    if(h.length===3)h=h.split('').map(function(c){return c+c;}).join('');
    var n=parseInt(h,16);
    var r=Math.max(0,((n>>16)&255)-a);
    var g=Math.max(0,((n>>8)&255)-a);
    var b=Math.max(0,(n&255)-a);
    return '#'+[r,g,b].map(function(v){return v.toString(16).padStart(2,'0');}).join('');
  }
  function Balloon(init){
    this.x=Math.random()*C.width;
    this.y=init? C.height+Math.random()*C.height : C.height+70;
    this.r=26+Math.random()*22;
    this.col=PAL[Math.floor(Math.random()*PAL.length)];
    this.vy=-(1.3+Math.random()*2.2);
    this.vx=(Math.random()-.5)*.8;
    this.sway=Math.random()*Math.PI*2;
    this.swayS=.018+Math.random()*.014;
    this.wob=Math.random()*Math.PI*2;
    this.wobS=.04+Math.random()*.03;
    this.str=22+Math.random()*28;
    this.popped=false; this.popP=0; this.parts=[];
  }
  Balloon.prototype.pop=function(){
    if(this.popped)return; this.popped=true;
    for(var i=0;i<20;i++){
      var a=Math.random()*Math.PI*2,s=3+Math.random()*6;
      this.parts.push({x:this.x,y:this.y,
        vx:Math.cos(a)*s,vy:Math.sin(a)*s-2.5,
        r:3+Math.random()*5,col:PAL[Math.floor(Math.random()*PAL.length)],a:1});
    }
  };
  Balloon.prototype.hit=function(mx,my){
    if(this.popped)return false;
    return Math.sqrt((mx-this.x)*(mx-this.x)+(my-this.y)*(my-this.y))<this.r*1.2;
  };
  Balloon.prototype.update=function(){
    if(this.popped){
      this.popP+=.06;
      for(var i=0;i<this.parts.length;i++){
        var p=this.parts[i];
        p.x+=p.vx; p.y+=p.vy; p.vy+=.2; p.a-=.032; p.r*=.97;
      }
      return this.popP<1.4;
    }
    this.wob+=this.wobS; this.sway+=this.swayS;
    this.x+=this.vx+Math.sin(this.sway)*.55;
    this.y+=this.vy;
    return this.y+this.r>-30;
  };
  Balloon.prototype.draw=function(){
    if(this.popped){
      for(var i=0;i<this.parts.length;i++){
        var p=this.parts[i];
        if(p.a<=0)continue;
        X.save(); X.globalAlpha=Math.max(0,p.a);
        X.fillStyle=p.col;
        X.beginPath(); X.arc(p.x,p.y,p.r,0,Math.PI*2); X.fill();
        X.restore();
      }
      return;
    }
    X.save(); X.translate(this.x,this.y);
    var sx=1+Math.sin(this.wob)*.028, sy=1-Math.sin(this.wob)*.028;
    X.scale(sx,sy);
    X.shadowColor='rgba(0,0,0,.3)'; X.shadowBlur=14;
    X.shadowOffsetX=4; X.shadowOffsetY=7;
    var g=X.createRadialGradient(-this.r*.3,-this.r*.36,this.r*.04,0,0,this.r*1.06);
    g.addColorStop(0,'rgba(255,255,255,.55)');
    g.addColorStop(.22,this.col);
    g.addColorStop(1,dk(this.col,60));
    X.fillStyle=g;
    X.beginPath(); X.ellipse(0,0,this.r,this.r*1.18,0,0,Math.PI*2); X.fill();
    X.shadowBlur=0; X.shadowOffsetX=0; X.shadowOffsetY=0;
    var hl=X.createRadialGradient(-this.r*.27,-this.r*.38,this.r*.02,-this.r*.22,-this.r*.3,this.r*.38);
    hl.addColorStop(0,'rgba(255,255,255,.72)');
    hl.addColorStop(1,'rgba(255,255,255,0)');
    X.fillStyle=hl;
    X.beginPath(); X.ellipse(-this.r*.22,-this.r*.36,this.r*.34,this.r*.2,-.4,0,Math.PI*2); X.fill();
    X.fillStyle=dk(this.col,80);
    X.beginPath(); X.ellipse(0,this.r*1.18,this.r*.11,this.r*.10,0,0,Math.PI*2); X.fill();
    X.strokeStyle='rgba(201,168,76,.45)'; X.lineWidth=1.2;
    X.beginPath(); X.moveTo(0,this.r*1.28);
    X.quadraticCurveTo(this.r*.18,this.r*1.55+this.str*.4,0,this.r*1.28+this.str);
    X.stroke();
    X.restore();
  };
  var balls=[];
  for(var i=0;i<24;i++) balls.push(new Balloon(true));
  var t=0, alive=true;
  C.addEventListener('click',function(e){
    var rc=C.getBoundingClientRect();
    var mx=e.clientX-rc.left, my=e.clientY-rc.top;
    balls.forEach(function(b){if(b.hit(mx,my))b.pop();});
  });
  C.addEventListener('mousemove',function(e){
    var rc=C.getBoundingClientRect();
    var mx=e.clientX-rc.left, my=e.clientY-rc.top;
    C.style.cursor=balls.some(function(b){return b.hit(mx,my);})?'pointer':'default';
  });
  function loop(){
    if(!alive)return;
    X.clearRect(0,0,C.width,C.height); t++;
    for(var i=balls.length-1;i>=0;i--){
      if(!balls[i].update()){balls.splice(i,1);balls.push(new Balloon(false));}
      else balls[i].draw();
    }
    if(t>600){
      C.style.transition='opacity .8s'; C.style.opacity='0';
      setTimeout(function(){alive=false;C.remove();},900);
    }
    requestAnimationFrame(loop);
  }
  loop();
})();
</script>
"""

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap');

* { font-family: 'Jost', sans-serif; }

.stApp {
    background: linear-gradient(160deg, #080808 0%, #0e0d0b 45%, #110e08 100%);
    color: #f5f0e8;
}
h1, h2, h3 { font-family: 'Cormorant Garamond', serif !important; color: #c9a84c !important; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0806, #130e06) !important;
    border-right: 1px solid rgba(201,168,76,0.2) !important;
}
section[data-testid="stSidebar"] * { color: #e8d5a3 !important; }

.stTextInput > div > div {
    background: #111008 !important; border-color: rgba(201,168,76,0.25) !important;
    color: #f5f0e8 !important; border-radius: 10px !important;
}
.stSelectbox > div > div {
    background: #111008 !important; border-color: rgba(201,168,76,0.25) !important;
    color: #f5f0e8 !important; border-radius: 10px !important;
}
.stDateInput > div > div {
    background: #111008 !important; border-color: rgba(201,168,76,0.25) !important;
    border-radius: 10px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #a07820, #c9a84c, #a07820) !important;
    background-size: 200% auto !important; color: #080808 !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'Jost', sans-serif !important; font-weight: 600 !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    font-size: 11px !important; padding: 12px 28px !important;
    transition: all 0.3s !important; box-shadow: 0 4px 18px rgba(201,168,76,0.15) !important;
}
.stButton > button:hover {
    background-position: right center !important;
    box-shadow: 0 6px 28px rgba(201,168,76,0.32) !important;
    transform: translateY(-1px) !important;
}
.ai-float .stButton > button {
    border-radius: 50% !important; width: 52px !important;
    height: 52px !important; padding: 0 !important; font-size: 20px !important;
}
.salon-header { text-align: center; padding: 56px 24px 36px; position: relative; overflow: hidden; }
.salon-header::before {
    content: ''; position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
    width: 700px; height: 360px;
    background: radial-gradient(ellipse, rgba(201,168,76,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.salon-title {
    font-family: 'Cormorant Garamond', serif; font-size: 68px; font-weight: 300;
    color: #c9a84c; letter-spacing: 6px; line-height: 1.1; margin: 0;
    text-shadow: 0 0 80px rgba(201,168,76,0.22);
}
.salon-tagline { color: #5a4e2e; font-size: 11px; letter-spacing: 5px; text-transform: uppercase; margin-top: 12px; }
.gold-line { width: 120px; height: 1px; background: linear-gradient(90deg, transparent, #c9a84c, transparent); margin: 18px auto; }
.section-heading { font-family: 'Cormorant Garamond', serif; font-size: 36px; color: #c9a84c; margin: 8px 0 24px; letter-spacing: 2px; }
.svc-body {
    background: linear-gradient(145deg, #0f0d09, #1a1610);
    border: 1px solid rgba(201,168,76,0.12); border-top: none;
    border-radius: 0 0 16px 16px; padding: 16px; margin-bottom: 4px;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.svc-body:hover { border-color: rgba(201,168,76,0.38); box-shadow: 0 8px 32px rgba(201,168,76,0.08); }
.svc-name { font-family: 'Cormorant Garamond', serif; font-size: 20px; color: #c9a84c; margin: 0 0 5px; line-height: 1.3; }
.svc-desc { color: #666; font-size: 12px; line-height: 1.5; margin-bottom: 10px; }
.svc-price { font-family: 'Cormorant Garamond', serif; font-size: 26px; font-weight: 600; color: #c9a84c; }
.svc-dur { color: #444; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }
.otp-reveal {
    background: linear-gradient(135deg, rgba(201,168,76,0.09), rgba(201,168,76,0.02));
    border: 1px solid rgba(201,168,76,0.4); border-radius: 18px;
    padding: 30px; text-align: center; margin: 18px 0;
}
.otp-label { color: #7a6640; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 8px; }
.otp-number {
    font-family: 'Cormorant Garamond', serif; font-size: 60px; font-weight: 600;
    color: #c9a84c; letter-spacing: 14px; text-shadow: 0 0 40px rgba(201,168,76,0.5);
}
.booking-card {
    background: linear-gradient(145deg, #0e0c09, #1a1610);
    border: 1px solid rgba(201,168,76,0.14); border-radius: 16px;
    padding: 22px; margin-bottom: 16px;
}
.status-pending   { color: #e0a030; font-weight: 600; font-size: 13px; }
.status-accepted  { color: #3ab26e; font-weight: 600; font-size: 13px; }
.status-completed { color: #555;    font-weight: 600; font-size: 13px; }
.w-badge {
    display: inline-block; background: rgba(201,168,76,0.08);
    border: 1px solid rgba(201,168,76,0.22); border-radius: 20px;
    padding: 3px 14px; font-size: 11px; color: #c9a84c;
    letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;
}
.loy-banner {
    background: linear-gradient(135deg, rgba(201,168,76,0.1), rgba(201,168,76,0.03));
    border: 1px solid rgba(201,168,76,0.3); border-radius: 20px;
    padding: 24px 30px; margin-bottom: 28px;
    display: flex; align-items: center; gap: 22px; flex-wrap: wrap;
}
.pet-card { border-radius: 20px; padding: 24px; text-align: center; margin-bottom: 8px; }
.salon-footer {
    text-align: center; padding: 28px 20px; margin-top: 48px;
    border-top: 1px solid rgba(201,168,76,0.07);
    color: #2e2618; font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
}
.salon-footer span { color: #c9a84c; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.markdown("""
<div class='salon-header'>
  <p class='salon-tagline'>Welcome to</p>
  <h1 class='salon-title'>PNB Smart &amp; Luxurious Salon</h1>
  <div class='gold-line'></div>
  <p class='salon-tagline'>AI-Powered Beauty &amp; Wellness Experience</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR NAV
# ======================================================

mode = st.sidebar.radio(
    "Navigation",
    ["💎 Services", "📅 My Bookings", "🐾 Pet Shop", "🔒 Worker Login"],
)

# ══════════════════════════════════════════════════════
#  💎  SERVICES
# ══════════════════════════════════════════════════════

if mode == "💎 Services":

    c1, c2 = st.columns([11, 1])
    with c1:
        search = st.text_input("🔍 Search services...", placeholder="e.g. keratin, bridal, pedicure")
    with c2:
        st.markdown("<div class='ai-float'>", unsafe_allow_html=True)
        if st.button("✨"):
            st.session_state["open_ai"]          = True
            st.session_state["selected_service"] = None
        st.markdown("</div>", unsafe_allow_html=True)

    cats     = sorted({s["category"] for s in services})
    category = st.selectbox("Filter by Category", ["All"] + cats)

    filtered = [
        s for s in services
        if (category == "All" or s["category"] == category)
        and search.lower() in s["name"].lower()
    ]

    if filtered:
        st.markdown(
            f"<div class='section-heading'>"
            f"{category if category != 'All' else 'All Services'}"
            f"<span style='font-size:15px;color:#333;margin-left:12px;font-family:Jost'>"
            f"{len(filtered)} services</span></div>",
            unsafe_allow_html=True,
        )

    cols = st.columns(3)
    for i, svc in enumerate(filtered):
        with cols[i % 3]:
            st.image(svc["image"], use_container_width=True)
            st.markdown(f"""
            <div class='svc-body'>
              <div class='svc-name'>{svc['name']}</div>
              <div class='svc-desc'>{svc['description'][:85]}...</div>
              <div style='display:flex;justify-content:space-between;align-items:center'>
                <div class='svc-price'>₹{svc['price']:,}</div>
                <div class='svc-dur'>⏱ {svc['duration']}</div>
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button("View & Book", key=f"vb_{i}"):
                st.session_state["selected_service"] = svc
                st.session_state["open_ai"]          = False

    # ── SERVICE BOOKING DIALOG ──────────────────────────────

    if st.session_state["selected_service"] is not None:
        sel = st.session_state["selected_service"]

        @st.dialog(f"✨ {sel['name']}", width="large")
        def _service_dialog():
            img_col, info_col = st.columns([1, 1])
            with img_col:
                st.image(sel["image"], use_container_width=True)
            with info_col:
                st.markdown(
                    f"<h2 style='font-family:Cormorant Garamond;color:#c9a84c;font-size:30px'>"
                    f"{sel['name']}</h2>", unsafe_allow_html=True)
                st.markdown(
                    f"<p style='color:#888;line-height:1.7;font-size:13px'>{sel['description']}</p>",
                    unsafe_allow_html=True)
                st.markdown(f"""
                <div style='margin:14px 0'>
                  <span style='background:rgba(201,168,76,0.07);border:1px solid rgba(201,168,76,0.22);
                    border-radius:20px;padding:4px 12px;font-size:11px;color:#c9a84c;
                    letter-spacing:1px;text-transform:uppercase;margin-right:8px'>
                    ⏱ {sel['duration']}
                  </span>
                  <span style='background:rgba(201,168,76,0.07);border:1px solid rgba(201,168,76,0.22);
                    border-radius:20px;padding:4px 12px;font-size:11px;color:#c9a84c;
                    letter-spacing:1px;text-transform:uppercase'>
                    👤 {sel['role']}
                  </span>
                </div>
                <div style='font-family:Cormorant Garamond;font-size:44px;
                  color:#c9a84c;font-weight:600;margin:12px 0'>
                  ₹{sel['price']:,}
                </div>""", unsafe_allow_html=True)

            st.markdown("<hr style='border-color:rgba(201,168,76,0.1);margin:18px 0'>",
                        unsafe_allow_html=True)
            st.markdown(
                "<h3 style='font-family:Cormorant Garamond;color:#c9a84c;"
                "font-size:22px;margin-bottom:16px'>📋 Book This Service</h3>",
                unsafe_allow_html=True)

            bc1, bc2 = st.columns(2)
            with bc1:
                b_date = st.date_input("📅 Date")
                c_name = st.text_input("👤 Your Name")
            with bc2:
                b_slot  = st.selectbox("🕐 Time Slot", TIME_SLOTS)
                c_phone = st.text_input("📱 Phone Number")

            if st.button("💎 Confirm Booking", use_container_width=True):
                if not c_name.strip() or not c_phone.strip():
                    st.error("Please enter your name and phone number.")
                else:
                    taken = list(
                        db.collection("bookings")
                        .where("booking_date", "==", str(b_date))
                        .where("time_slot",    "==", b_slot)
                        .where("service",      "==", sel["name"])
                        .stream()
                    )
                    if len(taken) >= 4:
                        st.error("⚠️ This slot is fully booked (max 4). Please pick another time.")
                    else:
                        otp = generate_otp()

                        # AI tip (non-blocking)
                        ai_tip = f"Thank you for booking {sel['name']}! We look forward to welcoming you."
                        try:
                            resp = requests.post(
                                AI_API_URL,
                                headers={"Authorization": f"Bearer {AI_API_KEY}",
                                         "Content-Type": "application/json"},
                                json={"messages": [{"role": "user",
                                      "content": (f"In 2-3 warm, luxurious sentences, "
                                                  f"give a welcoming tip about this salon service: {sel['name']}.")}]},
                                timeout=8,
                            )
                            ai_tip = resp.json()["choices"][0]["message"]["content"]
                        except Exception:
                            pass

                        # Save booking (OTP stored alongside)
                        db.collection("bookings").add({
                            "customer_name": c_name.strip(),
                            "phone":         c_phone.strip(),
                            "service":       sel["name"],
                            "booking_date":  str(b_date),
                            "time_slot":     b_slot,
                            "assigned_role": sel["role"],
                            "price":         sel["price"],
                            "status":        "Pending",
                            "otp":           otp,
                            "created_at":    str(datetime.now()),
                        })

                        # ── Booking confirmed + OTP display ────────────
                        st.success("✅ Booking confirmed!")
                        st.markdown(f"""
                        <div class='otp-reveal'>
                          <div class='otp-label'>Your Service OTP</div>
                          <div class='otp-number'>{otp}</div>
                          <div style='color:#5a4e2e;font-size:12px;margin-top:12px;
                            letter-spacing:1px;line-height:1.6'>
                            Show this code to your worker when the service is finished.<br>
                            They will enter it to mark the service as complete.
                          </div>
                        </div>""", unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style='background:rgba(201,168,76,0.06);
                          border:1px solid rgba(201,168,76,0.2);border-radius:12px;
                          padding:16px;color:#c9a84c;font-style:italic;
                          line-height:1.7;font-size:13px;margin-top:4px'>
                          ✨ {ai_tip}
                        </div>""", unsafe_allow_html=True)

                        st.markdown(
                            "<p style='color:#555;font-size:12px;margin-top:10px'>"
                            "🎈 Click the balloons to pop them!</p>",
                            unsafe_allow_html=True)
                        st.markdown(BALLOON_HTML, unsafe_allow_html=True)

            if st.button("✕ Close"):
                st.session_state["selected_service"] = None
                st.rerun()

        _service_dialog()

    # ── AI ASSISTANT DIALOG ──────────────────────────────────

    if st.session_state["open_ai"]:
        @st.dialog("✨ PNB Beauty AI Assistant", width="large")
        def _ai_dialog():
            st.markdown(
                "<p style='color:#777;line-height:1.7;margin-bottom:14px'>"
                "Ask anything about beauty, skincare, haircare, makeup or wellness.</p>",
                unsafe_allow_html=True)
            q = st.text_input("💬 Your Question",
                              placeholder="e.g. What treatment is best for frizzy hair?")
            if st.button("✨ Ask AI", use_container_width=True):
                if q.strip():
                    with st.spinner("Consulting our beauty expert..."):
                        try:
                            r = requests.post(
                                AI_API_URL,
                                headers={"Authorization": f"Bearer {AI_API_KEY}",
                                         "Content-Type": "application/json"},
                                json={"messages": [{"role": "user",
                                      "content": (f"You are a luxury salon AI beauty consultant "
                                                  f"for PNB Smart & Luxurious Salon. "
                                                  f"Answer helpfully and warmly: {q}")}]},
                                timeout=15,
                            )
                            ans = r.json()["choices"][0]["message"]["content"]
                            st.markdown(f"""
                            <div style='background:rgba(201,168,76,0.06);
                              border:1px solid rgba(201,168,76,0.2);border-radius:12px;
                              padding:20px;color:#e8d5a3;line-height:1.8;font-size:14px'>
                              {ans}
                            </div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(str(e))
            if st.button("✕ Close"):
                st.session_state["open_ai"] = False
                st.rerun()

        _ai_dialog()


# ══════════════════════════════════════════════════════
#  📅  MY BOOKINGS
# ══════════════════════════════════════════════════════

elif mode == "📅 My Bookings":
    st.markdown("<h1 class='section-heading'>📅 My Bookings</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#555;margin-bottom:22px'>"
        "Enter your phone number to view your bookings and OTP.</p>",
        unsafe_allow_html=True)

    ph = st.text_input("📱 Phone Number")
    if st.button("Load My Bookings"):
        if ph.strip():
            st.session_state["bookings_phone"] = ph.strip()
        else:
            st.warning("Please enter your phone number.")

    lookup = st.session_state.get("bookings_phone", "")
    if lookup:
        # Loyalty points
        ldoc  = db.collection("loyalty_points").document(lookup).get()
        pts   = ldoc.to_dict().get("points", 0) if ldoc.exists else 0
        snap  = [d.to_dict() for d in db.collection("bookings").stream()
                 if d.to_dict().get("phone") == lookup]
        cname = ldoc.to_dict().get("customer_name", "Guest") if ldoc.exists else (
                snap[0].get("customer_name", "Guest") if snap else "Guest")

        st.markdown(f"""
        <div class='loy-banner'>
          <div style='font-size:48px'>💎</div>
          <div>
            <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:24px'>{cname}</div>
            <div style='color:#555;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-top:3px'>Loyalty Points</div>
            <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:38px;font-weight:600;line-height:1'>{pts}</div>
            <div style='color:#444;font-size:12px;margin-top:3px'>🐾 Spend in the Pet Shop!</div>
          </div>
        </div>""", unsafe_allow_html=True)

        docs = [(d.id, d.to_dict()) for d in db.collection("bookings").stream()
                if d.to_dict().get("phone") == lookup]

        if not docs:
            st.markdown("""
            <div style='text-align:center;padding:44px;color:#3a3020'>
              <div style='font-size:44px;margin-bottom:12px'>🔍</div>
              <p>No active bookings found for this number.</p>
            </div>""", unsafe_allow_html=True)
        else:
            for doc_id, bk in docs:
                status = bk.get("status", "Pending")
                otp    = bk.get("otp", "——")

                st.markdown(f"""
                <div class='booking-card'>
                  <div style='font-family:Cormorant Garamond;font-size:22px;
                    color:#c9a84c;margin-bottom:8px'>{bk.get('service')}</div>
                  <div style='display:flex;gap:18px;flex-wrap:wrap;
                    color:#666;font-size:12px;margin-bottom:14px'>
                    <span>📅 {bk.get('booking_date')}</span>
                    <span>🕐 {bk.get('time_slot')}</span>
                    <span>💰 ₹{bk.get('price','—')}</span>
                    <span>👤 {bk.get('assigned_role','')}</span>
                  </div>
                  <div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:12px'>
                    <span class='status-{status.lower()}'>● {status}</span>
                    <div style='background:rgba(201,168,76,0.08);
                      border:1px solid rgba(201,168,76,0.28);border-radius:12px;
                      padding:6px 18px;font-family:Cormorant Garamond;color:#c9a84c;
                      font-size:22px;letter-spacing:8px;font-weight:600'>
                      🔐 {otp}
                    </div>
                  </div>
                  <div style='color:#444;font-size:11px;letter-spacing:1px'>
                    Show this OTP to your worker when the service is finished
                  </div>
                </div>""", unsafe_allow_html=True)

                if st.button("❌ Cancel Booking", key=f"cancel_{doc_id}"):
                    db.collection("bookings").document(doc_id).delete()
                    st.success(f"✅ '{bk.get('service')}' booking cancelled.")
                    st.rerun()


# ══════════════════════════════════════════════════════
#  🐾  PET SHOP
# ══════════════════════════════════════════════════════

elif mode == "🐾 Pet Shop":
    st.markdown("<h1 class='section-heading'>🐾 Digital Pet Shop</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#666;margin-bottom:8px;line-height:1.7'>
      Earn <span style='color:#c9a84c;font-weight:600'>5 loyalty points</span> every time a
      service is completed. Adopt digital companions,
      <span style='color:#c9a84c'>sell them back</span> for full points, or
      <span style='color:#c05050'>delete them</span> (no refund).
    </p>""", unsafe_allow_html=True)

    sp = st.text_input("📱 Enter your phone number", key="sp_input")
    if st.button("Check My Points & Shop"):
        if sp.strip():
            st.session_state["shop_phone"] = sp.strip()
        else:
            st.warning("Please enter your phone number.")

    spv = st.session_state.get("shop_phone", "")
    if spv:
        lref  = db.collection("loyalty_points").document(spv)
        ldoc  = lref.get()
        pts   = ldoc.to_dict().get("points", 0) if ldoc.exists else 0
        cname = ldoc.to_dict().get("customer_name", "Guest") if ldoc.exists else "Guest"

        oref     = db.collection("owned_pets").document(spv)
        odoc     = oref.get()
        own_pets = odoc.to_dict().get("pets", []) if odoc.exists else []

        # Points banner
        st.markdown(f"""
        <div class='loy-banner' style='margin:18px 0 30px'>
          <div style='font-size:56px'>💎</div>
          <div>
            <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:26px'>{cname}</div>
            <div style='color:#444;font-size:10px;letter-spacing:2px;text-transform:uppercase'>Balance</div>
            <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:52px;font-weight:600;line-height:1'>{pts}</div>
            <div style='color:#666;font-size:12px'>loyalty points</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Owned pets section
        if own_pets:
            st.markdown("<h3 style='font-family:Cormorant Garamond;color:#c9a84c;"
                        "font-size:24px;margin-bottom:14px'>🏡 Your Pets</h3>",
                        unsafe_allow_html=True)
            pg = st.columns(min(len(own_pets), 4))
            for pi, pname in enumerate(own_pets):
                pd = next((p for p in DIGITAL_PETS if p["name"] == pname), None)
                if not pd:
                    continue
                rc = RARITY_COLORS.get(pd["rarity"], "#888")
                with pg[pi % 4]:
                    st.markdown(f"""
                    <div class='pet-card' style='background:linear-gradient(145deg,#0f0d09,#1a1610);
                      border:1px solid {rc}55'>
                      <div style='font-size:52px;margin-bottom:8px'>{pd['emoji']}</div>
                      <div style='font-family:Cormorant Garamond;color:#c9a84c;font-size:17px'>{pd['name']}</div>
                      <div style='color:{rc};font-size:10px;letter-spacing:1px;
                        text-transform:uppercase;margin-top:3px'>✦ {pd['rarity']} ✦</div>
                      <div style='color:#555;font-size:11px;margin-top:5px'>Worth {pd['cost']} pts</div>
                    </div>""", unsafe_allow_html=True)

                    sc, dc = st.columns(2)
                    with sc:
                        if st.button("💰 Sell", key=f"sell_{pi}_{pname}"):
                            lref.set({"customer_name": cname, "phone": spv,
                                      "points": pts + pd["cost"]})
                            oref.set({"phone": spv,
                                      "pets": [p for p in own_pets if p != pname]})
                            st.success(f"💰 Sold {pd['name']} · +{pd['cost']} pts!")
                            st.rerun()
                    with dc:
                        if st.button("🗑️ Delete", key=f"del_{pi}_{pname}"):
                            oref.set({"phone": spv,
                                      "pets": [p for p in own_pets if p != pname]})
                            st.warning(f"🗑️ {pd['name']} deleted. No points refunded.")
                            st.rerun()

        # Shop
        st.markdown("<h3 style='font-family:Cormorant Garamond;color:#c9a84c;"
                    "font-size:24px;margin:26px 0 14px'>🛒 Available Pets</h3>",
                    unsafe_allow_html=True)
        pc = st.columns(3)
        for pi, pet in enumerate(DIGITAL_PETS):
            rc     = RARITY_COLORS.get(pet["rarity"], "#888")
            owned  = pet["name"] in own_pets
            afford = pts >= pet["cost"]
            with pc[pi % 3]:
                st.markdown(f"""
                <div class='pet-card' style='background:linear-gradient(145deg,#0f0d09,#1a1610);
                  border:1px solid {rc}55; {"opacity:.42;" if owned else ""}'>
                  <div style='font-size:60px;margin-bottom:10px'>{pet['emoji']}</div>
                  <div style='font-family:Cormorant Garamond;color:#c9a84c;
                    font-size:20px;margin-bottom:4px'>{pet['name']}</div>
                  <div style='color:{rc};font-size:10px;letter-spacing:2px;
                    text-transform:uppercase;margin-bottom:10px'>✦ {pet['rarity']} ✦</div>
                  <div style='color:#555;font-size:12px;line-height:1.5;margin-bottom:12px'>{pet['description']}</div>
                  <div style='font-family:Cormorant Garamond;color:#c9a84c;
                    font-size:26px;font-weight:600'>{pet['cost']} pts</div>
                  {"<div style='color:#3ab26e;font-size:11px;margin-top:6px;letter-spacing:1px'>✅ OWNED</div>" if owned else ""}
                  {"<div style='color:#333;font-size:11px;margin-top:6px'>Not enough points</div>" if not afford and not owned else ""}
                </div>""", unsafe_allow_html=True)

                if not owned:
                    if st.button("🐾 Adopt", key=f"adopt_{pi}", disabled=not afford):
                        lref.set({"customer_name": cname, "phone": spv,
                                  "points": pts - pet["cost"]})
                        oref.set({"phone": spv, "pets": own_pets + [pet["name"]]})
                        st.success(f"🎉 You adopted {pet['emoji']} {pet['name']}!")
                        st.rerun()


# ══════════════════════════════════════════════════════
#  🔒  WORKER LOGIN
# ══════════════════════════════════════════════════════

elif mode == "🔒 Worker Login":
    st.markdown("<h1 class='section-heading'>🔒 Worker Dashboard</h1>", unsafe_allow_html=True)

    pwd = st.text_input("Password", type="password")

    if pwd == WORKER_PASSWORD:
        st.markdown(
            "<div style='color:#3ab26e;font-size:12px;letter-spacing:1px;"
            "margin-bottom:18px'>✅ ACCESS GRANTED</div>",
            unsafe_allow_html=True)

        role = st.selectbox("Select Your Role", WORKER_ROLES)

        all_docs = [
            (d.id, d.to_dict()) for d in db.collection("bookings").stream()
            if d.to_dict().get("assigned_role") == role
        ]

        if not all_docs:
            st.markdown("""
            <div style='text-align:center;padding:44px;color:#2e2618'>
              <div style='font-size:44px;margin-bottom:12px'>🎉</div>
              <p>No bookings assigned to your role right now.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<p style='color:#555;font-size:12px;margin-bottom:18px'>"
                f"{len(all_docs)} booking(s) assigned to you</p>",
                unsafe_allow_html=True)

            for doc_id, bk in all_docs:
                status = bk.get("status", "Pending")

                st.markdown(f"""
                <div class='booking-card'>
                  <div class='w-badge'>{bk.get('assigned_role','')}</div>
                  <div style='font-family:Cormorant Garamond;font-size:24px;
                    color:#c9a84c;margin-bottom:6px'>{bk.get('service')}</div>
                  <div style='color:#aaa;font-size:13px;margin-bottom:4px'>
                    👤 {bk.get('customer_name')} &nbsp;·&nbsp; 📱 {bk.get('phone')}
                  </div>
                  <div style='display:flex;gap:18px;flex-wrap:wrap;
                    color:#555;font-size:12px;margin-bottom:10px'>
                    <span>📅 {bk.get('booking_date')}</span>
                    <span>🕐 {bk.get('time_slot')}</span>
                    <span>💰 ₹{bk.get('price','—')}</span>
                  </div>
                  <span class='status-{status.lower()}'>● {status}</span>
                </div>""", unsafe_allow_html=True)

                col_a, col_c, col_d = st.columns([2, 4, 2])

                # Accept
                with col_a:
                    if status == "Pending":
                        if st.button("✅ Accept", key=f"acc_{doc_id}"):
                            db.collection("bookings").document(doc_id).update({"status": "Accepted"})
                            st.rerun()

                # Verify OTP → Complete
                with col_c:
                    if status == "Accepted":
                        entered = st.text_input(
                            "🔐 Ask customer for their OTP",
                            key=f"otp_in_{doc_id}",
                            max_chars=6,
                            placeholder="Enter 6-digit OTP from customer",
                        )
                        if st.button("🏆 Verify OTP & Complete", key=f"cmp_{doc_id}"):
                            stored_otp = bk.get("otp", "")
                            if not stored_otp:
                                # Edge case: no OTP stored — allow completion
                                complete_booking(doc_id, bk)
                                st.success("✅ Service completed! Customer earned 5 💎 loyalty points.")
                                st.rerun()
                            elif entered.strip() == stored_otp:
                                complete_booking(doc_id, bk)
                                st.success("✅ OTP verified! Service marked complete. Customer earned 5 💎 loyalty points.")
                                st.rerun()
                            else:
                                st.error("❌ Incorrect OTP. Ask the customer to check their booking screen.")
                    elif status == "Pending":
                        st.markdown(
                            "<div style='color:#444;font-size:12px;padding-top:8px'>"
                            "Accept the booking first to enable OTP verification.</div>",
                            unsafe_allow_html=True)

                # Delete
                with col_d:
                    if st.button("🗑️ Delete", key=f"wdel_{doc_id}"):
                        db.collection("bookings").document(doc_id).delete()
                        st.warning("Booking deleted.")
                        st.rerun()

    elif pwd:
        st.error("❌ Incorrect password.")


# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class='salon-footer'>
  <div class='gold-line'></div>
  <p>Crafted with elegance by
    <span>PNB Smart &amp; Luxurious Salon</span>
    &nbsp;·&nbsp; AI-Powered Beauty Experience
  </p>
</div>""", unsafe_allow_html=True)
