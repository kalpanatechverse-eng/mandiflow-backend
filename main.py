import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
# In-memory storage for live roster demo
LIVE_BOOKINGS = []

app = FastAPI(title="MandiFlow API")

# CORS fix for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    # sslmode require add pannirukom Supabase connection-kaga
    return psycopg2.connect(DATABASE_URL, sslmode='require', cursor_factory=RealDictCursor)

CROP_CAPS = {
    "Paddy": 100,
    "Maize": 90,
    "Wheat": 60,
    "Groundnut": 36,
    "Cotton": 30,
    "Chana": 24,
    "Mustard": 24
}

class LandVerifyRequest(BaseModel):
    khasra_no: str
    commodity: str

class BookingRequest(BaseModel):
    farmer_name: str
    phone: str
    aadhaar_id: str
    khasra_no: str
    commodity: str
    quantity_bags: int

@app.get("/")
def root():
    return {"status": "online", "message": "MandiFlow Backend is running smoothly"}

@app.post("/api/verify-land")
def verify_land(req: LandVerifyRequest):
    acres = 3.5
    cap = CROP_CAPS.get(req.commodity, 50)
    max_bags = int(acres * cap)
    return {
        "verified": True,
        "farmer_name": "Gurpreet Singh Gill",
        "certified_acres": acres,
        "commodity": req.commodity,
        "max_bags": max_bags
    }

@app.post("/api/book-slot")
def book_slot(req: BookingRequest):
    acres = 3.5
    cap = CROP_CAPS.get(req.commodity, 50)
    max_bags = int(acres * cap)

    if req.quantity_bags > max_bags:
        raise HTTPException(status_code=400, detail=f"Quota exceeded! Max allowed for {req.commodity} is {max_bags} bags.")

    token_id = f"FM-{random.randint(200, 999)}"
    arrival_window = "10:30 AM - 11:00 AM"

    new_entry = {
        "token_id": token_id,
        "farmer_name": req.farmer_name,
        "commodity": req.commodity,
        "quantity_bags": req.quantity_bags,
        "arrival_window": arrival_window,
        "status": "Approved / Anti-Recycling Active"
    }
    
    # Save into live roster memory
    LIVE_BOOKINGS.insert(0, new_entry)

    return new_entry

    @app.get("/api/bookings")
def get_bookings():
    return LIVE_BOOKINGS
       


