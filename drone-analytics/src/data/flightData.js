// src/data/flightData.js
// Вспомогательная функция для генерации случайной даты в пределах последнего месяца
function getRandomDate() {
  const now = new Date();
  const oneMonthAgo = new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000)); // 30 дней в миллисекундах
  const randomTime = oneMonthAgo.getTime() + Math.random() * (now.getTime() - oneMonthAgo.getTime());
  return new Date(randomTime);
}

// Вспомогательная функция для генерации случайных координат (пример для России)
function getRandomCoords() {
  // Приблизительные границы России (для упрощения)
  const minLat = 41.18; // южная точка
  const maxLat = 81.86; // северная точка
  const minLon = 19.62; // западная точка (Калининград)
  const maxLon = 190.0; // восточная точка

  const lat = (Math.random() * (maxLat - minLat)) + minLat;
  const lon = (Math.random() * (maxLon - minLon)) + minLon;
  return { lat: parseFloat(lat.toFixed(6)), lon: parseFloat(lon.toFixed(6)) };
}

// Генерация массива данных о полётах
const generateFlightData = (count = 100) => {
  const flights = [];
  for (let i = 0; i < count; i++) {
    const takeoffTime = getRandomDate();
    // Посадка должна быть позже взлёта, например, от 10 минут до 2 часов
    const landingTime = new Date(takeoffTime.getTime() + Math.random() * (2 * 60 * 60 * 1000) + (10 * 60 * 1000));
    const takeoffCoords = getRandomCoords();
    const landingCoords = getRandomCoords(); // Для простоты, необязательно рядом

    flights.push({
      id: `flight_${i + 1}`, // Уникальный ID для каждого полёта
      takeoffTime: takeoffTime.toISOString(),
      landingTime: landingTime.toISOString(),
      takeoffCoords: takeoffCoords,
      landingCoords: landingCoords,
      // Дополнительные поля можно добавить позже
      // regionCode: 'RU-MOW', // Поле, которое может быть получено из координат или предоставлено бекендом
      duration: (landingTime - takeoffTime) / (1000 * 60), // Длительность в минутах
    });
  }
  return flights;
};

const flightData = generateFlightData(200); // Генерируем 200 полётов

export default flightData;