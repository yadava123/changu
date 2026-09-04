import { useEffect, useState } from 'react'
import { ArrowLeft, MapPin } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import ErrorState from '../components/ErrorState'
import FoodCard from '../components/FoodCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { getFood } from '../services/foodService'
import { getRestaurant } from '../services/restaurantService'
import api from '../services/api'

export default function RestaurantDetails() {
  const { id } = useParams()
  const [restaurant, setRestaurant] = useState(null)
  const [food, setFood] = useState([])
  const [state, setState] = useState('loading')
  useEffect(() => { Promise.all([getRestaurant(id), getFood({ restaurant_id: id })]).then(([restaurantResponse, foodResponse]) => { setRestaurant(restaurantResponse.data); setFood(foodResponse.data); api.post('/api/events', { event_type: 'VIEW_RESTAURANT', entity_type: 'RESTAURANT', entity_id: Number(id) }).catch(() => {}); setState('ready') }).catch(() => setState('error')) }, [id])
  if (state === 'loading') return <LoadingSpinner label="Loading restaurant..." />
  if (state === 'error') return <ErrorState />
  return <div className="detail-page"><Link to="/food" className="back-link"><ArrowLeft size={15} /> Back to food</Link><div className="restaurant-hero"><div className="catalog-image food-image"><span>Local kitchen</span></div><div><span className="section-kicker">Restaurant & home chef</span><h1>{restaurant.name}</h1><p>{restaurant.description}</p><small><MapPin size={14} /> {restaurant.address}, {restaurant.city}</small></div></div><section className="catalog-section"><div className="section-heading"><h2>Available food</h2><span>{food.length} dishes</span></div>{food.length ? <div className="catalog-grid">{food.map((item) => <FoodCard key={item.id} food={item} />)}</div> : <p>No dishes available right now.</p>}</section></div>
}
