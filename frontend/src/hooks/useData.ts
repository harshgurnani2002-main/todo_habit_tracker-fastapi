import { useState, useEffect, useCallback } from 'react';
import { todosAPI, habitsAPI, pomodoroAPI, dashboardAPI } from '../utils/api';
import { DashboardStats } from '../types/dashboard';

// Hook for managing todos
export const useTodos = (token: string | null, filters?: { status?: string; priority?: string; search?: string; category?: string }) => {
  const [todos, setTodos] = useState<any[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTodos = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      // Prepare filter parameters
      const params: Record<string, any> = {};
      
      if (filters?.status) {
        params.completed = filters.status === 'completed' ? true : filters.status === 'pending' ? false : undefined;
      }
      
      if (filters?.priority) {
        params.priority = filters.priority;
      }
      
      if (filters?.search) {
        params.search = filters.search;
      }
      
      if (filters?.category) {
        params.category = filters.category;
      }
      
      const data = await todosAPI.getTodos(token, params);
      setTodos(data);
      
      // Extract unique categories
      const uniqueCategories = Array.from(new Set(data.map((todo: any) => todo.category).filter(Boolean))) as string[];
      setCategories(uniqueCategories);
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch todos');
    } finally {
      setLoading(false);
    }
  }, [token, filters]);

  const createTodo = async (todoData: any) => {
    if (!token) return;
    
    try {
      const newTodo = await todosAPI.createTodo(token, todoData);
      setTodos(prev => [newTodo, ...prev]);
      
      // Add category to categories list if it's new
      if (todoData.category && !categories.includes(todoData.category)) {
        setCategories(prev => [...prev, todoData.category]);
      }
      
      return newTodo;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create todo');
      // Re-throw the error so it can be handled by the calling function
      throw err;
    }
  };

  const updateTodo = async (id: number, todoData: any) => {
    if (!token) return;
    
    try {
      console.log('Updating todo:', id, todoData);
      const updatedTodo = await todosAPI.updateTodo(token, id, todoData);
      console.log('Todo updated successfully:', updatedTodo);
      setTodos(prev => prev.map(todo => todo.id === id ? { ...todo, ...updatedTodo, id: id } : todo));
      return updatedTodo;
    } catch (err) {
      console.error('Error updating todo:', err);
      setError(err instanceof Error ? err.message : 'Failed to update todo');
      // Re-throw the error so it can be handled by the calling function
      throw err;
    }
  };

  const deleteTodo = async (id: number) => {
    if (!token) return;
    
    try {
      // Get the todo before deleting to check its category
      const todoToDelete = todos.find(todo => todo.id === id);
      
      await todosAPI.deleteTodo(token, id);
      setTodos(prev => prev.filter(todo => todo.id !== id));
      
      // Remove category from categories list if no other todos use it
      if (todoToDelete?.category) {
        const remainingTodosWithCategory = todos.filter(todo => todo.id !== id && todo.category === todoToDelete.category);
        if (remainingTodosWithCategory.length === 0) {
          setCategories(prev => prev.filter(cat => cat !== todoToDelete.category));
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete todo');
      // Re-throw the error so it can be handled by the calling function
      throw err;
    }
  };

  useEffect(() => {
    fetchTodos();
  }, [token, fetchTodos]);

  return { todos, categories, loading, error, fetchTodos, createTodo, updateTodo, deleteTodo };
};

// Hook for managing habits
export const useHabits = (token: string | null, filters?: { frequency?: string; search?: string }) => {
  const [habits, setHabits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHabits = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      // Prepare filter parameters
      const params: Record<string, any> = {};
      
      if (filters?.frequency) {
        params.frequency = filters.frequency;
      }
      
      if (filters?.search) {
        params.search = filters.search;
      }
      
      const data = await habitsAPI.getHabits(token, params);
      setHabits(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch habits');
    } finally {
      setLoading(false);
    }
  }, [token, filters]);

  const createHabit = async (habitData: any) => {
    if (!token) return;
    
    try {
      const newHabit = await habitsAPI.createHabit(token, habitData);
      setHabits(prev => [newHabit, ...prev]);
      return newHabit;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create habit');
      throw err;
    }
  };

  const updateHabit = async (id: number, habitData: any) => {
    if (!token) return;
    
    try {
      const updatedHabit = await habitsAPI.updateHabit(token, id, habitData);
      setHabits(prev => prev.map(habit => habit.id === id ? updatedHabit : habit));
      return updatedHabit;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update habit');
      throw err;
    }
  };

  const deleteHabit = async (id: number) => {
    if (!token) return;
    
    try {
      await habitsAPI.deleteHabit(token, id);
      setHabits(prev => prev.filter(habit => habit.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete habit');
      throw err;
    }
  };

  const createHabitEntry = async (habitId: number, entryData: any) => {
    if (!token) return;
    
    try {
      const newEntry = await habitsAPI.createHabitEntry(token, habitId, entryData);
      // Update the habit with the new entry
      setHabits(prev => prev.map(h => {
        if (h.id === habitId) {
          return {
            ...h,
            entries: [...(h.entries || []), newEntry]
          };
        }
        return h;
      }));
      return newEntry;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create habit entry');
      throw err;
    }
  };

  useEffect(() => {
    fetchHabits();
  }, [token, fetchHabits]);

  return { habits, loading, error, fetchHabits, createHabit, updateHabit, deleteHabit, createHabitEntry };
};

// Hook for managing Pomodoro sessions
export const usePomodoroSessions = (token: string | null) => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      const data = await pomodoroAPI.getSessions(token);
      setSessions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
    } finally {
      setLoading(false);
    }
  }, [token]);

  const createSession = async (sessionData: any) => {
    if (!token) return;
    
    try {
      const newSession = await pomodoroAPI.createSession(token, sessionData);
      setSessions(prev => [newSession, ...prev]);
      return newSession;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
      throw err;
    }
  };

  const updateSession = async (id: number, sessionData: any) => {
    if (!token) return;
    
    try {
      const updatedSession = await pomodoroAPI.updateSession(token, id, sessionData);
      setSessions(prev => prev.map(session => session.id === id ? updatedSession : session));
      return updatedSession;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update session');
      throw err;
    }
  };

  const deleteSession = async (id: number) => {
    if (!token) return;
    
    try {
      await pomodoroAPI.deleteSession(token, id);
      setSessions(prev => prev.filter(session => session.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete session');
      throw err;
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [token, fetchSessions]);

  return { sessions, loading, error, fetchSessions, createSession, updateSession, deleteSession };
};

// Hook for dashboard stats
export const useDashboardStats = (token: string | null) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      const data = await dashboardAPI.getStats(token);
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard stats');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchStats();
  }, [token, fetchStats]);

  return { stats, loading, error, fetchStats };
};