import React, { useState, useEffect } from 'react'
import styles from './Nav.module.css'
import { Link, useNavigate } from 'react-router-dom'
import logo from '../../assets/logo.png'
import { FaSearch, FaUser, FaHeart, FaShoppingCart, FaUserCheck } from 'react-icons/fa'
import { useAuth } from '../../context/AuthContext'
import axios from 'axios'

const Nav = () => {
    const [isSticky, setIsSticky] = useState(false);
    const [searchActive, setSearchActive] = useState(false);
    const [scrollPosition, setScrollPosition] = useState(0);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [username, setUsername] = useState('');
    const navigate = useNavigate();
    const [cartCount, setCartCount] = useState(0);
    const [wishlistCount, setWishlistCount] = useState(0);
    
    const { isAuthenticated, token } = useAuth() || { isAuthenticated: false, token: null };

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        
        if (token && userStr) {
            try {
                const userData = JSON.parse(userStr);
                setIsLoggedIn(true);
                setUsername(userData.username || '');
                console.log('User logged in:', userData.username);
            } catch (error) {
                console.error('Error parsing user data:', error);
                setIsLoggedIn(!!token);
            }
        } else {
            setIsLoggedIn(false);
            setUsername('');
        }

        const handleScroll = () => {
            const position = window.scrollY;
            setScrollPosition(position);
            
            const topNavHeight = 150;
            if (position > topNavHeight) {
                setIsSticky(true);
            } else {
                setIsSticky(false);
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    useEffect(() => {
        // Initialize cart count from localStorage on page load
        const savedCount = localStorage.getItem('cartCount');
        if (savedCount) {
            setCartCount(parseInt(savedCount));
        }
    }, []);

    useEffect(() => {
        // Function to fetch cart count
        const fetchCartCount = async () => {
            if (!isAuthenticated) {
                setCartCount(0);
                localStorage.setItem('cartCount', '0');
                return;
            }

            try {
                const response = await axios.get('http://localhost:5000/cart', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (response.data.success && response.data.data) {
                    const count = response.data.data.length;
                    setCartCount(count);
                    localStorage.setItem('cartCount', count.toString());
                } else {
                    setCartCount(0);
                    localStorage.setItem('cartCount', '0');
                }
            } catch (error) {
                console.error('Error fetching cart count:', error);
                setCartCount(0);
            }
        };

        fetchCartCount();

        // Listen for cart update events
        const handleCartUpdate = () => {
            fetchCartCount();
        };
        
        // Listen for direct cart count updates
        const handleCartCountUpdate = (event) => {
            const newCount = event.detail.count;
            setCartCount(newCount);
            localStorage.setItem('cartCount', newCount.toString());
        };
        
        window.addEventListener('cartUpdated', handleCartUpdate);
        window.addEventListener('cartCountUpdated', handleCartCountUpdate);

        return () => {
            window.removeEventListener('cartUpdated', handleCartUpdate);
            window.removeEventListener('cartCountUpdated', handleCartCountUpdate);
        };
    }, [isAuthenticated, token]);

    useEffect(() => {
        // Function to fetch wishlist count
        const fetchWishlistCount = async () => {
            if (!isAuthenticated) {
                setWishlistCount(0);
                localStorage.setItem('wishlistCount', '0');
                return;
            }

            try {
                const response = await axios.get('http://localhost:5000/wishlist', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (response.data.success && response.data.data) {
                    const count = response.data.data.length;
                    setWishlistCount(count);
                    localStorage.setItem('wishlistCount', count.toString());
                } else {
                    setWishlistCount(0);
                    localStorage.setItem('wishlistCount', '0');
                }
            } catch (error) {
                console.error('Error fetching wishlist count:', error);
                setWishlistCount(0);
            }
        };

        fetchWishlistCount();

        // Listen for wishlist update events
        const handleWishlistUpdate = () => {
            fetchWishlistCount();
        };
        
        window.addEventListener('wishlistUpdated', handleWishlistUpdate);

        return () => {
            window.removeEventListener('wishlistUpdated', handleWishlistUpdate);
        };
    }, [isAuthenticated, token]);

    const handleSearchClick = () => {
        setSearchActive(true);
    };

    const handleAccountClick = (e) => {
        if (!isLoggedIn) {
            e.preventDefault();
            navigate('/signin');
        }
        // If logged in, the Link will navigate to /account
    };

    return (
        <div className={styles.navigation}>
            <div className={styles.upperNav}>
                <div className={styles.navSides}>
                    <div
                        className={styles.searchGroup}
                        onClick={handleSearchClick}
                    >
                        <FaSearch className={styles.searchIcon} />
                        {!searchActive && <span className={styles.searchText}>Search products...</span>}
                        {searchActive && (
                            <input
                                type="text"
                                autoFocus
                                className={styles.searchInput}
                                placeholder="Search products..."
                                onBlur={() => setSearchActive(false)}
                            />
                        )}
                    </div>

                    <Link to="/" className={styles.brandLogo}>
                        <img src={logo} alt="CakeOlicious" className={styles.logoImage} />
                        <span className={styles.brandName}>akeOlicious</span>
                    </Link>

                    <div className={styles.navIcons}>
                        <Link 
                            to={isLoggedIn ? "/account" : "#"} 
                            className={styles.iconGroup}
                            onClick={handleAccountClick}
                        >
                            {isLoggedIn ? (
                                <FaUserCheck className={`${styles.icon} ${styles.loggedInIcon}`} />
                            ) : (
                                <FaUser className={styles.icon} />
                            )}
                            <span className={styles.iconText}>
                                {isLoggedIn ? (username || "Account") : "Sign In"}
                            </span>
                        </Link>
                        <Link to="/wishlist" className={styles.iconGroup}>
                            <div className={styles.iconWrapper}>
                                <FaHeart className={styles.icon} />
                                {wishlistCount > 0 && (
                                    <span className={styles.cartCountBadge}>{wishlistCount}</span>
                                )}
                            </div>
                            <span className={styles.iconText}>Wishlist</span>
                        </Link>
                        <Link to="/cart" className={styles.iconGroup}>
                            <div className={styles.iconWrapper}>
                                <FaShoppingCart className={styles.icon} />
                                {cartCount > 0 && (
                                    <span className={styles.cartCountBadge}>{cartCount}</span>
                                )}
                            </div>
                            <span className={styles.iconText}>Cart</span>
                        </Link>
                    </div>
                </div>
            </div>

            <div className={`${styles.lowerNav} ${isSticky ? styles.sticky : ''}`}>
                <div className={styles.menuItems}>
                    <Link to="/" className={styles.menuItem}>HOME</Link>
                    <Link to="/products?category_id=2" className={styles.menuItem}>CHOCOLATES</Link>
                    <Link to="/products?category_id=1" className={styles.menuItem}>CAKES</Link>
                    <Link to="/products?category_id=3" className={styles.menuItem}>JUICES</Link>
                    <Link to="/about" className={styles.menuItem}>ABOUT US</Link>
                    <Link to="/contact">
                        <button className={styles.contactButton}>
                            <span className={styles.buttonText}>Contact Us</span>
                        </button>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Nav
