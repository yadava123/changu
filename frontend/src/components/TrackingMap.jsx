import { CircleMarker, MapContainer, TileLayer, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

function Recenter({ position }) {
  const map = useMap()
  map.setView(position, Math.max(map.getZoom(), 14))
  return null
}

export default function TrackingMap({ location, label = 'Current location' }) {
  if (!location) return <div className="map-state"><strong>Map waiting for location</strong><span>The assigned driver has not shared a current position yet.</span></div>
  const position = [location.latitude, location.longitude]
  const tileUrl = import.meta.env.VITE_MAP_TILE_URL || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
  const attribution = import.meta.env.VITE_MAP_ATTRIBUTION || '&copy; OpenStreetMap contributors'
  return <div className="tracking-map" aria-label={label}><MapContainer center={position} zoom={14} scrollWheelZoom={false}><TileLayer url={tileUrl} attribution={attribution} /><Recenter position={position} /><CircleMarker center={position} radius={10} pathOptions={{ color: '#d36b3d', fillColor: '#d36b3d', fillOpacity: 0.85 }} /></MapContainer></div>
}
