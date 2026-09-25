import React, { useState } from 'react';
import { Mail, Lock, AlertCircle, User } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [loginError, setLoginError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    
    if (/[A-Z]/.test(value)) {
      setEmailError('Capital letters are not allowed in email.');
    } else {
      setEmailError('');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (emailError) return; 

    setIsLoading(true);
    setLoginError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('http://localhost:8000/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      localStorage.setItem('hr_token', response.data.access_token);
      navigate('/dashboard');
    } catch (error) {
      setLoginError(error.response?.data?.detail || "Invalid email or password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // 🔴 Premium Gradient Background
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-slate-50 to-slate-200 flex items-center justify-center p-4">
      
      {/* 🔴 Floating Card with Shadow */}
      <div className="bg-white p-8 rounded-2xl shadow-xl shadow-blue-900/5 border border-slate-100 w-full max-w-md">
        
        <div className="flex flex-col items-center mb-8">
          <div className="bg-blue-600 p-3 rounded-full mb-4 shadow-md shadow-blue-600/20">
            <User className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800">HR Login</h1>
        </div>

        {loginError && (
          <div className="mb-6 p-3 bg-red-50 text-red-600 rounded-lg flex items-center justify-center gap-2 text-sm font-medium">
            <AlertCircle className="h-4 w-4" />
            {loginError}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email ID</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input 
                type="text" 
                required 
                value={email} 
                onChange={handleEmailChange} 
                placeholder="Enter the email ID" 
                className={`w-full pl-10 pr-4 py-2.5 bg-slate-50/50 border rounded-lg focus:outline-none transition-colors bg-white ${emailError ? 'border-red-400 focus:ring-2 focus:ring-red-500' : 'border-slate-200 focus:ring-2 focus:ring-blue-500'}`} 
              />
            </div>
            {emailError && (
              <p className="text-red-500 text-xs mt-1.5 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />{emailError}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input 
                type="password" 
                required 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••••" 
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors bg-white" 
              />
            </div>
          </div>

          {/* 🔴 Button with hover animation and shadow */}
          <button 
            type="submit" 
            disabled={isLoading || emailError !== ''} 
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 rounded-lg mt-4 shadow-lg shadow-blue-600/30 transition-all transform hover:-translate-y-0.5"
          >
            {isLoading ? 'Logging in...' : 'Secure Login'}
          </button>

        </form>

        <div className="mt-6 text-center text-sm text-slate-600">
          Don't have an account? <Link to="/register" className="text-blue-600 font-semibold hover:underline">Register here</Link>
        </div>

      </div>
    </div>
  );
}