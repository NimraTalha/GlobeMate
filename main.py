# smart_travel_agent/main.py

import os
import re
import chainlit as cl
from dotenv import load_dotenv
from google.generativeai import configure, GenerativeModel

# Agents
from agents.route_agent import get_route_distance
from agents.expense_agent import calculate_trip_expenses
from agents.hotel import get_hotels
from agents.food_agent import get_foods
from agents.attraction_agent import get_attractions

# Load Gemini API Key
load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-1.5-flash")

@cl.on_chat_start
async def start():
    await cl.Message(content="""
✨ **Welcome to the Smart Travel Agent!** 
Ask your travel question in **any language** (Urdu, Hindi, English, etc.)

**Examples:**
- *Main Lahore se Hunza jana chahti hoon bike pe. Petrol 295 ka hai. 5 din ka tour hai.*
- *Plan a 7-day road trip from Islamabad to Skardu by car.*
    """).send()

@cl.on_message
async def main(message: cl.Message):
    user_input = message.content

    # Step 1: Extract trip info via Gemini
    prompt = f"""
You are an AI travel agent. Parse the user's message (in any language) and extract:
From: (city)
To: (city)
Mode: (car/bike)
Average: (fuel average)
FuelPrice: (price per liter)
Days: (trip duration)

User message: {user_input}
    """

    response = model.generate_content(prompt)
    parsed = response.text.strip()

    # Step 2: Extract structured data
    def extract(pattern, text):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    from_city = extract(r'From:\s*(.+)', parsed)
    to_city = extract(r'To:\s*(.+)', parsed)
    mode = extract(r'Mode:\s*(.+)', parsed)
    avg = extract(r'Average:\s*(\d+)', parsed)
    fuel_price = extract(r'FuelPrice:\s*(\d+)', parsed)
    days = extract(r'Days:\s*(\d+)', parsed)

    if not all([from_city, to_city, avg, fuel_price, days]):
        await cl.Message(content="⚠️ Couldn't extract all travel details. Please rephrase your query.").send()
        return

    # Step 3: Get distance
    distance = get_route_distance(from_city, to_city)
    if distance is None:
        await cl.Message(content=f"❌ No route data found for: {from_city} → {to_city}").send()
        return

    # Step 4: Expense Calculation
    result = calculate_trip_expenses(
        distance_km=distance,
        days=int(days),
        avg_kmpl=int(avg),
        fuel_price=int(fuel_price)
    )

    # Step 5: Hotel, Food, Attractions
    hotels = get_hotels(to_city)
    foods = get_foods(to_city)
    spots = get_attractions(to_city)

    hotel_list = "\n".join(
        [f"- 🏨 {h['name']} — Rs. {h['price']} (⭐ {h['rating']})" for h in hotels]
    ) if hotels else "No hotel data available."

    food_list = "\n".join([f"- 🍽️ {f}" for f in foods]) if foods else "No food data."
    spot_list = "\n".join([f"- 📍 {s}" for s in spots]) if spots else "No tourist spot info."

    # Step 6: Final Output
    await cl.Message(content=f"""
✅ **Travel Summary**

- **From:** {from_city.title()}
- **To:** {to_city.title()}
- **Distance:** {distance} km
- **Mode:** {mode}
- **Days:** {days}

💰 **Estimated Costs**
- ⛽ Fuel: Rs. {result['fuel_cost']}
- 🏨 Hotel: Rs. {result['hotel_cost']}
- 🍽️ Food: Rs. {result['food_cost']}
- 💵 **Total: Rs. {result['total_trip_cost']}**

🏨 **Hotels in {to_city.title()}**
{hotel_list}

🍽️ **Popular Foods**
{food_list}

🗺️ **Attractions**
{spot_list}
    """).send()
# streamlit_main.py

import os
import re
import streamlit as st
from dotenv import load_dotenv
from google.generativeai import configure, GenerativeModel

# Custom agents
from agents.route_agent import get_route_distance
from agents.expense_agent import calculate_trip_expenses
from agents.hotel import get_hotels
from agents.food_agent import get_foods
from agents.attraction_agent import get_attractions

# Load Gemini API key
load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-1.5-flash")

# UI Title
st.set_page_config(page_title="🌍 Smart Travel Agent")
st.title("🌍 Smart Travel Agent (Multilingual)")

st.markdown("""
Type your travel query in **any language** (English, Urdu, Hindi etc.)

📌 Examples:
- *Main Lahore se Hunza jana chahti hoon bike pe. Petrol 295 ka hai. 5 din ka tour hai.*
- *Plan a 7-day road trip from Islamabad to Skardu by car.*

---
""")

user_input = st.text_area("✈️ Enter your travel query:")

if st.button("Plan My Trip") and user_input:
    with st.spinner("🔎 Understanding your trip..."):

        prompt = f"""
You are an AI travel agent. Parse the user's message (in any language) and extract:
From: (city)
To: (city)
Mode: (car/bike)
Average: (fuel average)
FuelPrice: (price per liter)
Days: (trip duration)

User message: {user_input}
        """

        response = model.generate_content(prompt)
        parsed = response.text.strip()

        def extract(pattern, text):
            match = re.search(pattern, text, re.IGNORECASE)
            return match.group(1).strip() if match else None

        from_city = extract(r'From:\s*(.+)', parsed)
        to_city = extract(r'To:\s*(.+)', parsed)
        mode = extract(r'Mode:\s*(.+)', parsed)
        avg = extract(r'Average:\s*(\d+)', parsed)
        fuel_price = extract(r'FuelPrice:\s*(\d+)', parsed)
        days = extract(r'Days:\s*(\d+)', parsed)

        if not all([from_city, to_city, avg, fuel_price, days]):
            st.error("❌ Sorry! Could not understand your full travel plan. Please rephrase.")
        else:
            distance = get_route_distance(from_city, to_city)
            if distance is None:
                st.warning(f"⚠️ Unable to calculate distance from **{from_city}** to **{to_city}**.")
            else:
                result = calculate_trip_expenses(
                    distance_km=distance,
                    days=int(days),
                    avg_kmpl=int(avg),
                    fuel_price=int(fuel_price)
                )

                hotels = get_hotels(to_city)
                foods = get_foods(to_city)
                spots = get_attractions(to_city)

                # Show summary
                st.subheader("✅ Travel Summary")
                st.markdown(f"""
- **From:** {from_city.title()}  
- **To:** {to_city.title()}  
- **Distance:** {distance} km  
- **Mode:** {mode}  
- **Days:** {days}  

💰 **Estimated Costs**  
- ⛽ Fuel: Rs. {result['fuel_cost']}  
- 🏨 Hotel: Rs. {result['hotel_cost']}  
- 🍽️ Food: Rs. {result['food_cost']}  
- 💵 **Total: Rs. {result['total_trip_cost']}**
                """)

                # Hotels
                st.subheader(f"🏨 Hotels in {to_city.title()}")
                if hotels:
                    for h in hotels:
                        st.markdown(f"- **{h['name']}** — Rs. {h['price']} (⭐ {h['rating']})")
                else:
                    st.info("No hotel data found.")

                # Foods
                st.subheader("🍽️ Popular Foods")
                if foods:
                    for f in foods:
                        st.markdown(f"- {f}")
                else:
                    st.info("No food data available.")

                # Attractions
                st.subheader("🗺️ Attractions")
                if spots:
                    for s in spots:
                        st.markdown(f"- {s}")
                else:
                    st.info("No tourist spots found.")
