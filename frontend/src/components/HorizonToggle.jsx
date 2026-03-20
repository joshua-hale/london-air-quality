const HORIZONS = [
    { key: 'now',        label: 'Now'  },
    { key: 'forecast4h', label: '+4h'  },
    { key: 'forecast8h', label: '+8h'  },
  ];
  
  export default function HorizonToggle({ active, onChange }) {
    return (
      <div className="horizon-row">
        {HORIZONS.map(h => (
          <button
            key={h.key}
            className={`horizon-btn ${active === h.key ? 'active' : ''}`}
            onClick={() => onChange(h.key)}
          >
            {h.label}
          </button>
        ))}
      </div>
    );
  }