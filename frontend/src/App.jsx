import { useEffect, useState } from 'react'
import { getHeatmap } from './api'
import Heatmap from './components/Heatmap'

export default function App() {
  const [d, setD] = useState(null)

  useEffect(() => {
    getHeatmap().then(setD).catch((e) => console.error(e))
  }, [])

  return (
    <div className="wrap">
      <div className="sh"><h2>gamma heatmap</h2></div>
      <div className="eyebrow">SPX · STRIKE × EXPIRY</div>

      <div className="viz">
        <div className="vh">
          <span>net dealer gamma</span>
          <span className="v">{d ? `spot ${d.spot.toFixed(0)}` : '—'}</span>
        </div>
        <div className="body"><Heatmap data={d} /></div>
        <div className="scale">
          <span>short γ</span><span className="bar" /><span>long γ</span>
          <span style={{ marginLeft: 'auto' }}>dashed line = spot</span>
        </div>
      </div>
      <div className="foot">synthetic chain by default · set <code>CBOE_TOKEN</code> for a live chain</div>
    </div>
  )
}
