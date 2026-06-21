export async function getHeatmap() {
  const res = await fetch('/api/heatmap')
  if (!res.ok) throw new Error(`API ${res.status}`)
  return res.json()
}
