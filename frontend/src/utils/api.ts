// API base URL - in a real app, this would come from environment variables
const API_BASE_URL = 'http://localhost:8000';

// Helper function for API requests
export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (parseError) {
        // If we can't parse the error response, use the status text
        errorData = { detail: `HTTP error! status: ${response.status}` };
      }
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Authentication API functions
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return response.json();
  },
  
  register: async (email: string, username: string, full_name: string, password: string) => {
    const response = await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, full_name, password }),
    });
    return response.json();
  },
  
  getCurrentUser: async (token: string) => {
    const response = await apiRequest('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
  
  sendOTP: async (email: string) => {
    const response = await apiRequest('/auth/send-otp', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
    return response.json();
  },
  
  verifyOTP: async (email: string, otp_code: string) => {
    const response = await apiRequest('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ email, otp_code }),
    });
    return response.json();
  },

  googleLogin: async (code: string) => {
    const response = await apiRequest(`/auth/google/callback?code=${code}`, {
      method: 'GET',
    });
    return response.json();
  }
};

// Todos API functions
export const todosAPI = {
  getTodos: async (token: string, params?: Record<string, any>) => {
    const searchParams = new URLSearchParams(params);
    const response = await apiRequest(`/todos/?${searchParams.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
  
  createTodo: async (token: string, data: any) => {
    const response = await apiRequest('/todos/', {
      method: 'POST',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  updateTodo: async (token: string, id: number, data: any) => {
    console.log('API call - updateTodo:', id, data);
    const response = await apiRequest(`/todos/${id}`, {
      method: 'PUT',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    console.log('API response - updateTodo:', result);
    return result;
  },
  
  deleteTodo: async (token: string, id: number) => {
    const response = await apiRequest(`/todos/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.status === 204 ? null : response.json();
  }
};

// Habits API functions
export const habitsAPI = {
  getHabits: async (token: string, params?: Record<string, any>) => {
    const searchParams = new URLSearchParams(params);
    const response = await apiRequest(`/habits/?${searchParams.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
  
  createHabit: async (token: string, data: any) => {
    const response = await apiRequest('/habits/', {
      method: 'POST',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  updateHabit: async (token: string, id: number, data: any) => {
    const response = await apiRequest(`/habits/${id}`, {
      method: 'PUT',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  deleteHabit: async (token: string, id: number) => {
    const response = await apiRequest(`/habits/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
  
  getHabitAnalytics: async (token: string, id: number, days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('days', days.toString());
    
    const response = await apiRequest(`/habits/${id}/analytics?${params.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
  
  createHabitEntry: async (token: string, habitId: number, data: any) => {
    const response = await apiRequest(`/habits/${habitId}/entries`, {
      method: 'POST',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }
};

// Pomodoro API functions
export const pomodoroAPI = {
  getSessions: async (token: string, params?: Record<string, any>) => {
    const searchParams = new URLSearchParams(params);
    const response = await apiRequest(`/pomodoro/?${searchParams.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
  
  createSession: async (token: string, data: any) => {
    const response = await apiRequest('/pomodoro/', {
      method: 'POST',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  updateSession: async (token: string, id: number, data: any) => {
    const response = await apiRequest(`/pomodoro/${id}`, {
      method: 'PUT',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  
  deleteSession: async (token: string, id: number) => {
    const response = await apiRequest(`/pomodoro/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
  
  getAnalytics: async (token: string, days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('days', days.toString());
    
    const response = await apiRequest(`/pomodoro/analytics?${params.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  }
};

// Dashboard API functions
export const dashboardAPI = {
  getStats: async (token: string, params?: Record<string, any>) => {
    const searchParams = new URLSearchParams(params);
    const response = await apiRequest(`/dashboard/stats?${searchParams.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  }
};