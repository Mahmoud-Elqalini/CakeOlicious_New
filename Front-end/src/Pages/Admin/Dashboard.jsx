import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './Dashboard.module.css';
import AdminNav from '../../Components/AdminNav/AdminNav';
import { formatDistanceToNow } from 'date-fns';

const AdminDashboard = () => {
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
    
    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                setLoading(true);
                const token = localStorage.getItem('token');
                
                // Fetch dashboard statistics from the existing /admin endpoint
                const response = await axios.get('http://localhost:5000/admin', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                // Update state with fetched data
                setMessage(response.data.message);
                
                // Check if stats and recentActivity exist in the response
                if (response.data.stats) {
                    setStats(response.data.stats);
                }
                
                if (response.data.recentActivity) {
                    setRecentActivity(response.data.recentActivity);
                }
            } catch (err) {
                console.error('Dashboard error:', err);
                setError(err.response?.data?.message || 'Failed to load admin dashboard');
            } finally {
                setLoading(false);
            }
        };
        
        fetchDashboard();
    }, []);
    
    // Function to format activity message
    const formatActivityMessage = (activity) => {
        if (activity.type === 'order') {
            return `New order #${activity.id} from ${activity.username} (${activity.status})`;
        } else if (activity.type === 'user') {
            return `User ${activity.username} registered`;
        }
        return 'Unknown activity';
    };
    
    // Function to format date for display
    const formatActivityDate = (dateString) => {
        if (!dateString) return 'Recently';
        
        try {
            const date = new Date(dateString);
            return formatDistanceToNow(date, { addSuffix: true });
        } catch (error) {
            return 'Unknown date';
        }
    };
    
    return (
        <div className={styles.adminLayout}>
            <AdminNav />
            
            <div className={styles.dashboardContainer}>
                <h1>Admin Dashboard</h1>
                
                {error && <div className={styles.error}>{error}</div>}
                {message && <div className={styles.message}>{message}</div>}
                
                {loading ? (
                    <div className={styles.loading}>Loading dashboard data...</div>
                ) : (
                    <>
                        <div className={styles.statsGrid}>
                            <div className={styles.statCard}>
                                <h3>Total Products</h3>
                                <p className={styles.statValue}>{stats.totalProducts}</p>
                            </div>
                            
                            <div className={styles.statCard}>
                                <h3>Total Users</h3>
                                <p className={styles.statValue}>{stats.totalUsers}</p>
                            </div>
                            
                            <div className={styles.statCard}>
                                <h3>Total Orders</h3>
                                <p className={styles.statValue}>{stats.totalOrders}</p>
                            </div>
                            
                            <div className={styles.statCard}>
                                <h3>Total Revenue</h3>
                                <p className={styles.statValue}>${stats.totalRevenue.toLocaleString()}</p>
                            </div>
                        </div>
                        
                        <div className={styles.recentActivity}>
                            <h2>Recent Activity</h2>
                            {recentActivity.length > 0 ? (
                                <div className={styles.activityList}>
                                    {recentActivity.map((activity, index) => (
                                        <div key={index} className={styles.activityItem}>
                                            <p>{formatActivityMessage(activity)}</p>
                                            <span>{formatActivityDate(activity.date)}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className={styles.noActivity}>No recent activity found</p>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;

