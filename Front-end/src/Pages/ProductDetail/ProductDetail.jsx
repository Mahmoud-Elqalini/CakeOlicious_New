import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import AddToCart from '../../Components/AddToCart/AddToCart';
import { useAuth } from '../../context/AuthContext';
import styles from './ProductDetail.module.css';
import { FaHeart } from 'react-icons/fa';

const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const { token, isAuthenticated } = useAuth();

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        // Try to get product from the products endpoint
        const response = await axios.get(`http://localhost:5000/products`, {
          params: { id: productId }
        });
        
        if (response.data && response.data.products) {
          // Find the product with matching ID
          const foundProduct = response.data.products.find(
            p => p.id.toString() === productId.toString()
          );
          
          if (foundProduct) {
            setProduct(foundProduct);
          } else {
            toast.error('Product not found');
          }
        } else {
          toast.error('Failed to load product details');
        }
      } catch (error) {
        console.error('Error fetching product:', error);
        toast.error('Failed to load product details');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId]);

  if (loading) return <div className={styles.loading}>Loading...</div>;
  if (!product) return <div className={styles.error}>Product not found</div>;

  // Helper function to get product image URL
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

  const addToWishlist = async () => {
    if (!isAuthenticated) {
      toast.info('Please sign in to add items to your wishlist');
      navigate('/signin');
      return;
    }

    try {
      console.log('Adding to wishlist, product ID:', productId);
      const response = await axios.post(
        'http://localhost:5000/wishlist/add',
        { product_id: productId },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        toast.success('Added to wishlist');
        // Update wishlist count
        window.dispatchEvent(new Event('wishlistUpdated'));
      } else {
        toast.error(response.data.message || 'Failed to add to wishlist');
      }
    } catch (error) {
      console.error('Error adding to wishlist:', error);
      console.error('Error response data:', error.response?.data);
      
      if (error.response?.data?.error) {
        toast.error(`Server error: ${error.response.data.error}`);
      } else if (error.response?.data?.message) {
        toast.error(error.response.data.message);
      } else {
        toast.error('Failed to add to wishlist. Server error occurred.');
      }
    }
  };

  return (
    <div className={styles.productDetailContainer}>
      <div className={styles.productImage}>
        <img src={getProductImageUrl(product.image_url)} alt={product.product_name} />
      </div>
      <div className={styles.productInfo}>
        <h1>{product.product_name}</h1>
        <p className={styles.description}>{product.description || product.product_description}</p>
        <div className={styles.priceContainer}>
          {product.discount > 0 ? (
            <>
              <span className={styles.originalPrice}>${product.price}</span>
              <span className={styles.discountedPrice}>
                ${(product.price * (1 - product.discount / 100)).toFixed(2)}
              </span>
              <span className={styles.discountBadge}>{product.discount}% OFF</span>
            </>
          ) : (
            <span className={styles.price}>${product.price}</span>
          )}
        </div>
        <p className={styles.stock}>In Stock: {product.stock}</p>
        
        {isAuthenticated ? (
          <AddToCart productId={product.id || product.product_id} token={token} />
        ) : (
          <p className={styles.loginPrompt}>Please log in to add items to your cart</p>
        )}
        <button 
          className={styles.wishlistButton} 
          onClick={addToWishlist}
        >
          <FaHeart /> Add to Wishlist
        </button>
      </div>
    </div>
  );
};

export default ProductDetail;








