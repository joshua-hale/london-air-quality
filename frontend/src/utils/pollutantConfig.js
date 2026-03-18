export const POLLUTANTS = [
    { key: 'european_aqi', label: 'European AQI', unit: '',        colors: ['#1a9850','#91cf60','#fee08b','#fc8d59','#d73027'] },
    { key: 'pm2_5',        label: 'PM2.5',        unit: ' μg/m³', colors: ['#1a9850','#91cf60','#fee08b','#fc8d59','#d73027'] },
    { key: 'pm10',         label: 'PM10',         unit: ' μg/m³', colors: ['#1a9850','#91cf60','#fee08b','#fc8d59','#d73027'] },
    { key: 'no2',          label: 'NO₂',          unit: ' μg/m³', colors: ['#1a9850','#91cf60','#fee08b','#fc8d59','#d73027'] },
    { key: 'o3',           label: 'O₃',           unit: ' μg/m³', colors: ['#1a9850','#91cf60','#fee08b','#fc8d59','#d73027'] },
    { key: 'so2',          label: 'SO₂',          unit: ' μg/m³', colors: ['#1a9850','#91cf60','#fee08b','#fc8d59','#d73027'] },
  ];
  
  export const POLLUTANT_BOUNDS = {
    european_aqi: { min: 0, max: 100 },
    pm2_5:        { min: 0, max: 50  },
    pm10:         { min: 0, max: 100 },
    no2:          { min: 0, max: 230 },
    o3:           { min: 0, max: 240 },
    so2:          { min: 0, max: 500 },
  };
  
  function hexToRgb(hex) {
    return [
      parseInt(hex.slice(1, 3), 16),
      parseInt(hex.slice(3, 5), 16),
      parseInt(hex.slice(5, 7), 16),
    ];
  }
  
  export function getColor(value, minV, maxV, colors) {
    const t = Math.max(0, Math.min(1, (value - minV) / (maxV - minV)));
    const n = colors.length - 1;
    const i = Math.min(Math.floor(t * n), n - 1);
    const f = t * n - i;
    const [r1, g1, b1] = hexToRgb(colors[i]);
    const [r2, g2, b2] = hexToRgb(colors[i + 1]);
    return `rgb(${Math.round(r1 + (r2-r1)*f)},${Math.round(g1 + (g2-g1)*f)},${Math.round(b1 + (b2-b1)*f)})`;
  }
  
  export function getBoroughValue(feature, apiData, pollutantKey) {
    const match = apiData.find(
      d => d.borough.toLowerCase() === feature.properties.name.toLowerCase()
    );
    return match?.[pollutantKey] ?? null;
  }