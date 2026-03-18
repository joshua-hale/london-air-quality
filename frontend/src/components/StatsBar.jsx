import { POLLUTANTS } from '../utils/pollutantConfig';

export default function StatsBar({ data, pollutantKey }) {
  if (!data.length) return null;

  const pol    = POLLUTANTS.find(p => p.key === pollutantKey);
  const values = data.map(d => d[pollutantKey]);
  const avg    = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1);
  const max    = Math.max(...values);
  const min    = Math.min(...values);
  const highest = data.find(d => d[pollutantKey] === max);
  const lowest  = data.find(d => d[pollutantKey] === min);

  return (
    <div className="stats-bar">
      <div className="stat-card">
        <div className="stat-label">London average</div>
        <div className="stat-value">{avg}{pol.unit}</div>
        <div className="stat-sub">{pol.label}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Highest borough</div>
        <div className="stat-value">{max}{pol.unit}</div>
        <div className="stat-sub">{highest?.borough}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Lowest borough</div>
        <div className="stat-value">{min}{pol.unit}</div>
        <div className="stat-sub">{lowest?.borough}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Boroughs monitored</div>
        <div className="stat-value">{data.length}</div>
        <div className="stat-sub">of 33 total</div>
      </div>
    </div>
  );
}