import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { toast } from 'react-toastify'
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
            const response = await axios.post('http://localhost:5000/login', formData)
            
            // Store token and user data in localStorage
            localStorage.setItem('token', response.data.token)
            localStorage.setItem('user', JSON.stringify(response.data.user))
            
            // Debug: Log the user data
            console.log('User data:', response.data.user)
            console.log('User role:', response.data.user.role)
            
            toast.success('Login successful!')
            
            // Redirect based on user role
            if (response.data.user.role === 'admin') {
                console.log('Redirecting to admin dashboard')
                navigate('/admin/dashboard')
            } else {
                console.log('Redirecting to home page')
                navigate('/')
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
                <h2>Sign In</h2>
                <form onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
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
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>
            </div>
        </div>
    )
}

export default SignIn
