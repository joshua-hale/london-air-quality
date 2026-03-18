import { POLLUTANTS } from '../utils/pollutantConfig';

export default function PollutantToggle({ active, onChange }) {
  return (
    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>
      {POLLUTANTS.map(p => (
        <button
          key={p.key}
          onClick={() => onChange(p.key)}
          style={{
            padding: '5px 14px',
            borderRadius: '20px',
            border: '1px solid #ccc',
            cursor: 'pointer',
            fontWeight: active === p.key ? 600 : 400,
            background: active === p.key ? '#1d1d1d' : '#fff',
            color:  active === p.key ? '#fff' : '#333',
          }}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}