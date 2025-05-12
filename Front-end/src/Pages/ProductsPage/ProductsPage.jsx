import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import styles from './ProductsPage.module.css';
import axios from 'axios';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [categoryName, setCategoryName] = useState('All Products');
  const location = useLocation();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const queryParams = new URLSearchParams(location.search);
        const categoryId = queryParams.get('category_id');
        
        const url = categoryId 
          ? `http://127.0.0.1:5000/products?category_id=${categoryId}`
          : 'http://127.0.0.1:5000/products';
          
        const response = await axios.get(url);
        
        if (response.data && response.data.products) {
          setProducts(response.data.products);
          
          // Set category name based on the first product's category
          if (response.data.products.length > 0) {
            setCategoryName(response.data.products[0].category_name);
          } else {
            setCategoryName('All Products');
          }
        }
      } catch (err) {
        setError('Failed to fetch products. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [location.search]);

  if (loading) return <div className={styles.loading}>Loading products...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={styles.productsPage}>
      <h1>{categoryName}</h1>
      {products.length === 0 ? (
        <p>No products found.</p>
      ) : (
        <div className={styles.productsGrid}>
          {products.map(product => (
            <div key={product.id} className={styles.productCard}>
              <img src={product.image_url} alt={product.product_name} />
              <h3>{product.product_name}</h3>
              <p>{product.product_description}</p>
              <p className={styles.price}>
                ${product.discount > 0 
                  ? (product.price * (1 - product.discount/100)).toFixed(2) 
                  : product.price.toFixed(2)}
                {product.discount > 0 && 
                  <span className={styles.originalPrice}>${product.price.toFixed(2)}</span>}
              </p>
              <button>Add to Cart</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductsPage;
