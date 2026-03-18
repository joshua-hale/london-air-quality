import { useState, useEffect } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import { useAirQuality }   from '../hooks/useAirQuality';
import PollutantToggle     from './PollutantToggle';
import ChoroplethLayer     from './ChoroplethLayer';
import MapLegend           from './MapLegend';

export default function MapView({ activePollutant, onPollutantChange, onDataLoad }) {
  const { data, loading, error } = useAirQuality();

  // Notify App when data arrives
  useEffect(() => {
    if (data.length) onDataLoad(data);
  }, [data]);

  if (loading) return <p>Loading air quality data…</p>;
  if (error)   return <p>Error: {error}</p>;

  return (
    <div>
      <PollutantToggle active={activePollutant} onChange={onPollutantChange} />
      <MapContainer
        center={[51.505, -0.09]}
        zoom={10}
        style={{ height: '600px', width: '100%' }}
      >
        <TileLayer
          attribution="© OpenStreetMap contributors"
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        <ChoroplethLayer apiData={data} pollutantKey={activePollutant} />
        <MapLegend pollutantKey={activePollutant} />
      </MapContainer>
    </div>
  );
}