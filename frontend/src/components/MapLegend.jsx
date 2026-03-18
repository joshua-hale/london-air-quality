import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { POLLUTANTS } from '../utils/pollutantConfig';

export default function MapLegend({ pollutantKey }) {
  const map = useMap();
  const pol = POLLUTANTS.find(p => p.key === pollutantKey);

  useEffect(() => {
    const legend = L.control({ position: 'bottomright' });

    legend.onAdd = () => {
        const div = L.DomUtil.create('div');
        div.style.cssText = `
          background: #0a0a0a;
          padding: 12px 16px;
          border-radius: 8px;
          font-size: 12px;
          font-family: Inter, sans-serif;
          line-height: 1.6;
          min-width: 130px;
          border: 1px solid #1a1a1a;
        `;
        div.innerHTML = `
          <div style="font-size:10px;font-weight:500;color:#555;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px">${pol.label}</div>
          ${pol.colors.map((c, i) => `
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
              <span style="width:12px;height:12px;border-radius:3px;background:${c};display:inline-block;flex-shrink:0"></span>
              <span style="color:#888;font-size:11px;font-weight:300">${i === 0 ? 'Low' : i === pol.colors.length - 1 ? 'High' : ''}</span>
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