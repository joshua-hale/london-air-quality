import { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts';
import { POLLUTANTS, POLLUTANT_BOUNDS, getColor } from '../utils/pollutantConfig';

const HORIZON_LABELS = {
  now:        'Now',
  forecast4h: '+4h',
  forecast8h: '+8h',
};

export default function ChartsView({ allData }) {
  const [activePollutant, setActivePollutant] = useState('european_aqi');
  const [selectedBorough, setSelectedBorough] = useState('City of London');
  const [heatmapHorizon, setHeatmapHorizon] = useState('now');

  const pol = POLLUTANTS.find(p => p.key === activePollutant);
  const boroughs = allData.now.map(d => d.borough);

  const barData = boroughs.map(borough => {
    const row = { borough: borough.replace(' upon Thames', '').replace(' and ', ' & ') };
    ['now', 'forecast4h', 'forecast8h'].forEach(h => {
      const match = allData[h]?.find(d => d.borough === borough);
      row[h] = match?.[activePollutant] ?? null;
    });
    return row;
  });

  const lineData = ['now', 'forecast4h', 'forecast8h'].map(h => {
    const match = allData[h]?.find(d => d.borough === selectedBorough);
    return {
      horizon: HORIZON_LABELS[h],
      value: match?.[activePollutant] ?? null,
    };
  });

  const uniqueBoroughs = allData.now.map(d => d.borough).sort();
  const heatmapData = allData[heatmapHorizon] ?? [];

  return (
    <div className="charts-page">

        <div className="charts-header">
        <h2 className="charts-title">Forecast comparison</h2>
        <p className="charts-sub">Live readings vs 4h and 8h predictions across London boroughs</p>
        </div>

      <div className="toggle-row" style={{ marginBottom: '36px' }}>
        {POLLUTANTS.map(p => (
          <button
            key={p.key}
            className={`tog ${activePollutant === p.key ? 'active' : ''}`}
            onClick={() => setActivePollutant(p.key)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Bar chart */}
      <div className="chart-card">
        <div className="chart-card-header">
          <div className="chart-card-title">All boroughs — {pol.label}</div>
          <div className="chart-card-sub">Grouped by time horizon</div>
        </div>
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={barData} margin={{ top: 8, right: 16, left: 0, bottom: 90 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
            <XAxis
              dataKey="borough"
              tick={{ fill: '#555', fontSize: 10 }}
              angle={-45}
              textAnchor="end"
              interval={0}
            />
            <YAxis tick={{ fill: '#555', fontSize: 11 }} unit={pol.unit} width={55} />
            <Tooltip
              contentStyle={{ background: '#0a0a0a', border: '1px solid #1f1f1f', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#fff', fontWeight: 500, marginBottom: '4px' }}
              itemStyle={{ color: '#aaa' }}
            />
            <Bar dataKey="now"        name="Now" fill="#4ade80" radius={[3,3,0,0]} />
            <Bar dataKey="forecast4h" name="+4h" fill="#facc15" radius={[3,3,0,0]} />
            <Bar dataKey="forecast8h" name="+8h" fill="#f97316" radius={[3,3,0,0]} />
          </BarChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginTop: '12px' }}>
          {[{ color: '#4ade80', label: 'Now' }, { color: '#facc15', label: '+4h' }, { color: '#f97316', label: '+8h' }].map(item => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: item.color, display: 'inline-block' }} />
              <span style={{ fontSize: '12px', color: '#555' }}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Line chart */}
      <div className="chart-card" style={{ marginTop: '20px' }}>
        <div className="chart-card-header">
          <div className="chart-card-title">{pol.label} forecast trajectory</div>
          <div className="chart-card-sub">Live → +4h → +8h for a selected borough</div>
        </div>
        <div style={{ marginBottom: '24px' }}>
          <select
            className="borough-select"
            value={selectedBorough}
            onChange={e => setSelectedBorough(e.target.value)}
          >
            {uniqueBoroughs.map(b => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={lineData} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
            <XAxis dataKey="horizon" tick={{ fill: '#555', fontSize: 12 }} />
            <YAxis tick={{ fill: '#555', fontSize: 11 }} unit={pol.unit} width={55} domain={['auto', 'auto']} />
            <Tooltip
              contentStyle={{ background: '#0a0a0a', border: '1px solid #1f1f1f', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#fff', fontWeight: 500 }}
              itemStyle={{ color: '#aaa' }}
            />
            <Line
              type="monotone"
              dataKey="value"
              name={pol.label}
              stroke="#4ade80"
              strokeWidth={2}
              dot={{ fill: '#4ade80', r: 5 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Heatmap */}
      <div className="chart-card" style={{ marginTop: '20px' }}>
        <div className="chart-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="chart-card-title">Pollution heatmap — all boroughs</div>
            <div className="chart-card-sub">All pollutants colour-coded by WHO thresholds</div>
          </div>
          <div className="horizon-row" style={{ marginBottom: 0 }}>
            {Object.entries(HORIZON_LABELS).map(([key, label]) => (
              <button
                key={key}
                className={`horizon-btn ${heatmapHorizon === key ? 'active' : ''}`}
                onClick={() => setHeatmapHorizon(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ overflowX: 'auto', marginTop: '16px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '8px 12px', color: '#444', fontWeight: 500, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', borderBottom: '1px solid #1f1f1f', minWidth: '160px' }}>
                  Borough
                </th>
                {POLLUTANTS.map(p => (
                  <th key={p.key} style={{ padding: '8px 10px', color: '#444', fontWeight: 500, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', borderBottom: '1px solid #1f1f1f', textAlign: 'center', minWidth: '80px' }}>
                    {p.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {heatmapData.map((d) => (
                <tr key={d.borough} style={{ borderBottom: '1px solid #111' }}>
                  <td style={{ padding: '7px 12px', color: '#888', fontSize: '12px', whiteSpace: 'nowrap' }}>
                    {d.borough}
                  </td>
                  {POLLUTANTS.map(p => {
                    const value = d[p.key];
                    const { min, max } = POLLUTANT_BOUNDS[p.key];
                    const bg = getColor(value, min, max, p.colors);
                    return (
                      <td key={p.key} style={{ padding: '7px 10px', textAlign: 'center' }}>
                        <div style={{
                          background: bg,
                          borderRadius: '5px',
                          padding: '4px 6px',
                          color: '#000',
                          fontSize: '11px',
                          fontWeight: 500,
                        }}>
                          {value}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '16px', justifyContent: 'flex-end' }}>
          <span style={{ fontSize: '11px', color: '#444' }}>Low</span>
          <div style={{ width: '120px', height: '8px', borderRadius: '4px', background: 'linear-gradient(to right, #1a9850, #91cf60, #fee08b, #fc8d59, #d73027)' }} />
          <span style={{ fontSize: '11px', color: '#444' }}>High</span>
        </div>
      </div>

    </div>
  );
}