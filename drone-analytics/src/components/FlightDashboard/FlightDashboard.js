// src/components/FlightDashboard/FlightDashboard.js
import React, { useEffect, useState } from 'react';
import { fetchFlightData } from '../../services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const FlightDashboard = ({ selectedRegionCode = null }) => { // Принимаем код региона как пропс
  // Состояния для сырых данных (все регионы)
  const [rawTakeoffData, setRawTakeoffData] = useState([]);
  const [rawLandingData, setRawLandingData] = useState([]);
  const [dashboardData, setDashboardData] = useState({
    totalFlights: 0,
    totalDuration: 0,
    averageDuration: 0,
    flightsByDay: [],
    flightsByDuration: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- Состояния фильтров для каждого графика ---
  const [takeoffFilters, setTakeoffFilters] = useState({
    topCount: 20,
    showWorst: false
  });
  const [landingFilters, setLandingFilters] = useState({
    topCount: 20,
    showWorst: false
  });

  useEffect(() => {
    const getFlightData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchFlightData();
        processAndSetDashboardData(data);
      } catch (err) {
        setError(err.message);
        console.error("Ошибка при загрузке данных дашборда:", err);
        setDashboardData({
          totalFlights: 0,
          totalDuration: 0,
          averageDuration: 0,
          flightsByDay: [],
          flightsByDuration: [],
        });
        setRawTakeoffData([]);
        setRawLandingData([]);
      } finally {
        setLoading(false);
      }
    };

    getFlightData();
  }, []); // Зависимость пустая, данные загружаются один раз

  // --- Функция обработки данных ---
  const processAndSetDashboardData = (data) => {
    if (!data || data.length === 0) {
      setDashboardData({
        totalFlights: 0,
        totalDuration: 0,
        averageDuration: 0,
        flightsByDay: [],
        flightsByDuration: [],
      });
      setRawTakeoffData([]);
      setRawLandingData([]);
      return;
    }

    const totalFlights = data.length;
    const totalDurationMinutes = data.reduce((sum, flight) => sum + (flight.duration || 0), 0);
    const averageDuration = totalFlights > 0 ? totalDurationMinutes / totalFlights : 0;

    const dayNames = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
    const flightsByDayCount = Array(7).fill(0);
    data.forEach(flight => {
      const dayIndex = dayNames.indexOf(flight.takeoff_day_of_week);
      if (dayIndex !== -1) {
        flightsByDayCount[dayIndex]++;
      }
    });
    const flightsByDay = dayNames.map((name, index) => ({
      name,
      count: flightsByDayCount[index]
    }));

    const durationBuckets = [
      { name: '< 10 мин', count: 0 },
      { name: '10-30 мин', count: 0 },
      { name: '30-60 мин', count: 0 },
      { name: '1-2 ч', count: 0 },
      { name: '2-3 ч', count: 0 },
      { name: '3-4 ч', count: 0 },
      { name: '4-5 ч', count: 0 },
      { name: '5-6 ч', count: 0 },
      { name: '6+ ч', count: 0 },
    ];
    data.forEach(flight => {
      const duration = flight.duration || 0;
      if (duration < 10) {
        durationBuckets[0].count++;
      } else if (duration < 30) {
        durationBuckets[1].count++;
      } else if (duration < 60) {
        durationBuckets[2].count++;
      } else if (duration < 120) {
        durationBuckets[3].count++;
      } else if (duration < 180) {
        durationBuckets[4].count++;
      } else if (duration < 240) {
        durationBuckets[5].count++;
      } else if (duration < 300) {
        durationBuckets[6].count++; // Если решили не добавлять 4-5ч, пропустите этот блок
      } else if (duration < 360) {
        durationBuckets[7].count++;
      } else {
        durationBuckets[8].count++;
      }
    });

    // Подсчёт количества полётов по регионам
    const flightsByTakeoffRegionMap = new Map();
    const flightsByLandingRegionMap = new Map();
    data.forEach(flight => {
      const takeoffRegion = flight.takeoff_region;
      const landingRegion = flight.landing_region;
      flightsByTakeoffRegionMap.set(takeoffRegion, (flightsByTakeoffRegionMap.get(takeoffRegion) || 0) + 1);
      flightsByLandingRegionMap.set(landingRegion, (flightsByLandingRegionMap.get(landingRegion) || 0) + 1);
    });

    // Преобразуем Map в массивы
    const takeoffArray = Array.from(flightsByTakeoffRegionMap.entries())
      .map(([region, count]) => ({ name: region, count: count }));
    const landingArray = Array.from(flightsByLandingRegionMap.entries())
      .map(([region, count]) => ({ name: region, count: count }));

    setDashboardData({
      totalFlights,
      totalDuration: totalDurationMinutes,
      averageDuration: parseFloat(averageDuration.toFixed(2)),
      flightsByDay,
      flightsByDuration: durationBuckets,
    });
    setRawTakeoffData(takeoffArray);
    setRawLandingData(landingArray);
  };

  // --- Обработчики изменений фильтров ---
  const handleTakeoffFilterChange = (key, value) => {
    setTakeoffFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleLandingFilterChange = (key, value) => {
    setLandingFilters(prev => ({ ...prev, [key]: value }));
  };

  // --- Функция для фильтрации и сортировки данных ---
  const getFilteredData = (rawData, filters, regionCode) => { // Добавлен regionCode
    let filteredData = rawData;
    // Если выбран регион, фильтруем по нему
    if (regionCode) {
      filteredData = rawData.filter(item => item.name === regionCode);
    }

    if (!filteredData || filteredData.length === 0) return [];
    let sortedData = [...filteredData]; // Копируем массив, чтобы не мутировать исходный
    const sortDirection = filters.showWorst ? 1 : -1;
    sortedData.sort((a, b) => (b.count - a.count) * sortDirection);
    return sortedData.slice(0, filters.topCount);
  };

  if (loading) {
    return <div className="flight-dashboard">Загрузка данных о полётах...</div>;
  }

  if (error) {
    return <div className="flight-dashboard">Ошибка загрузки данных: {error}</div>;
  }

  // --- Вычисляем данные для отображения ---
  // Передаём selectedRegionCode в getFilteredData
  const displayedTakeoffData = getFilteredData(rawTakeoffData, takeoffFilters, selectedRegionCode);
  const displayedLandingData = getFilteredData(rawLandingData, landingFilters, selectedRegionCode);

  // --- Заголовки графиков ---
  const takeoffChartTitle = selectedRegionCode
    ? `Полёты из ${selectedRegionCode}`
    : `${takeoffFilters.showWorst ? `Антитоп-${takeoffFilters.topCount}` : `Топ-${takeoffFilters.topCount}`} регионов взлёта`;

  const landingChartTitle = selectedRegionCode
    ? `Полёты в ${selectedRegionCode}`
    : `${landingFilters.showWorst ? `Антитоп-${landingFilters.topCount}` : `Топ-${landingFilters.topCount}`} регионов посадки`;

  return (
    <div className="flight-dashboard">
      <h2>Статистика полётов дронов {selectedRegionCode && `для региона ${selectedRegionCode}`}</h2>

      <div className="dashboard-stats">
        <div className="stat-card">
          <h3>Всего полётов</h3>
          <p>{dashboardData.totalFlights}</p>
        </div>
        <div className="stat-card">
          <h3>Общая длительность (мин)</h3>
          <p>{dashboardData.totalDuration.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Средняя длительность (мин)</h3>
          <p>{dashboardData.averageDuration}</p>
        </div>
      </div>

      <div className="dashboard-charts">
        <div className="chart-container">
          <h3>Количество полётов по дням недели</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboardData.flightsByDay}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Количество полётов" fill="#337AB7" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Распределение по длительности полёта</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboardData.flightsByDuration}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80}/>
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Количество полётов" fill="#116f21" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>{takeoffChartTitle}</h3>
          {/* --- Фильтры для графика взлёта --- */}
          <div className="chart-filters">
            <div className="filter-item">
              <label>Показать топ:</label>
              <select value={takeoffFilters.topCount} onChange={(e) => handleTakeoffFilterChange('topCount', Number(e.target.value))} disabled={!!selectedRegionCode}>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={30}>30</option>
              </select>
            </div>
            <div className="filter-item">
              <label>Худшие:</label>
              <input
                type="checkbox"
                checked={takeoffFilters.showWorst}
                onChange={(e) => handleTakeoffFilterChange('showWorst', e.target.checked)}
                disabled={!!selectedRegionCode} // Отключаем, если выбран регион
              />
            </div>
          </div>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              layout="vertical"
              data={displayedTakeoffData}
              margin={{ top: 20, right: 30, left: 150, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis
                type="category"
                dataKey="name"
                width={120}
                tick={{ fontSize: 12 }}
              />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Количество полётов" fill="#d17520" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>{landingChartTitle}</h3>
          {/* --- Фильтры для графика посадки --- */}
          <div className="chart-filters">
            <div className="filter-item">
              <label>Показать топ:</label>
              <select value={landingFilters.topCount} onChange={(e) => handleLandingFilterChange('topCount', Number(e.target.value))} disabled={!!selectedRegionCode}>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={30}>30</option>
              </select>
            </div>
            <div className="filter-item">
              <label>Худшие:</label>
              <input
                type="checkbox"
                checked={landingFilters.showWorst}
                onChange={(e) => handleLandingFilterChange('showWorst', e.target.checked)}
                disabled={!!selectedRegionCode} // Отключаем, если выбран регион
              />
            </div>
          </div>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              layout="vertical"
              data={displayedLandingData}
              margin={{ top: 20, right: 30, left: 150, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis
                type="category"
                dataKey="name"
                width={120}
                tick={{ fontSize: 12 }}
              />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Количество полётов" fill="#901aad" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default FlightDashboard;