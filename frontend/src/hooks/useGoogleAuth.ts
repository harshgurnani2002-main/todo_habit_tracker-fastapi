import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin, CodeResponse } from '@react-oauth/google';
import { useUser } from '../context/UserContext';
import { authAPI } from '../utils/api';

interface GoogleAuthCodeResponse extends CodeResponse {}

export const useGoogleAuth = () => {
  const [user, setUser] = useState<GoogleAuthCodeResponse | null>(null);
  const [profile, setProfile] = useState<any | null>(null);
  const { login } = useUser();
  const navigate = useNavigate();

  const loginHandler = useGoogleLogin({
    onSuccess: (codeResponse) => {
      setUser(codeResponse);
      console.log("Google login success:", codeResponse);
    },
    onError: (error) => console.log('Login Failed:', error),
    flow: 'auth-code',
  });

  useEffect(() => {
    const handleGoogleAuth = async () => {
      if (user) {
        try {
          // Send the authorization code to your backend
          const data = await authAPI.googleLogin(user.code);
          console.log("Backend auth response:", data);
          
          // Get user details after login
          const userData = await authAPI.getCurrentUser(data.access_token);
          
          // Set user context and store in localStorage
          login({ ...userData, token: data.access_token });
          
          // Redirect to dashboard
          navigate('/');
        } catch (error) {
          console.error("Backend authentication failed:", error);
        }
      }
    };

    handleGoogleAuth();
  }, [user, login, navigate]);

  return { login: loginHandler, profile };
};