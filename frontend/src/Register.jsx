import React, { useState } from 'react';
import { Mail, Lock, AlertCircle, UserPlus, User } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

export default function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [regError, setRegError] = useState('');
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

  const handleRegister = async (e) => {
    e.preventDefault();
    if (emailError) return;

    setIsLoading(true);
    setRegError('');

    try {
      await axios.post('https://resumeai-b934.onrender.com/auth/register', {
        name: name,
        email: email,
        password: password
      });
      
      navigate('/');
    } catch (error) {
      setRegError(error.response?.data?.detail || "Registration failed. Try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-slate-50 to-slate-200 flex items-center justify-center p-4">
      
      <div className="bg-white p-8 rounded-2xl shadow-xl shadow-indigo-900/5 border border-slate-100 w-full max-w-md">
        
        <div className="flex flex-col items-center mb-8">
          <div className="bg-indigo-600 p-3 rounded-full mb-4 shadow-md shadow-indigo-600/20">
            <UserPlus className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800">HR Registration</h1>
        </div>

        {regError && (
          <div className="mb-6 p-3 bg-red-50 text-red-600 rounded-lg flex items-center justify-center gap-2 text-sm font-medium">
            <AlertCircle className="h-4 w-4" />
            {regError}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-5">
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              {/* 🔴 Removed bg-white, changed to bg-slate-50 */}
              <input 
                type="text" 
                required 
                value={name} 
                onChange={(e) => setName(e.target.value)} 
                placeholder="Enter your name"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors" 
              />
            </div>
          </div>

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
                className={`w-full pl-10 pr-4 py-2.5 bg-slate-50 border rounded-lg focus:outline-none transition-colors ${emailError ? 'border-red-400 focus:ring-2 focus:ring-red-500' : 'border-slate-200 focus:ring-2 focus:ring-indigo-500'}`} 
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
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors" 
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isLoading || emailError !== ''} 
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold py-3 rounded-lg mt-4 shadow-lg shadow-indigo-600/30 transition-all transform hover:-translate-y-0.5"
          >
            {isLoading ? 'Registering...' : 'Create Account'}
          </button>

        </form>

        <div className="mt-6 text-center text-sm text-slate-600">
          Already have an account? <Link to="/" className="text-indigo-600 font-semibold hover:underline">Login here</Link>
        </div>

      </div>
    </div>
  );
}