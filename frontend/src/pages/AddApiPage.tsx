import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiApi } from '../api/apiApi'
import { HttpMethod } from '../types/api'
import { motion } from 'framer-motion'
import { ArrowLeft, Save, AlertCircle } from 'lucide-react'

export default function AddApiPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    method: 'GET' as HttpMethod,
    interval_seconds: 60,
    timeout_seconds: 30,
    expected_status_code: 200,
    headers: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'interval_seconds' || name === 'timeout_seconds' || name === 'expected_status_code'
        ? parseInt(value) || 0
        : name === 'method' ? value as HttpMethod
          : value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')

    try {
      const headers = formData.headers
        ? JSON.parse(formData.headers)
        : {}

      const apiData = {
        name: formData.name,
        url: formData.url,
        method: formData.method as HttpMethod,
        headers: headers,
        expected_status_code: formData.expected_status_code,
        timeout_seconds: formData.timeout_seconds,
        interval_seconds: formData.interval_seconds,
      }

      await apiApi.create(apiData)

      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create API endpoint')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.14 }}
      className="max-w-2xl mx-auto"
    >
      <div className="mb-5">
        <button 
          onClick={() => navigate('/dashboard')} 
          className="flex items-center text-xs font-medium text-content-tertiary hover:text-content-secondary transition-colors mb-3"
        >
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> 
          Back to Dashboard
        </button>
        <h1 className="text-lg font-semibold text-content-primary">Add New Endpoint</h1>
        <p className="text-xs text-content-tertiary mt-1">Configure a new API endpoint for active monitoring</p>
      </div>

      <div className="card">
        <div className="px-4 py-3.5 border-b border-border/30">
          <h2 className="text-sm font-medium text-content-primary">Endpoint Configuration</h2>
          <p className="text-xs text-content-tertiary mt-0.5">Provide the basic details for your API.</p>
        </div>
        <div className="p-5">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="p-2.5 bg-danger/5 border border-danger/10 text-danger text-xs flex items-start gap-2 rounded"
              >
                <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                <div className="font-medium">{error}</div>
              </motion.div>
            )}

            <div>
              <label htmlFor="name" className="label">Endpoint Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="input"
                placeholder="e.g. Production Payment API"
              />
            </div>

            <div>
              <label htmlFor="url" className="label">Target URL</label>
              <input
                type="url"
                id="url"
                name="url"
                value={formData.url}
                onChange={handleChange}
                required
                className="input font-mono-nums text-xs"
                placeholder="https://api.example.com/v1/payments"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="method" className="label">HTTP Method</label>
                <select
                  id="method"
                  name="method"
                  value={formData.method}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="DELETE">DELETE</option>
                  <option value="PATCH">PATCH</option>
                </select>
              </div>

              <div>
                <label htmlFor="expected_status_code" className="label">Expected Status Code</label>
                <input
                  type="number"
                  id="expected_status_code"
                  name="expected_status_code"
                  value={formData.expected_status_code}
                  onChange={handleChange}
                  required
                  className="input font-mono-nums"
                  min="100"
                  max="599"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="interval_seconds" className="label">Check Interval</label>
                <div className="relative">
                  <input
                    type="number"
                    id="interval_seconds"
                    name="interval_seconds"
                    value={formData.interval_seconds}
                    onChange={handleChange}
                    required
                    className="input pr-9 font-mono-nums"
                    min="10"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                    <span className="text-content-tertiary text-xs">sec</span>
                  </div>
                </div>
              </div>

              <div>
                <label htmlFor="timeout_seconds" className="label">Timeout</label>
                <div className="relative">
                  <input
                    type="number"
                    id="timeout_seconds"
                    name="timeout_seconds"
                    value={formData.timeout_seconds}
                    onChange={handleChange}
                    required
                    className="input pr-9 font-mono-nums"
                    min="1"
                    max="300"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                    <span className="text-content-tertiary text-xs">sec</span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="headers" className="label">Headers (JSON)</label>
              <textarea
                id="headers"
                name="headers"
                value={formData.headers}
                onChange={handleChange}
                className="input font-mono-nums text-xs leading-relaxed"
                rows={3}
                placeholder='{ "Authorization": "Bearer token" }'
              />
              <p className="mt-1.5 text-[10px] text-content-tertiary">Optional. Enter headers as valid JSON.</p>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-border/30 mt-4">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="btn btn-secondary px-4 text-xs"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary px-4 flex items-center gap-2 text-xs"
              >
                {isSubmitting ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-3.5 w-3.5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating...
                  </span>
                ) : (
                  <>
                    <Save className="w-3.5 h-3.5" />
                    Save Endpoint
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </motion.div>
  )
}

