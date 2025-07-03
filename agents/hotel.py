import os
from google.generativeai import GenerativeModel

# Static data
HOTEL_DATA = {
    "hunza": [
        {"name": "Hunza Serena Inn", "price": 4000, "rating": 4.5},
        {"name": "Eagle's Nest Hotel", "price": 3500, "rating": 4.3}
    ],
    "skardu": [
        {"name": "Hotel One Skardu", "price": 4500, "rating": 4.6},
        {"name": "Shangrila Resort", "price": 6000, "rating": 4.8}
    ],
    "murree": [
        {"name": "Move n Pick Hotel Murree", "price": 3200, "rating": 4.4},
        {"name": "Lockwood Hotel", "price": 2800, "rating": 4.2}
    ]
}

# Initialize Gemini Model
model = GenerativeModel("gemini-1.5-flash")

def get_hotels(city):
    city = city.lower()
    
    # If city is in static list, return it
    if city in HOTEL_DATA:
        return HOTEL_DATA[city]
    
    # Else, use Gemini to suggest
    prompt = f"""
    Suggest 2 affordable hotels in {city.title()} with approx prices (in PKR) and ratings.
    Format as: Name, Price, Rating.
    Example: Hotel One, 4000, 4.5
    """

    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split("\n")
        hotels = []

        for line in lines:
            parts = line.split(",")
            if len(parts) == 3:
                name = parts[0].strip()
                price = int("".join(filter(str.isdigit, parts[1])))
                rating = float(parts[2])
                hotels.append({"name": name, "price": price, "rating": rating})

        return hotels if hotels else [{"name": f"{city.title()} Guest House", "price": 3000, "rating": 4.0}]
    
    except Exception as e:
        return [{"name": f"{city.title()} Hotel", "price": 3000, "rating": 4.0}]
