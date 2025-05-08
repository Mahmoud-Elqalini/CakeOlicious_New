USE Sweets_Store;

-- Sample Users
INSERT INTO users (username, pass_word, email, full_name, user_address, phone_number, user_role)
VALUES 
('admin_user', 'Admin1234!', 'admin@sweetsstore.com', 'Admin User', '123 Admin Street, Candy City', '123-456-7890', 'Admin'),
('john_doe', 'Password123!', 'john.doe@email.com', 'John Doe', '456 Sweet Lane, Sugar Town', '987-654-3210', 'Customer'),
('jane_smith', 'JanePass2025!', 'jane.smith@email.com', 'Jane Smith', '789 Chocolate Ave, Choco City', '555-123-4567', 'Customer'),
('mike_brown', 'MikeBrown2025!', 'mike.brown@email.com', 'Mike Brown', '101 Candy Blvd, Candy City', '222-333-4444', 'Customer');

-- Sample Categories
INSERT INTO categories (category_name, category_description)
VALUES 
('Chocolate', 'All kinds of delicious chocolates including milk, dark, and white chocolate.'),
('Candy', 'Various candies from gummies to hard candies, perfect for a sweet treat.'),
('Bakery', 'Freshly baked goods including cakes, cookies, and pastries.'),
('Ice Cream', 'Creamy and delicious ice cream in various flavors and styles.');

-- Sample Products
INSERT INTO products (product_name, product_description, price, stock, category_id, image_url, discount)
VALUES 
('Milk Chocolate Bar', 'Delicious creamy milk chocolate.', 5.99, 100, 1, 'https://example.com/images/milk_chocolate.jpg', 0),
('Gummy Bears', 'Colorful gummy bears with fruity flavors.', 2.99, 200, 2, 'https://example.com/images/gummy_bears.jpg', 10.00),
('Chocolate Cake', 'Rich chocolate cake with creamy frosting.', 15.50, 50, 3, 'https://example.com/images/chocolate_cake.jpg', 5.00),
('Vanilla Ice Cream', 'Smooth vanilla ice cream.', 4.99, 80, 4, 'https://example.com/images/vanilla_ice_cream.jpg', 0),
('Dark Chocolate Bar', 'High-quality dark chocolate.', 6.99, 120, 1, 'https://example.com/images/dark_chocolate.jpg', 0),
('Candy Cane', 'Sweet peppermint candy stick.', 1.50, 300, 2, 'https://example.com/images/candy_cane.jpg', 20.00);

-- Sample Cart (fixed with price from products)
INSERT INTO Cart (user_id, product_id, quantity, price)
VALUES 
(1, 3, 1, 15.50), -- Chocolate Cake
(2, 1, 2, 5.99),  -- Milk Chocolate Bar
(4, 5, 1, 6.99);  -- Dark Chocolate Bar

-- Sample Orders
INSERT INTO orders (user_id, total_amount, status)
VALUES 
(2, 29.99, 'Pending'),
(3, 45.50, 'Shipped'),
(4, 15.99, 'Delivered'),
(2, 8.75, 'Pending'),
(3, 60.00, 'Shipped');

-- Sample OrderDetails
INSERT INTO order_details (order_id, product_id, quantity, price)
VALUES 
(1, 1, 2, 5.99),
(1, 2, 1, 2.99),
(2, 3, 1, 15.50),
(3, 5, 2, 6.99),
(4, 6, 3, 1.50),
(5, 4, 4, 4.99);

-- Sample Payments
INSERT INTO payments (order_id, amount, payment_method, status)
VALUES 
(1, 29.99, 'Credit Card', 'Completed'),
(2, 45.50, 'PayPal', 'Completed'),
(3, 15.99, 'Bank Transfer', 'Completed'),
(4, 8.75, 'Cash on Delivery', 'Pending'),
(5, 60.00, 'Gift Card', 'Completed');