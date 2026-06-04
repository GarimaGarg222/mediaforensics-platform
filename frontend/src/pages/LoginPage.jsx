import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function LoginPage() {
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const [mode,     setMode]     = useState("login")
  const [email,    setEmail]    = useState("")
  const [password, setPassword] = useState("")
  const [name,     setName]     = useState("")
  const [error,    setError]    = useState("")
  const [loading,  setLoading]  = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      if (mode === "login") {
        await login(email, password)
      } else {
        await register(email, password, name)
      }
      navigate("/")
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-4xl mb-3">🛡</div>
          <div className="font-display text-2xl font-bold text-surface-50">MediaForensics</div>
          <div className="text-surface-400 text-sm mt-1">AI Deepfake Detection Platform</div>
        </div>

        <div className="card p-6">
          {/* Mode toggle */}
          <div className="flex bg-surface-800 rounded-xl p-1 mb-6">
            {["login", "register"].map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
                  mode === m
                    ? "bg-surface-700 text-surface-100"
                    : "text-surface-500 hover:text-surface-300"
                }`}
              >
                {m === "login" ? "Sign In" : "Register"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "register" && (
              <div>
                <label className="text-xs text-surface-400 mb-1.5 block">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Garima Garg"
                  className="w-full bg-surface-800 border border-surface-700 rounded-xl px-3 py-2.5 text-sm text-surface-100 placeholder-surface-600 focus:outline-none focus:border-brand-500 transition-colors"
                />
              </div>
            )}

            <div>
              <label className="text-xs text-surface-400 mb-1.5 block">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full bg-surface-800 border border-surface-700 rounded-xl px-3 py-2.5 text-sm text-surface-100 placeholder-surface-600 focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="text-xs text-surface-400 mb-1.5 block">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full bg-surface-800 border border-surface-700 rounded-xl px-3 py-2.5 text-sm text-surface-100 placeholder-surface-600 focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            {error && (
              <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center py-2.5"
            >
              {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>
        </div>

        <div className="text-center mt-4 text-xs text-surface-600">
          Continue without account → <Link to="/" className="text-brand-400 hover:underline">Skip for now</Link>
        </div>
      </div>
    </div>
  )
}
