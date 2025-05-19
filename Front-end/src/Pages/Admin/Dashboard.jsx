import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './Dashboard.module.css';
import AdminNav from '../../Components/AdminNav/AdminNav';
import { formatDistanceToNow } from 'date-fns';
import { FiPackage, FiUsers, FiShoppingCart, FiDollarSign, FiActivity, FiRefreshCw } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
    console.log("AdminDashboard component rendering");
    console.log("Styles loaded:", styles); // Check if styles are loading properly
    
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalProducts: 0,
        totalUsers: 0,
        totalOrders: 0,
        totalRevenue: 0
    });
    const [recentActivity, setRecentActivity] = useState([]);
    const navigate = useNavigate();

    const fetchDashboard = async () => {
        console.log("Fetching dashboard data...");
        try {
            setLoading(true);
            setError('');
            const token = localStorage.getItem('token');
            console.log("Token retrieved:", token ? "Token exists" : "No token found");
            
            if (!token) {
                toast.error('Authentication required');
                navigate('/signin');
                return;
            }

            // Set the base URL for the API request
            const baseURL = 'http://localhost:5000';
            console.log("Making API request to:", `${baseURL}/admin`);
            
            // Fetch dashboard statistics
            const response = await axios.get(`${baseURL}/admin`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            console.log('Dashboard response:', response.data);

            // Update state with fetched data
            setMessage(response.data.message || 'Welcome to the admin dashboard');

            // Check if stats exist in the response
            if (response.data.stats) {
                // Ensure all stats are numbers
                const sanitizedStats = {
                    totalProducts: Number(response.data.stats.totalProducts || 0),
                    totalUsers: Number(response.data.stats.totalUsers || 0),
                    totalOrders: Number(response.data.stats.totalOrders || 0),
                    totalRevenue: Number(response.data.stats.totalRevenue || 0)
                };
                setStats(sanitizedStats);
            }

            if (response.data.recentActivity && Array.isArray(response.data.recentActivity)) {
                setRecentActivity(response.data.recentActivity);
            } else {
                setRecentActivity([]);
            }
        } catch (err) {
            console.error('Dashboard error:', err);
            
            // Handle different error scenarios
            if (err.response) {
                console.log("Error response status:", err.response.status);
                console.log("Error response data:", err.response.data);
                
                if (err.response.status === 401 || err.response.status === 403) {
                    toast.error('You are not authorized to access the admin dashboard');
                    navigate('/signin');
                } else {
                    setError(err.response.data?.message || 'Failed to load admin dashboard');
                }
            } else if (err.request) {
                console.log("No response received:", err.request);
                setError('No response from server. Please check your connection.');
            } else {
                console.log("Request setup error:", err.message);
                setError('Error setting up request: ' + err.message);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboard();
    }, [navigate]);

    return (
        <div className={styles.adminLayout || "adminLayout"}>
            <AdminNav />
            <div className={styles.dashboardContainer || "dashboardContainer"}>
                <div className={styles.dashboardHeader || "dashboardHeader"}>
                    <h1>Admin Dashboard</h1>
                    <button 
                        className={styles.refreshButton || "refreshButton"}
                        onClick={fetchDashboard}
                        disabled={loading}
                    >
                        <FiRefreshCw className={loading ? (styles.spinning || "spinning") : ''} />
                        Refresh
                    </button>
                </div>

                {}
                <div style={{padding: "20px", backgroundColor: "#f8d7da", color: "#721c24", marginBottom: "20px"}}>
                    Dashboard is loading... If you see this message, the component is rendering.
                </div>

                {error && (
                    <div className={styles.error}>
                        <p>{error}</p>
                        <button 
                            className={styles.retryButton}
                            onClick={fetchDashboard}
                        >
                            Retry
                        </button>
                    </div>
                )}
                
                {message && !error && <div className={styles.message}>{message}</div>}

                {loading ? (
                    <div className={styles.loading}>Loading dashboard data...</div>
                ) : (
                    !error && (
                        <>
                            <div className={styles.statsGrid}>
                                <div className={styles.statCard}>
                                    <h3><FiPackage style={{ marginRight: '8px' }} />Total Products</h3>
                                    <p className={styles.statValue}>{stats.totalProducts}</p>
                                </div>

                                <div className={styles.statCard}>
                                    <h3><FiUsers style={{ marginRight: '8px' }} />Total Users</h3>
                                    <p className={styles.statValue}>{stats.totalUsers}</p>
                                </div>

                                <div className={styles.statCard}>
                                    <h3><FiShoppingCart style={{ marginRight: '8px' }} />Total Orders</h3>
                                    <p className={styles.statValue}>{stats.totalOrders}</p>
                                </div>

                                <div className={styles.statCard}>
                                    <h3><FiDollarSign style={{ marginRight: '8px' }} />Total Revenue</h3>
                                    <p className={styles.statValue}>${parseFloat(stats.totalRevenue).toFixed(2)}</p>
                                </div>
                            </div>

                            <div className={styles.recentActivity}>
                                <h2><FiActivity style={{ marginRight: '8px' }} />Recent Activity</h2>
                                {recentActivity.length > 0 ? (
                                    <div className={styles.activityList}>
                                        {recentActivity.map((activity, index) => (
                                            <div key={index} className={styles.activityItem}>
                                                <p>{activity.description}</p>
                                                <span>
                                                    {activity.timestamp ? 
                                                        formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true }) : 
                                                        'Recently'}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className={styles.noActivity}>No recent activity to display</div>
                                )}
                            </div>
                        </>
                    )
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;





