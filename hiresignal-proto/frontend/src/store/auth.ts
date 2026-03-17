import { create } from 'zustand'

interface User {
  id: string
  email: string
  full_name?: string
  role: string
  tenant_id: string
}

interface AuthStore {
  token: string | null
  user: User | null
  setToken: (token: string) => void
  setUser: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: localStorage.getItem('token'),
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  
  setToken: (token) => {
    localStorage.setItem('token', token)
    set({ token })
  },
  
  setUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user))
    set({ user })
  },
  
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ token: null, user: null })
  },
}))
