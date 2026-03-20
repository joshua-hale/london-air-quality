import { useState, useEffect } from 'react'; 

const BASE_URL = `${import.meta.env.VITE_API_URL}/api`;

export function useAirQuality() {
  const [data, setData]       = useState({ now: [], forecast4h: [], forecast8h: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/boroughs`).then(r => r.json()),
      fetch(`${BASE_URL}/predictions/4h`).then(r => r.json()),
      fetch(`${BASE_URL}/predictions/8h`).then(r => r.json()),
    ])
      .then(([now, forecast4h, forecast8h]) => {
        setData({ now, forecast4h, forecast8h });
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { data, loading, error };
}