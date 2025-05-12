// Shahd Elwan
import React from 'react'
import styles from './HomePage.module.css'
import { Link } from 'react-router-dom'
import HeroSection from '../../Components/HeroSection/HeroSection'
import BestSellers from '../../Components/BestSellers/BestSellers'
import ChocoBanner from '../../Components/ChocoBanner/ChocoBanner'
import CakeBanner from '../../Components/CakeBanner/CakeBanner'
import JuiceBanner from '../../Components/JuiceBanner/JuiceBanner'

const HomePage = () => {
    return (
        <div className={styles.HomePage}>
            <HeroSection />
            <BestSellers />
            <ChocoBanner />
            <CakeBanner />
            <JuiceBanner />
        </div>
    )
}

export default HomePage
