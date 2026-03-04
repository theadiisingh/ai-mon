import { useEffect, useRef } from 'react'
import { TimeSeriesPoint } from '../../types/monitoring'

interface ResponseTimeChartProps {
  data: TimeSeriesPoint[]
  loading?: boolean
}

export default function ResponseTimeChart({ data, loading }: ResponseTimeChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!canvasRef.current || !data.length) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Set up dimensions
    const padding = 40
    const paddingRight = 20
    const paddingBottom = 40
    const chartWidth = canvas.width - padding - paddingRight
    const chartHeight = canvas.height - padding - paddingBottom

    // Calculate min/max values
    const values = data.map(d => d.value)
    const maxValue = Math.max(...values, 100)
    const minValue = 0
    const valueRange = maxValue - minValue || 1

    // Draw grid lines
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.1)'
    ctx.lineWidth = 1
    ctx.setLineDash([4, 4])
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight / 4) * i
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(canvas.width - paddingRight, y)
      ctx.stroke()
    }
    ctx.setLineDash([])

    // Draw line - muted blue for professional look
    ctx.strokeStyle = '#3B82F6'
    ctx.lineWidth = 2
    ctx.lineJoin = 'round'
    ctx.lineCap = 'round'
    ctx.beginPath()

    data.forEach((point, idx) => {
      const x = padding + (chartWidth / (data.length - 1)) * idx
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight

      if (idx === 0) {
        ctx.moveTo(x, y)
      } else {
        const prevX = padding + (chartWidth / (data.length - 1)) * (idx - 1)
        const prevY = padding + chartHeight - ((data[idx - 1].value - minValue) / valueRange) * chartHeight
        const cpX = (prevX + x) / 2
        ctx.bezierCurveTo(cpX, prevY, cpX, y, x, y)
      }
    })

    ctx.stroke()

    // Create gradient fill
    const gradient = ctx.createLinearGradient(0, padding, 0, padding + chartHeight)
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.15)')
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0)')

    ctx.fillStyle = gradient
    ctx.lineTo(padding + chartWidth, padding + chartHeight)
    ctx.lineTo(padding, padding + chartHeight)
    ctx.closePath()
    ctx.fill()

    // Draw last point
    if (data.length > 0) {
      const lastPoint = data[data.length - 1]
      const lastX = padding + chartWidth
      const lastY = padding + chartHeight - ((lastPoint.value - minValue) / valueRange) * chartHeight

      ctx.fillStyle = '#0F172A'
      ctx.strokeStyle = '#3B82F6'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(lastX, lastY, 4, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()
    }

    // Draw labels
    ctx.fillStyle = '#64748B'
    ctx.font = '500 11px IBM Plex Sans, sans-serif'
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'

    for (let i = 0; i <= 4; i++) {
      const value = maxValue - (valueRange / 4) * i
      const y = padding + (chartHeight / 4) * i
      ctx.fillText(`${Math.round(value)}ms`, padding - 10, y)
    }
  }, [data])

  if (loading) {
    return (
      <div className="card p-4 h-[300px] flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center w-full">
          <div className="h-[200px] w-full bg-surface-700/50 rounded-lg"></div>
        </div>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="card p-6 h-[300px] flex flex-col items-center justify-center">
        <div className="w-10 h-10 bg-surface-700 rounded-full flex items-center justify-center mb-3 border border-border">
          <svg className="w-5 h-5 text-content-tertiary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
        </div>
        <p className="text-xs font-medium text-content-primary mb-1">No latency data</p>
        <p className="text-[10px] text-content-tertiary">Wait for the monitoring service to start recording data.</p>
      </div>
    )
  }

  return (
    <div className="card p-4 h-[300px]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-content-primary">Response Time History</h3>
      </div>
      <div className="relative w-full h-[220px]">
        <canvas ref={canvasRef} width={600} height={220} className="w-full h-full"></canvas>
      </div>
    </div>
  )
}

