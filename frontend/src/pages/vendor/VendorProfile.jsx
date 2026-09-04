import { useEffect,useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
export default function VendorProfile(){const [vendor,setVendor]=useState(null);useEffect(()=>{api.get('/api/vendor/store').then(({data})=>setVendor(data))},[]);if(!vendor)return <LoadingSpinner/>;return <div className="simple-page"><span className="section-kicker">Partner account</span><h1>{vendor.business_name}</h1><p>{vendor.business_type}</p><p>{vendor.email}<br/>{vendor.phone}<br/>{vendor.address}, {vendor.city}, {vendor.state} - {vendor.pincode}</p><span className="application-status approved">{vendor.is_active?'Active':'Inactive'}</span></div>}
