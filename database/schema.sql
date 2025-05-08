USE Sweets_Store;

-- Users table for customers and admins
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username VARCHAR(100) UNIQUE NOT NULL,
    pass_word VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    user_address TEXT,
    phone_number VARCHAR(20),
    user_role VARCHAR(20) CHECK (user_role IN ('Admin', 'Customer')) NOT NULL
);

-- Categories table for product categories
CREATE TABLE categories (
    id INT PRIMARY KEY IDENTITY(1,1),
    category_name VARCHAR(50) NOT NULL,
    category_description TEXT
);

-- Products table for catalog
CREATE TABLE products (
    id INT PRIMARY KEY IDENTITY(1,1),
    product_name VARCHAR(100) NOT NULL,
    product_description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    category_id INT NOT NULL,
    image_url VARCHAR(255),
    discount DECIMAL(5, 2) DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Cart table for cart 
CREATE TABLE Cart (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    is_checked_out BIT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Cart table for cart_details 
CREATE TABLE cart_details (
    id INT PRIMARY KEY IDENTITY(1,1),
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0,
    added_date DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (cart_id) REFERENCES cart(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT UQ_Cart_Product UNIQUE (cart_id, product_id)
);

-- Orders table for checkout
CREATE TABLE orders (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address VARCHAR(255) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('Pending', 'Shipped', 'Delivered')) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- OrderDetails table for order items
CREATE TABLE order_details (
    id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Payments table for payment processing
CREATE TABLE payments (
    id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) CHECK (payment_method IN ('Credit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery', 'Gift Card')) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('Pending', 'Completed')) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- ProductReviews table for product reviews
CREATE TABLE product_reviews (
    id INT PRIMARY KEY IDENTITY(1,1),
    product_id INT,
    user_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);