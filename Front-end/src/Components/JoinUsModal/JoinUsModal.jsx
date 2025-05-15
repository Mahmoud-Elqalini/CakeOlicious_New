import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiLogIn, FiUser, FiLock } from 'react-icons/fi';
import styles from './JoinUsModal.module.css';

const JoinUsModal = ({ isOpen, onClose }) => {
  const [showSignIn, setShowSignIn] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    pass_word: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  
  if (!isOpen) {
    return null;
  }
  
  const toggleView = (e) => {
    if (e) e.preventDefault();
    setShowSignIn(!showSignIn);
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/login', formData);
      
      // Store token and user data in localStorage
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      toast.success('Login successful!');
      onClose(); // Close the modal
      
      // Redirect based on user role
      if (response.data.user.role === 'admin') {
        navigate('/admin/dashboard');
      } else {
        // Refresh the current page to update UI based on logged-in state
        window.location.reload();
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };
  
  // Join Us View
  const joinUsView = (
    <>
      <h2 className={styles.title}>Join Our Sweet Community!</h2>
      <p className={styles.subtitle}>Sign up today for exclusive offers and delicious treats</p>
      <div className={styles.buttonContainer}>
        <Link to="/signup" className={styles.signupButton}>Sign Up</Link>
        <button className={styles.signinButton} onClick={toggleView}>Sign In</button>
      </div>
    </>
  );
  
  // Sign In View
  const signInView = (
    <>
      <div className={styles.signInHeader}>
        <h2 className={styles.title}>Welcome Back</h2>
        <p className={styles.subtitle}>Sign in to your sweet account</p>
      </div>
      
      <form onSubmit={handleSubmit} className={styles.signInForm}>
        <div className={styles.formGroup}>
          <label htmlFor="username">Username</label>
          <div className={styles.inputWrapper}>
            <FiUser className={styles.inputIcon} />
            <input
              type="text"
              id="username"
              name="username"
              placeholder="Enter your username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        
        <div className={styles.formGroup}>
          <label htmlFor="pass_word">Password</label>
          <div className={styles.inputWrapper}>
            <FiLock className={styles.inputIcon} />
            <input
              type="password"
              id="pass_word"
              name="pass_word"
              placeholder="Enter your password"
              value={formData.pass_word}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        
        <button 
          type="submit" 
          className={styles.submitButton}
          disabled={loading}
        >
          {loading ? 'Signing in...' : (
            <>
              <FiLogIn className={styles.loginIcon} />
              <span>Sign In</span>
            </>
          )}
        </button>
      </form>
      
      <div className={styles.formFooter}>
        <button onClick={toggleView} className={styles.backButton}>
          Back to Join Options
        </button>
      </div>
    </>
  );
  
  return (
    <div className={styles.modalOverlay} onClick={(e) => {
      if (e.target === e.currentTarget) onClose();
    }}>
      <div className={`${styles.modalContent} ${showSignIn ? styles.signInContent : ''}`}>
        <button className={styles.closeButton} onClick={onClose}>×</button>
        {showSignIn ? signInView : joinUsView}
      </div>
    </div>
  );
};

export default JoinUsModal;




