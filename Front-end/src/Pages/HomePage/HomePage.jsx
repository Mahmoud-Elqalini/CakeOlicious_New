// Shahd Elwan
import React, { useState, useEffect } from 'react'
import styles from './HomePage.module.css'
import HeroSection from '../../Components/HeroSection/HeroSection'
import BestSellers from '../../Components/BestSellers/BestSellers'
import ChocoBanner from '../../Components/ChocoBanner/ChocoBanner'
import CakeBanner from '../../Components/CakeBanner/CakeBanner'
import JuiceBanner from '../../Components/JuiceBanner/JuiceBanner'
import JoinUsModal from '../../Components/JoinUsModal/JoinUsModal'

const HomePage = () => {
    const [showModal, setShowModal] = useState(false);
    
    useEffect(() => {
        // Check if user is logged in
        const isLoggedIn = localStorage.getItem('token');
        
        // Check if modal has been shown in this session
        const modalShown = sessionStorage.getItem('modalShown');
        
        // Only show modal if user is not logged in and modal hasn't been shown
        if (!isLoggedIn && !modalShown) {
            const timer = setTimeout(() => {
                setShowModal(true);
            }, 10000); // Show after 10 seconds
            
            return () => clearTimeout(timer);
        }
    }, []);
    
    const closeModal = () => {
        setShowModal(false);
        // Store in session storage that we've shown the modal
        sessionStorage.setItem('modalShown', 'true');
    };
    
    return (
        <div className={styles.HomePage}>
            <HeroSection />
            <BestSellers />
            <ChocoBanner />
            <CakeBanner />
            <JuiceBanner />
            <JoinUsModal isOpen={showModal} onClose={closeModal} />
        </div>
    )
}

export default HomePage
