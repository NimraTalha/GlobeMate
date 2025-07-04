def calculate_fuel_cost(distance_km, avg_kmpl, fuel_price_per_liter):
    liters = distance_km / avg_kmpl
    cost = liters * fuel_price_per_liter
    return round(cost, 2)

def calculate_trip_expenses(distance_km, days, avg_kmpl, fuel_price, hotel_per_night=3000, food_per_day=1000):
    fuel_cost = calculate_fuel_cost(distance_km, avg_kmpl, fuel_price)
    hotel_cost = days * hotel_per_night
    food_cost = days * food_per_day
    total = fuel_cost + hotel_cost + food_cost

    return {
        "fuel_cost": fuel_cost,
        "hotel_cost": hotel_cost,
        "food_cost": food_cost,
        "total_trip_cost": total
    }
