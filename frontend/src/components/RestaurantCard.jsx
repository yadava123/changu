import { ArrowUpRight, MapPin, Star } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function RestaurantCard({ restaurant }) {
  return <Link to={`/restaurants/${restaurant.id}`} className="catalog-card restaurant-card"><div className="catalog-image food-image"><span>Local kitchen</span></div><div className="catalog-card-body"><div className="card-title-row"><strong>{restaurant.name}</strong><span className="rating"><Star size={13} /> 4.8</span></div><p>{restaurant.description}</p><small><MapPin size={13} /> {restaurant.city}</small><span className="view-link">View restaurant <ArrowUpRight size={15} /></span></div></Link>
}
