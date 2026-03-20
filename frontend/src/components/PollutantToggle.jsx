import { POLLUTANTS } from '../utils/pollutantConfig';

export default function PollutantToggle({ active, onChange }) {
  return (
    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
      {POLLUTANTS.map(p => (
        <button
          key={p.key}
          onClick={() => onChange(p.key)}
          style={{
            padding: '6px 18px',
            borderRadius: '20px',
            fontSize: '13px',
            fontFamily: 'Inter, sans-serif',
            fontWeight: active === p.key ? 500 : 400,
            cursor: 'pointer',
            border: active === p.key ? '1px solid #fff' : '1px solid #2a2a2a',
            color: active === p.key ? '#000' : '#666',
            background: active === p.key ? '#fff' : 'transparent',
            transition: 'all 0.15s',
          }}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}