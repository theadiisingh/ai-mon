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
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2

    // Calculate min/max values
    const values = data.map(d => d.value)
    const maxValue = Math.max(...values)
    const minValue = Math.min(...values)
    const valueRange = maxValue - minValue || 1

    // Draw grid lines
    ctx.strokeStyle = '#e5e7eb'
    ctx.lineWidth = 1
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight / 4) * i
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(canvas.width - padding, y)
      ctx.stroke()
    }

    // Draw line
    ctx.strokeStyle = '#0ea5e9'
    ctx.lineWidth = 2
    ctx.beginPath()

    data.forEach((point, index) => {
      const x = padding + (chartWidth / (data.length - 1)) * index
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight
      
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // Draw points
    ctx.fillStyle = '#0ea5e9'
    data.forEach((point, index) => {
      const x = padding + (chartWidth / (data.length - 1)) * index
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight
      
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, Math.PI * 2)
      ctx.fill()
    })

    // Draw labels
    ctx.fillStyle = '#6b7280'
    ctx.font = '12px sans-serif'
    ctx.textAlign = 'right'
    
    for (let i = 0; i <= 4; i++) {
      const value = maxValue - (valueRange / 4) * i
      const y = padding + (chartHeight / 4) * i + 4
      ctx.fillText(`${Math.round(value)}ms`, padding - 8, y)
    }
  }, [data])

  if (loading) {
    return (
      <div className="card p-6 h-64 flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-32 w-full bg-gray-200 rounded"></div>
          <p className="mt-2 text-sm text-gray-500">Loading chart data...</p>
        </div>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="card p-6 h-64 flex items-center justify-center">
        <p className="text-sm text-gray-500">No data available</p>
      </div>
    )
  }

  return (
    <div className="card p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Response Time</h3>
      <canvas ref={canvasRef} width={500} height={200} className="w-full h-48"></canvas>
    </div>
  )
}
