import { Search, X } from 'lucide-react'

export default function SearchBar({ value, onChange, onSubmit, placeholder = 'Search food, stores, services...', compact = false }) {
  function submit(event) {
    event.preventDefault()
    onSubmit?.(value)
  }

  return <form className={`discovery-search ${compact ? 'compact' : ''}`} onSubmit={submit} role="search">
    <Search size={19} aria-hidden="true" />
    <input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} aria-label={placeholder} />
    {value && <button type="button" className="clear-search" onClick={() => onChange('')} aria-label="Clear search"><X size={16} /></button>}
    <button type="submit" className="search-submit">Search</button>
  </form>
}
