import React from 'react'
import styles from './BestSellers.module.css'
import images from '../../assets/assets'
import { Link } from 'react-router-dom'
import { FaShoppingCart, FaStar, FaEye, FaArrowRight } from 'react-icons/fa'

const BestSellers = () => {
    const bestSellers = [
        {
            id: 1,
            name: "Brownies",
            imageKey: "brownies",
            price: 42.99,
            rating: 4.9,
            category: "cakes"
        },
        {
            id: 2,
            name: "Tiramisu Cake",
            imageKey: "TiramisuCake",
            price: 38.99,
            rating: 4.8,
            category: "cakes"
        },
        {
            id: 3,
            name: "Cupcake",
            imageKey: "cupcake",
            price: 24.99,
            rating: 4.7,
            category: "chocolates"
        },
        {
            id: 4,
            name: "Donuts",
            imageKey: "donuts",
            price: 18.99,
            rating: 4.6,
            category: "pastries"
        }
    ];

    // Log available images to help debug
    // console.log("Available images:", Object.keys(images));

    return (
        <section className={styles.bestSellers}>
            <div className={styles.container}>
                <div className={styles.sectionHeader}>
                    <h2 className={styles.sectionTitle}>Our Best Sellers</h2>
                    <p className={styles.sectionSubtitle}>Handcrafted with love, enjoyed by many</p>
                </div>

                <div className={styles.productsGrid}>
                    {bestSellers.map(product => (
                        <div key={product.id} className={styles.productCard}>
                            <div className={styles.imageContainer}>
                                {images[product.imageKey] ? (
                                    <img
                                        src={images[product.imageKey]}
                                        alt={product.name}
                                        className={styles.productImage}
                                    />
                                ) : (
                                    <img
                                        src={`https://via.placeholder.com/300x300?text=${product.name}`}
                                        alt={product.name}
                                        className={styles.productImage}
                                    />
                                )}
                                <div className={styles.overlay}>
                                    {/* <button 
                                        className={styles.quickView}
                                        onClick={() => window.location.href = `/products/${product.id}`}
                                    >
                                        <FaEye style={{ marginRight: '6px' }} /> Quick View
                                    </button> */}
                                </div>
                            </div>
                            <div className={styles.productInfo}>
                                <div className={styles.categoryBadge}>{product.category}</div>
                                <h3 className={styles.productName}>{product.name}</h3>
                                <div className={styles.productMeta}>
                                    <span className={styles.productPrice}>${product.price}</span>
                                    <div className={styles.productRating}>
                                        <span className={styles.ratingValue}>{product.rating}</span>
                                        <FaStar className={styles.ratingIcon} />
                                    </div>
                                </div>
                                {/* <button className={styles.addToCartBtn}>
                                    <FaShoppingCart style={{ marginRight: '8px' }} /> Add to Cart
                                </button> */}
                            </div>
                        </div>
                    ))}
                </div>

                <div className={styles.viewAllContainer}>
                    <Link to="/products" className={styles.viewAllButton}>
                        View All Products <FaArrowRight />
                    </Link>
                </div>
            </div>
        </section>
    )
}

export default BestSellers


// Shahd Elwan
