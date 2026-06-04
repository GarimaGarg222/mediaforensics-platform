import axios from "axios"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

const client = axios.create({
  baseURL: API_URL,
  timeout: 30000,
})

// Attach JWT token to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401 globally
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token")
      localStorage.removeItem("user")
    }
    return Promise.reject(err)
  }
)

export const api = {
  // Auth
  register: (data)      => client.post("/api/auth/register", data),
  login:    (data)      => client.post("/api/auth/login", data),

  // Analysis
  analyze:  (formData)  => client.post("/api/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }),
  getResult: (jobId)    => client.get(`/api/results/${jobId}`),

  // History
  getHistory: (params)  => client.get("/api/history", { params }),

  // Reports
  downloadReport: (jobId) => client.get(`/api/report/${jobId}/pdf`, {
    responseType: "blob",
  }),
}

export default client
