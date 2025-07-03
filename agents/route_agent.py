# agents/route_agent.py

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geolocator = Nominatim(user_agent="travel_agent_ai")

def get_coords(city):
    try:
        location = geolocator.geocode(city)
        if location:
            return (location.latitude, location.longitude)
    except:
        return None
    return None

def get_route_distance(from_city, to_city):
    from_coords = get_coords(from_city)
    to_coords = get_coords(to_city)

    if from_coords and to_coords:
        return int(geodesic(from_coords, to_coords).km)
    return None
