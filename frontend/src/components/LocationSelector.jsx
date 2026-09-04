import { ChevronDown, MapPin } from 'lucide-react'
import { useEffect, useState } from 'react'

const LOCATION_KEY = 'changu_city'
const locations = ['Bengaluru', 'Mumbai', 'Delhi', 'Hyderabad', 'Chennai']

export default function LocationSelector() {
  const [city, setCity] = useState(() => localStorage.getItem(LOCATION_KEY) || 'Bengaluru')

  useEffect(() => localStorage.setItem(LOCATION_KEY, city), [city])

  return <label className="location-selector"><MapPin size={17} /><span><small>Deliver to</small><strong>{city}</strong></span><ChevronDown size={16} /><select value={city} onChange={(event) => setCity(event.target.value)} aria-label="Select city">{locations.map((location) => <option key={location}>{location}</option>)}</select></label>
}
