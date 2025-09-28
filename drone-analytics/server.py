# python server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random
import pandas as pd
from preprocessing import transform

df = pd.read_excel('2025.xlsx', header=0)

app = FastAPI()

# Настройка CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Словарь для перевода номера дня недели в строку
DAY_NAMES = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

@app.get("/api/flights/")
def get_flights():
    """
    Возвращает список полётов.
    """
    return transform(df=df)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
