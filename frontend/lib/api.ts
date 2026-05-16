import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

// Optimized interceptor: Only attach token if it's already available in local storage/cookies
// to avoid slow async lookups on every single request.
api.interceptors.request.use((config) => {
  try {
    // We try to get the session from localStorage if available (Supabase standard)
    const storageKey = Object.keys(localStorage).find(key => key.includes('-auth-token'))
    if (storageKey) {
      const session = JSON.parse(localStorage.getItem(storageKey) || '{}')
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`
      }
    }
  } catch {}
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    // Removed automatic redirect to /login since we bypassed authentication
    return Promise.reject(error)
  }
)
