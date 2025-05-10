import { useState, useEffect } from 'react'
import './App.css'
import Layout from './Components/Layout/Layout'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './Pages/HomePage/HomePage'

function App() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.text();
        setMessage(data);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching home data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHomeData();
  }, []);

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </Layout>
      <div className="app-container">
        <h1>Backend Connection Test</h1>
        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p>Error: {error}</p>
        ) : (
          <div>
            <h2>Response from backend:</h2>
            <p>{message}</p>
          </div>
        )}
      </div>
    </Router>
  )
}

export default App



