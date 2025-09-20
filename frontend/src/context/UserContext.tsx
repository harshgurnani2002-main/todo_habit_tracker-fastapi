import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../utils/api';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  is_admin: boolean;
  role: string;
  profile_picture: string | null;
  token?: string;
}

interface UserContextType {
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isVerifying: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isVerifying, setIsVerifying] = useState(true);

  useEffect(() => {
    const verifyStoredUser = async () => {
      setIsVerifying(true);
      try {
        // Check if user is already logged in (from localStorage or session)
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          const parsedUser = JSON.parse(storedUser);
          if (parsedUser.token) {
            // Verify token with backend
            const userData = await authAPI.getCurrentUser(parsedUser.token);
            setUser({ ...userData, token: parsedUser.token });
          } else {
            // Invalid stored user data, clear it
            localStorage.removeItem('user');
          }
        }
      } catch (e) {
        console.error('Failed to verify stored user data', e);
        // Token is invalid, clear stored user
        localStorage.removeItem('user');
        setUser(null);
      } finally {
        setIsVerifying(false);
      }
    };

    verifyStoredUser();
  }, []);

  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const isAuthenticated = !!user;

  return (
    <UserContext.Provider value={{ user, login, logout, isAuthenticated, isVerifying }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};