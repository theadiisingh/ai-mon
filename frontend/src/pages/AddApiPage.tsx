import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiApi } from '../api/apiApi'
import { HttpMethod } from '../types/api'
import { motion } from 'framer-motion'
import { ArrowLeft, Save } from 'lucide-react'

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
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="max-w-3xl mx-auto"
    >
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <button onClick={() => navigate('/dashboard')} className="flex items-center text-sm font-medium text-zinc-500 hover:text-zinc-900 transition-colors mb-2">
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold text-zinc-900 tracking-tight">Add New Endpoint</h1>
          <p className="text-zinc-500 mt-1">Configure a new API endpoint for active monitoring</p>
        </div>
      </div>

      <div className="card shadow-sm border-zinc-200/80">
        <div className="card-header bg-zinc-50/50">
          <h2 className="text-base font-semibold text-zinc-900">Endpoint Configuration</h2>
          <p className="text-sm text-zinc-500">Provide the basic details and expected behavior for your API.</p>
        </div>
        <div className="p-6 md:p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-3"
              >
                <div className="mt-0.5">
                  <svg className="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="text-sm font-medium">{error}</div>
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
                className="input text-base py-2.5"
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
                className="input text-base py-2.5 font-mono text-sm"
                placeholder="https://api.example.com/v1/payments"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
              <div>
                <label htmlFor="method" className="label">HTTP Method</label>
                <select
                  id="method"
                  name="method"
                  value={formData.method}
                  onChange={handleChange}
                  className="input py-2.5"
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
                  className="input py-2.5"
                  min="100"
                  max="599"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
              <div>
                <label htmlFor="interval_seconds" className="label">Check Interval (seconds)</label>
                <div className="relative">
                  <input
                    type="number"
                    id="interval_seconds"
                    name="interval_seconds"
                    value={formData.interval_seconds}
                    onChange={handleChange}
                    required
                    className="input py-2.5 pr-12"
                    min="10"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                    <span className="text-zinc-400 text-sm">sec</span>
                  </div>
                </div>
              </div>

              <div>
                <label htmlFor="timeout_seconds" className="label">Timeout (seconds)</label>
                <div className="relative">
                  <input
                    type="number"
                    id="timeout_seconds"
                    name="timeout_seconds"
                    value={formData.timeout_seconds}
                    onChange={handleChange}
                    required
                    className="input py-2.5 pr-12"
                    min="1"
                    max="300"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                    <span className="text-zinc-400 text-sm">sec</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <label htmlFor="headers" className="label">Headers (JSON)</label>
              <textarea
                id="headers"
                name="headers"
                value={formData.headers}
                onChange={handleChange}
                className="input py-3 font-mono text-sm leading-relaxed"
                rows={4}
                placeholder='{
  "Authorization": "Bearer token",
  "Content-Type": "application/json"
}'
              />
              <p className="mt-2 text-xs text-zinc-500">Optional. Enter headers as a valid JSON string map.</p>
            </div>

            <div className="flex justify-end space-x-3 pt-6 border-t border-zinc-100 mt-8">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="btn btn-secondary px-6"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary px-6 flex items-center shadow-sm"
              >
                {isSubmitting ? (
                  <div className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating...
                  </div>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
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
