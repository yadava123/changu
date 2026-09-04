import { useEffect,useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
export default function Inventory(){const [items,setItems]=useState(null);useEffect(()=>{api.get('/api/vendor/products').then(({data})=>setItems(data))},[]);if(!items)return <LoadingSpinner/>;return <><span className="section-kicker">Stock control</span><h1 className="vendor-title">Inventory</h1><div className="vendor-table">{items.map(item=>{const status=item.stock_quantity>5?'IN STOCK':item.stock_quantity?'LOW STOCK':'OUT OF STOCK';return <div className="vendor-row" key={item.id}><strong>{item.name}</strong><span>{item.stock_quantity}</span><span className={`stock-status ${status.replace(' ','-').toLowerCase()}`}>{status}</span></div>})}</div></>}
