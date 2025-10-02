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
    const start = new Date(now.getFullYear(), 1, 1);
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
    params.append('linear_step', lineChartStep);
    if (selectedRegion) { // Отправляем region, если он выбран
      params.append('region', selectedRegion.title);
    }
    params.append('flag_full_dataset', analyzeFullBase.toString());

    let serverUrl = "localhost:8000"
    if (process.env.NODE_ENV === "production") {
      serverUrl = "193.168.46.16"
    }

    const apiUrl = `http://${serverUrl}/api/v1/flights/?${params.toString()}`;

    try {
      console.log("Выполнение GET-запроса к:", apiUrl);
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          // 'Authorization': `Bearer ${token}`, // Если нужна аутентификация
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`Ошибка: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      console.log("Получены данные анализа:", data);
      setDashboardData(data);

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