import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { toast } from 'react-toastify'
import { FiLogIn } from 'react-icons/fi'
import styles from './SignIn.module.css'

const SignIn = () => {
    const [formData, setFormData] = useState({
        username: '',
        pass_word: ''
    })
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: value
        }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)

        try {
            console.log('Submitting login form with data:', formData);
            const response = await axios.post('http://localhost:5000/login', formData)
            console.log('Login response:', response.data);
            console.log('User data in response:', response.data.user);
            
            // Check if the response contains the expected data
            if (!response.data.token) {
                throw new Error('No token received from server');
            }
            
            if (!response.data.user) {
                throw new Error('No user data received from server');
            }
            
            // Extract user role from response
            // The backend is using user_role, not role
            const userRole = response.data.user.user_role || response.data.user.role || 'customer';

            // Ensure the user object has both role properties to be safe
            const userData = {
                ...response.data.user,
                role: (userRole || '').toLowerCase(), // For frontend components - safely convert to lowercase
                user_role: userRole // Keep the original for backend compatibility
            };

            console.log('Processed user data:', userData);
            console.log('User role:', userData.role);
            console.log('User role (original):', userData.user_role);
            
            // Store token and user data in localStorage
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user', JSON.stringify(userData));
            
            toast.success('Login successful!');
            
            // Add this debugging code after login to check the actual user data
            console.log('Full response data:', response.data);
            
            // Check the exact format of the user role in the response
            console.log('User role from server:', 
                typeof response.data.user.user_role, 
                response.data.user.user_role);
            
            // Make sure role comparison is case-insensitive
            if (userData.role.toLowerCase() === 'admin') {
                console.log('Redirecting to admin dashboard');
                navigate('/admin/dashboard');
            } else {
                console.log('Redirecting to home page');
                navigate('/');
            }
        } catch (error) {
            console.error('Login error:', error)
            toast.error(error.response?.data?.message || 'Login failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className={styles.SignIn}>
            <div className={styles.formContainer}>
                <h2>Welcome Back</h2>
                <p className={styles.subtitle}>Sign in to your account</p>
                
                <form onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label htmlFor="username">Username</label>
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
                    
                    <div className={styles.formGroup}>
                        <label htmlFor="pass_word">Password</label>
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
                    <p>Don't have an account? <Link to="/signup" className={styles.signupLink}>Sign Up</Link></p>
                </div>
            </div>
        </div>
    )
}

export default SignIn
