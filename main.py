# main.py

import os
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Custom agents
from agents.route_agent import get_route_distance
from agents.expense_agent import calculate_trip_expenses
from agents.hotel import get_hotels
from agents.food_agent import get_foods
from agents.attraction_agent import get_attractions

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit App Configuration
st.set_page_config(page_title="🌍 GlobeMate — Smart Travel Agent", layout="centered")
st.markdown(
    "<h1 style='text-align: center; color: #00aaff;'>🌍 GlobeMate</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h4 style='text-align: center;'>Your AI-powered, Multilingual Travel Planner</h4>",
    unsafe_allow_html=True,
)
st.markdown("💬 **Ask your question in any language (Urdu, Hindi, English, etc.)**")
st.markdown("✈️ *Example:* `Main Lahore se Hunza bike pe jana chahti hoon. Petrol 295 ka hai.`")

# User Input
user_input = st.text_input("🗺️ Where are you planning to travel?", placeholder="e.g. Plan a 5-day road trip from Lahore to Skardu by car")

# Step 1: Gemini to parse trip info
@st.cache_data(ttl=600)
def parse_trip(text):
    prompt = f"""
You are a multilingual AI travel assistant. Parse this message and return:
From: 
To: 
Mode: (car or bike)
Average: (fuel avg km/l)
FuelPrice: (price per liter)
Days: (trip duration)

User message: {text}
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# Extract fields
def extract(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None

if user_input:
    with st.spinner("🧠 Understanding your travel plan..."):
        parsed = parse_trip(user_input)

    from_city = extract(r'From:\s*(.+)', parsed)
    to_city = extract(r'To:\s*(.+)', parsed)
    mode = extract(r'Mode:\s*(.+)', parsed)
    avg = extract(r'Average:\s*(\d+)', parsed)
    fuel_price = extract(r'FuelPrice:\s*(\d+)', parsed)
    days = extract(r'Days:\s*(\d+)', parsed)

    if not all([from_city, to_city, mode, avg, fuel_price, days]):
        st.error("⚠️ Sorry! Couldn't extract all travel details. Please rephrase your input.")
        st.stop()

    st.success("✅ Travel details detected:")
    st.markdown(f"""
- **From:** {from_city.title()}
- **To:** {to_city.title()}
- **Mode of Travel:** {mode}
- **Fuel Average:** {avg} km/l
- **Fuel Price:** Rs. {fuel_price}
- **Duration:** {days} days
    """)

    if st.button("🧭 Generate Full Travel Plan"):
        with st.spinner("📍 Getting route distance..."):
            distance = get_route_distance(from_city, to_city)
            if not distance:
                st.error(f"❌ Couldn't get route info from {from_city} to {to_city}")
                st.stop()

        with st.spinner("💰 Calculating estimated expenses..."):
            cost = calculate_trip_expenses(
                distance_km=distance,
                days=int(days),
                avg_kmpl=int(avg),
                fuel_price=int(fuel_price)
            )

        with st.spinner("🔎 Searching for hotels, foods & attractions..."):
            hotels = get_hotels(to_city)
            foods = get_foods(to_city)
            spots = get_attractions(to_city)

        hotel_list = "\n".join([f"- 🏨 {h['name']} — Rs. {h['price']} (⭐ {h['rating']})" for h in hotels]) if hotels else "No hotel data found."
        food_list = "\n".join([f"- 🍽️ {f}" for f in foods]) if foods else "No food data found."
        spot_list = "\n".join([f"- 📍 {s}" for s in spots]) if spots else "No attraction data found."

        # Final Report
        st.markdown("---")
        st.subheader("📋 Your Personalized Travel Plan")

        st.markdown(f"""
### 🚗 Trip Overview
- **From:** {from_city.title()}
- **To:** {to_city.title()}
- **Total Distance:** {distance} km
- **Travel Mode:** {mode}
- **Trip Duration:** {days} days

### 💸 Estimated Costs
- ⛽ **Fuel:** Rs. {cost['fuel_cost']}
- 🏨 **Hotel:** Rs. {cost['hotel_cost']}
- 🍽️ **Food:** Rs. {cost['food_cost']}
- 💵 **Total:** Rs. {cost['total_trip_cost']}

### 🏨 Hotel Recommendations
{hotel_list}

### 🍱 Local Food You Must Try
{food_list}

### 🗺️ Tourist Attractions in {to_city.title()}
{spot_list}
""")

        st.success("🎉 Trip planned successfully! Bon voyage!")
