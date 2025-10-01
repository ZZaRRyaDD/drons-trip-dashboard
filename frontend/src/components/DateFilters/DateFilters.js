// src/components/DateFilters/DateFilters.js
import React from 'react';

const DateFilters = ({ dateRange, analyzeFullBase, onFiltersChange }) => {
  const handleStartDateChange = (e) => {
    onFiltersChange({ ...dateRange, startDate: e.target.value }, analyzeFullBase);
  };

  const handleEndDateChange = (e) => {
    onFiltersChange({ ...dateRange, endDate: e.target.value }, analyzeFullBase);
  };

  const handleFullBaseToggle = (e) => {
    onFiltersChange(dateRange, e.target.checked);
  };

  return (
    <div className="date-filters">
      <div className="filter-item date-item"> {/* Добавим класс для стилизации */}
        <label htmlFor="start-date">Дата начала:</label>
        <input
          type="date"
          id="start-date"
          value={dateRange.startDate}
          onChange={handleStartDateChange}
          disabled={analyzeFullBase}
        />
      </div>
      <div className="filter-item date-item"> {/* Добавим класс для стилизации */}
        <label htmlFor="end-date">Дата окончания:</label>
        <input
          type="date"
          id="end-date"
          value={dateRange.endDate}
          onChange={handleEndDateChange}
          disabled={analyzeFullBase}
        />
      </div>
      <div className="filter-item checkbox-item">
        <label htmlFor="full-base-checkbox">
          <input
            type="checkbox"
            id="full-base-checkbox"
            checked={analyzeFullBase}
            onChange={handleFullBaseToggle}
          />
          Анализ всей базы данных
        </label>
      </div>
    </div>
  );
};

export default DateFilters;