FOOD_DATA = {
    "hunza": [
        "Chapshuro (Hunza meat pie)",
        "Giyaling (buttered wheat bread)",
        "Butter tea"
    ],
    "skardu": [
        "Mamtu (dumplings)",
        "Balay (noodle soup)",
        "Apricot soup"
    ]
}

def get_foods(city):
    city = city.lower()
    return FOOD_DATA.get(city, [])
