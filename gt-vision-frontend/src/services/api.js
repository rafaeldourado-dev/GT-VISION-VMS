
const API_BASE_URL = 'http://localhost:8000'

// Função para obter o token do localStorage
const getToken = () => localStorage.getItem('access_token')

// Função para remover o token e redirecionar para login
const handleUnauthorized = () => {
  localStorage.removeItem('access_token')
  window.location.href = '/login'
}

// Função base para fazer requisições
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  const token = getToken()
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  }

  try {
    console.log(`Fazendo requisição para: ${url}`)
    const response = await fetch(url, config)
    
    // Interceptar 401 Unauthorized
    if (response.status === 401) {
      handleUnauthorized()
      throw new Error('Não autorizado')
    }
    
    if (!response.ok) {
      console.error(`Erro na resposta: ${response.status} - ${response.statusText}`)
      throw new Error(`Erro ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    console.log('Resposta recebida:', data)
    return data
  } catch (error) {
    console.error('Erro na requisição:', error)
    throw error
  }
}

// Serviços de autenticação
export const authService = {
  login: async (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/token`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      throw new Error('Credenciais inválidas')
    }
    
    return await response.json()
  }
}

// Serviços do dashboard
export const dashboardService = {
  getStats: () => apiRequest('/api/v1/dashboard/stats/')
}

// Serviços de câmeras
export const camerasService = {
  getAll: () => apiRequest('/api/v1/cameras/'),
  create: (cameraData) => apiRequest('/api/v1/cameras/', {
    method: 'POST',
    body: JSON.stringify(cameraData),
  }),
  delete: (cameraId) => apiRequest(`/api/v1/cameras/${cameraId}`, {
    method: 'DELETE',
  }),
  getStreamUrl: (cameraId) => `${API_BASE_URL}/api/v1/cameras/${cameraId}/stream`
}

// Serviços de avistamentos
export const sightingsService = {
  getAll: () => apiRequest('/api/v1/sightings/')
}

// Serviços de tickets
export const ticketsService = {
  getAll: () => apiRequest('/api/v1/tickets/'),
  create: (ticketData) => apiRequest('/api/v1/tickets/', {
    method: 'POST',
    body: JSON.stringify(ticketData),
  })
}
