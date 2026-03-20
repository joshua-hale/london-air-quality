import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { POLLUTANTS, POLLUTANT_BOUNDS, getColor, getBoroughValue } from '../utils/pollutantConfig';

const GEOJSON_URL =
  'https://raw.githubusercontent.com/radoi90/housequest-data/master/london_boroughs.geojson';

function styleFeature(feature, apiData, pollutantKey) {
  const value        = getBoroughValue(feature, apiData, pollutantKey);
  const { min, max } = POLLUTANT_BOUNDS[pollutantKey];
  const colors       = POLLUTANTS.find(p => p.key === pollutantKey).colors;
  const color        = value !== null ? getColor(value, min, max, colors) : '#ccc';
  return { fillColor: color, weight: 1, color: 'white', fillOpacity: 0.75 };
}

function formatTime(iso) {
  if (!iso) return null;
  return new Date(iso).toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  });
}

export default function ChoroplethLayer({ apiData, pollutantKey }) {
  const map          = useMap();
  const layerRef     = useRef(null);
  const apiDataRef   = useRef(apiData);
  const pollutantRef = useRef(pollutantKey);

  useEffect(() => { apiDataRef.current   = apiData;      }, [apiData]);
  useEffect(() => { pollutantRef.current = pollutantKey; }, [pollutantKey]);

  useEffect(() => {
    if (!apiData.length) return;

    fetch(GEOJSON_URL)
      .then(r => r.json())
      .then(geojson => {
        layerRef.current?.remove();

        layerRef.current = L.geoJSON(geojson, {
          style: feature => styleFeature(feature, apiDataRef.current, pollutantRef.current),
          onEachFeature(feature, layer) {
            layer.on({
              mouseover(e) {
                e.target.setStyle({ weight: 3, color: '#333', fillOpacity: 0.9 });
                e.target.bringToFront();
              },
              mouseout(e) {
                layerRef.current.resetStyle(e.target);
              },
              click(e) {
                map.fitBounds(e.target.getBounds());
                const d = apiDataRef.current.find(
                  b => b.borough.toLowerCase() === feature.properties.name.toLowerCase()
                );
                if (d) {
                  const observedAt = formatTime(d.timestamp);
                  const validAt    = formatTime(d.valid_at);

                  layer.bindPopup(`
                    <div style="font-family: Inter, sans-serif; min-width: 180px;">
                      <div style="font-weight: 600; font-size: 14px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #eee;">
                        ${d.borough}
                      </div>

                      ${observedAt ? `
                        <div style="font-size: 11px; color: #888; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.4px;">Observed</div>
                        <div style="font-size: 12px; color: #333; margin-bottom: 10px;">${observedAt}</div>
                      ` : ''}

                      ${validAt ? `
                        <div style="font-size: 11px; color: #888; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.4px;">Forecast valid at</div>
                        <div style="font-size: 12px; color: #333; margin-bottom: 10px;">${validAt}</div>
                      ` : ''}

                      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 4px;">
                        <div style="font-size: 12px; color: #555;">AQI</div>
                        <div style="font-size: 12px; font-weight: 500; text-align: right;">${d.european_aqi}</div>
                        <div style="font-size: 12px; color: #555;">PM2.5</div>
                        <div style="font-size: 12px; font-weight: 500; text-align: right;">${d.pm2_5} μg/m³</div>
                        <div style="font-size: 12px; color: #555;">PM10</div>
                        <div style="font-size: 12px; font-weight: 500; text-align: right;">${d.pm10} μg/m³</div>
                        <div style="font-size: 12px; color: #555;">NO₂</div>
                        <div style="font-size: 12px; font-weight: 500; text-align: right;">${d.no2} μg/m³</div>
                        <div style="font-size: 12px; color: #555;">O₃</div>
                        <div style="font-size: 12px; font-weight: 500; text-align: right;">${d.o3} μg/m³</div>
                        <div style="font-size: 12px; color: #555;">SO₂</div>
                        <div style="font-size: 12px; font-weight: 500; text-align: right;">${d.so2} μg/m³</div>
                      </div>
                    </div>
                  `).openPopup();
                }
              },
            });
          },
        }).addTo(map);
      });

    return () => { layerRef.current?.remove(); };
  }, [apiData]);

  useEffect(() => {
    if (!layerRef.current) return;
    layerRef.current.setStyle(
      feature => styleFeature(feature, apiDataRef.current, pollutantKey)
    );
  }, [pollutantKey]);

  return null;
}