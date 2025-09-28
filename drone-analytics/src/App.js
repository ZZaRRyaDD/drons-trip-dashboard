// src/App.js
import React, { useState } from 'react';
import Header from './components/Header/Header';
import Map from './components/Map/Map';
import RegionDetails from './components/RegionDetails/RegionDetails';
import FlightDashboard from './components/FlightDashboard/FlightDashboard';
import './App.css';

function App() {
  const [selectedRegion, setSelectedRegion] = useState(null); // Теперь хранит объект {code, title}

  const handleRegionSelect = (region) => {
    setSelectedRegion(region);
  };

  return (
    <div className="App">
      <Header />
      <main className="app-main">
        <div className="map-container">
          <Map selectedRegionCode={selectedRegion?.code} onRegionSelect={handleRegionSelect} />
        </div>
        <div className="details-container">
          <RegionDetails region={selectedRegion} />
        </div>
        <div className="dashboard-container">
          <FlightDashboard selectedRegionCode={selectedRegion?.code} />
        </div>
      </main>
    </div>
  );
}

export default App;