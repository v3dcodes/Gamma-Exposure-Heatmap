import { useEffect, useRef } from 'react'

const lerp = (a, b, t) => a + (b - a) * t
function color(v, vmax) {
  const t = Math.max(-1, Math.min(1, v / vmax))
  const bg = [10, 14, 22], pos = [100, 255, 218], neg = [255, 107, 129]
  const c = t >= 0 ? bg.map((x, i) => lerp(x, pos[i], t)) : bg.map((x, i) => lerp(x, neg[i], -t))
  return `rgb(${c.map(Math.round).join(',')})`
}

function render(cv, tip, d) {
  if (!cv || !d) return
  const { strikes, expiries, z, vmax, spot } = d
  const dpr = window.devicePixelRatio || 1
  const padL = 56, padB = 26, padT = 6, padR = 6
  const cols = expiries.length, rows = strikes.length
  const cw = 70, ch = Math.max(6, Math.min(14, 520 / rows))
  const W = padL + cols * cw + padR, H = padT + rows * ch + padB
  cv.style.width = W + 'px'; cv.style.height = H + 'px'
  cv.width = W * dpr; cv.height = H * dpr
  const ctx = cv.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, W, H)
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) {
      ctx.fillStyle = color(z[r][c], vmax)
      ctx.fillRect(padL + c * cw, padT + (rows - 1 - r) * ch, cw - 1, ch - 1)
    }
  let si = 0, best = 1e18
  strikes.forEach((s, i) => { if (Math.abs(s - spot) < best) { best = Math.abs(s - spot); si = i } })
  const y = padT + (rows - 1 - si) * ch + ch / 2
  ctx.strokeStyle = '#ccd6f6'; ctx.setLineDash([4, 4])
  ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(padL + cols * cw, y); ctx.stroke(); ctx.setLineDash([])
  ctx.fillStyle = '#5b647f'; ctx.font = "10px 'JetBrains Mono',ui-monospace,monospace"
  expiries.forEach((e, c) => ctx.fillText(e, padL + c * cw + 18, H - 10))
  for (let r = 0; r < rows; r += Math.ceil(rows / 14))
    ctx.fillText(strikes[r].toFixed(0), 6, padT + (rows - 1 - r) * ch + ch)

  cv.onmousemove = (ev) => {
    const rect = cv.getBoundingClientRect()
    const c = Math.floor((ev.clientX - rect.left - padL) / cw)
    const r = rows - 1 - Math.floor((ev.clientY - rect.top - padT) / ch)
    if (c < 0 || c >= cols || r < 0 || r >= rows) { tip.style.opacity = 0; return }
    tip.style.opacity = 1
    tip.style.left = ev.clientX + 12 + 'px'
    tip.style.top = ev.clientY + 12 + 'px'
    tip.textContent = `${strikes[r].toFixed(0)} · ${expiries[c]} · ${(z[r][c] / 1e6).toFixed(1)}M`
  }
  cv.onmouseleave = () => { tip.style.opacity = 0 }
}

export default function Heatmap({ data }) {
  const ref = useRef(null)
  const tipRef = useRef(null)
  useEffect(() => { render(ref.current, tipRef.current, data) }, [data])
  return (
    <>
      <canvas ref={ref} />
      <div ref={tipRef} className="tip" />
    </>
  )
}
