import { useEffect, useState } from 'react'
import { ArrowLeft, Leaf } from 'lucide-react'
import { Link } from 'react-router-dom'

import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingSpinner from '../components/LoadingSpinner'
import ProductCard from '../components/ProductCard'
import SearchBar from '../components/SearchBar'
import { getProducts } from '../services/productService'

const categories = ['Grocery', 'Fresh Meat', 'Dairy', 'Handmade', 'Organic', 'Local Products']

export default function Shop() {
  const [products, setProducts] = useState([])
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [state, setState] = useState('loading')

  async function load() {
    setState('loading')
    try { setProducts((await getProducts({ search: query || undefined, category: category || undefined })).data); setState('ready') } catch { setState('error') }
  }
  useEffect(() => { load() }, [category])

  return <div className="discovery-page"><Link to="/home" className="back-link"><ArrowLeft size={15} /> Home</Link><div className="page-intro"><span className="section-kicker">Good things, close by</span><h1>Shop</h1><p>Products and makers from your local community.</p></div><SearchBar value={query} onChange={setQuery} onSubmit={load} placeholder="Search products, stores..." /><div className="category-row"><Leaf size={17} />{categories.map((item) => <button type="button" className={category === item ? 'selected' : ''} onClick={() => setCategory(category === item ? '' : item)} key={item}>{item}</button>)}</div>{state === 'loading' && <LoadingSpinner label="Loading products..." />}{state === 'error' && <ErrorState onRetry={load} />}{state === 'ready' && <section className="catalog-section"><div className="section-heading"><h2>Products & Sellers</h2><span>{products.length} available</span></div>{products.length ? <div className="catalog-grid">{products.map((product) => <ProductCard key={product.id} product={product} />)}</div> : <EmptyState title="No products found." detail="Try changing your category or search." />}</section>}</div>
}
