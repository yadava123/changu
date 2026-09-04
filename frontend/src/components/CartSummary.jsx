import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'

export default function CartSummary({ checkout = false }) {
  const { cart } = useCart()
  return <div className="cart-summary"><div><span>Subtotal</span><b>₹{Number(cart.subtotal).toFixed(0)}</b></div><div><span>Delivery</span><b>₹{Number(cart.delivery_fee).toFixed(0)}</b></div><div><span>Tax</span><b>₹{Number(cart.tax).toFixed(0)}</b></div><div><span>Discount</span><b>₹{Number(cart.discount).toFixed(0)}</b></div><div className="summary-total"><strong>Total</strong><strong>₹{Number(cart.total).toFixed(0)}</strong></div>{!checkout && <Link to="/checkout" className="auth-submit">Proceed to Checkout</Link>}</div>
}
