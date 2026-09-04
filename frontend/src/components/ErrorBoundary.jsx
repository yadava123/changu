import { Component } from 'react'

export default class ErrorBoundary extends Component {
  state = { hasError: false }
  static getDerivedStateFromError() { return { hasError: true } }
  render() {
    if (this.state.hasError) return <div className="simple-page"><h1>Something went wrong.</h1><button className="auth-submit" onClick={() => window.location.reload()}>Reload</button></div>
    return this.props.children
  }
}