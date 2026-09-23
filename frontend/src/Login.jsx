import React, { useState } from 'react';
import { Mail, Lock, UserCircle, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function Login() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // FastAPI OAuth2 Login form data setup
        const params = new URLSearchParams();
        params.append('username', email); // FastAPI maps email to 'username'
        params.append('password', password);

        const response = await axios.post('http://localhost:8000/auth/login', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        
        localStorage.setItem('hr_token', response.data.access_token);
        navigate('/dashboard'); 
      } else {
        // Real Backend Register API
        await axios.post('http://localhost:8000/auth/register', {
          name,
          email,
          password
        });
        alert("HR Registration Successful! Please login.");
        setIsLogin(true); // Switch to login view
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Connection error. Is FastAPI running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 w-full max-w-md">
        
        <div className="flex flex-col items-center mb-6">
          <div className="bg-blue-600 p-3 rounded-full mb-4">
            <UserCircle className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-slate-800">
            {isLogin ? 'HR Login' : 'Register HR'}
          </h2>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4 text-center">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input 
                  type="text" required value={name} onChange={(e) => setName(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-slate-50" 
                  placeholder="Jai Gengatharan Senthilmani" 
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email ID</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input 
                type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-slate-50" 
                placeholder="hr@company.com" 
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input 
                type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-slate-50" 
                placeholder="••••••••" 
              />
            </div>
          </div>

          <button 
            type="submit" disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors mt-4 disabled:bg-blue-400"
          >
            {loading ? 'Processing...' : (isLogin ? 'Secure Login' : 'Create Account')}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-600">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            type="button" 
            onClick={() => { setIsLogin(!isLogin); setError(''); }} 
            className="text-blue-600 font-semibold hover:underline"
          >
            {isLogin ? 'Register here' : 'Login here'}
          </button>
        </div>

      </div>
    </div>
  );
}