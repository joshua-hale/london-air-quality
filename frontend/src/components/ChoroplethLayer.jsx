import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { POLLUTANTS, POLLUTANT_BOUNDS, getColor, getBoroughValue } from '../utils/pollutantConfig';

const GEOJSON_URL =
  'https://raw.githubusercontent.com/radoi90/housequest-data/master/london_boroughs.geojson';

function styleFeature(feature, apiData, pollutantKey) {
  const value          = getBoroughValue(feature, apiData, pollutantKey);
  const { min, max }   = POLLUTANT_BOUNDS[pollutantKey];
  const colors         = POLLUTANTS.find(p => p.key === pollutantKey).colors;
  const color          = value !== null ? getColor(value, min, max, colors) : '#ccc';
  return { fillColor: color, weight: 1, color: 'white', fillOpacity: 0.75 };
}

export default function ChoroplethLayer({ apiData, pollutantKey }) {
  const map          = useMap();
  const layerRef     = useRef(null);
  const apiDataRef   = useRef(apiData);
  const pollutantRef = useRef(pollutantKey);

  useEffect(() => { apiDataRef.current   = apiData;      }, [apiData]);
  useEffect(() => { pollutantRef.current = pollutantKey; }, [pollutantKey]);

  // Build layer once — when API data first arrives
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
                  layer.bindPopup(`
                    <strong>${d.borough}</strong><br/>
                    AQI: ${d.european_aqi}<br/>
                    PM2.5: ${d.pm2_5} μg/m³<br/>
                    PM10: ${d.pm10} μg/m³<br/>
                    NO₂: ${d.no2} μg/m³<br/>
                    O₃: ${d.o3} μg/m³<br/>
                    SO₂: ${d.so2} μg/m³
                  `).openPopup();
                }
              },
            });
          },
        }).addTo(map);
      });

    return () => { layerRef.current?.remove(); };
  }, [apiData.length]);

  // Re-style on pollutant toggle
  useEffect(() => {
    if (!layerRef.current) return;
    layerRef.current.setStyle(
      feature => styleFeature(feature, apiDataRef.current, pollutantKey)
    );
  }, [pollutantKey]);

  return null;
}