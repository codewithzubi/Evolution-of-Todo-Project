'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signIn } from '../lib/auth';

type AuthMode = 'login' | 'register';

interface AuthFormProps {
  mode?: AuthMode;
}

const AuthForm: React.FC<AuthFormProps> = ({ mode: initialMode = 'login' }) => {
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // In a real implementation, we would call our backend API
      // For now, we'll simulate the auth process
      if (mode === 'login') {
        // Simulate login API call
        console.log('Login attempt with:', { email, password });
        // Here you would typically call your backend login endpoint
        // and store the JWT token
        setTimeout(() => {
          console.log('Login successful!');
          router.push('/dashboard');
          setLoading(false);
        }, 1000);
      } else {
        // Simulate register API call
        console.log('Register attempt with:', { email, password, firstName, lastName });
        // Here you would typically call your backend register endpoint
        setTimeout(() => {
          console.log('Registration successful!');
          setMode('login');
          setLoading(false);
        }, 1000);
      }
    } catch (err) {
      setError('Authentication failed. Please try again.');
      setLoading(false);
      console.error('Auth error:', err);
    }
  };

  const toggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError(null);
  };

  return (
    <div className="w-full max-w-md">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          {mode === 'login' ? 'Welcome Back' : 'Create Account'}
        </h1>
        <p className="text-purple-200">
          {mode === 'login'
            ? 'Sign in to your account'
            : 'Join us to get started'}
        </p>
      </div>

      {error && (
        <div className="mb-6 p-3 bg-red-500/20 backdrop-blur-sm rounded-lg text-red-200 text-center">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {mode === 'register' && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-purple-200 mb-1">
                First Name
              </label>
              <input
                id="firstName"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full glass-input text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
                placeholder="John"
                required={mode === 'register'}
              />
            </div>
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-purple-200 mb-1">
                Last Name
              </label>
              <input
                id="lastName"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full glass-input text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
                placeholder="Doe"
                required={mode === 'register'}
              />
            </div>
          </div>
        )}

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-purple-200 mb-1">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full glass-input text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
            placeholder="you@example.com"
            required
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-purple-200 mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full glass-input text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-4 rounded-xl font-medium text-white transition-all duration-300 ${
            loading
              ? 'bg-purple-700 cursor-not-allowed'
              : 'glass-button hover:backdrop-blur-2xl hover:scale-105'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
              {mode === 'login' ? 'Signing in...' : 'Creating account...'}
            </span>
          ) : mode === 'login' ? (
            'Sign In'
          ) : (
            'Create Account'
          )}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-purple-200">
          {mode === 'login'
            ? "Don't have an account?"
            : "Already have an account?"}
          <button
            onClick={toggleMode}
            className="ml-1 text-purple-300 font-medium hover:underline focus:outline-none focus:ring-2 focus:ring-purple-400 rounded"
          >
            {mode === 'login' ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
};

export default AuthForm;