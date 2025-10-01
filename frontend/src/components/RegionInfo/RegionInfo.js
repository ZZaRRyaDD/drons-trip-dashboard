// src/components/RegionInfo/RegionInfo.js
import React from 'react';

const RegionInfo = ({ region }) => {
  if (!region) {
    return <div className="region-info-placeholder">Выберите регион на карте</div>;
  }

  return (
    <div className="region-info">
      <h3>{region.title} ({region.code})</h3>
      <p>Информация о выбранном регионе.</p>
      {/* Здесь будет отображаться специфичная информация о регионе, полученная с бэкенда */}
    </div>
  );
};

export default RegionInfo;