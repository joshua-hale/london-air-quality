import { useState, useCallback } from 'react';
import MapView from './components/MapView';
import StatsBar from './components/StatsBar';
import PollutantInfo from './components/PollutantInfo';
import ChartsView from './pages/ChartsView';
import './App.css';

function App() {
  const [activePollutant, setActivePollutant] = useState('european_aqi');
  const [activeHorizon,   setActiveHorizon]   = useState('now');
  const [allData,         setAllData]         = useState({ now: [], forecast4h: [], forecast8h: [] });
  const [activePage,      setActivePage]      = useState('map');

  const handleDataLoad = useCallback((data) => setAllData(data), []);
  const activeData = allData[activeHorizon] ?? [];
  const hasData = allData.now.length > 0;

  return (
    <div className="layout">

      <header className="site-header">
        <div className="header-inner">
          <div className="header-brand">
            <span className="header-dot" />
            London air quality
          </div>
          <nav className="header-nav">
            <button
              className={`nav-btn ${activePage === 'map' ? 'active' : ''}`}
              onClick={() => setActivePage('map')}
            >
              Map
            </button>
            <button
              className={`nav-btn ${activePage === 'charts' ? 'active' : ''}`}
              onClick={() => setActivePage('charts')}
            >
              Charts
            </button>
          </nav>
        </div>
      </header>

      <main className="page">

        {activePage === 'map' && (
          <>
            <MapView
              activePollutant={activePollutant}
              onPollutantChange={setActivePollutant}
              onDataLoad={handleDataLoad}
              activeData={activeData}
              activeHorizon={activeHorizon}
              onHorizonChange={setActiveHorizon}
            />
            <StatsBar data={activeData} pollutantKey={activePollutant} />
            <div className="section-divider" />
            <PollutantInfo pollutantKey={activePollutant} />
          </>
        )}

        {activePage === 'charts' && (
          hasData
            ? <ChartsView allData={allData} />
            : <p className="loading">Loading data…</p>
        )}

      </main>

      <footer className="site-footer">
        <div className="footer-inner">
          <div className="footer-left">
            <span className="header-dot" />
            London air quality
          </div>
          <div className="footer-links">
            <span>Data: Open-Meteo API</span>
            <span>Boundaries: GLA Open Data</span>
            <a href="https://github.com/joshua-hale/london-air-quality" target="_blank" rel="noreferrer" style={{ color: '#555', textDecoration: 'none' }}>GitHub</a>
            <span>© {new Date().getFullYear()}</span>
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;