import { ArrowLeft, ShoppingCart } from 'lucide-react'
import { Link } from 'react-router-dom'
import CartItem from '../components/CartItem'
import CartSummary from '../components/CartSummary'
import EmptyState from '../components/EmptyState'
import LoadingSpinner from '../components/LoadingSpinner'
import { useCart } from '../context/CartContext'

export default function Cart() {
  const { items, loading, error } = useCart()
  return <div className="commerce-page"><Link to="/home" className="back-link"><ArrowLeft size={15} /> Home</Link><div className="page-intro"><span className="section-kicker">Ready when you are</span><h1>Your Cart</h1><p>Review your items before checkout.</p></div>{loading && !items.length ? <LoadingSpinner label="Loading cart..." /> : error && !items.length ? <EmptyState title={error} /> : !items.length ? <EmptyState title="Your cart is empty." detail="Start exploring ChanGu to add something delicious or useful." /> : <div className="commerce-layout"><div className="cart-list">{items.map((item) => <CartItem key={item.id} item={item} />)}</div><CartSummary /></div>}</div>
}
