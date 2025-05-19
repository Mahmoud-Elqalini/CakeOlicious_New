import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FaTrash, FaMinus, FaPlus, FaArrowLeft, FaCreditCard } from 'react-icons/fa';
import { useAuth } from '../../context/AuthContext';
import styles from './Cart.module.css';

const Cart = () => {
  const { isAuthenticated, token } = useAuth();
  const navigate = useNavigate();
  const [cartItems, setCartItems] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/signin');
      return;
    }
    fetchCartItems();
  }, [isAuthenticated, token, navigate]);

  const fetchCartItems = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/cart', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Cart response:', response.data);
      
      if (response.data.success) {
        // Ensure each item has a cart_item_id
        const items = response.data.data || [];
        const processedItems = items.map(item => {
          console.log('Cart item:', item);
          if (!item.cart_item_id) {
            console.warn('Item missing cart_item_id:', item);
          }
          return item;
        });
        
        setCartItems(processedItems);
        setTotalPrice(response.data.total_price || 0);
      } else {
        toast.error(response.data.message || 'Failed to load cart items');
        setCartItems([]);
        setTotalPrice(0);
      }
    } catch (error) {
      console.error('Error fetching cart:', error);
      toast.error(error.response?.data?.message || 'Failed to load cart items');
      setCartItems([]);
      setTotalPrice(0);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateQuantity = async (cartItemId, change) => {
    setUpdating(true);
    try {
      console.log('Updating quantity for cart item ID:', cartItemId, 'Change:', change);
      
      if (!cartItemId) {
        console.error('Cart item ID is undefined or null');
        toast.error('Cannot update quantity: Missing cart item ID');
        return;
      }
      
      const response = await axios.post(
        'http://localhost:5000/cart/update',
        { 
          cart_item_id: cartItemId, 
          change: change 
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('Update quantity response:', response.data);
      
      if (response.data.success) {
        toast.success(response.data.message || 'Quantity updated');
        fetchCartItems();
      } else {
        toast.error(response.data.message || 'Failed to update quantity');
      }
    } catch (error) {
      console.error('Error updating quantity:', error);
      console.error('Error response:', error.response?.data);
      toast.error(error.response?.data?.message || 'Failed to update quantity');
    } finally {
      setUpdating(false);
    }
  };

  const handleRemoveItem = async (cartItemId) => {
    setUpdating(true);
    try {
      console.log('Removing cart item with ID:', cartItemId);
      
      if (!cartItemId) {
        console.error('Cart item ID is undefined or null');
        toast.error('Cannot remove item: Missing cart item ID');
        return;
      }
      
      const response = await axios.post(
        'http://localhost:5000/cart/remove',
        { cart_item_id: cartItemId },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('Remove item response:', response.data);
      toast.success(response.data.message || 'Item removed from cart');
      fetchCartItems();
    } catch (error) {
      console.error('Error removing item:', error);
      console.error('Error response:', error.response?.data);
      toast.error(error.response?.data?.message || 'Failed to remove item');
    } finally {
      setUpdating(false);
    }
  };

  const handleCheckout = () => {
    navigate('/checkout');
  };

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loader}></div>
        <p>Loading your cart...</p>
      </div>
    );
  }

  if (cartItems.length === 0) {
    return (
      <div className={styles.emptyCartContainer}>
        <h2>Your Cart is Empty</h2>
        <p>Looks like you haven't added any items to your cart yet.</p>
        <Link to="/products" className={styles.continueShoppingBtn}>
          <FaArrowLeft style={{ marginRight: '8px' }} />
          Continue Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className={styles.cartContainer}>
      <h1 className={styles.cartTitle}>Your Shopping Cart</h1>
      
      <div className={styles.cartContent}>
        <div className={styles.cartItems}>
          <div className={styles.cartHeader}>
            <span className={styles.productColumn}>Product</span>
            <span className={styles.priceColumn}>Price</span>
            <span className={styles.quantityColumn}>Quantity</span>
            <span className={styles.totalColumn}>Total</span>
            <span className={styles.actionColumn}></span>
          </div>
          
          {cartItems.map((item) => (
            <div key={item.cart_item_id} className={styles.cartRow}>
              <div className={styles.productColumn}>
                <div className={styles.productInfo}>
                  <h3>{item.product_name}</h3>
                </div>
              </div>
              
              <div className={styles.priceColumn}>
                ${item.unit_price.toFixed(2)}
                {item.discount > 0 && (
                  <span className={styles.discountBadge}>-{item.discount}%</span>
                )}
              </div>
              
              <div className={styles.quantityColumn}>
                <div className={styles.quantityControls}>
                  <button 
                    className={styles.quantityBtn}
                    onClick={() => {
                      console.log('Decrease quantity for item:', item);
                      console.log('Cart item ID:', item.cart_item_id);
                      handleUpdateQuantity(item.cart_item_id, -1);
                    }}
                    disabled={updating || item.quantity <= 1}
                  >
                    <FaMinus />
                  </button>
                  <span className={styles.quantityValue}>{item.quantity}</span>
                  <button 
                    className={styles.quantityBtn}
                    onClick={() => {
                      console.log('Increase quantity for item:', item);
                      console.log('Cart item ID:', item.cart_item_id);
                      handleUpdateQuantity(item.cart_item_id, 1);
                    }}
                    disabled={updating}
                  >
                    <FaPlus />
                  </button>
                </div>
              </div>
              
              <div className={styles.totalColumn}>
                ${(item.quantity * item.unit_price * (1 - item.discount / 100)).toFixed(2)}
              </div>
              
              <div className={styles.actionColumn}>
                <button 
                  className={styles.removeBtn}
                  onClick={() => {
                    console.log('Remove button clicked for item:', item);
                    console.log('Cart item ID:', item.cart_item_id);
                    handleRemoveItem(item.cart_item_id);
                  }}
                  disabled={updating}
                >
                  <FaTrash />
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className={styles.cartSummary}>
          <h2>Order Summary</h2>
          <div className={styles.summaryRow}>
            <span>Subtotal:</span>
            <span>${totalPrice.toFixed(2)}</span>
          </div>
          <div className={styles.summaryRow}>
            <span>Shipping:</span>
            <span>Free</span>
          </div>
          <div className={styles.summaryTotal}>
            <span>Total:</span>
            <span>${totalPrice.toFixed(2)}</span>
          </div>
          
          <button 
            className={styles.checkoutBtn}
            onClick={handleCheckout}
            disabled={updating}
          >
            <FaCreditCard style={{ marginRight: '8px' }} />
            Proceed to Checkout
          </button>
          
          <Link to="/products" className={styles.continueShoppingLink}>
            <FaArrowLeft style={{ marginRight: '8px' }} />
            Continue Shopping
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Cart
