import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiApi } from '../api/apiApi'
import { HttpMethod } from '../types/api'

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

      // Map form field names to API field names
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
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Add New API</h1>
        <p className="text-gray-500">Configure a new API endpoint to monitor</p>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="input mt-1"
              placeholder="My API"
            />
          </div>

          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700">
              URL
            </label>
            <input
              type="url"
              id="url"
              name="url"
              value={formData.url}
              onChange={handleChange}
              required
              className="input mt-1"
              placeholder="https://api.example.com/endpoint"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="method" className="block text-sm font-medium text-gray-700">
                Method
              </label>
              <select
                id="method"
                name="method"
                value={formData.method}
                onChange={handleChange}
                className="input mt-1"
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
                <option value="PATCH">PATCH</option>
              </select>
            </div>

            <div>
              <label htmlFor="expected_status_code" className="block text-sm font-medium text-gray-700">
                Expected Status
              </label>
              <input
                type="number"
                id="expected_status_code"
                name="expected_status_code"
                value={formData.expected_status_code}
                onChange={handleChange}
                required
                className="input mt-1"
                min="100"
                max="599"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="interval_seconds" className="block text-sm font-medium text-gray-700">
                Check Interval (seconds)
              </label>
              <input
                type="number"
                id="interval_seconds"
                name="interval_seconds"
                value={formData.interval_seconds}
                onChange={handleChange}
                required
                className="input mt-1"
                min="10"
              />
            </div>

            <div>
              <label htmlFor="timeout_seconds" className="block text-sm font-medium text-gray-700">
                Timeout (seconds)
              </label>
              <input
                type="number"
                id="timeout_seconds"
                name="timeout_seconds"
                value={formData.timeout_seconds}
                onChange={handleChange}
                required
                className="input mt-1"
                min="1"
                max="300"
              />
            </div>
          </div>

          <div>
            <label htmlFor="headers" className="block text-sm font-medium text-gray-700">
              Headers (JSON)
            </label>
            <textarea
              id="headers"
              name="headers"
              value={formData.headers}
              onChange={handleChange}
              className="input mt-1"
              rows={3}
              placeholder='{"Authorization": "Bearer token"}'
            />
            <p className="mt-1 text-xs text-gray-500">Optional. Enter as valid JSON object.</p>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
            >
              {isSubmitting ? 'Creating...' : 'Create API'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
