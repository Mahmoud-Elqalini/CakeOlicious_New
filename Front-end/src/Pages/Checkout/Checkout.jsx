import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FaShoppingCart, FaCreditCard, FaArrowLeft } from 'react-icons/fa';
import styles from './Checkout.module.css';

const Checkout = () => {
  const [cartItems, setCartItems] = useState([]);
  const [totalAmount, setTotalAmount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [shippingAddress, setShippingAddress] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Credit Card');
  
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  
  useEffect(() => {
    if (!token) {
      toast.error('Please log in to proceed with checkout');
      navigate('/signin');
      return;
    }
    
    fetchCheckoutInfo();
  }, [token, navigate]);
  
  const fetchCheckoutInfo = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/checkout', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Checkout info:', response.data);
      
      if (response.data.status === 'success') {
        setCartItems(response.data.cart_items);
        setTotalAmount(response.data.total_amount);
      } else {
        toast.error(response.data.message || 'Failed to load checkout information');
        navigate('/cart');
      }
    } catch (error) {
      console.error('Error fetching checkout info:', error);
      toast.error(error.response?.data?.message || 'Failed to load checkout information');
      navigate('/cart');
    } finally {
      setLoading(false);
    }
  };
  
  const handlePlaceOrder = async () => {
    if (!shippingAddress) {
      toast.error('Please enter a shipping address');
      return;
    }
    
    setProcessing(true);
    try {
      console.log('Starting checkout process...');
      console.log('Shipping address:', shippingAddress);
      console.log('Payment method:', paymentMethod);
      
      // Step 1: Create the order
      console.log('Creating order...');
      const orderResponse = await axios.post(
        'http://localhost:5000/checkout',
        {
          shipping_address: shippingAddress,
          payment_method: paymentMethod
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('Order creation response:', orderResponse.data);
      
      if (orderResponse.data.success) {
        const orderId = orderResponse.data.order_id;
        console.log('Order created successfully with ID:', orderId);
        
        // Step 2: Create Stripe checkout session
        console.log('Creating Stripe checkout session...');
        const sessionResponse = await axios.post(
          'http://localhost:5000/create-checkout-session',
          {
            order_id: orderId
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        console.log('Checkout session response:', sessionResponse.data);
        
        if (sessionResponse.data.success) {
          console.log('Redirecting to Stripe checkout:', sessionResponse.data.url);
          window.location.href = sessionResponse.data.url;
        } else {
          console.error('Failed to create checkout session:', sessionResponse.data.message);
          toast.error(sessionResponse.data.message || 'Failed to create checkout session');
          setProcessing(false);
        }
      } else {
        console.error('Failed to create order:', orderResponse.data.message);
        toast.error(orderResponse.data.message || 'Failed to create order');
        setProcessing(false);
      }
    } catch (error) {
      console.error('Error during checkout:', error);
      
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
        
        toast.error(error.response.data?.message || `Server error: ${error.response.status}`);
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        toast.error('No response from server. Please check your connection.');
      } else {
        // Something happened in setting up the request
        console.error('Error message:', error.message);
        toast.error(`Error: ${error.message}`);
      }
      
      setProcessing(false);
    }
  };
  
  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loader}></div>
        <p>Loading checkout information...</p>
      </div>
    );
  }
  
  return (
    <div className={styles.checkoutContainer}>
      <h1 className={styles.checkoutTitle}>
        <FaShoppingCart /> Checkout
      </h1>
      
      <div className={styles.checkoutContent}>
        <div className={styles.orderSummary}>
          <h2>Order Summary</h2>
          
          <div className={styles.cartItems}>
            {cartItems.length > 0 ? (
              cartItems.map((item, index) => (
                <div key={index} className={styles.cartItem}>
                  <div className={styles.itemInfo}>
                    <h3>{item.product_name}</h3>
                    <p>Quantity: {item.quantity}</p>
                  </div>
                  <div className={styles.itemPrice}>
                    ${item.total_price.toFixed(2)}
                  </div>
                </div>
              ))
            ) : (
              <p>Your cart is empty. Please add items before checkout.</p>
            )}
          </div>
          
          <div className={styles.totalAmount}>
            <span>Total:</span>
            <span>${totalAmount.toFixed(2)}</span>
          </div>
        </div>
        
        <div className={styles.checkoutForm}>
          <h2>Shipping Information</h2>
          
          <div className={styles.formGroup}>
            <label htmlFor="shippingAddress">Shipping Address</label>
            <textarea
              id="shippingAddress"
              className={styles.addressInput}
              value={shippingAddress}
              onChange={(e) => setShippingAddress(e.target.value)}
              placeholder="Enter your full shipping address"
              required
            />
          </div>
          
          <h2>Payment Method</h2>
          
          <div className={styles.paymentOptions}>
            <div className={styles.paymentOption}>
              <input
                type="radio"
                id="creditCard"
                name="paymentMethod"
                value="Credit Card"
                checked={paymentMethod === 'Credit Card'}
                onChange={() => setPaymentMethod('Credit Card')}
              />
              <label htmlFor="creditCard">Credit Card (via Stripe)</label>
            </div>
          </div>
          
          <button
            className={styles.placeOrderBtn}
            onClick={handlePlaceOrder}
            disabled={processing || !shippingAddress || cartItems.length === 0}
          >
            {processing ? (
              <>Processing...</>
            ) : (
              <>
                <FaCreditCard /> Proceed to Payment
              </>
            )}
          </button>
          
          <button
            className={styles.backToCartBtn}
            onClick={() => navigate('/cart')}
            disabled={processing}
          >
            <FaArrowLeft /> Back to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

export default Checkout;


