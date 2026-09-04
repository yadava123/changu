import { useState } from 'react'
import { ShoppingCart } from 'lucide-react'
import { useCart } from '../context/CartContext'

export default function AddToCartButton({ item, label = 'Add to Cart' }) {
  const { addToCart } = useCart()
  const [message, setMessage] = useState('')
  async function add(event) { event.preventDefault(); event.stopPropagation(); try { await addToCart(item); setMessage('Added to cart'); setTimeout(() => setMessage(''), 1800) } catch {} }
  return <span className="add-cart-wrap"><button type="button" className="add-cart-button" onClick={add}><ShoppingCart size={14} /> {message || label}</button></span>
}
