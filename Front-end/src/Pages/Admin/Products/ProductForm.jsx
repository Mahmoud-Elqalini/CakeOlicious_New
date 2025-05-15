import React, { useState } from 'react';
import axios from 'axios';
import { FaUpload, FaImage, FaTag, FaCheck, FaTimes } from 'react-icons/fa';
import './ProductForm.css';

const ProductForm = () => {
  const [productName, setProductName] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);

    // Create preview URL for the selected image
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setPreviewUrl('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!productName.trim() || !selectedFile) {
      alert('Please provide both product name and image');
      return;
    }

    const formData = new FormData();
    formData.append('product_name', productName);
    formData.append('image', selectedFile);

    setUploading(true);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setImageUrl(response.data.image_url);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed: ' + (error.response?.data?.message || error.message));
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setProductName('');
    setSelectedFile(null);
    setPreviewUrl('');
    setImageUrl('');
  };

  return (
    <div className="product-form-container">
      <div className="form-header">
        <h2><FaImage className="icon" /> Upload Product Image</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="productName">
            <FaTag className="icon" /> Product Nameeee
          </label>
          <input
            type="text"
            id="productName"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            placeholder="Enter product name"
            required
          />
        </div>

        <div className="image-upload-container">
          <div className="image-preview-area" onClick={() => document.getElementById('productImage').click()}>
            {previewUrl ? (
              <img src={previewUrl} alt="Preview" className="image-preview" />
            ) : (
              <div className="upload-placeholder">
                <FaImage className="placeholder-icon" />
                <p>Click to select an image</p>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="productImage">
              <FaUpload className="icon" /> Product Image
            </label>
            <input
              type="file"
              id="productImage"
              onChange={handleFileChange}
              accept="image/*"
              className="file-input"
              required
            />
            <div className="file-input-wrapper">
              <button type="button" className="file-select-button" onClick={() => document.getElementById('productImage').click()}>
                {selectedFile ? 'Change Image' : 'Select Image'}
              </button>
              {selectedFile && <span className="selected-file-name">{selectedFile.name}</span>}
            </div>
          </div>
        </div>

        <div className="form-actions">
          {imageUrl ? (
            <button type="button" className="reset-button" onClick={resetForm}>
              <FaTimes /> Reset Form
            </button>
          ) : (
            <button type="submit" className="submit-button" disabled={uploading}>
              {uploading ? (
                <>
                  <span className="spinner"></span> Uploading...
                </>
              ) : (
                <>
                  <FaUpload /> Upload Product
                </>
              )}
            </button>
          )}
        </div>
      </form>

      {imageUrl && (
        <div className="success-container">
          <div className="success-icon">
            <FaCheck />
          </div>
          <h3>Upload Successful!</h3>
          <div className="preview-container">
            <img src={imageUrl} alt="Uploaded product" />
            <div className="image-url-container">
              <p>Image URL:</p>
              <div className="url-display">
                <input type="text" value={imageUrl} readOnly />
                <button
                  onClick={() => { navigator.clipboard.writeText(imageUrl); alert('URL copied to clipboard!') }}
                  className="copy-button"
                >
                  Copy
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductForm;
