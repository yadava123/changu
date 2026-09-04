import { ArrowUpRight, Star } from 'lucide-react'
import { Link } from 'react-router-dom'
import AddToCartButton from './AddToCartButton'

export default function FoodCard({ food }) {
  return <Link to={`/food/${food.id}`} className="catalog-card food-item-card"><div className="catalog-image meal-image"><span>{food.category}</span></div><div className="catalog-card-body"><div className="card-title-row"><strong>{food.name}</strong><span className="rating"><Star size={13} /> 4.7</span></div><p>{food.description}</p><div className="price-row"><b>₹{Number(food.price).toFixed(0)}</b><span className="view-link">View <ArrowUpRight size={15} /></span></div><AddToCartButton item={{ food_item_id: food.id, quantity: 1 }} /></div></Link>
}
