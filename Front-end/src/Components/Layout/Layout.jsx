import React from 'react'
import styles from './Layout.module.css'
import Nav from '../Nav/Nav'

const Layout = ({ children }) => {
  return (
    <div className={styles.layoutContainer}>
      <Nav />
      <main className={styles.mainContent}>
        {children}
      </main>
    </div>
  )
}

export default Layout
