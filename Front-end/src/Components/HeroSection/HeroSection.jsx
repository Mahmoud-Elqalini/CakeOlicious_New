// Shahd Elwan
import React from 'react'
import styles from './HeroSection.module.css'
import promo from '../../assets/promo.mp4'

const HeroSection = () => {
    return (
        <div className={`container-fluid p-0 ${styles.heroSection}`}>
            <div className={styles.videoContainer}>
                <video src={promo} autoPlay loop muted className={styles.backgroundVideo} />
                <div className={styles.overlay}></div>
            </div>
            <div className={styles.content}>
                <h1 className={styles.title}>Sweetness Awaits at CakeOlicious</h1>
                <p className={styles.subtitle}>Freshly baked daily</p>
                <button className={styles.ctaButton}>Taste the magic!</button>
            </div>
        </div>
    )
}

export default HeroSection
