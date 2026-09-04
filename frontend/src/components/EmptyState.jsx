export default function EmptyState({ title = 'No results found.', detail = 'Try changing your location or search.' }) {
  return <div className="state-panel empty-state"><strong>{title}</strong><span>{detail}</span></div>
}
