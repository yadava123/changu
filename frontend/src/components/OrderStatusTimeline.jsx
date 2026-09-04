const statuses = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY_FOR_PICKUP', 'OUT_FOR_DELIVERY', 'DELIVERED']
export default function OrderStatusTimeline({ status }) {
  if (status === 'CANCELLED') return <div className="order-timeline cancelled"><span className="timeline-dot" /><strong>Order Cancelled</strong></div>
  const current = statuses.indexOf(status)
  return <div className="order-timeline">{statuses.map((item, index) => <div className={index <= current ? 'timeline-step complete' : 'timeline-step'} key={item}><span className="timeline-dot" /> <small>{item.replaceAll('_', ' ')}</small></div>)}</div>
}
