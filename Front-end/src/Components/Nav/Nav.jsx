import React, { useState, useEffect } from 'react'
import styles from './Nav.module.css'
import { Link } from 'react-router-dom'
import logo from '../../assets/logo.png'
import { FaSearch, FaUser, FaHeart, FaShoppingCart } from 'react-icons/fa'

const Nav = () => {
    const [isSticky, setIsSticky] = useState(false);
    const [searchActive, setSearchActive] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            const topNavHeight = 150;
            if (window.scrollY > topNavHeight) {
                setIsSticky(true);
            } else {
                setIsSticky(false);
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleSearchClick = () => {
        setSearchActive(true);
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
                        <Link to="/account" className={styles.iconGroup}>
                            <FaUser className={styles.icon} />
                            <span className={styles.iconText}>Account</span>
                        </Link>
                        <Link to="/wishlist" className={styles.iconGroup}>
                            <FaHeart className={styles.icon} />
                            <span className={styles.iconText}>Wishlist</span>
                        </Link>
                        <Link to="/cart" className={styles.iconGroup}>
                            <FaShoppingCart className={styles.icon} />
                            <span className={styles.iconText}>Cart</span>
                        </Link>
                    </div>
                </div>
            </div>

            <div className={`${styles.lowerNav} ${isSticky ? styles.sticky : ''}`}>
                <div className={styles.menuItems}>
                    <Link to="/" className={styles.menuItem}>HOME</Link>
                    <Link to="/chocolates" className={styles.menuItem}>CHOCOLATES</Link>
                    <Link to="/cakes" className={styles.menuItem}>CAKES</Link>
                    <Link to="/juices" className={styles.menuItem}>JUICES</Link>
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
