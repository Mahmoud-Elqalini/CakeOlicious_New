import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './AdminNav.module.css';
import { FaHome, FaBox, FaUsers, FaShoppingCart, FaComments, FaSignOutAlt } from 'react-icons/fa';

const AdminNav = () => {
    const navigate = useNavigate();
    
    const handleLogout = () => {
        // Clear localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        // Redirect to login page
        navigate('/signin');
    };
    
    return (
        <div className={styles.adminNav}>
            <div className={styles.logo}>
                <h2>Admin Panel</h2>
            </div>
            
            <nav className={styles.navLinks}>
                <Link to="/admin/dashboard" className={styles.navLink}>
                    <FaHome className={styles.icon} />
                    <span>Dashboard</span>
                </Link>
                
                <Link to="/admin/products" className={styles.navLink}>
                    <FaBox className={styles.icon} />
                    <span>Products</span>
                </Link>
                
                <Link to="/admin/users" className={styles.navLink}>
                    <FaUsers className={styles.icon} />
                    <span>Users</span>
                </Link>
                
                <Link to="/admin/orders" className={styles.navLink}>
                    <FaShoppingCart className={styles.icon} />
                    <span>Orders</span>
                </Link>
                
                <Link to="/admin/reviews" className={styles.navLink}>
                    <FaComments className={styles.icon} />
                    <span>Reviews</span>
                </Link>
            </nav>
            
            <div className={styles.footer}>
                <button onClick={handleLogout} className={styles.logoutButton}>
                    <FaSignOutAlt className={styles.icon} />
                    <span>Logout</span>
                </button>
            </div>
        </div>
    );
};

export default AdminNav
