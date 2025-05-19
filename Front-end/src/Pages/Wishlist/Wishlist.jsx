import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import styles from './Wishlist.module.css';
import { FaTrash, FaShoppingCart } from 'react-icons/fa';

const Wishlist = () => {
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated, token } = useAuth();
  const navigate = useNavigate();

  // Add this helper function to properly format image URLs
  const getProductImageUrl = (url) => {
    if (!url) return '/src/assets/images/placeholder.svg';
    
    // If it's already an absolute URL
    if (url.startsWith('http')) {
      return url;
    }
    
    // If it's a relative URL from the backend
    const formattedUrl = url.startsWith('/') ? url : `/${url}`;
    return `http://localhost:5000${formattedUrl}`;
  };

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/signin');
      return;
    }
    
    fetchWishlistItems();
  }, [isAuthenticated, navigate, token]);

  const fetchWishlistItems = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/wishlist', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Wishlist response:', response.data);
      
      if (response.data.success) {
        setWishlistItems(response.data.data || []);
      } else {
        toast.error(response.data.message || 'Failed to load wishlist items');
        setWishlistItems([]);
      }
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      toast.error(error.response?.data?.message || 'Failed to load wishlist items');
      setWishlistItems([]);
    } finally {
      setLoading(false);
    }
  };

  const removeFromWishlist = async (productId) => {
    try {
      // Change from axios.delete to axios.post with the correct endpoint
      const response = await axios.post(
        'http://localhost:5000/wishlist/remove',
        { product_id: productId },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data.success) {
        toast.success('Item removed from wishlist');
        setWishlistItems(wishlistItems.filter(item => item.id !== productId));
        
        // Update wishlist count
        const newCount = wishlistItems.length - 1;
        localStorage.setItem('wishlistCount', newCount.toString());
        window.dispatchEvent(new CustomEvent('wishlistUpdated'));
      } else {
        toast.error(response.data.message || 'Failed to remove item from wishlist');
      }
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      toast.error(error.response?.data?.message || 'Failed to remove item from wishlist');
    }
  };

  const addToCart = async (productId) => {
    try {
      const response = await axios.post('http://localhost:5000/cart/add', 
        { product_id: productId, quantity: 1 },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data.success) {
        toast.success('Item added to cart');
        
        // Update cart count
        window.dispatchEvent(new Event('cartUpdated'));
        
        // Optionally remove from wishlist after adding to cart
        // removeFromWishlist(productId);
      } else {
        toast.error(response.data.message || 'Failed to add item to cart');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      toast.error(error.response?.data?.message || 'Failed to add item to cart');
    }
  };

  const handleProductClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  if (loading) {
    return <div className={styles.loading}>Loading wishlist...</div>;
  }

  return (
    <div className={styles.wishlistContainer}>
      <h1 className={styles.title}>My Wishlist</h1>
      
      {wishlistItems.length === 0 ? (
        <div className={styles.emptyWishlist}>
          <p>Your wishlist is empty.</p>
          <button 
            className={styles.shopNowButton}
            onClick={() => navigate('/products')}
          >
            Shop Now
          </button>
        </div>
      ) : (
        <div className={styles.wishlistGrid}>
          {wishlistItems.map(item => (
            <div key={item.id} className={styles.wishlistItem}>
              <div 
                className={styles.imageContainer}
                onClick={() => handleProductClick(item.id)}
              >
                <img 
                  src={getProductImageUrl(item.image_url)} 
                  alt={item.product_name}
                  onError={(e) => {
                    e.target.src = '/src/assets/images/placeholder.svg';
                  }}
                />
              </div>
              
              <div className={styles.itemDetails}>
                <h3 
                  className={styles.productName}
                  onClick={() => handleProductClick(item.id)}
                >
                  {item.product_name}
                </h3>
                
                <div className={styles.priceContainer}>
                  {item.discount > 0 ? (
                    <>
                      <span className={styles.discountedPrice}>
                        ${(item.price * (1 - item.discount/100)).toFixed(2)}
                      </span>
                      <span className={styles.originalPrice}>
                        ${item.price.toFixed(2)}
                      </span>
                    </>
                  ) : (
                    <span className={styles.price}>${item.price.toFixed(2)}</span>
                  )}
                </div>
                
                <div className={styles.actions}>
                  <button 
                    className={styles.addToCartButton}
                    onClick={() => addToCart(item.id)}
                  >
                    <FaShoppingCart /> Add to Cart
                  </button>
                  
                  <button 
                    className={styles.removeButton}
                    onClick={() => removeFromWishlist(item.id)}
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Wishlist;

