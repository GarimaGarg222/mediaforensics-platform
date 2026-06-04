import { createContext, useContext, useState, useEffect } from "react"
import { api } from "../api/client"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) setUser(JSON.parse(stored))
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const res = await api.login({ email, password })
    const { access_token, user: userData } = res.data
    localStorage.setItem("token", access_token)
    localStorage.setItem("user", JSON.stringify(userData))
    setUser(userData)
    return userData
  }

  const register = async (email, password, full_name) => {
    await api.register({ email, password, full_name })
    return login(email, password)
  }

  const logout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
