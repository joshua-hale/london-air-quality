import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { POLLUTANTS } from '../utils/pollutantConfig';

const BAND_LABELS = [
  { label: 'Good',      },
  { label: 'Fair',      },
  { label: 'Moderate',  },
  { label: 'Poor',      },
  { label: 'Very poor', },
];

const BAND_RANGES = {
  european_aqi: ['0–20', '20–40', '40–60', '60–80', '80–100'],
  pm2_5:        ['0–10', '10–20', '20–25', '25–50', '>50'],
  pm10:         ['0–20', '20–40', '40–50', '50–100', '>100'],
  no2:          ['0–40', '40–90', '90–120', '120–230', '>230'],
  o3:           ['0–50', '50–100', '100–130', '130–240', '>240'],
  so2:          ['0–100', '100–200', '200–350', '350–500', '>500'],
};

export default function MapLegend({ pollutantKey }) {
  const map = useMap();
  const pol = POLLUTANTS.find(p => p.key === pollutantKey);
  const ranges = BAND_RANGES[pollutantKey];

  useEffect(() => {
    const legend = L.control({ position: 'bottomright' });

    legend.onAdd = () => {
      const div = L.DomUtil.create('div');
      div.style.cssText = `
        background: #0a0a0a;
        padding: 12px 16px;
        border-radius: 8px;
        font-family: Inter, sans-serif;
        min-width: 160px;
        border: 1px solid #1a1a1a;
      `;
      div.innerHTML = `
        <div style="font-size:10px;font-weight:500;color:#555;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:10px">
          ${pol.label}
        </div>
        ${pol.colors.map((c, i) => `
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <span style="width:12px;height:12px;border-radius:3px;background:${c};display:inline-block;flex-shrink:0"></span>
            <span style="color:#aaa;font-size:11px;font-weight:300">${BAND_LABELS[i].label}</span>
            <span style="color:#555;font-size:11px;font-weight:300;margin-left:auto">${ranges[i]}${pol.unit}</span>
          </div>
        `).join('')}
      `;
      return div;
    };

    legend.addTo(map);
    return () => legend.remove();
  }, [map, pollutantKey]);

  return null;
}