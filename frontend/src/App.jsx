import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import MapView from "./mapview";

function App() {
  return (
    <div>
      <h1>London Air Quality Map</h1>
      <MapView />
    </div>
  );
}

export default App;