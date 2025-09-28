// src/components/RegionDetails/RegionDetails.js
import React from 'react';

// Имитация данных API. В реальном приложении это будет импортировано или получено через API.
const mockFlightData = [
  { regionCode: "RU-MOW", regionName: "Москва", flightCount: 12500, totalDuration: 350.5, averageDuration: 16.8 },
  { regionCode: "RU-SPE", regionName: "Санкт-Петербург", flightCount: 8200, totalDuration: 210.2, averageDuration: 15.4 },
  { regionCode: "RU-SAR", regionName: "Саратовская область", flightCount: 1500, totalDuration: 45.0, averageDuration: 18.0 },
  { regionCode: "RU-ROS", regionName: "Ростовская область", flightCount: 2100, totalDuration: 62.3, averageDuration: 17.8 },
  { regionCode: "RU-SA", regionName: "Республика Саха (Якутия)", flightCount: 800, totalDuration: 25.0, averageDuration: 18.75 },
  { regionCode: "RU-KO", regionName: "Республика Коми", flightCount: 1200, totalDuration: 38.0, averageDuration: 19.0 },
  { regionCode: "RU-ME", regionName: "Республика Марий Эл", flightCount: 950, totalDuration: 30.0, averageDuration: 19.0 },
  { regionCode: "RU-UD", regionName: "Удмуртская Республика", flightCount: 1100, totalDuration: 35.0, averageDuration: 19.1 },
  // ... добавьте данные для других регионов
];

const RegionDetails = ({ region }) => {
  if (!region) {
    return (
      <div className="region-details-placeholder">
        <h2>Добро пожаловать!</h2>
        <p>Выберите регион на карте, чтобы увидеть данные о полетной активности дронов.</p>
        <p><em>Данные на этой демонстрации являются примерными.</em></p>
      </div>
    );
  }

  const data = mockFlightData.find(item => item.regionCode === region.code);

  return (
    <div className="region-details">
      <h2>{region.title}</h2>
      {data ? (
        <div className="region-stats">
          <p><strong>Код региона:</strong> {data.regionCode}</p>
          <p><strong>Количество полетов:</strong> {data.flightCount.toLocaleString('ru-RU')}</p>
          <p><strong>Общая длительность (часы):</strong> {data.totalDuration.toFixed(2)}</p>
          <p><strong>Средняя длительность полета (минуты):</strong> {(data.averageDuration).toFixed(2)}</p>
          {/* Можно добавить больше метрик или визуализацию */}
        </div>
      ) : (
        <p>Нет данных для выбранного региона ({region.code}).</p>
      )}
    </div>
  );
};

export default RegionDetails;