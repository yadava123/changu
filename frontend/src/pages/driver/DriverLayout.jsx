import DriverSidebar from '../../components/DriverSidebar'
export default function DriverLayout({children}){return <div className="vendor-layout"><DriverSidebar/><main className="vendor-main">{children}</main></div>}
