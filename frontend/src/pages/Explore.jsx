import { useState } from 'react'
import { Search } from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import SearchBar from '../components/SearchBar'
import { serviceCategories } from '../config/services'
import { searchCatalog } from '../services/searchService'
import EmptyState from '../components/EmptyState'
import LoadingSpinner from '../components/LoadingSpinner'
import RestaurantCard from '../components/RestaurantCard'
import FoodCard from '../components/FoodCard'
import ProductCard from '../components/ProductCard'

export default function Explore() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  async function search(value) {
    if (!value.trim()) return
    setLoading(true)
    try { setResults((await searchCatalog({ q: value })).data) } finally { setLoading(false) }
  }

  useEffect(() => { const initialQuery = searchParams.get('q') || ''; if (initialQuery) { setQuery(initialQuery); search(initialQuery) } }, [searchParams])

  return <div className="discovery-page"><div className="page-intro"><span className="section-kicker">Find your local favourites</span><h1>Explore</h1><p>Search across food, stores, and services near you.</p></div><SearchBar value={query} onChange={setQuery} onSubmit={search} placeholder="Search food, products, stores..." /><div className="explore-service-strip">{serviceCategories.filter((service) => service.status === 'active').map((service) => <button type="button" key={service.id} onClick={() => navigate(service.route)}><service.icon size={17} />{service.name}</button>)}</div>{loading && <LoadingSpinner label="Searching ChanGu..." />}{results && !loading && <div className="search-results"><ResultGroup title="Restaurants" items={results.restaurants} render={(item) => <RestaurantCard key={item.id} restaurant={item} />} /><ResultGroup title="Food" items={results.food} render={(item) => <FoodCard key={item.id} food={item} />} /><ResultGroup title="Products" items={results.products} render={(item) => <ProductCard key={item.id} product={item} />} />{!results.restaurants.length && !results.food.length && !results.products.length && <EmptyState title="Nothing matched your search." />}</div>}</div>
}

function ResultGroup({ title, items, render }) {
  if (!items.length) return null
  return <section className="catalog-section"><div className="section-heading"><h2>{title}</h2><span>{items.length} results</span></div><div className="catalog-grid">{items.slice(0, 4).map(render)}</div></section>
}
