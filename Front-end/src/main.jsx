import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:5000'; // Set the base URL directly
axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.withCredentials = false; // Set to false for cross-origin requests

// Add request interceptor for authentication and debugging
axios.interceptors.request.use(
  config => {
    // Get the token from localStorage
    const token = localStorage.getItem('token');
    
    // If token exists, add it to the headers
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log(`Adding token to request: Bearer ${token.substring(0, 10)}...`);
      
      // Get user data from localStorage
      const userStr = localStorage.getItem('user');
      try {
        const userData = JSON.parse(userStr || '{}');
        console.log('User data for request:', userData);
        console.log('User role for request:', userData.role || userData.user_role);
      } catch (error) {
        console.error('Error parsing user data in interceptor:', error);
      }
    }
    
    console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`);
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
axios.interceptors.response.use(
  response => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  error => {
    console.error('Response error:', error);
    return Promise.reject(error);
  }
);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);


