ATTRACTION_DATA = {
    "hunza": [
        "Altit Fort", "Baltit Fort", "Attabad Lake", "Passu Cones"
    ],
    "skardu": [
        "Shangrila Resort", "Satpara Lake", "Deosai Plains", "Skardu Fort"
    ]
}

def get_attractions(city):
    city = city.lower()
    return ATTRACTION_DATA.get(city, [])
