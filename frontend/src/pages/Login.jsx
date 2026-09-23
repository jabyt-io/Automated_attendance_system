import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const navigate = useNavigate()

  const handleLogin = async () => {
    setError('')

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        {
          method: 'POST',
        }
      )

      const data = await response.json()

      if (data.success) {
        navigate('/dashboard')
      } else {
        setError(data.message)
      }

    } catch (error) {
      setError('Cannot connect to the backend')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sky-400 via-indigo-400 to-fuchsia-500 p-6">

      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl px-10 py-12">

        <div className="text-center mb-8">

          <div className="flex justify-center items-center gap-3 mb-4">

            <div className="w-10 h-10 bg-purple-700 text-white rounded-lg flex items-center justify-center font-bold text-xl">
              A
            </div>

            <h1 className="text-3xl font-bold text-purple-900">
              Login
            </h1>

          </div>

          <p className="text-gray-500 text-sm">
            Automated Student Attendance System
          </p>

        </div>

        <div className="mb-5">

          <label className="block text-sm font-semibold text-gray-600 mb-2">
            Username
          </label>

          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-5 py-4 rounded-2xl bg-gray-50 border border-gray-100 shadow-sm outline-none focus:ring-2 focus:ring-purple-400"
          />

        </div>

        <div className="mb-5">

          <label className="block text-sm font-semibold text-gray-600 mb-2">
            Password
          </label>

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-5 py-4 rounded-2xl bg-gray-50 border border-gray-100 shadow-sm outline-none focus:ring-2 focus:ring-purple-400"
          />

        </div>

        {error && (
          <p className="text-red-500 text-sm text-center mb-5">
            {error}
          </p>
        )}

        <button
          onClick={handleLogin}
          className="block mx-auto px-10 py-4 rounded-full bg-purple-600 text-white font-bold tracking-wide shadow-lg hover:bg-purple-700 hover:scale-105 transition"
        >
          LOGIN
        </button>

      </div>

    </div>
  )
}

export default Login