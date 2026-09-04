export const mapConfig = {
  tileUrl: import.meta.env.VITE_MAP_TILE_URL || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  attribution: import.meta.env.VITE_MAP_ATTRIBUTION || '&copy; OpenStreetMap contributors',
  routingUrl: import.meta.env.VITE_ROUTING_URL || 'https://router.project-osrm.org/route/v1/driving',
}

export function routingUrl(from, to) {
  return `${mapConfig.routingUrl}/${from.longitude},${from.latitude};${to.longitude},${to.latitude}?overview=false`
}