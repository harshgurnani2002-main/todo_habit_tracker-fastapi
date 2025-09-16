import { useState } from 'react';
import { useUser } from '../context/UserContext';
import { authAPI } from '../utils/api';

export const useAuth = () => {
  const { login, logout } = useUser();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (email: string, password: string, otp_code: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Always use OTP code for login
      const data = await authAPI.login(email, password, otp_code);
      // Get user details after login
      const userData = await authAPI.getCurrentUser(data.access_token);
      login({ ...userData, token: data.access_token });
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (email: string, username: string, full_name: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.register(email, username, full_name, password);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  const sendOTP = async (email: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.sendOTP(email);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send OTP');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const verifyOTP = async (email: string, otp_code: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.verifyOTP(email, otp_code);
      // Get user details after OTP verification
      const userData = await authAPI.getCurrentUser(data.access_token);
      login({ ...userData, token: data.access_token });
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify OTP');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async (code: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await authAPI.googleLogin(code);
      const userData = await authAPI.getCurrentUser(data.access_token);
      login({ ...userData, token: data.access_token });
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Google login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    handleLogin,
    handleRegister,
    handleLogout,
    sendOTP,
    verifyOTP,
    handleGoogleLogin
  };
};