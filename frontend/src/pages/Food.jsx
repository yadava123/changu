import { useEffect, useState } from 'react'
import { ArrowLeft, ChefHat } from 'lucide-react'
import { Link } from 'react-router-dom'

import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import FoodCard from '../components/FoodCard'
import LoadingSpinner from '../components/LoadingSpinner'
import LocationSelector from '../components/LocationSelector'
import RestaurantCard from '../components/RestaurantCard'
import SearchBar from '../components/SearchBar'
import { getFood } from '../services/foodService'
import { getRestaurants } from '../services/restaurantService'

const categories = ['Indian', 'Healthy', 'Fast Food', 'Bakery', 'Home Chef']

export default function Food() {
  const [restaurants, setRestaurants] = useState([])
  const [food, setFood] = useState([])
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [state, setState] = useState('loading')

  async function load() {
    setState('loading')
    try {
      const [restaurantResponse, foodResponse] = await Promise.all([getRestaurants({ city: localStorage.getItem('changu_city') || 'Bengaluru' }), getFood({ search: query || undefined, category: category || undefined })])
      setRestaurants(restaurantResponse.data)
      setFood(foodResponse.data)
      setState('ready')
    } catch { setState('error') }
  }

  useEffect(() => { load() }, [category])
  function submit() { load() }

  return <div className="discovery-page"><Link to="/home" className="back-link"><ArrowLeft size={15} /> Home</Link><div className="page-intro service-intro"><div><span className="section-kicker">Fresh from your neighbourhood</span><h1>Food</h1><p>Meals from local restaurants and home chefs.</p></div><LocationSelector /></div><SearchBar value={query} onChange={setQuery} onSubmit={submit} placeholder="Search dishes, restaurants..." /><div className="category-row"><ChefHat size={17} />{categories.map((item) => <button type="button" className={category === item ? 'selected' : ''} onClick={() => setCategory(category === item ? '' : item)} key={item}>{item}</button>)}</div>{state === 'loading' && <LoadingSpinner label="Loading restaurants and food..." />}{state === 'error' && <ErrorState onRetry={load} />}{state === 'ready' && <><CatalogSection title="Restaurants & Home Chefs" items={restaurants} empty="No restaurants found." render={(item) => <RestaurantCard restaurant={item} />} /><CatalogSection title="Popular nearby dishes" items={food} empty="No food found." render={(item) => <FoodCard food={item} />} /></>}</div>
}

function CatalogSection({ title, items, empty, render }) { return <section className="catalog-section"><div className="section-heading"><h2>{title}</h2><span>{items.length} available</span></div>{items.length ? <div className="catalog-grid">{items.map((item) => <div key={item.id}>{render(item)}</div>)}</div> : <EmptyState title={empty} />}</section> }
