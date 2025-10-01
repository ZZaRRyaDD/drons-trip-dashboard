// src/App.js
import React, { useState } from 'react';
import Header from './components/Header/Header';
import FileUpload from './components/FileUpload/FileUpload';
import Map from './components/Map/Map';
import DateFilters from './components/DateFilters/DateFilters';
import Dashboard from './components/Dashboard/Dashboard';
import './App.css';

function App() {
  const [selectedRegion, setSelectedRegion] = useState(null);
  // Состояния для фильтров
  const [dateRange, setDateRange] = useState(() => {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    return {
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0],
    };
  });
  const [analyzeFullBase, setAnalyzeFullBase] = useState(false);

  // Состояние для шага линейного графика
  const [lineChartStep, setLineChartStep] = useState('month');

  // Состояние для данных дашборда, полученных с бэкенда
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRegionSelect = (region) => {
    setSelectedRegion(region);
    // Автоматически вызываем анализ после выбора региона
    // Это приведёт к отправке запроса с новым параметром 'region'
    handleAnalysisClick();
  };

  const sendFiltersToBackend = (filters) => {
    console.log("Отправка фильтров на бэкенд:", filters);
  };

  const handleFiltersChange = (newDateRange, newAnalyzeFullBase) => {
    setDateRange(newDateRange);
    setAnalyzeFullBase(newAnalyzeFullBase);
    // Не вызываем handleAnalysisClick автоматически при изменении фильтров,
    // только при нажатии кнопки или выборе региона
    sendFiltersToBackend({
      start_date: newDateRange.startDate,
      end_date: newDateRange.endDate,
      analyze_full_base: newAnalyzeFullBase,
      line_chart_step: lineChartStep,
    });
  };

  const handleLineChartStepChange = (newStep) => {
    setLineChartStep(newStep);
    sendFiltersToBackend({
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      analyze_full_base: analyzeFullBase,
      line_chart_step: newStep,
    });
  };

  // --- Обработчик кнопки "Анализ" ---
  const handleAnalysisClick = async () => {
    setLoading(true);
    setDashboardData(null); // Сбрасываем предыдущие данные

    const params = new URLSearchParams();
    params.append('from', dateRange.startDate);
    params.append('to', dateRange.endDate);
    params.append('linear-step', lineChartStep);
    if (selectedRegion) { // Отправляем region, если он выбран
      params.append('region', selectedRegion.title);
    }
    params.append('flag_full_dataset', analyzeFullBase.toString());

    const apiUrl = `http://localhost:8000/api/flights/?${params.toString()}`;

    try {
      console.log("Выполнение GET-запроса к:", apiUrl);
      // const response = await fetch(apiUrl, {
      //   method: 'GET',
      //   headers: {
      //     // 'Authorization': `Bearer ${token}`, // Если нужна аутентификация
      //     'Content-Type': 'application/json',
      //   },
      // });
      // if (!response.ok) {
      //   throw new Error(`Ошибка: ${response.status} ${response.statusText}`);
      // }
      // const data = await response.json();
      // console.log("Получены данные анализа:", data);
      // setDashboardData(data);

      // --- ЗАГЛУШКА: используем фиктивные данные, возможно, с учётом region ---
      const mockData = {'total_count_flights': 76902, 'total_duration': 34518836, 'mean_duration': 478, 'count_flights_per_weekday': [{'Пн': 10830}, {'Вт': 11660}, {'Ср': 12414}, {'Чт': 11822}, {'Пт': 11210}, {'Сб': 9103}, {'Вс': 7798}], 'distribution_by_flight_duration': [{'4 - 8 ч': 19135}, {'1 - 2 ч': 6531}, {'8 - 12 ч': 19264}, {'12 - 24 ч': 13949}, {'2 - 4 ч': 9452}, {'10 - 30 мин': 948}, {'30 мин - 1 ч': 2623}, {'< 10 мин': 279}, {'24+ ч': 78}], 'distribution_by_type': {'SHAR': 83, 'BLA': 71620, 'AER': 5199}, 'distribution_null_features': {'Дата посадки': 2578, 'Время посадки': 2578, 'Регион посадки': 11996, 'Широта региона посадки': 11985, 'Долгота региона посадки': 11985, 'Регион вылета': 11484, 'Широта региона вылета': 11472, 'Долгота региона вылета': 11472, 'Дата вылета': 2065, 'Время вылета': 2065}, 'count_flights_by_month': [{'01.2025': 5778}, {'02.2025': 6907}, {'03.2025': 9956}, {'04.2025': 11271}, {'05.2025': 12469}, {'06.2025': 13401}, {'07.2025': 15055}]}
;
      // Имитация задержки
      await new Promise(resolve => setTimeout(resolve, 1000));
      setDashboardData(mockData);
      // --- /ЗАГЛУШКА ---
    } catch (error) {
      console.error("Ошибка при выполнении анализа:", error);
      setDashboardData(null);
    } finally {
      setLoading(false);
    }
  };
  // --- /Обработчик кнопки "Анализ" ---

  return (
    <div className="App">
      <Header />
      <main className="app-main">
        <div className="upload-container">
          <FileUpload />
        </div>
        <div className="map-container">
          <Map onRegionSelect={handleRegionSelect} />
        </div>
        <div className="filters-container">
          <DateFilters
            dateRange={dateRange}
            analyzeFullBase={analyzeFullBase}
            onFiltersChange={handleFiltersChange}
          />
          <button onClick={handleAnalysisClick} className="analyze-button" disabled={loading}>
            {loading ? 'Загрузка...' : 'Анализ'}
          </button>
        </div>
        {/* --- Индикатор выбранного региона --- */}
        {selectedRegion && (
          <div className="selected-region-info">
            <p><strong>Анализ для региона:</strong> {selectedRegion.title} ({selectedRegion.code})</p>
            <button onClick={() => { setSelectedRegion(null); handleAnalysisClick(); }} className="clear-region-button">
              Сбросить регион
            </button>
          </div>
        )}
        {/* --- /Индикатор выбранного региона --- */}
        <div className="dashboard-container">
          <Dashboard
            lineChartStep={lineChartStep}
            onLineChartStepChange={handleLineChartStepChange}
            apiData={dashboardData}
            loading={loading}
            selectedRegion={selectedRegion} // Передаём информацию о выбранном регионе в Dashboard
          />
        </div>
      </main>
    </div>
  );
}

export default App;