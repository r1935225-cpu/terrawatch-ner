import requests
import os

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_real_rainfall(lat, lon):
    """Fetch real rainfall from OpenWeatherMap"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_KEY,
            "units": "metric"
        }
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        
        # rainfall in last 1 hour (mm)
        rain = data.get("rain", {}).get("1h", 0)
        humidity = data.get("main", {}).get("humidity", 50)
        
        return {
            "rainfall_1hr": rain,
            "rainfall_24hr": rain * 24,  # estimate
            "humidity": humidity,
            "description": data.get("weather", [{}])[0].get("description", "")
        }
    except Exception as e:
        print(f"Weather API error: {e}")
        return {"rainfall_1hr": 0, "rainfall_24hr": 0, "humidity": 50}

def get_real_seismic(lat, lon):
    """Fetch real seismic data from USGS (completely free)"""
    try:
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "latitude": lat,
            "longitude": lon,
            "maxradius": 2,       # 2 degrees radius
            "minmagnitude": 2.0,
            "orderby": "time",
            "limit": 5
        }
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        features = data.get("features", [])
        
        if features:
            # Get strongest recent quake magnitude
            magnitudes = [f["properties"]["mag"] for f in features]
            return round(max(magnitudes) / 10, 2)  # normalize to 0-1
        return 0.1  # baseline low seismic
    except:
        return 0.1