import { useEffect, useState } from 'react'
import { ArrowLeft, Check, Clock3 } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import ErrorState from '../components/ErrorState'
import LoadingSpinner from '../components/LoadingSpinner'
import { getFoodItem } from '../services/foodService'
import { getRestaurant } from '../services/restaurantService'
import AddToCartButton from '../components/AddToCartButton'
import api from '../services/api'

export default function FoodDetails() {
  const { id } = useParams()
  const [food, setFood] = useState(null)
  const [restaurant, setRestaurant] = useState(null)
  const [state, setState] = useState('loading')
  useEffect(() => { getFoodItem(id).then(async (foodResponse) => { setFood(foodResponse.data); setRestaurant((await getRestaurant(foodResponse.data.restaurant_id)).data); api.post('/api/events', { event_type: 'VIEW_FOOD', entity_type: 'FOOD', entity_id: Number(id) }).catch(() => {}); setState('ready') }).catch(() => setState('error')) }, [id])
  if (state === 'loading') return <LoadingSpinner label="Loading food details..." />
  if (state === 'error') return <ErrorState />
  return <div className="detail-page"><Link to="/food" className="back-link"><ArrowLeft size={15} /> Back to food</Link><div className="detail-layout"><div className="detail-image meal-image"><span>{food.category}</span></div><div className="detail-copy"><span className="section-kicker">Freshly listed</span><h1>{food.name}</h1><p>{food.description}</p><div className="detail-meta"><b>₹{Number(food.price).toFixed(0)}</b><span><Clock3 size={15} /> Available now</span><span><Check size={15} /> {restaurant.name}</span></div><AddToCartButton item={{ food_item_id: food.id, quantity: 1 }} label="Add to Cart" /></div></div></div>
}
