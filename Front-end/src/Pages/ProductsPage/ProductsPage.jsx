import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styles from './ProductsPage.module.css';
import axios from 'axios';
import { FaStar, FaShoppingCart, FaEye, FaFilter, FaSearch, FaSortAmountDown, FaTimes, FaTag} from 'react-icons/fa';
import AddToCart from '../../Components/AddToCart/AddToCart';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'react-toastify';

const ProductsPage = () => {
  // Add a fallback for when useAuth() returns undefined
  const auth = useAuth() || { isAuthenticated: false, token: null };
  const { isAuthenticated, token } = auth;
  const [products, setProducts] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [categoryName, setCategoryName] = useState('All Products');
  const [showFilters, setShowFilters] = useState(false);
  const [priceRange, setPriceRange] = useState([0, 1000]);
  const [sortOption, setSortOption] = useState('default');
  const [searchTerm, setSearchTerm] = useState('');
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Function to handle quick view
  const handleQuickView = (productId) => {
    navigate(`/products/${productId}`);
  };

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
          setAllProducts(response.data.products);
          setProducts(response.data.products);
          
          // Set category name based on the first product's category
          if (categoryId && response.data.products.length > 0) {
            setCategoryName(response.data.products[0].category_name);
            // If a category is selected from URL, preselect it in filters
            setSelectedCategories([parseInt(categoryId)]);
          } else {
            setCategoryName('All Products');
          }

          // Find max price for range filter
          if (response.data.products.length > 0) {
            const maxPrice = Math.max(...response.data.products.map(p => p.price));
            setPriceRange([0, Math.ceil(maxPrice)]);
          }
          
          // Extract unique categories from products
          const uniqueCategories = [];
          const categoryIds = new Set();
          
          response.data.products.forEach(product => {
            if (product.category_id && !categoryIds.has(product.category_id)) {
              categoryIds.add(product.category_id);
              uniqueCategories.push({
                id: product.category_id,
                name: product.category_name
              });
            }
          });
          
          setCategories(uniqueCategories);
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

  // Handle category selection
  const handleCategoryChange = (categoryId) => {
    setSelectedCategories(prev => {
      if (prev.includes(categoryId)) {
        return prev.filter(id => id !== categoryId);
      } else {
        return [...prev, categoryId];
      }
    });
  };

  // Apply filters and sorting
  useEffect(() => {
    let filteredProducts = [...allProducts];
    
    // Apply search filter
    if (searchTerm) {
      filteredProducts = filteredProducts.filter(product => 
        product.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Apply category filter
    if (selectedCategories.length > 0) {
      filteredProducts = filteredProducts.filter(product => 
        selectedCategories.includes(product.category_id)
      );
    }
    
    // Apply price filter
    filteredProducts = filteredProducts.filter(product => 
      product.price >= priceRange[0] && product.price <= priceRange[1]
    );
    
    // Apply sorting
    switch(sortOption) {
      case 'price-asc':
        filteredProducts.sort((a, b) => a.price - b.price);
        break;
      case 'price-desc':
        filteredProducts.sort((a, b) => b.price - a.price);
        break;
      case 'name-asc':
        filteredProducts.sort((a, b) => a.product_name.localeCompare(b.product_name));
        break;
      case 'name-desc':
        filteredProducts.sort((a, b) => b.product_name.localeCompare(a.product_name));
        break;
      default:
        // Default sorting (newest first or featured)
        break;
    }
    
    setProducts(filteredProducts);
  }, [allProducts, searchTerm, priceRange, sortOption, selectedCategories]);

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

  const handlePriceChange = (e, index) => {
    const newRange = [...priceRange];
    newRange[index] = Number(e.target.value);
    setPriceRange(newRange);
  };

  const handlePriceStep = (index, step) => {
    const newRange = [...priceRange];
    newRange[index] = Math.max(0, Number(newRange[index]) + step);
    
    // Ensure min doesn't exceed max
    if (index === 0 && newRange[0] > newRange[1]) {
      newRange[0] = newRange[1];
    }
    
    // Ensure max doesn't go below min
    if (index === 1 && newRange[1] < newRange[0]) {
      newRange[1] = newRange[0];
    }
    
    setPriceRange(newRange);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSortOption('default');
    setSelectedCategories([]);
    // Reset price range to initial values
    const maxPrice = Math.max(...allProducts.map(p => p.price));
    setPriceRange([0, Math.ceil(maxPrice)]);
  };

  const CustomSortDropdown = () => {
    const options = [
      { value: 'default', label: 'Featured Products' },
      { value: 'price-asc', label: 'Price: Low to High' },
      { value: 'price-desc', label: 'Price: High to Low' },
      { value: 'name-asc', label: 'Name: A to Z' },
      { value: 'name-desc', label: 'Name: Z to A' }
    ];

    const handleOptionClick = (value) => {
      setSortOption(value);
      setIsDropdownOpen(false);
    };

    return (
      <div className={styles.customDropdown}>
        <div 
          className={styles.dropdownHeader} 
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        >
          <FaSortAmountDown className={styles.sortIcon} />
          <span>{options.find(opt => opt.value === sortOption)?.label}</span>
          <div className={styles.dropdownArrow}>
            {isDropdownOpen ? '▲' : '▼'}
          </div>
        </div>
        {isDropdownOpen && (
          <div className={styles.dropdownList}>
            {options.map(option => (
              <div 
                key={option.value}
                className={`${styles.dropdownItem} ${sortOption === option.value ? styles.selected : ''}`}
                onClick={() => handleOptionClick(option.value)}
              >
                {option.label}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  if (loading) return <div className={styles.loading}>Loading products...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={styles.productsPage}>
      <div className={styles.sectionHeader}>
        <h2 className={styles.sectionTitle}>Our All Products</h2>
        <p className={styles.sectionSubtitle}>Explore our delicious selection of treats</p>
      </div>
      
      <div className={styles.controlsContainer}>
        <div className={styles.searchContainer}>
          <FaSearch className={styles.searchIcon} />
          <input 
            type="text" 
            placeholder="Search for delicious treats..." 
            className={styles.searchInput}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button 
              className={styles.clearSearch} 
              onClick={() => setSearchTerm('')}
              aria-label="Clear search"
            >
              <FaTimes />
            </button>
          )}
        </div>
        
        <div className={styles.filterSortControls}>
          <button 
            className={`${styles.filterButton} ${showFilters ? styles.active : ''}`} 
            onClick={() => setShowFilters(!showFilters)}
          >
            <FaFilter /> Filters
          </button>
          
          <div className={styles.sortContainer}>
            <CustomSortDropdown />
          </div>
        </div>
      </div>
      
      {showFilters && (
        <div className={styles.filtersPanel}>
          <div className={styles.filtersHeader}>
            <h2 className={styles.filtersTitle}>
              <FaFilter style={{ color: 'var(--secondary-color)' }} /> Refine Results
            </h2>
            <button 
              className={styles.closeFilters} 
              onClick={() => setShowFilters(false)}
              aria-label="Close filters"
            >
              <FaTimes />
            </button>
          </div>
          
          <div className={styles.filterGroup}>
            <h3>
              <FaTag /> Categories
            </h3>
            <div className={styles.categoryCheckboxes}>
              {categories.map(category => (
                <div key={category.id} className={styles.categoryCheckbox}>
                  <input
                    type="checkbox"
                    id={`category-${category.id}`}
                    checked={selectedCategories.includes(category.id)}
                    onChange={() => handleCategoryChange(category.id)}
                  />
                  <label htmlFor={`category-${category.id}`}>
                    {category.name}
                  </label>
                </div>
              ))}
            </div>
          </div>
          
          <div className={styles.filterGroup}>
            <h3>
              <FaSortAmountDown /> Price Range
            </h3>
            <div className={styles.priceInputs}>
              <div className={styles.priceInput}>
                <label>Min ($)</label>
                <input 
                  type="number" 
                  value={priceRange[0]} 
                  onChange={(e) => handlePriceChange(e, 0)}
                  min="0"
                />
              </div>
              <div className={styles.priceInput}>
                <label>Max ($)</label>
                <input 
                  type="number" 
                  value={priceRange[1]} 
                  onChange={(e) => handlePriceChange(e, 1)}
                  min={priceRange[0]}
                />
              </div>
            </div>
            <input
              type="range"
              min="0"
              max={Math.max(...allProducts.map(p => p.price))}
              value={priceRange[1]}
              onChange={(e) => handlePriceChange(e, 1)}
              className={styles.priceSlider}
            />
          </div>
          
          <button className={styles.clearFiltersBtn} onClick={clearFilters}>
            Clear All Filters
          </button>
        </div>
      )}
      
      <div className={styles.resultsInfo}>
        <span>Showing {products.length} products</span>
      </div>
      
      {products.length === 0 ? (
        <div className={styles.noProducts}>
          <h3>No products found</h3>
          <p>Try adjusting your filters or search criteria</p>
          <button className={styles.clearFiltersBtn} onClick={clearFilters}>
            Clear All Filters
          </button>
        </div>
      ) : (
        <div className={styles.productsGrid}>
          {products.map(product => (
            <div key={product.id} className={styles.productCard}>
              {product.discount > 0 && (
                <div className={styles.discountBadge}>
                  {product.discount}% OFF
                </div>
              )}
              
              <div className={styles.imageContainer}>
                <img 
                  src={getProductImageUrl(product.image_url)} 
                  alt={product.product_name}
                  className={styles.productImage}
                  onError={(e) => {
                    e.target.src = '/src/assets/images/placeholder.svg';
                  }}
                />
                <div className={styles.overlay}>
                  <button 
                    className={styles.quickView}
                    onClick={() => handleQuickView(product.id)}
                  >
                    <FaEye style={{ marginRight: '6px' }} /> Quick View
                  </button>
                </div>
              </div>
              
              <div className={styles.productInfo}>
                <div className={styles.categoryBadge}>{product.category_name}</div>
                <h3 className={styles.productName}>{product.product_name}</h3>
                
                <div className={styles.productMeta}>
                  <div className={styles.priceContainer}>
                    {product.discount > 0 && (
                      <span className={styles.originalPrice}>${product.price.toFixed(2)}</span>
                    )}
                    <span className={styles.productPrice}>
                      ${product.discount > 0 
                        ? (product.price * (1 - product.discount/100)).toFixed(2) 
                        : product.price.toFixed(2)}
                    </span>
                  </div>
                  
                  <div className={styles.productRating}>
                    <span className={styles.ratingValue}>4.5</span>
                    <FaStar className={styles.ratingIcon} />
                  </div>
                </div>
                
                <button 
                  className={styles.addToCartBtn}
                  onClick={() => {
                    const token = localStorage.getItem('token');
                    if (token) {
                      // Add to cart logic
                      addToCart(product.id, token);
                    } else {
                      toast.info('Please log in to add items to cart');
                    }
                  }}
                >
                  <FaShoppingCart style={{ marginRight: '8px' }} /> Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const addToCart = async (productId, token) => {
  try {
    // Log token for debugging
    console.log('Token available:', !!token);
    if (!token) {
      toast.info('Please log in to add items to cart');
      return;
    }
    
    const response = await axios.post(
      'http://localhost:5000/cart/add',
      { product_id: productId, quantity: 1 },
      { 
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        } 
      }
    );
    
    if (response.data.success) {
      toast.success('Added to cart!');
      
      // Dispatch event to update cart count immediately
      const currentCount = parseInt(localStorage.getItem('cartCount') || '0');
      const newCount = currentCount + 1;
      localStorage.setItem('cartCount', newCount.toString());
      
      const cartCountEvent = new CustomEvent('cartCountUpdated', {
        detail: { count: newCount }
      });
      window.dispatchEvent(cartCountEvent);
    } else {
      toast.error(response.data.message || 'Failed to add to cart');
    }
  } catch (error) {
    console.error('Error adding to cart:', error);
    console.error('Error response:', error.response?.data);
    
    // Check if the error is due to authentication
    if (error.response?.status === 401) {
      toast.error('Authentication failed. Please log in again.');
      // You might want to redirect to login page here
    } else {
      toast.error('Failed to add to cart');
    }
  }
};

export default ProductsPage;
