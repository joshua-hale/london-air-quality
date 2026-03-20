import { useEffect } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import { useAirQuality }  from '../hooks/useAirQuality';
import PollutantToggle    from './PollutantToggle';
import ChoroplethLayer    from './ChoroplethLayer';
import MapLegend          from './MapLegend';

export default function MapView({ activePollutant, onPollutantChange, onDataLoad, activeData, activeHorizon, onHorizonChange }) {
  const { data, loading, error } = useAirQuality();

  useEffect(() => {
    if (data.now.length) onDataLoad(data);
  }, [data]);

  if (loading) return <p className="loading">Loading air quality data…</p>;
  if (error)   return <p className="loading">Error: {error}</p>;

  return (
    <div>
      {/* Title */}
      <div className="map-title-block">
        <h2 className="map-title">London air pollution map</h2>
        <p className="map-sub">Live pollution data, 4h and 8h forecasts</p>
      </div>

      {/* Controls row */}
      <div className="map-controls-row">
        <PollutantToggle active={activePollutant} onChange={onPollutantChange} />
        <div className="horizon-row" style={{ marginBottom: 0 }}>
          {[{ key: 'now', label: 'Now' }, { key: 'forecast4h', label: '+4h' }, { key: 'forecast8h', label: '+8h' }].map(h => (
            <button
              key={h.key}
              className={`horizon-btn ${activeHorizon === h.key ? 'active' : ''}`}
              onClick={() => onHorizonChange(h.key)}
            >
              {h.label}
            </button>
          ))}
        </div>
      </div>

      <MapContainer
        center={[51.505, -0.09]}
        zoom={10}
        style={{ height: '600px', width: '100%' }}
      >
        <TileLayer
          attribution='© <a href="https://carto.com">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        {activeData.length > 0 && (
          <ChoroplethLayer apiData={activeData} pollutantKey={activePollutant} />
        )}
        <MapLegend pollutantKey={activePollutant} />
      </MapContainer>
    </div>
  );
}