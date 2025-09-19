import React, { useState } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface VerifyOTPProps {
  email: string;
  onBack: () => void;
  flow: 'login' | 'signup';
}

export const VerifyOTP: React.FC<VerifyOTPProps> = ({ email, onBack, flow }) => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resending, setResending] = useState(false);
  const { verifyOTP, verifyOTPSignup, resendOTP } = useAuth();
  const navigate = useNavigate();

  const handleChange = (element: HTMLInputElement, index: number) => {
    if (isNaN(parseInt(element.value)) && element.value !== '') return;

    const newOtp = [...otp];
    newOtp[index] = element.value;
    setOtp(newOtp);

    // Move to next input field if current field is filled
    if (element.value !== '' && index < 5) {
      const nextElement = element.nextElementSibling as HTMLInputElement;
      if (nextElement) {
        nextElement.focus();
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    // Move to previous input field on backspace
    if (e.key === 'Backspace' && index > 0 && otp[index] === '') {
      const prevElement = e.currentTarget.previousElementSibling as HTMLInputElement;
      if (prevElement) {
        prevElement.focus();
      }
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text/plain').slice(0, 6);
    const newOtp = [...otp];
    
    for (let i = 0; i < pastedData.length; i++) {
      if (!isNaN(parseInt(pastedData[i]))) {
        newOtp[i] = pastedData[i];
      }
    }
    
    setOtp(newOtp);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const otpCode = otp.join('');
    
    if (otpCode.length !== 6) {
      setError('Please enter a 6-digit OTP code');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      if (flow === 'login') {
        await verifyOTP(email, otpCode);
        navigate('/');
      } else {
        await verifyOTPSignup(email, otpCode);
        navigate('/login');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setResending(true);
    setError(null);
    setOtp(['', '', '', '', '', '']); // Clear OTP fields
    
    try {
      await resendOTP(email);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resend OTP');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Verify Your Email
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            We've sent a 6-digit code to {email}
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 dark:bg-red-900 p-4">
              <div className="text-sm text-red-700 dark:text-red-200">
                {error}
              </div>
            </div>
          )}
          
          <div>
            <label htmlFor="otp" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Enter OTP Code
            </label>
            <div className="flex justify-center space-x-3">
              {otp.map((data, index) => (
                <input
                  key={index}
                  type="text"
                  maxLength={1}
                  value={data}
                  onChange={(e) => handleChange(e.target, index)}
                  onKeyDown={(e) => handleKeyDown(e, index)}
                  onPaste={handlePaste}
                  className="w-12 h-12 text-center text-2xl font-bold border-2 border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                  disabled={loading}
                />
              ))}
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-teal-600 hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 disabled:opacity-50"
              disabled={loading || otp.some(digit => digit === '')}
            >
              {loading ? 'Verifying...' : 'Verify Email'}
            </button>
          </div>
        </form>
        
        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Didn't receive the code?{' '}
            <button
              onClick={handleResendOTP}
              className="font-medium text-teal-600 hover:text-teal-500 dark:text-teal-400 dark:hover:text-teal-300"
              disabled={resending}
            >
              {resending ? 'Resending...' : 'Resend OTP'}
            </button>
          </p>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Wrong email address?{' '}
            <button
              onClick={onBack}
              className="font-medium text-teal-600 hover:text-teal-500 dark:text-teal-400 dark:hover:text-teal-300"
            >
              Back
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

const VerifyOTPPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const email = location.state?.email as string | undefined;

  if (!email) {
    return <Navigate to="/login" replace />;
  }

  return <VerifyOTP email={email} onBack={() => navigate(-1)} flow="login" />;
};

export default VerifyOTPPage;
