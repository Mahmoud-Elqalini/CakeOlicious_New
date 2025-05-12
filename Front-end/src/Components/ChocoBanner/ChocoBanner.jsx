import React from 'react'
import styles from './ChocoBanner.module.css'
import { getImage } from '../../assets/assets'
import { useInView } from 'react-intersection-observer'
import { useNavigate } from 'react-router-dom'

const ChocoBanner = () => {
    const [ref, inView] = useInView({
        triggerOnce: false,
        threshold: 0.2
    });

    const navigate = useNavigate();

    const handleShopNow = () => {

        navigate('/products?category_id=2');
    };

    return (
        <div className={styles.chocoBanner} ref={ref}>
            <div className={styles.bannerContent}>
                <div className={`${styles.textContent} ${inView ? styles.visible : ''}`}>
                    <h2 className={styles.title}>Our Chocolate Obsession</h2>
                    <p className={styles.subtitle}>Handcrafted with Love</p>
                    <button className={styles.shopButton} onClick={handleShopNow}>Shop Now</button>
                </div>
                <div className={`${styles.imageContainer} ${inView ? styles.visible : ''}`}>
                    <img src={getImage('stackedchoco')} alt="Stacked chocolate bars" />
                </div>
            </div>
        </div>
    )
}

export default ChocoBanner
