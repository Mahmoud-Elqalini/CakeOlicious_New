import React from 'react'
import styles from './JuiceBanner.module.css'
import { getImage } from '../../assets/assets'
import { useInView } from 'react-intersection-observer'

const JuiceBanner = () => {
    const [ref, inView] = useInView({
        triggerOnce: false,
        threshold: 0.2
    });

    return (
        <div className={styles.juiceBanner} ref={ref}>
            <div className={styles.bannerContent}>
                <div className={`${styles.textContent} ${inView ? styles.visible : ''}`}>
                    <h2 className={styles.title}>Juice Up Your Sweet Side</h2>
                    <p className={styles.subtitle}>Fruity Bliss Meets Cake</p>
                    <button className={styles.shopButton}>Shop Now</button>
                </div>
                <div className={`${styles.imageContainer} ${inView ? styles.visible : ''}`}>
                    <img src={getImage('juice')} alt="Refreshing fruit juice" />
                </div>
            </div>
        </div>
    )
}

export default JuiceBanner
