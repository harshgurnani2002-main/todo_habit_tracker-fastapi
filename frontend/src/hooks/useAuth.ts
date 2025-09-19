import { useState } from 'react';
import { useUser } from '../context/UserContext';
import { authAPI } from '../utils/api';

export const useAuth = () => {
  const { login, logout } = useUser();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.login(email, password);
      // Get user details after login
      const userData = await authAPI.getCurrentUser(data.access_token);
      login({ ...userData, token: data.access_token });
      return data;
    } catch (err) {
      if (err instanceof Error && err.message.includes('Please verify your email. OTP sent.')) {
        // Don't set an error, let the component handle the navigation
      } else {
        setError(err instanceof Error ? err.message : 'Login failed');
      }
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



  const resendOTP = async (email: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.resendOTP(email);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resend OTP');
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

  const verifyOTPSignup = async (email: string, otp_code: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.verifyOTPSignup(email, otp_code);
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

  const forgotPassword = async (email: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.forgotPassword(email);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send reset link');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (token: string, new_password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.resetPassword(token, new_password);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset password');
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
    resendOTP,
    verifyOTP,
    verifyOTPSignup,
    handleGoogleLogin,
    forgotPassword,
    resetPassword,
  };
};