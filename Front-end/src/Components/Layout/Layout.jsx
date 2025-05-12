import React from 'react'
import styles from './Layout.module.css'
import Nav from '../Nav/Nav'
import Footer from '../Footer/Footer'

const Layout = ({ children }) => {
  return (
    <div className={styles.layoutContainer}>
      <Nav />
      <main className={styles.mainContent}>
        {children}
      </main>
      <Footer />
    </div>
  )
}

export default Layout
