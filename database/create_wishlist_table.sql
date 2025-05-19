-- Create wishlist table
CREATE TABLE wishlist (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT UQ_User_Product UNIQUE (user_id, product_id)
);