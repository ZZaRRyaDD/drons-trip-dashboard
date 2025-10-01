// src/components/Dashboard/Dashboard.js
import React, { useState, useEffect } from 'react';
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
  Cell,
  LineChart,
  Line
} from 'recharts';

// Принимаем apiData, loading, lineChartStep, onLineChartStepChange, selectedRegion
const Dashboard = ({ apiData, loading, lineChartStep, onLineChartStepChange, selectedRegion }) => {
  // Состояние для форматированных данных, которые будут использоваться графиками
  const [formattedData, setFormattedData] = useState({
    total_count_flights: 0,
    total_duration: 0,
    mean_duration: 0,
    count_flights_per_weekday: [],
    distribution_by_flight_duration: [],
    distribution_by_type: [],
    distribution_null_features: [],
    count_flights_by_month: []
  });

  // Вспомогательная функция для генерации случайного цвета
  const getRandomColor = () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  };

  // Обновляем formattedData при изменении apiData
  useEffect(() => {
    if (apiData) {
      // Форматируем данные из API для использования в recharts
      const formattedWeekdayData = apiData.count_flights_per_weekday.map(item => {
        const [day, count] = Object.entries(item)[0];
        return { name: day, count };
      });

      const formattedDurationData = apiData.distribution_by_flight_duration.map(item => {
        const [range, count] = Object.entries(item)[0];
        return { name: range, count };
      });

      const formattedTypeData = Object.entries(apiData.distribution_by_type).map(([name, value]) => ({
        name,
        value
      }));

      const formattedNullFeaturesData = Object.entries(apiData.distribution_null_features).map(([name, count]) => ({
        name,
        count
      }));

      const formattedLineData = apiData.count_flights_by_month.map(item => {
        const [period, count] = Object.entries(item)[0];
        return { name: period, count };
      });

      setFormattedData({
        total_count_flights: apiData.total_count_flights,
        total_duration: apiData.total_duration,
        mean_duration: apiData.mean_duration,
        count_flights_per_weekday: formattedWeekdayData,
        distribution_by_flight_duration: formattedDurationData,
        distribution_by_type: formattedTypeData,
        distribution_null_features: formattedNullFeaturesData,
        count_flights_by_month: formattedLineData
      });
    } else {
      // Если apiData нет, сбрасываем форматированные данные
      setFormattedData({
        total_count_flights: 0,
        total_duration: 0,
        mean_duration: 0,
        count_flights_per_weekday: [],
        distribution_by_flight_duration: [],
        distribution_by_type: [],
        distribution_null_features: [],
        count_flights_by_month: []
      });
    }
  }, [apiData]);

  const handleLineChartStepChangeFromSelect = (e) => {
    const newStep = e.target.value;
    if (onLineChartStepChange) {
      onLineChartStepChange(newStep);
    }
  };

  // Если идёт загрузка, показываем сообщение
  if (loading) {
    return <div className="dashboard">Загрузка данных анализа...</div>;
  }

  // Если данные получены, но пусты (например, по какому-то фильтру)
  if (!loading && apiData && (
    formattedData.count_flights_per_weekday.length === 0 &&
    formattedData.distribution_by_flight_duration.length === 0 &&
    formattedData.distribution_by_type.length === 0 &&
    formattedData.distribution_null_features.length === 0 &&
    formattedData.count_flights_by_month.length === 0
  )) {
    return <div className="dashboard">Нет данных для отображения по указанным фильтрам.</div>;
  }

  // Если данные не получены (ещё не нажата кнопка или ошибка), показываем пустой дашборд или сообщение
  if (!loading && !apiData) {
    return <div className="dashboard">Нажмите кнопку "Анализ" для загрузки данных.</div>;
  }

  return (
    <div className="dashboard">
      {/* --- Заголовок дашборда с указанием региона --- */}
      <h3>
        {selectedRegion
          ? `Дашборд аналитики для региона: ${selectedRegion.title}`
          : 'Дашборд аналитики (Общий)'}
      </h3>
      {/* --- /Заголовок дашборда с указанием региона --- */}

      <div className="dashboard-stats">
        <div className="stat-card">
          <h4>Всего полётов</h4>
          <p>{formattedData.total_count_flights}</p>
        </div>
        <div className="stat-card">
          <h4>Общая длительность (мин)</h4>
          <p>{formattedData.total_duration}</p>
        </div>
        <div className="stat-card">
          <h4>Средняя длительность (мин)</h4>
          <p>{formattedData.mean_duration}</p>
        </div>
      </div>

      <div className="dashboard-charts">
        <div className="chart-container">
          <h4>Количество полётов по дням недели</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={formattedData.count_flights_per_weekday}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Количество" fill="#337AB7" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h4>Распределение по длительности полёта</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={formattedData.distribution_by_flight_duration}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Количество" fill="#116f21" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h4>Пропуски в признаках</h4>
          <ResponsiveContainer width="100%" height={400}> {/* Увеличена высота */}
            <BarChart
              layout="vertical"
              data={formattedData.distribution_null_features}
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
              <Bar dataKey="count" name="Количество" fill="#e74c3c" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h4>Количество полётов по {lineChartStep === 'day' ? 'дням' : lineChartStep === 'week' ? 'неделям' : lineChartStep === 'month' ? 'месяцам' : 'годам'}</h4>
          <div className="chart-filters">
            <div className="filter-item">
              <label htmlFor="line-chart-step">Шаг:</label>
              <select
                id="line-chart-step"
                value={lineChartStep}
                onChange={handleLineChartStepChangeFromSelect}
              >
                <option value="day">День</option>
                <option value="week">Неделя</option>
                <option value="month">Месяц</option>
                <option value="year">Год</option>
              </select>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={formattedData.count_flights_by_month}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" name="Количество" stroke="#3498db" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h4>Распределение по типу аппаратов</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={formattedData.distribution_by_type}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {formattedData.distribution_by_type.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getRandomColor()} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;