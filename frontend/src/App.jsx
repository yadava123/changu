import { useEffect, useState } from 'react'
import { Navigate, NavLink, Route, Routes } from 'react-router-dom'
import { ArrowUpRight, Bell, HeartPulse, Search } from 'lucide-react'
import { Link } from 'react-router-dom'
import Cart from './pages/Cart'
import Checkout from './pages/Checkout'
import BecomeVendor from './pages/BecomeVendor'
import VendorApplicationStatus from './pages/VendorApplicationStatus'
import AdminRoute from './components/AdminRoute'
import VendorRoute from './components/VendorRoute'
import VendorLayout from './pages/vendor/VendorLayout'
import VendorDashboard from './pages/vendor/VendorDashboard'
import VendorStore from './pages/vendor/VendorStore'
import VendorProducts from './pages/vendor/VendorProducts'
import AddProduct from './pages/vendor/AddProduct'
import EditProduct from './pages/vendor/EditProduct'
import Inventory from './pages/vendor/Inventory'
import VendorOrders from './pages/vendor/VendorOrders'
import VendorProfile from './pages/vendor/VendorProfile'
import VendorSettings from './pages/vendor/VendorSettings'
import VendorApplications from './pages/admin/VendorApplications'
import DriverRoute from './components/DriverRoute'
import BecomeDriver from './pages/BecomeDriver'
import DriverApplicationStatus from './pages/DriverApplicationStatus'
import DriverLayout from './pages/driver/DriverLayout'
import DriverDashboard from './pages/driver/DriverDashboard'
import DriverDeliveries from './pages/driver/DriverDeliveries'
import DeliveryDetails from './pages/driver/DeliveryDetails'
import DeliveryHistory from './pages/driver/DeliveryHistory'
import DriverProfile from './pages/driver/DriverProfile'
import DriverSettings from './pages/driver/DriverSettings'
import DriverTransport from './pages/driver/DriverTransport'
import Drivers from './pages/admin/Drivers'
import SirenRoute from './components/SirenRoute'
import Siren from './pages/Siren'
import MyEmergencyRequests from './pages/MyEmergencyRequests'
import EmergencyRequestDetails from './pages/EmergencyRequestDetails'
import BecomeProvider from './pages/BecomeProvider'
import ProviderDashboard from './pages/provider/ProviderDashboard'
import ProviderRequests from './pages/provider/ProviderRequests'
import ProviderLayout from './pages/provider/ProviderLayout'
import EmergencyRequests from './pages/admin/EmergencyRequests'
import Providers from './pages/admin/Providers'
import AdminLayout from './layouts/AdminLayout'
import AdminDashboard from './pages/admin/AdminDashboard'
import Financials from './pages/admin/Financials'
import Users from './pages/admin/Users'
import Operations from './pages/admin/Operations'
import Approvals from './pages/admin/Approvals'
import { AuditLogs, Settings as AdminSettings, Notifications as AdminNotifications } from './pages/admin/AdminUtilityPages'
import Assistant from './pages/Assistant'
import Preferences from './pages/Preferences'
import Notifications from './pages/Notifications'
import NotificationSettings from './pages/NotificationSettings'
import NotificationCenter from './components/NotificationCenter'

import CustomerNav from './components/CustomerNav'
import LocationSelector from './components/LocationSelector'
import SearchBar from './components/SearchBar'
import ServiceCard from './components/ServiceCard'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider, useAuth } from './context/AuthContext'
import { serviceCategories } from './config/services'
import ComingSoon from './pages/ComingSoon'
import Explore from './pages/Explore'
import Food from './pages/Food'
import FoodDetails from './pages/FoodDetails'
import Login from './pages/Login'
import Orders from './pages/Orders'
import OrderDetails from './pages/OrderDetails'
import DeliveryTracking from './pages/DeliveryTracking'
import Review from './pages/Review'
import Earnings from './pages/Earnings'
import Payments from './pages/Payments'
import Rewards from './pages/Rewards'
import Parcel from './pages/Parcel'
import Rides from './pages/Rides'
import TransportDetails from './pages/TransportDetails'
import ProductDetails from './pages/ProductDetails'
import Profile from './pages/Profile'
import Register from './pages/Register'
import { RoleChooser, RoleLogin, RoleRegister } from './pages/RoleAuth'
import RestaurantDetails from './pages/RestaurantDetails'
import CustomerDashboard from './pages/CustomerDashboard'
import Shop from './pages/Shop'
import { CartProvider } from './context/CartContext'
import api, { getHealth } from './services/api'

function Shell({ children }) {
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <div className="app-shell">
      <header className="topbar">
        <NavLink to="/home" className="brand" aria-label="ChanGu home">
          <span className="brand-mark">C</span>
          <span>ChanGu</span>
        </NavLink>
        <nav className="nav-links" aria-label="Main navigation">
          {isAuthenticated ? <>
            <span className="user-greeting">{user?.full_name}</span>
            <NotificationCenter />
            <Link to="/profile" className="profile-top-link"><Bell size={18} /></Link>
            <button type="button" className="logout-button" onClick={logout}>Logout</button>
          </> : <>
            <Link to="/login" className="login-link">Login <ArrowUpRight size={15} /></Link>
            <Link to="/register" className="register-link">Register</Link>
          </>}
        </nav>
      </header>
      <main>{children}</main>
      {isAuthenticated && <CustomerNav />}
    </div>
  )
}

function BackendStatus() {
  const [state, setState] = useState('loading')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let mounted = true
    getHealth()
      .then(() => mounted && setState('connected'))
      .catch((error) => {
        if (mounted) {
          setState('offline')
          setErrorMessage(error.message)
        }
      })
    return () => { mounted = false }
  }, [])

  const label = state === 'loading' ? 'Checking backend...' : `Backend Status: ${state === 'connected' ? 'Connected' : 'Offline'}`
  return (
    <div className={`status-pill ${state}`} role="status" title={state === 'offline' ? errorMessage : undefined}>
      <span className="status-dot" />{label}
    </div>
  )
}

function Home() {
  const { user } = useAuth()
  const [query, setQuery] = useState('')
  const [recommendations, setRecommendations] = useState(null)
  useEffect(() => { getRecommendations().then(setRecommendations).catch(() => {}) }, [])

  return (
    <div className="home-page customer-home">
      <section className="customer-head"><div><span className="eyebrow">Good morning, {user.full_name}</span><h1>What do you need <em>today?</em></h1></div><LocationSelector /></section>
      <SearchBar value={query} onChange={setQuery} onSubmit={() => { window.location.href = `/explore?q=${encodeURIComponent(query)}` }} />
      <Link to="/siren" className="siren-banner"><span className="siren-icon"><HeartPulse size={22} /></span><div><strong>ChanGu Siren</strong><small>Need urgent assistance? Connect with registered providers.</small></div><span className="auth-submit">Get Help</span></Link>
      <section className="services-section" aria-labelledby="quick-services-title">
        <div className="section-heading"><div><span className="section-kicker">Your neighbourhood</span><h2 id="quick-services-title">Quick services</h2></div><Link to="/explore" className="view-link">View all <ArrowUpRight size={15} /></Link></div>
        <div className="service-grid">
          {serviceCategories.map((service) => <ServiceCard service={service} key={service.id} />)}
        </div>
      </section>
      <section className="home-lower"><div><span className="section-kicker">Curated for you</span><h2>Recommended</h2><p>Discover local food and products after exploring a service.</p></div><div className="recent-activity"><span className="section-kicker">Your activity</span><h2>Recent Activity</h2><p>No recent activity yet.</p></div></section>
      {recommendations?.personalized?.length > 0 && <RecommendationStrip title="Recommended for you" items={recommendations.personalized} />}
      {recommendations?.recently_viewed?.length > 0 && <RecommendationStrip title="Recently viewed" items={recommendations.recently_viewed} />}
      {recommendations?.popular_nearby?.length > 0 && <RecommendationStrip title="Popular near you" items={recommendations.popular_nearby} />}
      {recommendations?.trending?.length > 0 && <RecommendationStrip title="Trending now" items={recommendations.trending} />}
    </div>
  )
}

async function getRecommendations() { const { data } = await api.get('/api/recommendations/home'); return data }
function RecommendationStrip({ title, items }) { return <section className="recommendation-strip"><div className="section-heading"><h2>{title}</h2><span>Personalized discovery</span></div><div className="recommendation-items">{items.slice(0, 10).map(item => <Link className="recommendation-item" to={item.type === 'food' ? `/food/${item.id}` : item.type === 'product' ? `/shop/${item.id}` : `/restaurants/${item.id}`} key={`${item.type}-${item.id}`}><strong>{item.name || `${item.type} #${item.id}`}</strong><small>{item.reason || 'From ChanGu'}</small></Link>)}</div></section> }

export default function App() {
  return <AuthProvider><CartProvider><Shell><Routes>
    <Route path="/" element={<Navigate to="/choose-role" replace />} />
    <Route path="/choose-role" element={<RoleChooser />} />
    <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
    <Route path="/customer/dashboard" element={<ProtectedRoute><CustomerDashboard /></ProtectedRoute>} />
    <Route path="/food" element={<ProtectedRoute><Food /></ProtectedRoute>} />
    <Route path="/food/:id" element={<ProtectedRoute><FoodDetails /></ProtectedRoute>} />
    <Route path="/restaurants/:id" element={<ProtectedRoute><RestaurantDetails /></ProtectedRoute>} />
    <Route path="/shop" element={<ProtectedRoute><Shop /></ProtectedRoute>} />
    <Route path="/shop/:id" element={<ProtectedRoute><ProductDetails /></ProtectedRoute>} />
    <Route path="/explore" element={<ProtectedRoute><Explore /></ProtectedRoute>} />
    <Route path="/cart" element={<ProtectedRoute><Cart /></ProtectedRoute>} />
    <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
    <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
    <Route path="/orders/:id" element={<ProtectedRoute><OrderDetails /></ProtectedRoute>} />
    <Route path="/orders/:orderId/tracking" element={<ProtectedRoute><DeliveryTracking /></ProtectedRoute>} />
    <Route path="/orders/:orderId/review" element={<ProtectedRoute><Review /></ProtectedRoute>} />
    <Route path="/earnings" element={<ProtectedRoute><Earnings /></ProtectedRoute>} />
    <Route path="/payments" element={<ProtectedRoute><Payments /></ProtectedRoute>} />
    <Route path="/rewards" element={<ProtectedRoute><Rewards /></ProtectedRoute>} />
    <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
    <Route path="/profile/preferences" element={<ProtectedRoute><Preferences /></ProtectedRoute>} />
    <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
    <Route path="/profile/notifications" element={<ProtectedRoute><NotificationSettings /></ProtectedRoute>} />
    <Route path="/become-vendor" element={<ProtectedRoute><BecomeVendor /></ProtectedRoute>} />
    <Route path="/vendor/application" element={<ProtectedRoute><VendorApplicationStatus /></ProtectedRoute>} />
    <Route path="/vendor/dashboard" element={<VendorRoute><VendorLayout><VendorDashboard /></VendorLayout></VendorRoute>} />
    <Route path="/vendor/store" element={<VendorRoute><VendorLayout><VendorStore /></VendorLayout></VendorRoute>} />
    <Route path="/vendor/products" element={<VendorRoute><VendorLayout><VendorProducts /></VendorLayout></VendorRoute>} />
    <Route path="/vendor/products/new" element={<VendorRoute><VendorLayout><AddProduct /></VendorLayout></VendorRoute>} />
    <Route path="/vendor/products/:id/edit" element={<VendorRoute><VendorLayout><EditProduct /></VendorLayout></VendorRoute>} />
    <Route path="/vendor/inventory" element={<VendorRoute><VendorLayout><Inventory /></VendorLayout></VendorRoute>} />
    <Route path="/vendor/orders" element={<VendorRoute><VendorLayout><VendorOrders /></VendorLayout></VendorRoute>} />
    <Route path="/vendor/profile" element={<VendorRoute><VendorLayout><VendorProfile /></VendorLayout></VendorRoute>} />
    <Route path="/vendor/settings" element={<VendorRoute><VendorLayout><VendorSettings /></VendorLayout></VendorRoute>} />
    <Route path="/admin/dashboard" element={<AdminRoute><AdminLayout><AdminDashboard /></AdminLayout></AdminRoute>} />
    <Route path="/admin/financials" element={<AdminRoute><AdminLayout><Financials /></AdminLayout></AdminRoute>} />
    <Route path="/admin/users" element={<AdminRoute><AdminLayout><Users /></AdminLayout></AdminRoute>} />
    <Route path="/admin/vendors" element={<AdminRoute><AdminLayout><Operations type="vendors" /></AdminLayout></AdminRoute>} />
    <Route path="/admin/vendor" element={<AdminRoute><AdminLayout><Operations type="vendors" /></AdminLayout></AdminRoute>} />
    <Route path="/admin/products" element={<AdminRoute><AdminLayout><Operations type="products" /></AdminLayout></AdminRoute>} />
    <Route path="/admin/orders" element={<AdminRoute><AdminLayout><Operations type="orders" /></AdminLayout></AdminRoute>} />
    <Route path="/admin/parcels" element={<AdminRoute><AdminLayout><Operations type="parcels" /></AdminLayout></AdminRoute>} />
    <Route path="/admin/rides" element={<AdminRoute><AdminLayout><Operations type="rides" /></AdminLayout></AdminRoute>} />
    <Route path="/admin/deliveries" element={<AdminRoute><AdminLayout><Operations type="deliveries" /></AdminLayout></AdminRoute>} />
    <Route path="/admin/siren" element={<AdminRoute><AdminLayout><Operations type="siren" /></AdminLayout></AdminRoute>} />
    <Route path="/admin/audit-logs" element={<AdminRoute><AdminLayout><AuditLogs /></AdminLayout></AdminRoute>} />
    <Route path="/admin/settings" element={<AdminRoute><AdminLayout><AdminSettings /></AdminLayout></AdminRoute>} />
    <Route path="/admin/notifications" element={<AdminRoute><AdminLayout><AdminNotifications /></AdminLayout></AdminRoute>} />
    <Route path="/admin/approvals" element={<AdminRoute><AdminLayout><Approvals /></AdminLayout></AdminRoute>} />
    <Route path="/admin/vendor-applications" element={<AdminRoute><AdminLayout><VendorApplications /></AdminLayout></AdminRoute>} />
    <Route path="/admin/vendor-application" element={<AdminRoute><AdminLayout><VendorApplications /></AdminLayout></AdminRoute>} />
    <Route path="/admin/drivers" element={<AdminRoute><AdminLayout><Drivers /></AdminLayout></AdminRoute>} />
    <Route path="/admin/driver" element={<AdminRoute><AdminLayout><Drivers /></AdminLayout></AdminRoute>} />
    <Route path="/become-driver" element={<ProtectedRoute><BecomeDriver /></ProtectedRoute>} />
    <Route path="/driver/application" element={<ProtectedRoute><DriverApplicationStatus /></ProtectedRoute>} />
    <Route path="/driver/dashboard" element={<DriverRoute><DriverLayout><DriverDashboard /></DriverLayout></DriverRoute>} />
    <Route path="/driver/deliveries" element={<DriverRoute><DriverLayout><DriverDeliveries /></DriverLayout></DriverRoute>} />
    <Route path="/driver/transport" element={<DriverRoute><DriverLayout><DriverTransport /></DriverLayout></DriverRoute>} />
    <Route path="/driver/parcels" element={<DriverRoute><DriverLayout><DriverTransport /></DriverLayout></DriverRoute>} />
    <Route path="/driver/parcels/history" element={<DriverRoute><DriverLayout><DriverTransport /></DriverLayout></DriverRoute>} />
    <Route path="/driver/rides" element={<DriverRoute><DriverLayout><DriverTransport /></DriverLayout></DriverRoute>} />
    <Route path="/driver/rides/history" element={<DriverRoute><DriverLayout><DriverTransport /></DriverLayout></DriverRoute>} />
    <Route path="/driver/deliveries/:id" element={<DriverRoute><DriverLayout><DeliveryDetails /></DriverLayout></DriverRoute>} />
    <Route path="/driver/deliveries/history" element={<DriverRoute><DriverLayout><DeliveryHistory /></DriverLayout></DriverRoute>} />
    <Route path="/driver/profile" element={<DriverRoute><DriverLayout><DriverProfile /></DriverLayout></DriverRoute>} />
    <Route path="/driver/settings" element={<DriverRoute><DriverLayout><DriverSettings /></DriverLayout></DriverRoute>} />
    <Route path="/parcel" element={<ProtectedRoute><Parcel /></ProtectedRoute>} />
    <Route path="/customer/parcels" element={<ProtectedRoute><Parcel /></ProtectedRoute>} />
    <Route path="/customer/parcels/create" element={<ProtectedRoute><Parcel /></ProtectedRoute>} />
    <Route path="/parcel/:id" element={<ProtectedRoute><TransportDetails type="parcel" /></ProtectedRoute>} />
    <Route path="/customer/parcels/:id" element={<ProtectedRoute><TransportDetails type="parcel" /></ProtectedRoute>} />
    <Route path="/rides" element={<ProtectedRoute><Rides /></ProtectedRoute>} />
    <Route path="/customer/rides" element={<ProtectedRoute><Rides /></ProtectedRoute>} />
    <Route path="/customer/rides/book" element={<ProtectedRoute><Rides /></ProtectedRoute>} />
    <Route path="/rides/:id" element={<ProtectedRoute><TransportDetails type="ride" /></ProtectedRoute>} />
    <Route path="/customer/rides/:id" element={<ProtectedRoute><TransportDetails type="ride" /></ProtectedRoute>} />
    <Route path="/siren" element={<ProtectedRoute><Siren /></ProtectedRoute>} />
    <Route path="/emergency/requests" element={<ProtectedRoute><MyEmergencyRequests /></ProtectedRoute>} />
    <Route path="/emergency/requests/:id" element={<ProtectedRoute><EmergencyRequestDetails /></ProtectedRoute>} />
    <Route path="/customer/siren/:id" element={<ProtectedRoute><EmergencyRequestDetails /></ProtectedRoute>} />
    <Route path="/emergency/history" element={<ProtectedRoute><MyEmergencyRequests /></ProtectedRoute>} />
    <Route path="/provider/apply" element={<ProtectedRoute><BecomeProvider /></ProtectedRoute>} />
    <Route path="/provider/application" element={<ProtectedRoute><BecomeProvider /></ProtectedRoute>} />
    <Route path="/provider" element={<SirenRoute><ProviderLayout><ProviderDashboard /></ProviderLayout></SirenRoute>} />
    <Route path="/provider/dashboard" element={<SirenRoute><ProviderLayout><ProviderDashboard /></ProviderLayout></SirenRoute>} />
    <Route path="/provider/requests" element={<SirenRoute><ProviderLayout><ProviderRequests /></ProviderLayout></SirenRoute>} />
    <Route path="/admin/emergency" element={<AdminRoute><AdminLayout><EmergencyRequests /></AdminLayout></AdminRoute>} />
    <Route path="/admin/providers" element={<AdminRoute><AdminLayout><Providers /></AdminLayout></AdminRoute>} />
    <Route path="/assistant" element={<ProtectedRoute><Assistant /></ProtectedRoute>} />
    <Route path="/admin/ai" element={<AdminRoute><AdminLayout><Operations type="ai" /></AdminLayout></AdminRoute>} />
    <Route path="/login" element={<Navigate to="/customer/login" replace />} />
    <Route path="/register" element={<Navigate to="/customer/register" replace />} />
    <Route path="/:role/login" element={<RoleLogin />} />
    <Route path="/:role/register" element={<RoleRegister />} />
    <Route path="*" element={<ComingSoon />} />
  </Routes></Shell></CartProvider></AuthProvider>
}
