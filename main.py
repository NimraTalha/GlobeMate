# main.py

import os
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Local imports
from agents.route_agent import get_route_distance
from agents.expense_agent import calculate_trip_expenses
from agents.hotel import get_hotels
from agents.food_agent import get_foods
from agents.attraction_agent import get_attractions


st.set_page_config(page_title="GlobeMate AI", layout="centered")
st.title("🌍 GlobeMate — Smart Travel Agent")
st.markdown("Ask your travel question in any language (Urdu, Hindi, English...)")

user_input = st.text_input("✈️ Enter your travel plan here:")

# Step 1: Get structured trip details from Gemini
@st.cache_data(ttl=3600)
def parse_trip(text):
    prompt = f"""
You are a multilingual AI travel agent. Parse this message into:
From:
To:
Mode: (car or bike)
Average: (km per litre)
FuelPrice: (Rs. per litre)
Days: (trip duration)

User message: {text}
"""
    res = model.generate_content(prompt)
    return res.text.strip()

if user_input:
    with st.spinner("🤖 Understanding your trip..."):
        parsed = parse_trip(user_input)

    # Extract structured info using regex
    def extract(pattern, text):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    from_city = extract(r'From:\s*(.+)', parsed)
    to_city = extract(r'To:\s*(.+)', parsed)
    mode = extract(r'Mode:\s*(.+)', parsed)
    avg = extract(r'Average:\s*(\d+)', parsed)
    fuel_price = extract(r'FuelPrice:\s*(\d+)', parsed)
    days = extract(r'Days:\s*(\d+)', parsed)

    if not all([from_city, to_city, mode, avg, fuel_price, days]):
        st.error("⚠️ Couldn't understand all travel details. Please rephrase your message.")
    else:
        # Show extracted info for confirmation
        with st.expander("📋 Confirm Trip Details"):
            st.markdown(f"""
- **From:** {from_city.title()}
- **To:** {to_city.title()}
- **Mode:** {mode.title()}
- **Average:** {avg} km/l
- **Fuel Price:** Rs. {fuel_price}/l
- **Days:** {days}
""")

        if st.button("🧭 Plan My Trip"):
            with st.spinner("🛣️ Planning your route..."):
                distance = get_route_distance(from_city, to_city)
                if not distance:
                    st.error(f"❌ Route not found from {from_city} to {to_city}.")
                    st.stop()

            with st.spinner("💰 Calculating expenses..."):
                result = calculate_trip_expenses(
                    distance_km=distance,
                    days=int(days),
                    avg_kmpl=int(avg),
                    fuel_price=int(fuel_price)
                )

            with st.spinner("🏨 Fetching hotels, food & places..."):
                hotels = get_hotels(to_city)
                foods = get_foods(to_city)
                spots = get_attractions(to_city)

            hotel_list = "\n".join(
                [f"- 🏨 {h['name']} — Rs. {h['price']} (⭐ {h['rating']})" for h in hotels]
            ) if hotels else "No hotel data available."

            food_list = "\n".join([f"- 🍽️ {f}" for f in foods]) if foods else "No food data."
            spot_list = "\n".join([f"- 📍 {s}" for s in spots]) if spots else "No tourist spot info."

            st.success("✅ Trip Plan Ready!")
            st.markdown(f"""
### ✨ **Travel Summary**

- **From:** {from_city.title()}
- **To:** {to_city.title()}
- **Distance:** {distance} km
- **Mode:** {mode}
- **Days:** {days}

### 💰 **Estimated Costs**
- ⛽ Fuel: Rs. {result['fuel_cost']}
- 🏨 Hotel: Rs. {result['hotel_cost']}
- 🍽️ Food: Rs. {result['food_cost']}
- 💵 **Total: Rs. {result['total_trip_cost']}**

---

### 🏨 Hotels in {to_city.title()}
{hotel_list}

### 🍽️ Popular Foods
{food_list}

### 🗺️ Attractions
{spot_list}
""")
