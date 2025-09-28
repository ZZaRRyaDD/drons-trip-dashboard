// src/services/api.js
const API_BASE_URL = 'http://127.0.0.1:8000/api'; // URL вашего FastAPI сервера

export const fetchFlightData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/flights/`); // Путь к эндпоинту

    if (!response.ok) {
      throw new Error(`Ошибка при получении данных: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Полученные данные с API:', data);
    return data;
  } catch (error) {
    console.error('Ошибка при вызове API:', error);
    throw error;
  }
};