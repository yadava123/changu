import { useEffect, useState } from 'react'
import { ArrowLeft, Package, ShieldCheck } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import ErrorState from '../components/ErrorState'
import LoadingSpinner from '../components/LoadingSpinner'
import { getProduct } from '../services/productService'
import AddToCartButton from '../components/AddToCartButton'
import api from '../services/api'

export default function ProductDetails() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [state, setState] = useState('loading')
  useEffect(() => { getProduct(id).then(({ data }) => { setProduct(data); api.post('/api/events', { event_type: 'VIEW_PRODUCT', entity_type: 'PRODUCT', entity_id: Number(id) }).catch(() => {}); setState('ready') }).catch(() => setState('error')) }, [id])
  if (state === 'loading') return <LoadingSpinner label="Loading product details..." />
  if (state === 'error') return <ErrorState />
  return <div className="detail-page"><Link to="/shop" className="back-link"><ArrowLeft size={15} /> Back to shop</Link><div className="detail-layout"><div className="detail-image product-image"><Package size={55} /></div><div className="detail-copy"><span className="section-kicker">Local product</span><h1>{product.name}</h1><p>{product.description}</p><div className="detail-meta"><b>₹{Number(product.price).toFixed(0)}</b><span><ShieldCheck size={15} /> {product.category}</span><span>{product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'Out of stock'}</span></div><AddToCartButton item={{ product_id: product.id, quantity: 1 }} /></div></div></div>
}
