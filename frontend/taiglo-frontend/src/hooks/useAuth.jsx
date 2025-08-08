import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

const API_BASE_URL = 'http://localhost:3000/api'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar se há token salvo no localStorage
    const token = localStorage.getItem('taiglo_token')
    if (token) {
      // Verificar se o token é válido
      fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => {
        if (response.ok) {
          return response.json()
        }
        throw new Error('Token inválido')
      })
      .then(data => {
        setUser(data.user)
      })
      .catch(() => {
        localStorage.removeItem('taiglo_token')
      })
      .finally(() => {
        setLoading(false)
      })
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Erro no login')
      }

      const data = await response.json()
      localStorage.setItem('taiglo_token', data.access_token)
      setUser(data.user)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Erro no registro')
      }

      const data = await response.json()
      localStorage.setItem('taiglo_token', data.access_token)
      setUser(data.user)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const logout = () => {
    localStorage.removeItem('taiglo_token')
    setUser(null)
  }

  const updateProfile = async (profileData) => {
    try {
      const token = localStorage.getItem('taiglo_token')
      const response = await fetch(`${API_BASE_URL}/users/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profileData)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Erro ao atualizar perfil')
      }

      const data = await response.json()
      setUser(data.user)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateProfile
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}

