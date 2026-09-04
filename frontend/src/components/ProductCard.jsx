import { ArrowUpRight, Package, Star } from 'lucide-react'
import { Link } from 'react-router-dom'
import AddToCartButton from './AddToCartButton'

export default function ProductCard({ product }) {
  return <Link to={`/shop/${product.id}`} className="catalog-card product-card"><div className="catalog-image product-image"><Package size={29} /></div><div className="catalog-card-body"><div className="card-title-row"><strong>{product.name}</strong><span className="rating"><Star size={13} /> 4.6</span></div><p>{product.description}</p><div className="price-row"><b>₹{Number(product.price).toFixed(0)}</b><span className="view-link">View <ArrowUpRight size={15} /></span></div><small>{product.stock_quantity > 0 ? `${product.stock_quantity} available` : 'Out of stock'}</small><AddToCartButton item={{ product_id: product.id, quantity: 1 }} /></div></Link>
}
