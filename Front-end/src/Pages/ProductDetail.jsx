import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import AddToCart from '../components/AddToCart';
import { useAuth } from '../context/AuthContext'; // Assuming you have an auth context

const ProductDetail = () => {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const { token, isAuthenticated } = useAuth();

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/products/${productId}`);
        setProduct(response.data);
      } catch (error) {
        console.error('Error fetching product:', error);
        toast.error('Failed to load product details');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId]);

  if (loading) return <div className="loading">Loading...</div>;
  if (!product) return <div className="error">Product not found</div>;

  return (
    <div className="product-detail-container">
      <div className="product-image">
        <img src={product.image_url} alt={product.product_name} />
      </div>
      <div className="product-info">
        <h1>{product.product_name}</h1>
        <p className="description">{product.description}</p>
        <div className="price-container">
          {product.discount > 0 ? (
            <>
              <span className="original-price">${product.price}</span>
              <span className="discounted-price">
                ${(product.price * (1 - product.discount / 100)).toFixed(2)}
              </span>
              <span className="discount-badge">{product.discount}% OFF</span>
            </>
          ) : (
            <span className="price">${product.price}</span>
          )}
        </div>
        <p className="stock">In Stock: {product.stock}</p>
        
        {isAuthenticated ? (
          <AddToCart productId={product.id} token={token} />
        ) : (
          <p className="login-prompt">Please log in to add items to your cart</p>
        )}
      </div>
    </div>
  );
};

export default ProductDetail;
