import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FaCheckCircle, FaArrowRight } from 'react-icons/fa';
import styles from './OrderSuccess.module.css';

const OrderSuccess = () => {
  const [loading, setLoading] = useState(true);
  const [orderDetails, setOrderDetails] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) {
      toast.error('Please log in to view order details');
      navigate('/login');
      return;
    }

    const queryParams = new URLSearchParams(location.search);
    const orderId = queryParams.get('order_id');
    const sessionId = queryParams.get('session_id');

    if (!orderId) {
      toast.error('Order ID not found');
      navigate('/account');
      return;
    }

    fetchOrderDetails(orderId);
  }, [location, navigate, token]);

  const fetchOrderDetails = async (orderId) => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/order/${orderId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('Order details:', response.data);

      if (response.data.status === 'success') {
        setOrderDetails({
          order: response.data.order,
          orderItems: response.data.order_items
        });
      } else {
        toast.error(response.data.message || 'Failed to load order details');
        navigate('/account');
      }
    } catch (error) {
      console.error('Error fetching order details:', error);
      toast.error(error.response?.data?.message || 'Failed to load order details');
      navigate('/account');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loader}></div>
        <p>Loading order details...</p>
      </div>
    );
  }

  return (
    <div className={styles.successContainer}>
      <div className={styles.successCard}>
        <div className={styles.successHeader}>
          <FaCheckCircle className={styles.successIcon} />
          <h className={styles.successTitle}>Order Placed Successfully</h>
        </div>
        <p className={styles.successMessage}>
          Thank you for your order! Your order has been placed successfully.
        </p>
        <div className={styles.orderDetails}>
          <h2 className={styles.orderDetailsTitle}>Order Details</h2>
          <div className={styles.orderInfo}>
            <p>Order ID: {orderDetails?.order.id}</p>
            <p>Order Date: {orderDetails?.order.order_date}</p>
            <p>Total Amount: ${orderDetails?.order.total_amount.toFixed(2)}</p>
            <p>Status: {orderDetails?.order.status}</p>
          </div>
        </div>
        <button
          className={styles.backToAccountBtn}
          onClick={() => navigate('/account')}
        >
          <FaArrowLeft /> Back to Account
        </button>
      </div>
    </div>
  );
};

export default OrderSuccess;