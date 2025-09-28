// src/App.js
import React, { useState } from 'react';
import Header from './components/Header/Header';
import Map from './components/Map/Map';
// import RegionDetails from './components/RegionDetails/RegionDetails'; // Убираем импорт
import FlightDashboard from './components/FlightDashboard/FlightDashboard';
import './App.css';

function App() {
  const [selectedRegion, setSelectedRegion] = useState(null); // Теперь хранит объект {code, title} или null

  const handleRegionSelect = (region) => {
    setSelectedRegion(region);
    console.log("Выбран регион:", region); // Для отладки
  };

  const handleShowAllRegions = () => {
    setSelectedRegion(null); // Сбрасываем выбранный регион
    console.log("Показать все регионы"); // Для отладки
  };

  return (
    <div className="App">
      <Header />
      <main className="app-main">
        <div className="map-container">
          <Map selectedRegionCode={selectedRegion?.code} onRegionSelect={handleRegionSelect} />
        </div>
        <div className="dashboard-container">
          {/* Передаём код региона в FlightDashboard */}
          <FlightDashboard selectedRegionCode={selectedRegion?.code} />
        </div>
        {/* Добавляем кнопку "Все регионы" */}
        <div className="controls-container">
          <button onClick={handleShowAllRegions} disabled={!selectedRegion}>
            Анализ всех регионов
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;