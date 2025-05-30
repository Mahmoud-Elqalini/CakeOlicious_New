import React from 'react'
import styles from './CakeBanner.module.css'
import { getImage } from '../../assets/assets'
import { useInView } from 'react-intersection-observer'
import { useNavigate } from 'react-router-dom'

const CakeBanner = () => {
    const [ref, inView] = useInView({
        triggerOnce: false,
        threshold: 0.2
    });
    
    const navigate = useNavigate();

    const handleShopNow = () => {
        navigate('/products?category_id=1');
    };

    return (
        <div className={styles.cakeBanner} ref={ref}>
            <div className={styles.bannerContent}>
                <div className={`${styles.imageContainer} ${inView ? styles.visible : ''}`}>
                    <img src={getImage('TiramisuCake')} alt="Delicious layer cake" />
                </div>
                <div className={`${styles.textContent} ${inView ? styles.visible : ''}`}>
                    <h2 className={styles.title}>Cakes That Steal the Show</h2>
                    <p className={styles.subtitle}>Spotlight on Sweet Perfection</p>
                    <button className={styles.shopButton} onClick={handleShopNow}>Shop Now</button>
                </div>
            </div>
        </div>
    )
}

export default CakeBanner
