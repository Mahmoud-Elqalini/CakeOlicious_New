import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiUserPlus } from 'react-icons/fi';
import styles from './SignUp.module.css';

const SignUp = () => {
    const [formData, setFormData] = useState({
        username: '',
        pass_word: '',
        confirm_password: '',
        email: '',
        full_name: '',
        user_address: '',
        phone_number: '',
        user_role: 'Customer'
    });
    
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const validateForm = () => {
        if (!formData.username || !formData.pass_word || !formData.email || !formData.full_name) {
            toast.error('Please fill in all required fields');
            return false;
        }
        
        if (formData.pass_word !== formData.confirm_password) {
            toast.error('Passwords do not match');
            return false;
        }
        
        if (formData.pass_word.length < 6) {
            toast.error('Password must be at least 6 characters long');
            return false;
        }
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            toast.error('Please enter a valid email address');
            return false;
        }
        
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        setLoading(true);
        
        // Create a copy of formData without confirm_password
        const { confirm_password, ...dataToSend } = formData;
        
        try {
            const response = await axios.post('http://localhost:5000/signup', dataToSend);
            
            toast.success('Account created successfully!');
            navigate('/signin');
        } catch (error) {
            console.error('Signup error:', error);
            toast.error(error.response?.data?.message || 'Failed to create account');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.signUpContainer}>
            <div className={styles.formWrapper}>
                <h2>Create an Account</h2>
                <p className={styles.subtitle}>Join our sweet community today</p>
                
                <form onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label htmlFor="username">Username*</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            placeholder="Choose a username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    
                    <div className={styles.formGroup}>
                        <label htmlFor="email">Email*</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            placeholder="Enter your email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    
                    <div className={styles.formGroup}>
                        <label htmlFor="full_name">Full Name*</label>
                        <input
                            type="text"
                            id="full_name"
                            name="full_name"
                            placeholder="Enter your full name"
                            value={formData.full_name}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    
                    <div className={styles.formRow}>
                        <div className={styles.formGroup}>
                            <label htmlFor="pass_word">Password*</label>
                            <input
                                type="password"
                                id="pass_word"
                                name="pass_word"
                                placeholder="Create a password"
                                value={formData.pass_word}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        
                        <div className={styles.formGroup}>
                            <label htmlFor="confirm_password">Confirm Password*</label>
                            <input
                                type="password"
                                id="confirm_password"
                                name="confirm_password"
                                placeholder="Confirm your password"
                                value={formData.confirm_password}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>
                    
                    <div className={styles.formGroup}>
                        <label htmlFor="user_address">Address</label>
                        <input
                            type="text"
                            id="user_address"
                            name="user_address"
                            placeholder="Enter your address"
                            value={formData.user_address}
                            onChange={handleChange}
                        />
                    </div>
                    
                    <div className={styles.formGroup}>
                        <label htmlFor="phone_number">Phone Number</label>
                        <input
                            type="tel"
                            id="phone_number"
                            name="phone_number"
                            placeholder="Enter your phone number"
                            value={formData.phone_number}
                            onChange={handleChange}
                        />
                    </div>
                    
                    <button 
                        type="submit" 
                        className={styles.submitButton}
                        disabled={loading}
                    >
                        {loading ? 'Creating Account...' : (
                            <>
                                <FiUserPlus className={styles.signupIcon} />
                                <span>Create Account</span>
                            </>
                        )}
                    </button>
                </form>
                
                <div className={styles.loginLink}>
                    Already have an account? <Link to="/signin">Sign In</Link>
                </div>
            </div>
        </div>
    );
};

export default SignUp
