import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import styles from './NotFound.module.css'
import { useInView } from 'react-intersection-observer'

const NotFound = () => {
    const [ref, inView] = useInView({
        triggerOnce: true,
        threshold: 0.2
    });

    useEffect(() => {
        // Set page title when component mounts
        document.title = "Page Not Found | CakeOlicious";
        
        // Reset title when component unmounts
        return () => {
            document.title = "CakeOlicious";
        };
    }, []);

    return (
        <div className={styles.notFound} ref={ref}>
            <div className={`${styles.content} ${inView ? styles.visible : ''}`}>
                <h1 className={styles.errorCode}>404</h1>
                <div className={styles.messageContainer}>
                    <h2 className={styles.title}>Oops! Page Not Found</h2>
                    <p className={styles.message}>
                        Looks like this page has gone missing, just like the last slice of cake at a birthday party!
                    </p>
                    <div className={styles.buttonContainer}>
                        <Link to="/" className={styles.homeButton}>
                            Back to Home
                        </Link>
                        <Link to="/products" className={styles.productsButton}>
                            Browse Treats
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default NotFound
