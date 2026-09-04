import { RotateCcw } from 'lucide-react'

export default function ErrorState({ message = 'Unable to load services. Please check your connection and try again.', onRetry }) {
  return <div className="state-panel error-state" role="alert"><strong>{message}</strong>{onRetry && <button type="button" onClick={onRetry}><RotateCcw size={15} /> Retry</button>}</div>
}
