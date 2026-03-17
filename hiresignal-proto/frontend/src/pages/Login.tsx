import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../api/client'
import { useAuthStore } from '../store/auth'

export default function Login() {
  const [email, setEmail] = useState('hr@acme.com')
  const [password, setPassword] = useState('demo1234')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const navigate = useNavigate()
  const { setToken, setUser } = useAuthStore()

  async function handleLogin() {
    setError('')
    setLoading(true)

    try {
      const response = await authAPI.login(email, password)
      const { access_token } = response.data

      setToken(access_token)
      
      // Get user info
      const userResponse = await authAPI.getMe()
      setUser(userResponse.data)

      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-center mb-2">HireSignal</h1>
        <p className="text-center text-gray-600 mb-6">Resume Screening Platform</p>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-semibold mb-2">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="hr@acme.com"
          />
        </div>

        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-semibold mb-2">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="demo1234"
          />
        </div>

        <button
          onClick={handleLogin}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg disabled:opacity-50 transition"
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
          <p className="text-sm text-gray-600 mb-2 font-semibold">Demo Credentials:</p>
          <p className="text-sm text-gray-600">📧 hr@acme.com</p>
          <p className="text-sm text-gray-600">🔑 demo1234</p>
          <p className="text-sm text-gray-600 mt-2">Or try hr@startup.com</p>
        </div>
      </div>
    </div>
  )
}
