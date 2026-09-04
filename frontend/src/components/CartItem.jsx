import { Minus, Plus, Trash2 } from 'lucide-react'
import { useCart } from '../context/CartContext'

export default function CartItem({ item }) {
  const { updateQuantity, removeFromCart } = useCart()
  return <div className="cart-item"><div className="cart-item-image">{item.type}</div><div className="cart-item-copy"><strong>{item.name}</strong><small>₹{Number(item.unit_price).toFixed(0)} each</small><div className="quantity-control"><button type="button" onClick={() => item.quantity > 1 ? updateQuantity(item.id, item.quantity - 1) : removeFromCart(item.id)}><Minus size={14} /></button><span>{item.quantity}</span><button type="button" onClick={() => updateQuantity(item.id, item.quantity + 1)}><Plus size={14} /></button></div></div><div className="cart-item-total"><strong>₹{Number(item.total_price).toFixed(0)}</strong><button type="button" aria-label="Remove item" onClick={() => removeFromCart(item.id)}><Trash2 size={16} /></button></div></div>
}
