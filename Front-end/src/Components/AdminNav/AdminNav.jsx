import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FaHome, FaBox, FaUsers, FaShoppingCart, FaComments, FaSignOutAlt } from 'react-icons/fa';
import styles from './AdminNav.module.css';

const AdminNav = () => {
    const navigate = useNavigate();
    const location = useLocation();
    
    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/signin');
    };
    
    // Function to check if a link is active
    const isActive = (path) => {
        return location.pathname === path;
    };
    
    return (
        <div className={styles.adminNav}>
            <div className={styles.logo}>
                <h2>Admin Panel</h2>
            </div>
            
            <nav className={styles.navLinks}>
                <Link 
                    to="/admin/dashboard" 
                    className={`${styles.navLink} ${isActive('/admin/dashboard') ? styles.active : ''}`}
                >
                    <FaHome className={styles.icon} />
                    <span>Dashboard</span>
                </Link>
                
                <Link 
                    to="/admin/products" 
                    className={`${styles.navLink} ${isActive('/admin/products') ? styles.active : ''}`}
                >
                    <FaBox className={styles.icon} />
                    <span>Products</span>
                </Link>
                
                <Link 
                    to="/admin/users" 
                    className={`${styles.navLink} ${isActive('/admin/users') ? styles.active : ''}`}
                >
                    <FaUsers className={styles.icon} />
                    <span>Users</span>
                </Link>
                
                <Link 
                    to="/admin/orders" 
                    className={`${styles.navLink} ${isActive('/admin/orders') ? styles.active : ''}`}
                >
                    <FaShoppingCart className={styles.icon} />
                    <span>Orders</span>
                </Link>
                
                <Link 
                    to="/admin/reviews" 
                    className={`${styles.navLink} ${isActive('/admin/reviews') ? styles.active : ''}`}
                >
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

export default AdminNav;
