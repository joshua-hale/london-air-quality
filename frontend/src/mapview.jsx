import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { useEffect, useState } from "react";

export default function MapView() {
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/boroughs")
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        setLocations(data);
      })
      .catch((err) => console.error("Fetch error:", err));
  }, []);

  return (
    <MapContainer
      center={[51.505, -0.09]}
      zoom={10}
      style={{ height: "500px", width: "100%" }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {locations.map((loc, index) => (
        <Marker
          key={index}
          position={[loc.latitude, loc.longitude]}
        >
          <Popup>
            <div>
              <h3>{loc.borough}</h3>
              <p><strong>European AQI:</strong> {loc.european_aqi}</p>
              <p><strong>PM2.5:</strong> {loc.pm2_5}</p>
              <p><strong>PM10:</strong> {loc.pm10}</p>
              <p><strong>NO2:</strong> {loc.no2}</p>
              <p><strong>O3:</strong> {loc.o3}</p>
              <p><strong>SO2:</strong> {loc.so2}</p>
              <p><strong>Timestamp:</strong> {loc.timestamp}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}