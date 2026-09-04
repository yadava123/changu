import VendorSidebar from '../../components/VendorSidebar'
export default function VendorLayout({children}){return <div className="vendor-layout"><VendorSidebar/><main className="vendor-main">{children}</main></div>}
