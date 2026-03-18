import { useState, useCallback } from 'react';
import MapView from './components/MapView';
import StatsBar from './components/StatsBar';
import PollutantInfo from './components/PollutantInfo';
import './App.css';

function App() {
  const [activePollutant, setActivePollutant] = useState('european_aqi');
  const [apiData, setApiData] = useState([]);

  const handleDataLoad = useCallback((data) => setApiData(data), []);

  return (
    <div className="page">
      <header className="page-header">
        <h1>London air quality</h1>
        <p>Real-time pollutant readings across all 33 boroughs</p>
      </header>
      <MapView
        activePollutant={activePollutant}
        onPollutantChange={setActivePollutant}
        onDataLoad={handleDataLoad}
      />
      <StatsBar data={apiData} pollutantKey={activePollutant} />
      <PollutantInfo pollutantKey={activePollutant} />
    </div>
  );
}

export default App;