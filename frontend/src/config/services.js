import { Bot, Box, Car, HeartPulse, ShoppingBag, Utensils } from 'lucide-react'

export const serviceCategories = [
  { id: 'food', name: 'Food', description: 'Meals from local kitchens', icon: Utensils, route: '/food', status: 'active' },
  { id: 'shop', name: 'Shop', description: 'Everyday stores nearby', icon: ShoppingBag, route: '/shop', status: 'active' },
  { id: 'parcel', name: 'Parcel', description: 'Send it across town', icon: Box, route: '/parcel', status: 'active' },
  { id: 'rides', name: 'Rides', description: 'Move around your city', icon: Car, route: '/rides', status: 'active' },
  { id: 'siren', name: 'Siren', description: 'Help when it matters', icon: HeartPulse, route: '/siren', status: 'active' },
  { id: 'assistant', name: 'AI Assistant', description: 'A smarter local guide', icon: Bot, route: '/assistant', status: 'active' },
]
