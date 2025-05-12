import React from 'react'
import styles from './Footer.module.css'
import { Link } from 'react-router-dom'
import { FaFacebook, FaInstagram, FaTwitter, FaPinterest, FaEnvelope, FaPhone, FaMapMarkerAlt } from 'react-icons/fa'

const Footer = () => {
    return (
        <footer className={styles.footer} role="contentinfo">
            
            <div className={styles.footerContent}>
                <section className={styles.footerSection}>
                    <h2 className={styles.footerTitle}>CakeOlicious</h2>
                    <p className={styles.footerText}>Sweetness delivered to your doorstep. Handcrafted with love since 2023.</p>
                    <div className={styles.socialIcons} aria-label="Social Media Links">
                        <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" className={styles.socialIcon} aria-label="Facebook">
                            <FaFacebook />
                        </a>
                        <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className={styles.socialIcon} aria-label="Instagram">
                            <FaInstagram />
                        </a>
                        <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className={styles.socialIcon} aria-label="Twitter">
                            <FaTwitter />
                        </a>
                        <a href="https://pinterest.com" target="_blank" rel="noopener noreferrer" className={styles.socialIcon} aria-label="Pinterest">
                            <FaPinterest />
                        </a>
                    </div>
                </section>

                <nav className={styles.footerSection} aria-labelledby="footer-navigation">
                    <h2 className={styles.footerTitle} id="footer-navigation">Quick Links</h2>
                    <ul className={styles.footerLinks}>
                        <li><Link to="/">Home</Link></li>
                        <li><Link to="/chocolates">Chocolates</Link></li>
                        <li><Link to="/cakes">Cakes</Link></li>
                        <li><Link to="/juices">Juices</Link></li>
                        <li><Link to="/about">About Us</Link></li>
                    </ul>
                </nav>

                <section className={styles.footerSection} aria-labelledby="contact-info">
                    <h2 className={styles.footerTitle} id="contact-info">Contact Us</h2>
                    <address className={styles.contactInfo}>
                        <p className={styles.contactItem}>
                            <FaMapMarkerAlt aria-hidden="true" /> 
                            <span>123 Sweet Street, Bakery Lane</span>
                        </p>
                        <p className={styles.contactItem}>
                            <FaPhone aria-hidden="true" /> 
                            <a href="tel:+15551234567">+1 (555) 123-4567</a>
                        </p>
                        <p className={styles.contactItem}>
                            <FaEnvelope aria-hidden="true" /> 
                            <a href="mailto:hello@cakeolicious.com">hello@cakeolicious.com</a>
                        </p>
                    </address>
                </section>

                <section className={styles.footerSection} aria-labelledby="newsletter">
                    <h2 className={styles.footerTitle} id="newsletter">Newsletter</h2>
                    <p className={styles.footerText}>Subscribe for sweet deals and updates!</p>
                    <form className={styles.newsletterForm} onSubmit={(e) => e.preventDefault()}>
                        <label htmlFor="email-input" className={styles.srOnly}>Email address</label>
                        <input 
                            type="email" 
                            id="email-input"
                            placeholder="Your email" 
                            className={styles.newsletterInput} 
                            required
                            aria-required="true"
                        />
                        <button type="submit" className={styles.newsletterButton}>Subscribe</button>
                    </form>
                </section>
            </div>
            
            <div className={styles.footerBottom}>
                <p className={styles.copyright}>&copy; {new Date().getFullYear()} CakeOlicious. All rights reserved.</p>
                <nav className={styles.footerBottomLinks} aria-label="Legal">
                    <Link to="/privacy">Privacy Policy</Link>
                    <Link to="/terms">Terms of Service</Link>
                    <Link to="/sitemap">Sitemap</Link>
                </nav>
            </div>
        </footer>
    )
}

export default Footer
