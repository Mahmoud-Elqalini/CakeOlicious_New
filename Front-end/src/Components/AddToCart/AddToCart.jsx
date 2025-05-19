import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import styles from './AddToCart.module.css';
import { FaShoppingCart } from 'react-icons/fa';
import { Link } from 'react-router-dom';

const AddToCart = ({ productId, token, compact = false }) => {
    const [quantity, setQuantity] = useState(1);
    const [loading, setLoading] = useState(false);
    const [showViewCart, setShowViewCart] = useState(false);
    const [cartCount, setCartCount] = useState(0);
    
    // Get initial cart count from localStorage
    useEffect(() => {
        const savedCount = localStorage.getItem('cartCount');
        if (savedCount) {
            setCartCount(parseInt(savedCount));
        }
    }, []);
    
    const handleAddToCart = async () => {
        if (quantity < 1) {
            toast.error('Quantity must be at least 1');
            return;
        }

        // Check if token exists and log it for debugging
        if (!token) {
            console.error('Token is missing when trying to add to cart');
            toast.error('You must be logged in to add items to cart');
            return;
        }
        
        console.log('Using token for cart request:', token.substring(0, 10) + '...');

        setLoading(true);
        try {
            const response = await axios.post(
                'http://localhost:5000/cart/add',
                { product_id: productId, quantity },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    withCredentials: false // Set to false to avoid CORS preflight issues
                }
            );
            
            // Log the response for debugging
            console.log('Add to cart response:', response.data);
            
            if (response.data.message) {
                toast.success(response.data.message);
                setShowViewCart(true);
                
                // Update local cart count
                const newCount = cartCount + quantity;
                setCartCount(newCount);
                
                // Store in localStorage
                localStorage.setItem('cartCount', newCount.toString());
                
                // Directly update the cart count without waiting for a second request
                const cartCountEvent = new CustomEvent('cartCountUpdated', {
                    detail: { count: newCount }
                });
                window.dispatchEvent(cartCountEvent);
                
                // Still dispatch the general update event as a backup
                const cartUpdateEvent = new CustomEvent('cartUpdated');
                window.dispatchEvent(cartUpdateEvent);
            } else {
                toast.error('Failed to add product to cart');
            }
        } catch (error) {
            console.error('Add to cart error:', error);
            toast.error(error.response?.data?.message || 'Failed to add product to cart');
        } finally {
            setLoading(false);
        }
    };

    // Compact version for product listings
    if (compact) {
        return (
            <button
                className={styles.compactAddToCartBtn}
                onClick={handleAddToCart}
                disabled={loading}
                aria-label="Add to cart"
            >
                <FaShoppingCart className={styles.cartIcon} />
                <span>{loading ? 'Adding...' : 'Add to Cart'}</span>
            </button>
        );
    }

    // Full version with quantity selector for product detail page
    return (
        <div className={styles.addToCartContainer}>
            <div className={styles.quantitySelector}>
                <button
                    className={styles.quantityButton}
                    onClick={() => setQuantity(prev => Math.max(1, prev - 1))}
                    disabled={quantity <= 1}
                    aria-label="Decrease quantity"
                >
                    -
                </button>
                <input
                    className={styles.quantityInput}
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                    aria-label="Quantity"
                />
                <button 
                    className={styles.quantityButton}
                    onClick={() => setQuantity(prev => prev + 1)}
                    aria-label="Increase quantity"
                >
                    +
                </button>
            </div>
            <button
                className={styles.addToCartBtn}
                onClick={handleAddToCart}
                disabled={loading}
            >
                <FaShoppingCart className={styles.cartIcon} />
                <span>{loading ? 'Adding...' : 'Add to Cart'}</span>
            </button>

            {showViewCart && (
                <Link to="/cart" className={styles.viewCartBtn}>
                    View Cart
                </Link>
            )}
        </div>
    );
};

export default AddToCart;
