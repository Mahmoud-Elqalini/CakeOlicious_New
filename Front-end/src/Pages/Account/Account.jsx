import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FaUser, FaShoppingBag, FaSignOutAlt, FaEdit } from 'react-icons/fa';
import styles from './Account.module.css';

const Account = () => {
    const [userData, setUserData] = useState(null);
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('profile');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        
        if (!token) {
            navigate('/signin');
            return;
        }
        
        fetchUserData(token);
    }, [navigate]);

    const fetchUserData = async (token) => {
        try {
            setLoading(true);
            const response = await axios.get('http://localhost:5000/profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            setUserData(response.data.user_profile);
            setOrders(response.data.orders);
        } catch (error) {
            console.error('Error fetching user data:', error);
            toast.error('Failed to load profile data');
            
            // If unauthorized, redirect to login
            if (error.response && error.response.status === 401) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                navigate('/signin');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        toast.success('Logged out successfully');
        navigate('/');
    };

    const formatDate = (dateString) => {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    };

    const getStatusClass = (status) => {
        switch (status.toLowerCase()) {
            case 'completed':
                return styles.statusCompleted;
            case 'processing':
                return styles.statusProcessing;
            case 'shipped':
                return styles.statusShipped;
            case 'cancelled':
                return styles.statusCancelled;
            default:
                return '';
        }
    };

    if (loading) {
        return <div className={styles.loading}>Loading profile...</div>;
    }

    return (
        <div className={styles.accountPage}>
            <div className={styles.accountContainer}>
                <div className={styles.sidebar}>
                    <div className={styles.userInfo}>
                        <div className={styles.userAvatar}>
                            <FaUser />
                        </div>
                        <h3>{userData?.username || 'User'}</h3>
                    </div>
                    
                    <div className={styles.navMenu}>
                        <button 
                            className={`${styles.navItem} ${activeTab === 'profile' ? styles.active : ''}`}
                            onClick={() => setActiveTab('profile')}
                        >
                            <FaUser className={styles.navIcon} />
                            <span>My Profile</span>
                        </button>
                        
                        <button 
                            className={`${styles.navItem} ${activeTab === 'orders' ? styles.active : ''}`}
                            onClick={() => setActiveTab('orders')}
                        >
                            <FaShoppingBag className={styles.navIcon} />
                            <span>My Orders</span>
                        </button>
                        
                        <button 
                            className={styles.navItem}
                            onClick={handleLogout}
                        >
                            <FaSignOutAlt className={styles.navIcon} />
                            <span>Logout</span>
                        </button>
                    </div>
                </div>
                
                <div className={styles.contentArea}>
                    {activeTab === 'profile' && (
                        <div className={styles.profileSection}>
                            <div className={styles.sectionHeader}>
                                <h2>My Profile</h2>
                                <button className={styles.editButton}>
                                    <FaEdit /> Edit
                                </button>
                            </div>
                            
                            <div className={styles.profileInfo}>
                                <div className={styles.infoGroup}>
                                    <label>Username</label>
                                    <p>{userData?.username || 'N/A'}</p>
                                </div>
                                
                                <div className={styles.infoGroup}>
                                    <label>Email</label>
                                    <p>{userData?.email || 'N/A'}</p>
                                </div>
                                
                                <div className={styles.infoGroup}>
                                    <label>Phone</label>
                                    <p>{userData?.phone || 'N/A'}</p>
                                </div>
                                
                                <div className={styles.infoGroup}>
                                    <label>Address</label>
                                    <p>{userData?.address || 'N/A'}</p>
                                </div>
                                
                                <div className={styles.infoGroup}>
                                    <label>Total Orders</label>
                                    <p>{userData?.number_of_orders || 0}</p>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    {activeTab === 'orders' && (
                        <div className={styles.ordersSection}>
                            <h2>My Orders</h2>
                            
                            {orders.length === 0 ? (
                                <div className={styles.emptyOrders}>
                                    <p>You haven't placed any orders yet.</p>
                                    <button 
                                        className={styles.shopButton}
                                        onClick={() => navigate('/products')}
                                    >
                                        Start Shopping
                                    </button>
                                </div>
                            ) : (
                                <div className={styles.ordersList}>
                                    {orders.map(order => (
                                        <div key={order.order_id} className={styles.orderCard}>
                                            <div className={styles.orderHeader}>
                                                <div>
                                                    <h3>Order #{order.order_id}</h3>
                                                    <p className={styles.orderDate}>
                                                        {formatDate(order.created_at)}
                                                    </p>
                                                </div>
                                                <div className={`${styles.orderStatus} ${getStatusClass(order.status)}`}>
                                                    {order.status}
                                                </div>
                                            </div>
                                            
                                            <div className={styles.orderDetails}>
                                                <p className={styles.orderTotal}>
                                                    Total: ${parseFloat(order.total_price).toFixed(2)}
                                                </p>
                                                <button 
                                                    className={styles.viewOrderButton}
                                                    onClick={() => navigate(`/order/${order.order_id}`)}
                                                >
                                                    View Details
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Account;