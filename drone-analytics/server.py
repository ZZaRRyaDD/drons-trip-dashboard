# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random

app = FastAPI()

# Настройка CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Фиктивные данные для генерации
REGIONS = [
    "RU-MOW", "RU-SPE", "RU-SAR", "RU-ROS", "RU-KO", "RU-SA", "RU-ME", "RU-UD",
    "RU-STA", "RU-KDA", "RU-LEN", "RU-YAR", "RU-IVA", "RU-KIR", "RU-NIZ", "RU-VLA"
]

COORDS_MAP = {
    "RU-MOW": (55.7558, 37.6176),
    "RU-SPE": (59.9311, 30.3609),
    "RU-SAR": (51.5406, 46.0086),
    "RU-ROS": (47.2357, 39.7015),
    "RU-KO": (63.8883, 53.1079),
    "RU-SA": (62.0083, 129.7332),
    "RU-ME": (56.6442, 47.8206),
    "RU-UD": (56.8520, 53.2012),
    "RU-STA": (45.0448, 42.2692),
    "RU-KDA": (45.0405, 38.9758),
    "RU-LEN": (59.9311, 30.3609),
    "RU-YAR": (57.6266, 39.8941),
    "RU-IVA": (56.8579, 40.5926),
    "RU-KIR": (58.5967, 49.6601),
    "RU-NIZ": (56.3287, 44.0020),
    "RU-VLA": (55.3906, 39.9488),
}

# Словарь для перевода номера дня недели в строку
DAY_NAMES = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

@app.get("/api/flights/")
def get_flights():
    """
    Возвращает список фиктивных полётов дронов с новыми полями.
    """
    flights = []
    num_flights = 200

    for i in range(num_flights):
        # Генерируем случайные даты за последний месяц
        now = datetime.now()
        start_date = now - timedelta(days=30)
        takeoff_datetime = start_date + timedelta(
            seconds=random.randint(0, int((now - start_date).total_seconds()))
        )
        duration_minutes = random.uniform(5, 180)
        landing_datetime = takeoff_datetime + timedelta(minutes=duration_minutes)

        # Выбираем случайные регионы
        takeoff_region_code = random.choice(REGIONS)
        landing_region_code = random.choice(REGIONS)

        takeoff_base_lat, takeoff_base_lon = COORDS_MAP[takeoff_region_code]
        landing_base_lat, landing_base_lon = COORDS_MAP[landing_region_code]

        takeoff_coords = {
            "lat": round(takeoff_base_lat + random.uniform(-0.5, 0.5), 6),
            "lon": round(takeoff_base_lon + random.uniform(-0.5, 0.5), 6)
        }
        landing_coords = {
            "lat": round(landing_base_lat + random.uniform(-0.5, 0.5), 6),
            "lon": round(landing_base_lon + random.uniform(-0.5, 0.5), 6)
        }

        # --- Новое вычисление дня недели на сервере ---
        takeoff_day_of_week = DAY_NAMES[takeoff_datetime.weekday()]

        flight = {
            "id": f"flight_{i+1}",
            "takeoff_region": takeoff_region_code,
            "landing_region": landing_region_code,
            "takeoff_time": takeoff_datetime.strftime("%H:%M:%S"),
            "takeoff_date": takeoff_datetime.strftime("%Y-%m-%d"),
            "landing_time": landing_datetime.strftime("%H:%M:%S"),
            "landing_date": landing_datetime.strftime("%Y-%m-%d"),
            "takeoff_day_of_week": takeoff_day_of_week, # Новое поле
            "takeoffCoords": takeoff_coords,
            "landingCoords": landing_coords,
            "duration": round(duration_minutes, 2),
        }
        flights.append(flight)

    return flights

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
