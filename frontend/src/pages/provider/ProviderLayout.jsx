import ProviderSidebar from '../../components/ProviderSidebar'

export default function ProviderLayout({ children }) {
  return <div className="vendor-layout"><ProviderSidebar /><main className="vendor-main">{children}</main></div>
}
