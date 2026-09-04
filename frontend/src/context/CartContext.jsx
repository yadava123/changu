import { createContext, useContext, useEffect, useState } from 'react'
import api from '../services/api'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [cart, setCart] = useState({ cart_id: null, items: [], subtotal: 0, delivery_fee: 0, tax: 0, discount: 0, total: 0 })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function refreshCart() {
    if (!localStorage.getItem('changu_access_token')) return
    setLoading(true)
    try { setCart((await api.get('/api/cart')).data); setError('') } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to load cart.') } finally { setLoading(false) }
  }
  useEffect(() => { refreshCart() }, [])
  async function mutate(request) { setLoading(true); try { const { data } = await request; setCart(data); setError(''); return data } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to update cart.'); throw requestError } finally { setLoading(false) } }
  const addToCart = (item) => mutate(api.post('/api/cart/items', item))
  const updateQuantity = (id, quantity) => mutate(api.patch(`/api/cart/items/${id}`, { quantity }))
  const removeFromCart = (id) => mutate(api.delete(`/api/cart/items/${id}`))
  const clearCart = () => mutate(api.delete('/api/cart'))
  return <CartContext.Provider value={{ cart, items: cart.items, itemCount: cart.items.reduce((sum, item) => sum + item.quantity, 0), subtotal: cart.subtotal, total: cart.total, loading, error, addToCart, updateQuantity, removeFromCart, clearCart, refreshCart }}>{children}</CartContext.Provider>
}

export function useCart() { const value = useContext(CartContext); if (!value) throw new Error('useCart must be used within CartProvider'); return value }
