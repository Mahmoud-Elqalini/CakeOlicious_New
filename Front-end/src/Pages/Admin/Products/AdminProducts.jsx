import React, { useState, useEffect, useRef, useMemo } from 'react';
import axios from 'axios';
import styles from './AdminProducts.module.css';
import { toast } from 'react-toastify';
import {
    FaEdit,
    FaTrash,
    FaPlus,
    FaSearch,
    FaFilter,
    FaTimes,
    FaEye,
    FaEyeSlash,
    FaArrowLeft,
    FaUpload,
    FaImage,
    FaBox,
    FaDollarSign,
    FaTag,
    FaCheck,
    FaThLarge,
    FaList,
    FaChevronLeft,
    FaChevronRight
} from 'react-icons/fa';
import { motion } from 'framer-motion';
// import { useDropzone } from 'react-dropzone';

// Import the ProductForm component
import ProductForm from './ProductForm';
import AdminNav from '../../../Components/AdminNav/AdminNav';

const AdminProducts = () => {
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [editingProduct, setEditingProduct] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');
    const [animateItem, setAnimateItem] = useState(null);
    const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
    const [currentPage, setCurrentPage] = useState(1);
    const [productsPerPage] = useState(8);

    // Form state
    const [formData, setFormData] = useState({
        product_name: '',
        description: '', // Changed from product_description to match backend
        price: '',
        stock: '',
        category_id: '',
        image_url: '',
        discount: 0
    });

    // Ref for file input
    const fileInputRef = useRef(null);

    // Add this function before the useEffect that calls it
    const fetchProducts = async () => {
        setLoading(true);
        setError(null);

        try {
            console.log("Fetching products...");
            const token = localStorage.getItem('token');
            
            if (!token) {
                throw new Error('Authentication token not found');
            }
            
            console.log("Making request to: http://localhost:5000/admin/products");
            const response = await axios.get('http://localhost:5000/admin/products', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            console.log("Products response:", response.data);

            if (response.data && response.data.products) {
                console.log(`Received ${response.data.products.length} products`);
                setProducts(response.data.products);
                
                // Also fetch categories for the filter
                try {
                    const categoriesResponse = await axios.get('http://localhost:5000/categories');
                    console.log("Categories response:", categoriesResponse.data);
                    setCategories(categoriesResponse.data.categories || []);
                } catch (categoryErr) {
                    console.error('Error fetching categories:', categoryErr);
                }
            } else {
                throw new Error('Invalid response format');
            }
        } catch (err) {
            console.error('Error fetching products:', err);
            setError(`Failed to load products: ${err.message}`);
            toast.error(`Failed to load products: ${err.response?.data?.message || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    // Fetch products on component mount
    useEffect(() => {
        fetchProducts();
    }, []);


    // Function to filter products based on search and category
    const filteredProducts = products.filter(product => {
        const matchesSearch = product.product_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (product.description && product.description.toLowerCase().includes(searchTerm.toLowerCase()));

        const matchesCategory = categoryFilter === '' || product.category_id === parseInt(categoryFilter);

        return matchesSearch && matchesCategory;
    });

    // Calculate pagination values
    const indexOfLastProduct = currentPage * productsPerPage;
    const indexOfFirstProduct = indexOfLastProduct - productsPerPage;
    const currentProducts = filteredProducts.slice(indexOfFirstProduct, indexOfLastProduct);
    const totalPages = Math.ceil(filteredProducts.length / productsPerPage);

    // Update pagination handlers to use the new variables
    const handlePageChange = (pageNumber) => {
        setCurrentPage(pageNumber);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handlePrevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage(currentPage + 1);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    const handleClearSearch = () => {
        setSearchTerm('');
    };

    const handleImageUploaded = (imageUrl) => {
        setFormData(prev => ({
            ...prev,
            image_url: imageUrl
        }));
    };

    const ImageUploader = ({ onImageUploaded, currentImage }) => {
        const [uploading, setUploading] = useState(false);
        const [uploadError, setUploadError] = useState(null);

        const onDrop = useCallback(async (acceptedFiles) => {
            const file = acceptedFiles[0];
            if (!file) return;

            // Validate file type
            const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                toast.error('Invalid file type. Please upload a JPG, PNG, GIF, or WEBP image.');
                return;
            }

            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                toast.error('File too large. Maximum size is 5MB.');
                return;
            }

            setUploading(true);
            setUploadError(null);

            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    throw new Error('Authentication required');
                }

                const formData = new FormData();
                formData.append('image', file);

                const response = await axios.post('http://localhost:5000/admin/upload-image', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.data && response.data.imageUrl) {
                    onImageUploaded(response.data.imageUrl);
                    toast.success('Image uploaded successfully');
                } else {
                    throw new Error('Invalid server response');
                }
            } catch (error) {
                console.error('Upload error:', error);
                setUploadError(error.message);
                toast.error(`Upload failed: ${error.response?.data?.message || error.message}`);
            } finally {
                setUploading(false);
            }
        }, [onImageUploaded]);

        const { getRootProps, getInputProps, isDragActive } = useDropzone({
            onDrop,
            accept: {
                'image/jpeg': ['.jpg', '.jpeg'],
                'image/png': ['.png'],
                'image/gif': ['.gif'],
                'image/webp': ['.webp']
            },
            multiple: false
        });

        return (
            <div className={styles.imageUploadSection}>
                {currentImage ? (
                    <div className={styles.currentImageContainer}>
                        <img
                            src={currentImage.startsWith('http') ? currentImage : `http://localhost:5000${currentImage}`}
                            alt="Product"
                            className={styles.currentImage}
                            onError={(e) => {
                                e.target.src = '/src/assets/images/placeholder.svg';
                            }}
                        />
                        <button
                            type="button"
                            className={styles.removeImageButton}
                            onClick={() => onImageUploaded('')}
                        >
                            <FaTimes /> Remove
                        </button>
                    </div>
                ) : (
                    <div
                        {...getRootProps()}
                        className={`${styles.dropzone} ${isDragActive ? styles.active : ''}`}
                    >
                        <input {...getInputProps()} />
                        {uploading ? (
                            <div className={styles.uploadingIndicator}>
                                <div className={styles.spinner}></div>
                                <p>Uploading...</p>
                            </div>
                        ) : (
                            <>
                                <FaUpload size={32} />
                                <p>{isDragActive ? 'Drop the image here' : 'Drag & drop an image here, or click to select'}</p>
                                {uploadError && <p className={styles.errorText}>{uploadError}</p>}
                            </>
                        )}
                    </div>
                )}
            </div>
        );
    };

    // Add this simple image uploader component with improved error handling
    const SimpleImageUploader = ({ value, onChange }) => {
        const [isUploading, setIsUploading] = useState(false);
        const [previewUrl, setPreviewUrl] = useState(value || '');
        const [localPreview, setLocalPreview] = useState(null); // Separate state for local preview
        const fileInputRef = useRef(null);

        // Effect to handle cleanup of object URLs
        useEffect(() => {
            // Cleanup function to revoke object URL when component unmounts or URL changes
            return () => {
                if (localPreview && localPreview.startsWith('blob:')) {
                    URL.revokeObjectURL(localPreview);
                }
            };
        }, [localPreview]);

        // Function to handle file selection
        const handleFileChange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Basic validation
            const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                toast.error('Please select a valid image file (JPG, PNG, GIF, WEBP)');
                return;
            }

            if (file.size > 5 * 1024 * 1024) {
                toast.error('Image is too large. Maximum size is 5MB.');
                return;
            }

            // Create a preview immediately from the local file
            const objectUrl = URL.createObjectURL(file);
            setLocalPreview(objectUrl);

            // Upload the file
            setIsUploading(true);

            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    throw new Error('Authentication required');
                }

                const formData = new FormData();
                formData.append('image', file);

                console.log('Uploading image...');

                // Correct way to use axios for file upload
                const response = await axios.post('http://localhost:5000/admin/upload-image', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        'Authorization': `Bearer ${token}`
                    }
                });

                console.log('Upload response:', response.data);

                if (response.data.success && response.data.imageUrl) {
                    // Store the server URL
                    setPreviewUrl(response.data.imageUrl);
                    onChange(response.data.imageUrl);
                    toast.success('Image uploaded successfully');
                } else {
                    throw new Error('Invalid server response');
                }
            } catch (error) {
                console.error('Upload error:', error);
                toast.error(`Upload failed: ${error.response?.data?.message || error.message}`);
                // Keep the local preview even if server upload fails
            } finally {
                setIsUploading(false);
            }
        };

        // Function to handle image removal
        const handleRemoveImage = () => {
            if (localPreview && localPreview.startsWith('blob:')) {
                URL.revokeObjectURL(localPreview);
            }
            setLocalPreview(null);
            setPreviewUrl('');
            onChange('');
            // Reset file input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        };

        // Function to get the appropriate image source
        const getImageSource = () => {
            // First priority: use local preview if available
            if (localPreview) {
                return localPreview;
            }

            // Second priority: use server URL if available
            if (previewUrl) {
                // If it's already an absolute URL
                if (previewUrl.startsWith('http')) {
                    return previewUrl;
                }

                // If it's a relative URL from the backend
                return `http://localhost:5000${previewUrl}`;
            }

            // Fallback to placeholder
            return '/src/assets/images/placeholder.svg';
        };

        return (
            <div className={styles.simpleImageUploader}>
                {(localPreview || previewUrl) ? (
                    <div className={styles.imagePreviewContainer}>
                        <img
                            src={getImageSource()}
                            alt="Preview"
                            className={styles.imagePreview}
                            onError={(e) => {
                                console.error("Image failed to load:", getImageSource());
                                e.target.src = '/src/assets/images/placeholder.svg';
                            }}
                        />
                        <div className={styles.imageControls}>
                            <button
                                type="button"
                                className={styles.removeButton}
                                onClick={handleRemoveImage}
                            >
                                Remove Image
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className={styles.uploadPlaceholder}>
                        <FaImage size={40} color="#ccc" />
                        <p>No image selected</p>
                    </div>
                )}

                <div className={styles.uploadControls}>
                    <input
                        type="file"
                        accept="image/jpeg,image/png,image/gif,image/webp"
                        onChange={handleFileChange}
                        ref={fileInputRef}
                        className={styles.fileInput}
                        id="product-image-upload"
                    />
                    <label
                        htmlFor="product-image-upload"
                        className={styles.uploadButton}
                        style={{ opacity: isUploading ? 0.7 : 1, cursor: isUploading ? 'not-allowed' : 'pointer' }}
                    >
                        {isUploading ? 'Uploading...' : 'Select Image'}
                    </label>
                </div>
            </div>
        );
    };

    // Add this helper function to get full image URL
    const getProductImageUrl = (url) => {
        if (!url) return '/src/assets/images/placeholder.svg';

        // If it's already an absolute URL
        if (url.startsWith('http')) {
            return url;
        }

        // If it's a relative URL from the backend
        // Make sure it starts with a slash
        const formattedUrl = url.startsWith('/') ? url : `/${url}`;
        return `http://localhost:5000${formattedUrl}`;
    };

    // Add this function to get stock status
    const getStockStatus = (stock) => {
        if (stock <= 0) return 'outOfStock';
        if (stock < 10) return 'lowStock';
        return 'inStock';
    };

    // Add this function to get stock text
    const getStockText = (stock) => {
        if (stock <= 0) return 'Out of stock';
        if (stock < 10) return 'Low stock';
        return 'In stock';
    };

    const handleAddProduct = () => {
        // Reset form data to defaults
        setFormData({
            product_name: '',
            description: '',
            price: '',
            stock: '',
            category_id: '',
            image_url: '',
            discount: 0
        });

        // Clear any editing state
        setEditingProduct(null);

        // Show the form
        setShowForm(true);

        // Scroll to top for better UX
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleEdit = (product) => {
        // Set the form data with the product's current values
        setFormData({
            product_name: product.product_name,
            description: product.description || '',
            price: product.price,
            stock: product.stock,
            category_id: product.category_id,
            image_url: product.image_url || '',
            discount: product.discount || 0
        });

        // Set the editing product state
        setEditingProduct(product);

        // Show the form
        setShowForm(true);

        // Scroll to top for better UX
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleDelete = async (productId) => {
        if (!window.confirm('Are you sure you want to delete this product?')) {
            return;
        }

        try {
            const token = localStorage.getItem('token');

            await axios.delete(`http://localhost:5000/admin/product/delete/${productId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            // Remove the product from the state
            setProducts(products.filter(product => product.id !== productId));
            toast.success('Product deleted successfully');
        } catch (err) {
            console.error('Error deleting product:', err);
            toast.error('Failed to delete product: ' + (err.response?.data?.message || err.message));
        }
    };

    const handleToggleVisibility = async (productId, isCurrentlyActive) => {
        try {
            const token = localStorage.getItem('token');
            const newStatus = !isCurrentlyActive;

            await axios.post(`http://localhost:5000/admin/product/toggle-visibility/${productId}`,
                { is_active: newStatus },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            // Update the product in the state
            setProducts(products.map(product =>
                product.id === productId
                    ? { ...product, is_active: newStatus }
                    : product
            ));

            // Set animation for the updated item
            setAnimateItem(productId);

            toast.success(`Product ${newStatus ? 'activated' : 'deactivated'} successfully`);
        } catch (err) {
            console.error('Error toggling product visibility:', err);
            toast.error('Failed to update product: ' + (err.response?.data?.message || err.message));
        }
    };

    const resetForm = () => {
        setFormData({
            product_name: '',
            description: '',
            price: '',
            stock: '',
            category_id: '',
            image_url: '',
            discount: 0
        });
        setEditingProduct(null);
        setShowForm(false);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setLoading(true);
            const token = localStorage.getItem('token');

            if (editingProduct) {
                // Update existing product
                await axios.post(
                    `http://localhost:5000/admin/product/update/${editingProduct.id}`,
                    formData,
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }
                );

                // Update the product in the state
                setProducts(products.map(product =>
                    product.id === editingProduct.id
                        ? { ...product, ...formData }
                        : product
                ));

                // Set animation for the updated item
                setAnimateItem(editingProduct.id);

                toast.success('Product updated successfully');
            } else {
                // Add new product
                const response = await axios.post(
                    'http://localhost:5000/admin/product/add',
                    formData,
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }
                );

                // Add the new product to the state
                if (response.data && response.data.product) {
                    setProducts([...products, response.data.product]);

                    // Set animation for the new item
                    setAnimateItem(response.data.product.id);
                }

                toast.success('Product added successfully');
            }

            // Reset form and hide it
            resetForm();
        } catch (err) {
            console.error('Error saving product:', err);
            toast.error('Failed to save product: ' + (err.response?.data?.message || err.message));
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const CustomCategorySelect = ({ categories, value, onChange }) => {
        const [isOpen, setIsOpen] = useState(false);
        const [selectedId, setSelectedId] = useState(value);
        const dropdownRef = useRef(null);

        // Close dropdown when clicking outside
        useEffect(() => {
            const handleClickOutside = (event) => {
                if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                    setIsOpen(false);
                }
            };

            document.addEventListener('mousedown', handleClickOutside);
            return () => {
                document.removeEventListener('mousedown', handleClickOutside);
            };
        }, []);

        // Update when value changes externally
        useEffect(() => {
            setSelectedId(value);
        }, [value]);

        const handleSelect = (categoryId) => {
            setSelectedId(categoryId);
            onChange({ target: { name: 'category_id', value: categoryId } });
            setIsOpen(false);
        };

        const selectedCategory = categories.find(c => c.id === parseInt(selectedId)) || {};

        return (
            <div className={`${styles.categorySelectWrapper} ${isOpen ? styles.open : ''}`} ref={dropdownRef}>
                <div
                    className={styles.modernSelect}
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {selectedCategory.category_name || 'Select a category'}
                </div>

                {isOpen && (
                    <div className={styles.customDropdownList}>
                        <div
                            className={`${styles.dropdownItem} ${!selectedId ? styles.selected : ''}`}
                            onClick={() => handleSelect('')}
                        >
                            Select a category
                        </div>

                        {categories.map(category => (
                            <div
                                key={category.id}
                                className={`${styles.dropdownItem} ${parseInt(selectedId) === category.id ? styles.selected : ''}`}
                                onClick={() => handleSelect(category.id)}
                            >
                                {category.category_name}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    const DashboardCategoryFilter = ({ categories, value, onChange }) => {
        const [isOpen, setIsOpen] = useState(false);
        const dropdownRef = useRef(null);

        // Close dropdown when clicking outside - optimized event listener
        useEffect(() => {
            const handleClickOutside = (event) => {
                if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                    setIsOpen(false);
                }
            };

            if (isOpen) {
                document.addEventListener('mousedown', handleClickOutside);
                return () => document.removeEventListener('mousedown', handleClickOutside);
            }
        }, [isOpen]);

        const handleSelect = (categoryId) => {
            onChange(categoryId);
            setIsOpen(false);
        };

        // Find selected category efficiently
        const selectedCategory = useMemo(() => {
            return categories.find(c => c.id === parseInt(value)) || {};
        }, [categories, value]);

        return (
            <div className={`${styles.categoryFilter} ${isOpen ? styles.open : ''}`} ref={dropdownRef}>
                <FaFilter />
                <div
                    className={styles.filterDisplay}
                    onClick={() => setIsOpen(!isOpen)}
                    title={selectedCategory.category_name || 'All Categories'} // Add tooltip for truncated text
                >
                    {selectedCategory.category_name || 'All Categories'}
                </div>

                {isOpen && (
                    <div className={styles.dashboardDropdownList}>
                        <div
                            className={`${styles.dashboardDropdownItem} ${value === '' ? styles.selected : ''}`}
                            onClick={() => handleSelect('')}
                        >
                            All Categories
                        </div>

                        {categories.map(category => (
                            <div
                                key={category.id}
                                className={`${styles.dashboardDropdownItem} ${parseInt(value) === category.id ? styles.selected : ''}`}
                                onClick={() => handleSelect(category.id.toString())}
                            >
                                {category.category_name}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    // Add a function to get the product status class
    const getProductStatusClass = (isActive) => {
        return isActive ? styles.activeProduct : styles.inactiveProduct;
    };

    return (
        <div className={styles.adminLayout}>
            <AdminNav />

            <div className={styles.mainContent}>
                <div className={styles.adminProductsContainer}>
                    { }
                    <div className={styles.header}>
                        <h1>Manage Products</h1>
                        {!showForm && (
                            <button className={styles.addButton} onClick={handleAddProduct}>
                                <FaPlus /> Add New Product
                            </button>
                        )}
                    </div>

                    {showForm ? (
                        <motion.div
                            className={styles.productForm}
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            <div className={styles.formHeader}>
                                <button className={styles.backButton} onClick={resetForm}>
                                    <FaArrowLeft /> Back to Products
                                </button>
                                <h2>{editingProduct ? 'Edit Product' : 'Add New Product'}</h2>
                                <div style={{ width: '24px' }}></div> { }
                            </div>

                            <form onSubmit={handleSubmit}>
                                <div className={styles.formGrid}>
                                    { }
                                    <div className={styles.formColumn}>
                                        <div className={styles.formSection}>
                                            <h3 className={styles.sectionTitle}>
                                                <FaTag /> Basic Information
                                            </h3>

                                            { }
                                            <div className={styles.formGroup}>
                                                <label htmlFor="product_name">
                                                    <FaTag /> Product Name *
                                                </label>
                                                <input
                                                    type="text"
                                                    id="product_name"
                                                    name="product_name"
                                                    className={styles.modernInput}
                                                    value={formData.product_name}
                                                    onChange={handleInputChange}
                                                    required
                                                    placeholder="Enter product name"
                                                />
                                            </div>

                                            { }
                                            <div className={styles.formRow}>
                                                <div className={styles.formGroup}>
                                                    <label htmlFor="price">
                                                        <FaDollarSign /> Price *
                                                    </label>
                                                    <div className={styles.inputWithIcon}>
                                                        <span className={styles.currencySymbol}>$</span>
                                                        <input
                                                            type="number"
                                                            id="price"
                                                            name="price"
                                                            className={styles.modernInput}
                                                            value={formData.price}
                                                            onChange={handleInputChange}
                                                            required
                                                            min="0"
                                                            step="0.01"
                                                            placeholder="0.00"
                                                        />
                                                    </div>
                                                </div>

                                                <div className={styles.formGroup}>
                                                    <label htmlFor="discount">
                                                        <FaTag /> Discount (%)
                                                    </label>
                                                    <div className={styles.inputWithIcon}>
                                                        <input
                                                            type="number"
                                                            id="discount"
                                                            name="discount"
                                                            className={styles.modernInput}
                                                            value={formData.discount}
                                                            onChange={handleInputChange}
                                                            min="0"
                                                            max="100"
                                                            step="0.01"
                                                            placeholder="0.00"
                                                        />
                                                        <span className={styles.percentSymbol}>%</span>
                                                    </div>
                                                </div>
                                            </div>

                                            { }
                                            <div className={styles.formRow}>
                                                <div className={styles.formGroup}>
                                                    <label htmlFor="stock">
                                                        <FaBox /> Stock Quantity *
                                                    </label>
                                                    <input
                                                        type="number"
                                                        id="stock"
                                                        name="stock"
                                                        className={styles.modernInput}
                                                        value={formData.stock}
                                                        onChange={handleInputChange}
                                                        required
                                                        min="0"
                                                        placeholder="0"
                                                    />
                                                </div>

                                                <div className={styles.formGroup}>
                                                    <label htmlFor="category_id">
                                                        <FaFilter /> Category *
                                                    </label>
                                                    <CustomCategorySelect
                                                        categories={categories}
                                                        value={formData.category_id}
                                                        onChange={handleInputChange}
                                                    />
                                                </div>
                                            </div>

                                            { }
                                            <div className={styles.formGroup}>
                                                <label htmlFor="description">
                                                    <FaEdit /> Product Description
                                                </label>
                                                <textarea
                                                    id="description"
                                                    name="description"
                                                    className={styles.modernTextarea}
                                                    value={formData.description}
                                                    onChange={handleInputChange}
                                                    placeholder="Enter product description"
                                                    rows="5"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    { }
                                    <div className={styles.formColumn}>
                                        <div className={styles.formSection}>
                                            <h3 className={styles.sectionTitle}>
                                                <FaImage /> Product Image
                                            </h3>

                                            <div className={styles.imageUploadContainer}>
                                                <SimpleImageUploader
                                                    value={formData.image_url}
                                                    onChange={(url) => setFormData(prev => ({ ...prev, image_url: url }))}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className={styles.formActions}>
                                    <button
                                        type="button"
                                        className={styles.cancelButton}
                                        onClick={resetForm}
                                    >
                                        <FaTimes /> Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className={styles.saveButton}
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <span className={styles.spinner}></span>
                                                {editingProduct ? 'Updating...' : 'Saving...'}
                                            </>
                                        ) : (
                                            <>
                                                <FaCheck /> {editingProduct ? 'Update Product' : 'Save Product'}
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ duration: 0.3 }}
                        >
                            { }
                            <div className={styles.filters}>
                                <div className={styles.searchBar}>
                                    <FaSearch />
                                    <input
                                        type="text"
                                        placeholder="Search products..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                    />
                                    {searchTerm && (
                                        <button
                                            className={styles.clearSearch}
                                            onClick={handleClearSearch}
                                            title="Clear search"
                                        >
                                            <FaTimes />
                                        </button>
                                    )}
                                </div>

                                <div className={styles.categoryFilter}>
                                    <DashboardCategoryFilter
                                        categories={categories}
                                        value={categoryFilter}
                                        onChange={setCategoryFilter}
                                    />
                                </div>
                            </div>

                            {loading ? (
                                <div className={styles.loading}>Loading products...</div>
                            ) : error ? (
                                <div className={styles.error}>{error}</div>
                            ) : filteredProducts.length === 0 ? (
                                <div className={styles.noProducts}>
                                    <p>No products found. Try adjusting your search or add a new product.</p>
                                </div>
                            ) : (
                                <>
                                    <div className={styles.viewToggle}>
                                        <button
                                            className={`${styles.viewToggleButton} ${viewMode === 'grid' ? styles.active : ''}`}
                                            onClick={() => setViewMode('grid')}
                                            title="Grid view"
                                        >
                                            <FaThLarge />
                                        </button>
                                        <button
                                            className={`${styles.viewToggleButton} ${viewMode === 'list' ? styles.active : ''}`}
                                            onClick={() => setViewMode('list')}
                                            title="List view"
                                        >
                                            <FaList />
                                        </button>
                                    </div>

                                    {viewMode === 'grid' ? (
                                        <div className={styles.productsGrid}>
                                            {currentProducts.map(product => (
                                                <motion.div
                                                    key={product.id}
                                                    className={`${styles.productCard} ${getProductStatusClass(product.is_active)}`}
                                                    animate={animateItem === product.id ?
                                                        { backgroundColor: ['#fff', '#e8f5e9', '#fff'] } :
                                                        {}
                                                    }
                                                    transition={{ duration: 2 }}
                                                >
                                                    {!product.is_active && (
                                                        <div className={styles.inactiveOverlay}>
                                                            <span>Inactive</span>
                                                        </div>
                                                    )}

                                                    {product.discount > 0 && (
                                                        <div className={styles.productDiscount}>
                                                            {product.discount}% OFF
                                                        </div>
                                                    )}

                                                    <div className={styles.productImageContainer}>
                                                        <img
                                                            src={getProductImageUrl(product.image_url)}
                                                            alt={product.product_name}
                                                            className={styles.productImage}
                                                            onError={(e) => {
                                                                console.error("Failed to load product image:", product.image_url);
                                                                e.target.src = '/src/assets/images/placeholder.svg';
                                                            }}
                                                        />
                                                    </div>

                                                    <div className={styles.productDetails}>
                                                        <h3 className={styles.productName}>{product.product_name}</h3>

                                                        <div className={styles.productCategory}>
                                                            <FaTag size={12} />
                                                            {categories.find(c => c.id === product.category_id)?.category_name || 'Unknown'}
                                                        </div>

                                                        <div className={styles.productMeta}>
                                                            <div className={styles.productPrice}>
                                                                ${parseFloat(product.price).toFixed(2)}
                                                            </div>

                                                            <div className={`${styles.productStock} ${styles[getStockStatus(product.stock)]}`}>
                                                                <FaBox size={12} />
                                                                {getStockText(product.stock)} ({product.stock})
                                                            </div>
                                                        </div>

                                                        <div className={styles.productActions}>
                                                            <button
                                                                className={styles.actionButton}
                                                                onClick={() => handleEdit(product)}
                                                                title="Edit product"
                                                            >
                                                                <FaEdit />
                                                            </button>

                                                            <button
                                                                className={`${styles.actionButton} ${product.is_active ? styles.visibleBtn : styles.hiddenBtn}`}
                                                                onClick={() => handleToggleVisibility(product.id, product.is_active)}
                                                                title={product.is_active ? "Deactivate product" : "Activate product"}
                                                            >
                                                                {product.is_active ? <FaEye /> : <FaEyeSlash />}
                                                            </button>

                                                            <button
                                                                className={styles.actionButton}
                                                                onClick={() => handleDelete(product.id)}
                                                                title="Delete product"
                                                            >
                                                                <FaTrash />
                                                            </button>
                                                        </div>
                                                    </div>
                                                </motion.div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className={styles.productsTable}>
                                            <table>
                                                <thead>
                                                    <tr>
                                                        <th>Image</th>
                                                        <th>Name</th>
                                                        <th>Category</th>
                                                        <th>Price</th>
                                                        <th>Stock</th>
                                                        <th>Discount</th>
                                                        <th>Actions</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {currentProducts.map(product => (
                                                        <motion.tr
                                                            key={product.id}
                                                            className={getProductStatusClass(product.is_active)}
                                                            animate={animateItem === product.id ?
                                                                { backgroundColor: ['#fff', '#e8f5e9', '#fff'] } :
                                                                {}
                                                            }
                                                            transition={{ duration: 2 }}
                                                        >
                                                            <td>
                                                                <img
                                                                    src={getProductImageUrl(product.image_url)}
                                                                    alt={product.product_name}
                                                                    className={styles.productImage}
                                                                    onError={(e) => {
                                                                        console.error("Failed to load product image:", product.image_url);
                                                                        e.target.src = '/src/assets/images/placeholder.svg';
                                                                    }}
                                                                />
                                                            </td>
                                                            <td>{product.product_name}</td>
                                                            <td>
                                                                {categories.find(c => c.id === product.category_id)?.category_name || 'Unknown'}
                                                            </td>
                                                            <td>${parseFloat(product.price).toFixed(2)}</td>
                                                            <td className={styles[getStockStatus(product.stock)]}>
                                                                {product.stock}
                                                            </td>
                                                            <td>{product.discount > 0 ? `${product.discount}%` : 'No discount'}</td>
                                                            <td>
                                                                <div className={styles.actions}>
                                                                    <button
                                                                        className={styles.editButton}
                                                                        onClick={() => handleEdit(product)}
                                                                        title="Edit product"
                                                                    >
                                                                        <FaEdit />
                                                                    </button>
                                                                    <button
                                                                        className={`${styles.visibilityButton} ${product.is_active ? styles.visible : styles.hidden}`}
                                                                        onClick={() => handleToggleVisibility(product.id, product.is_active)}
                                                                        title={product.is_active ? "Deactivate product" : "Activate product"}
                                                                    >
                                                                        {product.is_active ? <FaEye /> : <FaEyeSlash />}
                                                                    </button>
                                                                    <button
                                                                        className={styles.deleteButton}
                                                                        onClick={() => handleDelete(product.id)}
                                                                        title="Delete product"
                                                                    >
                                                                        <FaTrash />
                                                                    </button>
                                                                </div>
                                                            </td>
                                                        </motion.tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    )}

                                    { }
                                    {filteredProducts.length > 0 && (
                                        <div className={styles.pagination}>
                                            <button
                                                className={`${styles.paginationButton} ${currentPage === 1 ? styles.disabled : ''}`}
                                                onClick={handlePrevPage}
                                                disabled={currentPage === 1}
                                            >
                                                <FaChevronLeft />
                                            </button>

                                            <div className={styles.pageNumbers}>
                                                {Array.from({ length: totalPages }, (_, i) => i + 1)
                                                    .filter(num => {
                                                        // Show first page, last page, current page, and pages around current page
                                                        return num === 1 ||
                                                            num === totalPages ||
                                                            (num >= currentPage - 1 && num <= currentPage + 1);
                                                    })
                                                    .map((number, index, array) => {
                                                        // Add ellipsis where needed
                                                        if (index > 0 && array[index - 1] !== number - 1) {
                                                            return (
                                                                <React.Fragment key={`ellipsis-${number}`}>
                                                                    <span className={styles.ellipsis}>...</span>
                                                                    <button
                                                                        className={`${styles.pageNumber} ${currentPage === number ? styles.activePage : ''}`}
                                                                        onClick={() => handlePageChange(number)}
                                                                    >
                                                                        {number}
                                                                    </button>
                                                                </React.Fragment>
                                                            );
                                                        }
                                                        return (
                                                            <button
                                                                key={number}
                                                                className={`${styles.pageNumber} ${currentPage === number ? styles.activePage : ''}`}
                                                                onClick={() => handlePageChange(number)}
                                                            >
                                                                {number}
                                                            </button>
                                                        );
                                                    })}
                                            </div>

                                            <button
                                                className={`${styles.paginationButton} ${currentPage === totalPages ? styles.disabled : ''}`}
                                                onClick={handleNextPage}
                                                disabled={currentPage === totalPages}
                                            >
                                                <FaChevronRight />
                                            </button>
                                        </div>
                                    )}
                                </>
                            )}
                        </motion.div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default AdminProducts;
