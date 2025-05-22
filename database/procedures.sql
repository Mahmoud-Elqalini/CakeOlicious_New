USE Sweets_Store;
GO

DROP PROCEDURE IF EXISTS AddNewCustomer;
DROP PROCEDURE IF EXISTS AddNewProduct;
DROP PROCEDURE IF EXISTS AddProductDiscount;
DROP PROCEDURE IF EXISTS AddProductReview;
DROP PROCEDURE IF EXISTS AddToCart;
DROP PROCEDURE IF EXISTS CreateOrder;
DROP PROCEDURE IF EXISTS DeleteProduct;
DROP PROCEDURE IF EXISTS DeleteProductReview;
DROP PROCEDURE IF EXISTS GetAllOrders;
DROP PROCEDURE IF EXISTS GetAllProducts;
DROP PROCEDURE IF EXISTS GetAllUsers;
DROP PROCEDURE IF EXISTS GetCartDetails;
DROP PROCEDURE IF EXISTS GetOrderDetails;
DROP PROCEDURE IF EXISTS GetOrderItems;
DROP PROCEDURE IF EXISTS GetProductReview;
DROP PROCEDURE IF EXISTS RemoveFromCart;
DROP PROCEDURE IF EXISTS SearchProduct;
DROP PROCEDURE IF EXISTS UpdateCartQuantity;
DROP PROCEDURE IF EXISTS UpdateProductPrice;
DROP PROCEDURE IF EXISTS UpdateProductStock;
DROP PROCEDURE IF EXISTS GetAllReviews;
GO

-- ################################################################ Add Customer #########################################################
-- Add Customer
CREATE PROCEDURE AddNewCustomer
    @username VARCHAR(100),
    @pass_word VARCHAR(255),
    @email VARCHAR(255),
    @full_name VARCHAR(100),
    @user_address TEXT = NULL,
    @phone_number VARCHAR(20) = NULL
AS
BEGIN
    -- Check if user already exists
    IF EXISTS (SELECT 1 FROM users WHERE username = @username OR email = @email)
    BEGIN
        SELECT 
            'fail' AS status,
            'User already exists. Please try again with different user name or email.' AS message;
    END
    ELSE
    BEGIN
        -- Insert new customer
        INSERT INTO users (username, pass_word, email, full_name, user_address, phone_number, user_role)
        VALUES (@username, @pass_word, @email, @full_name, @user_address, @phone_number, 'Customer');
        
        -- Return success message and customer details
        SELECT 
            'success' AS status,
            'Customer added successfully!' AS message,
            u.id AS user_id,
            u.username,
            u.email,
            u.full_name,
            u.user_address,
            u.phone_number,
            u.user_role
        FROM users u
        WHERE u.username = @username;
    END
END;
GO
-- ################################################################ Add Product #########################################################
CREATE PROCEDURE AddNewProduct
    @product_name VARCHAR(100),
    @description TEXT = NULL,
    @price DECIMAL(10, 2),
    @stock INT,
    @category_id INT,
    @image_url VARCHAR(255) = NULL,
    @discount DECIMAL(5, 2) = 0
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Result TABLE (status VARCHAR(10), message VARCHAR(255));
    DECLARE @ExistingProductID INT;
    DECLARE @ExistingPrice DECIMAL(10, 2);

    -- Verify that price and inventory are correct
    IF @price <= 0
    BEGIN
        INSERT INTO @Result (status, message)
        VALUES ('fail', 'Invalid price value. Please enter a positive value.');
    END
    ELSE IF @stock < 0
    BEGIN
        INSERT INTO @Result (status, message)
        VALUES ('fail', 'Invalid stock value. Stock cannot be negative.');
    END
    ELSE IF NOT EXISTS (SELECT 1 FROM categories WHERE id = @category_id)
    BEGIN
        INSERT INTO @Result (status, message)
        VALUES ('fail', 'Invalid category_id. The category does not exist.');
    END
    ELSE
    BEGIN
        -- Verify that the product already exists
        SELECT @ExistingProductID = id, @ExistingPrice = price
        FROM products
        WHERE product_name = @product_name;

        IF @ExistingProductID IS NOT NULL
        BEGIN
            -- Inventory Update
            UPDATE products
            SET stock = stock + @stock
            WHERE id = @ExistingProductID;

            IF @ExistingPrice <> @price
            BEGIN
                -- Update price if different
                UPDATE products
                SET price = @price
                WHERE id = @ExistingProductID;

                INSERT INTO @Result (status, message)
                VALUES ('success', 'Product exists. Stock updated and price updated successfully!');
            END
            ELSE
            BEGIN
                INSERT INTO @Result (status, message)
                VALUES ('success', 'Product exists. Stock updated successfully!');
            END
        END
        ELSE
        BEGIN
            -- Add new product
            INSERT INTO products (product_name, product_description, price, stock, category_id, image_url, discount)
            VALUES (@product_name, @description, @price, @stock, @category_id, @image_url, @discount);

            INSERT INTO @Result (status, message)
            VALUES ('success', 'New product added successfully!');
        END
    END

    -- Return the result from the temporary table
    SELECT status, message FROM @Result;
END
GO
-- ################################################################ update Product price #########################################################
CREATE PROCEDURE UpdateProductPrice
    @product_name VARCHAR(100),
    @new_price DECIMAL(10, 2)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Result TABLE (status VARCHAR(10), message VARCHAR(255));
    DECLARE @ExistingProductID INT;
    DECLARE @CurrentPrice DECIMAL(10, 2);

    -- Validate price value
    IF @new_price <= 0
    BEGIN
        INSERT INTO @Result (status, message)
        VALUES ('fail', 'Invalid price value. Please enter a positive value.');
    END
    ELSE
    BEGIN
        -- Check if product exists
        SELECT @ExistingProductID = id, @CurrentPrice = price
        FROM products
        WHERE product_name = @product_name;

        IF @ExistingProductID IS NOT NULL
        BEGIN
            IF @CurrentPrice = @new_price
            BEGIN
                INSERT INTO @Result (status, message)
                VALUES ('info', 'The price is already the same. No changes made.');
            END
            ELSE
            BEGIN
                -- Update price
                UPDATE products
                SET price = @new_price
                WHERE id = @ExistingProductID;

                INSERT INTO @Result (status, message)
                VALUES ('success', 'Price updated successfully!');
            END
        END
        ELSE
        BEGIN
            INSERT INTO @Result (status, message)
            VALUES ('fail', 'Product not found.');
        END
    END

    -- Return the result from the temporary table
    SELECT status, message FROM @Result;
END
GO
-- ########################################################################### GetCartDetails #####################################
-- Get Cart Details
CREATE PROCEDURE GetCartDetails
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        DECLARE @CartID INT;

        -- Check if user exists
        IF NOT EXISTS (SELECT 1 FROM users WHERE id = @UserID)
        BEGIN
            SELECT 'User not found.' AS Message;
            RETURN;
        END

        -- Get open cart for the user
        SELECT TOP 1 @CartID = id
        FROM cart
        WHERE user_id = @UserID AND is_checked_out = 0;

        IF @CartID IS NULL
        BEGIN
            SELECT 'Cart is empty or not found for this user.' AS Message;
            RETURN;
        END

        -- Return cart item details
        SELECT 
            u.full_name AS [Customer Name],
            p.product_name AS [Product Name],
            cd.quantity,
            cd.price AS [Unit Price],
            cd.discount,
            (cd.price - (cd.price * cd.discount / 100.0)) * cd.quantity AS [Total Per Item],
            cd.added_date AS [Added Date Time],
            (
                SELECT SUM((cd2.price - (cd2.price * cd2.discount / 100.0)) * cd2.quantity)
                FROM cart_details cd2
                WHERE cd2.cart_id = @CartID
            ) AS [Total Price]
        FROM cart_details cd
        JOIN products p ON cd.product_id = p.id
        JOIN cart c ON cd.cart_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE cd.cart_id = @CartID
        ORDER BY cd.added_date;

    END TRY
    BEGIN CATCH
        SELECT 'Error: ' + ERROR_MESSAGE() AS Message;
    END CATCH
END;
GO

-- ################################################################################# AddProductReview ###############################
-- Add Product Review that return a table
CREATE PROCEDURE AddProductReview
    @ProductName VARCHAR(100),
    @Username VARCHAR(100),
    @Rating INT,
    @ReviewText VARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ProductID INT;
    DECLARE @UserID INT;
    DECLARE @ExistingReviewID INT;
    DECLARE @ExistingReviewText VARCHAR(MAX);

    -- Validate rating
    IF @Rating < 1 OR @Rating > 5
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'Invalid rating. Rating must be between 1 and 5.' AS message;
        RETURN;
    END

    -- Get product ID
    SELECT @ProductID = id
    FROM products
    WHERE product_name = @ProductName;

    IF @ProductID IS NULL
    BEGIN
        SELECT 
            'fail' AS status,
            2 AS StatusCode,
            'Product not found.' AS message;
        RETURN;
    END

    -- Get user ID
    SELECT @UserID = id
    FROM users
    WHERE username = @Username;

    IF @UserID IS NULL
    BEGIN
        SELECT 
            'fail' AS status,
            3 AS StatusCode,
            'User not found.' AS message;
        RETURN;
    END

    -- Check for existing review
    SELECT 
        @ExistingReviewID = id,
        @ExistingReviewText = review_text
    FROM product_reviews
    WHERE product_id = @ProductID AND user_id = @UserID;

    IF @ExistingReviewID IS NOT NULL
    BEGIN
        IF ISNULL(@ExistingReviewText, '') = ISNULL(@ReviewText, '')
        BEGIN
            SELECT 
                'fail' AS status,
                4 AS StatusCode,
                'Duplicate review. Your review is identical to the previous one.' AS message;
            RETURN;
        END
    END

    -- Insert new review
    INSERT INTO product_reviews (product_id, user_id, rating, review_text, review_date)
    VALUES (@ProductID, @UserID, @Rating, @ReviewText, GETDATE());

    SELECT 
        'success' AS status,
        0 AS StatusCode,
        'Review successfully added.' AS message;
END;
GO
-- ####################################################################### GetProductReview #########################################
-- Get Product Review that return table
CREATE PROCEDURE GetProductReview
    @ProductName VARCHAR(100),
    @Username VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ProductID INT;
    DECLARE @UserID INT;

    -- Check for empty inputs
    IF LTRIM(RTRIM(@ProductName)) = '' OR LTRIM(RTRIM(@Username)) = ''
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'Product name and username cannot be empty.' AS message;
        RETURN;
    END

    -- Get product ID
    SELECT @ProductID = id
    FROM products
    WHERE product_name = @ProductName;

    IF @ProductID IS NULL
    BEGIN
        SELECT 
            'fail' AS status,
            2 AS StatusCode,
            'Product not found.' AS message;
        RETURN;
    END

    -- Get user ID
    SELECT @UserID = id
    FROM users
    WHERE username = @Username;

    IF @UserID IS NULL
    BEGIN
        SELECT 
            'fail' AS status,
            3 AS StatusCode,
            'User not found.' AS message;
        RETURN;
    END

    -- Check for review existence
    IF NOT EXISTS (
        SELECT 1 FROM product_reviews
        WHERE product_id = @ProductID AND user_id = @UserID
    )
    BEGIN
        SELECT 
            'fail' AS status,
            4 AS StatusCode,
            'No review found for this product by this user.' AS message;
        RETURN;
    END

    -- Return the review data
    SELECT 
        u.full_name AS Username,
        p.product_name AS ProductName,
        p.image_url AS PhotoURL,
        pr.rating AS Rating,
        pr.review_text AS ReviewText,
        pr.review_date AS ReviewDate
    FROM product_reviews pr
    JOIN users u ON pr.user_id = u.id
    JOIN products p ON pr.product_id = p.id
    WHERE pr.product_id = @ProductID AND pr.user_id = @UserID;

    -- Return status row
    SELECT 
        'success' AS status,
        0 AS StatusCode,
        'Review found.' AS message;
END;
GO
-- ############################################################################## DeleteProductReview ##################################
-- Delete Product Review (Improved - returns structured table)
CREATE PROCEDURE DeleteProductReview
    @ProductName VARCHAR(100),
    @Username VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ProductID INT;
    DECLARE @UserID INT;
    DECLARE @ReviewID INT;

    BEGIN TRANSACTION;
    BEGIN TRY
        -- Get product ID
        SELECT @ProductID = id
        FROM products
        WHERE product_name = @ProductName;

        -- Get user ID
        SELECT @UserID = id
        FROM users
        WHERE username = @Username;

        -- Validate product and user
        IF @ProductID IS NULL OR @UserID IS NULL
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 
                'fail' AS status,
                1 AS StatusCode,
                'Product or user not found.' AS message;
            RETURN;
        END

        -- Get review ID
        SELECT @ReviewID = id
        FROM product_reviews
        WHERE product_id = @ProductID AND user_id = @UserID;

        IF @ReviewID IS NULL
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 
                'fail' AS status,
                2 AS StatusCode,
                'No review found for this product by this user.' AS message;
            RETURN;
        END

        -- Delete review
        DELETE FROM product_reviews
        WHERE id = @ReviewID;

        IF @@ROWCOUNT > 0
        BEGIN
            COMMIT TRANSACTION;
            SELECT 
                'success' AS status,
                0 AS StatusCode,
                'Review successfully deleted.' AS message;
        END
        ELSE
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 
                'fail' AS status,
                3 AS StatusCode,
                'Review deletion failed.' AS message;
        END
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        SELECT 
            'error' AS status,
            4 AS StatusCode,
            ERROR_MESSAGE() AS message;
    END CATCH
END;
GO

-- ######################################################################## AddToCart ########################################
-- Add To Cart (Improved)
CREATE PROCEDURE AddToCart
    @UserID INT,
    @ProductID INT,
    @Quantity INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @CartID INT;
        DECLARE @Price DECIMAL(10, 2);
        DECLARE @Discount DECIMAL(5, 2);
        DECLARE @ExistingCartDetailID INT;
        DECLARE @ExistingQuantity INT;

        -- Check if user exists
        IF NOT EXISTS (SELECT 1 FROM users WHERE id = @UserID)
        BEGIN
            ROLLBACK;
            SELECT 1 AS StatusCode, 'User not found.' AS Message;
            RETURN;
        END

        -- Check if product exists
        IF NOT EXISTS (SELECT 1 FROM products WHERE id = @ProductID)
        BEGIN
            ROLLBACK;
            SELECT 1 AS StatusCode, 'Product not found.' AS Message;
            RETURN;
        END

        -- Check quantity
        IF @Quantity <= 0
        BEGIN
            ROLLBACK;
            SELECT 1 AS StatusCode, 'Invalid quantity. Must be greater than 0.' AS Message;
            RETURN;
        END

        -- Get price and discount
        SELECT @Price = price, @Discount = discount
        FROM products
        WHERE id = @ProductID;

        -- Check if user already has an open cart
        SELECT TOP 1 @CartID = id
        FROM cart
        WHERE user_id = @UserID AND is_checked_out = 0;

        -- If no cart exists, create one
        IF @CartID IS NULL
        BEGIN
            INSERT INTO cart (user_id, created_at, is_checked_out)
            VALUES (@UserID, GETDATE(), 0);

            SET @CartID = SCOPE_IDENTITY();
        END

        -- Check if product is already in cart_details
        SELECT @ExistingCartDetailID = id, @ExistingQuantity = quantity
        FROM cart_details
        WHERE cart_id = @CartID AND product_id = @ProductID;

        IF @ExistingCartDetailID IS NOT NULL
        BEGIN
            -- Update quantity
            UPDATE cart_details
            SET quantity = @ExistingQuantity + @Quantity
            WHERE id = @ExistingCartDetailID;

            COMMIT;
            SELECT 0 AS StatusCode, 'Product quantity updated in cart successfully!' AS Message;
        END
        ELSE
        BEGIN
            -- Insert new product into cart_details
            INSERT INTO cart_details (cart_id, product_id, quantity, price, discount, added_date)
            VALUES (@CartID, @ProductID, @Quantity, @Price, @Discount, GETDATE());

            COMMIT;
            SELECT 0 AS StatusCode, 'Product added to cart successfully!' AS Message;
        END

    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK;

        SELECT 1 AS StatusCode, ERROR_MESSAGE() AS Message;
    END CATCH
END;
GO

-- ######################################################################### UpdateCartQuantity #######################################
-- Update Cart Quantity (with Product Existence Check)
CREATE PROCEDURE UpdateCartQuantity
    @CartItemID INT,
    @Change INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @CurrentQuantity INT;
        DECLARE @ProductID INT;
        DECLARE @NewQuantity INT;
        DECLARE @Stock INT;

        -- Check if the cart item exists in cart_details
        IF NOT EXISTS (SELECT 1 FROM cart_details WHERE id = @CartItemID)
        BEGIN
            ROLLBACK;
            SELECT 1 AS StatusCode, 'Cart item not found.' AS Message;
            RETURN;
        END

        -- Get the current quantity and product ID from cart_details
        SELECT @CurrentQuantity = quantity, @ProductID = product_id
        FROM cart_details
        WHERE id = @CartItemID;

        SET @NewQuantity = @CurrentQuantity + @Change;

        -- Check if the product exists
        IF NOT EXISTS (SELECT 1 FROM products WHERE id = @ProductID)
        BEGIN
            ROLLBACK;
            SELECT 1 AS StatusCode, 'Product not found.' AS Message;
            RETURN;
        END

        -- Check if the new quantity is valid (must be > 0)
		IF @NewQuantity <= 0
		BEGIN
			ROLLBACK;
			SELECT 1 AS StatusCode, 'Total quantity for the product must be greater than zero.' AS Message;
			RETURN;
		END

        -- Get available stock
        SELECT @Stock = stock
        FROM products
        WHERE id = @ProductID;

        -- Validate stock availability
        IF @NewQuantity > @Stock
        BEGIN
            ROLLBACK;
            SELECT 1 AS StatusCode, 'Not enough stock available.' AS Message;
            RETURN;
        END

        -- Update the item quantity
        UPDATE cart_details
        SET quantity = @NewQuantity
        WHERE id = @CartItemID;

        COMMIT;
        SELECT 0 AS StatusCode, 'Cart quantity updated successfully!' AS Message;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK;

        SELECT 1 AS StatusCode, ERROR_MESSAGE() AS Message;
    END CATCH
END;

GO

-- ############################################################################# RemoveFromCart ###################################
-- Remove an item from the Cart (cart_details table)
CREATE PROCEDURE RemoveFromCart
    @CartItemID INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Check if the cart item exists in cart_details
        IF NOT EXISTS (SELECT 1 FROM cart_details WHERE id = @CartItemID)
        BEGIN
            ROLLBACK;
            SELECT
                1 AS status,
                'Cart item not found.' AS message;
            RETURN;
        END

        -- Delete the cart item from cart_details
        DELETE FROM cart_details
        WHERE id = @CartItemID;

        COMMIT;
        SELECT
            0 AS status,
            'Cart item removed successfully!' AS message;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK;

        DECLARE @ErrorMessage NVARCHAR(MAX) = ERROR_MESSAGE();

        SELECT
            1 AS status,
            @ErrorMessage AS message;
    END CATCH
END;
GO

-- ############################################################################ CreateOrder ####################################
-- Create a new order and return a table result
CREATE PROCEDURE CreateOrder
    @UserID INT,
    @ShippingAddress TEXT,
    @TotalAmount DECIMAL(10, 2),
    @PaymentMethod VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON; -- Prevent row count messages from interfering with result sets

    DECLARE @OrderID INT;
    DECLARE @CartID INT;

    -- Start transaction
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Check if the user exists
        IF NOT EXISTS (SELECT 1 FROM users WHERE id = @UserID)
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 
                'fail' AS status,
                1 AS StatusCode,
                'User not found.' AS message,
                NULL AS order_id;
            RETURN;
        END

        -- Validate payment method
        IF @PaymentMethod NOT IN ('Credit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery', 'Gift Card')
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 
                'fail' AS status,
                4 AS StatusCode,
                'Invalid payment method.' AS message,
                NULL AS order_id;
            RETURN;
        END

        -- Get the cart ID for the user (assuming one active cart per user where is_checked_out = 0)
        SELECT @CartID = id
        FROM Cart
        WHERE user_id = @UserID AND is_checked_out = 0;

        IF @CartID IS NULL
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 
                'fail' AS status,
                3 AS StatusCode,
                'No active cart found.' AS message,
                NULL AS order_id;
            RETURN;
        END

        -- Check if the cart has items
        IF NOT EXISTS (SELECT 1 FROM cart_details WHERE cart_id = @CartID)
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 
                'fail' AS status,
                3 AS StatusCode,
                'Cart is empty. Cannot create order.' AS message,
                NULL AS order_id;
            RETURN;
        END

        -- Insert a new order
        INSERT INTO orders (user_id, order_date, total_amount, status, shipping_address)
        VALUES (@UserID, GETDATE(), @TotalAmount, 'Pending', @ShippingAddress);

        -- Get new order ID
        SET @OrderID = SCOPE_IDENTITY();

        -- Insert payment record
        INSERT INTO payments (order_id, payment_date, amount, payment_method, status)
        VALUES (@OrderID, GETDATE(), @TotalAmount, @PaymentMethod, 'Pending');

        -- Move cart items to order details
        INSERT INTO order_details (order_id, product_id, quantity, price, discount)
        SELECT @OrderID, product_id, quantity, price, discount
        FROM cart_details
        WHERE cart_id = @CartID;

        -- Update stock
        UPDATE products
        SET stock = stock - cd.quantity
        FROM cart_details cd
        WHERE products.id = cd.product_id
        AND cd.cart_id = @CartID;

        -- Mark cart as checked out
        UPDATE Cart
        SET is_checked_out = 1
        WHERE id = @CartID;

        -- Commit transaction
        COMMIT TRANSACTION;

        -- Return success as a table
        SELECT 
            'success' AS status,
            0 AS StatusCode,
            'Order created successfully!' AS message,
            @OrderID AS order_id;
    END TRY
    BEGIN CATCH
        -- Rollback in case of error
        ROLLBACK TRANSACTION;

        -- Return error message as a table
        SELECT 
            'error' AS status,
            2 AS StatusCode,
            ERROR_MESSAGE() AS message,
            NULL AS order_id;
    END CATCH
END;
GO
-- ########################################################################### GetAllProducts #####################################
CREATE PROCEDURE GetAllProducts
    @category_id INT = NULL,
    @only_active BIT = 0
AS
BEGIN
    SET NOCOUNT ON;

    -- Check for the presence of products (respecting both filters)
    IF NOT EXISTS (
        SELECT 1
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE (@category_id IS NULL OR p.category_id = @category_id)
          AND (@only_active = 0 OR p.is_active = 1)
    )
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'No products found.' AS message;
        RETURN;
    END

    -- Return filtered product list
    SELECT 
        p.id,
        p.product_name,
        p.product_description,
        p.price,
        p.stock,
        p.category_id,
        c.category_name,
        p.image_url,
        p.discount
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE (@category_id IS NULL OR p.category_id = @category_id)
      AND (@only_active = 0 OR p.is_active = 1);
END;
GO

-- ######################################################################### GetAllOrders ###################################
-- Get All Orders
CREATE PROCEDURE GetAllOrders
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if there are orders
    IF NOT EXISTS (SELECT 1 FROM orders)
    BEGIN
        SELECT 
            'fail' AS status,
            'No orders found.' AS message;
        RETURN;
    END

    -- Return orders list as regular rows
    SELECT 
        o.id,
        o.user_id,
        u.username,
		u.full_name,
		u.user_address,
		u.phone_number,
        o.total_amount,
        o.status,
        o.order_date
    FROM orders o
    JOIN users u ON o.user_id = u.id;
END
GO

-- ################################################################## GetAllUsers ##############################################
-- Get All Users and return as Table
CREATE PROCEDURE GetAllUsers
AS
BEGIN
    -- Check if there are users
    IF NOT EXISTS (SELECT 1 FROM users)
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'No users found.' AS message;
        RETURN;
    END

    -- Return users list as a table
    SELECT 
        id,
        username,
        email,
        full_name,
        user_address,
        phone_number,
        user_role
    FROM users;
END;
GO
-- ################################################################## GetUserOrders ##############################################
CREATE PROCEDURE GetUserOrders
    @user_id INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if the user exists
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = @user_id)
    BEGIN
        SELECT 
            'fail' AS status,
            'User not found.' AS message;
        RETURN;
    END

    -- Check if the user has orders
    IF NOT EXISTS (SELECT 1 FROM orders WHERE user_id = @user_id)
    BEGIN
        SELECT 
            'fail' AS status,
            'No orders found for this user.' AS message;
        RETURN;
    END

    -- Return the user's orders
    SELECT 
        o.id,
        o.total_amount,
        o.status,
        o.order_date
    FROM orders o
    WHERE o.user_id = @user_id;
END
GO
-- ################################################################# GetOrderDetails ###############################################
-- Get Order Details and return as table
CREATE PROCEDURE GetOrderDetails
    @order_id INT,
    @caller_user_id INT,
    @is_admin BIT
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if the order exists
    IF NOT EXISTS (SELECT 1 FROM orders WHERE id = @order_id)
    BEGIN
        SELECT 
            'fail' AS status,
            'Order not found.' AS message;
        RETURN;
    END

    -- If not admin, check if the order belongs to the user
    IF @is_admin = 0 AND NOT EXISTS (
        SELECT 1 FROM orders WHERE id = @order_id AND user_id = @caller_user_id
    )
    BEGIN
        SELECT 
            'fail' AS status,
            'You are not authorized to view this order.' AS message;
        RETURN;
    END

    -- Return order details
    SELECT 
        o.id,
        o.user_id,
        u.username,
        u.full_name,
        u.user_address,
        u.phone_number,
        o.total_amount,   -- total price for all items
        o.status,
        o.order_date
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE o.id = @order_id;
END
GO

-- ################################################################# GetOrderItems ###############################################
CREATE PROCEDURE GetOrderItems
    @order_id INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if the order exists
    IF NOT EXISTS (SELECT 1 FROM orders WHERE id = @order_id)
    BEGIN
        SELECT 
            'fail' AS [status],
            'Order not found.' AS [message];
        RETURN;
    END

    -- Return order items (products)
    SELECT 
        p.product_name AS ProductName,     
        od.quantity AS Quantity,          
        od.price AS UnitPrice,             
        (od.quantity * od.price * (1 - od.discount / 100)) AS TotalPrice   -- return total price for each item after discount 
    FROM order_details od
    JOIN products p ON od.product_id = p.id
    WHERE od.order_id = @order_id
    ORDER BY p.product_name; -- Optional: order the results
END
GO
-- ################################################################# DeleteProduct ###############################################
-- Create the DeleteProduct procedure that uses product_id
CREATE PROCEDURE DeleteProduct
    @product_id INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if product exists
    IF NOT EXISTS (SELECT 1 FROM products WHERE id = @product_id)
    BEGIN
        SELECT 'fail' AS status, 'Product not found.' AS message;
        RETURN;
    END
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Store product name for logging
        DECLARE @product_name VARCHAR(100);
        SELECT @product_name = product_name FROM products WHERE id = @product_id;
        
        -- Delete from cart_details first
        DELETE FROM cart_details WHERE product_id = @product_id;
        
        -- Delete from product_reviews
        DELETE FROM product_reviews WHERE product_id = @product_id;
        
        -- Delete from order_details
        DELETE FROM order_details WHERE product_id = @product_id;
        
        -- Finally delete the product
        DELETE FROM products WHERE id = @product_id;
        
        COMMIT TRANSACTION;
        
        SELECT 'success' AS status, 'Product deleted successfully.' AS message;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        SELECT 
            'fail' AS status, 
            'Error deleting product: ' + ERROR_MESSAGE() AS message;
    END CATCH
END;
GO
-- ################################################################# UpdateProduct ###############################################
-- Drop the procedure if it exists
DROP PROCEDURE IF EXISTS UpdateProduct;
GO

-- Create the UpdateProduct procedure
CREATE PROCEDURE UpdateProduct
    @product_id INT,
    @product_name VARCHAR(100),
    @description TEXT = NULL,
    @price DECIMAL(10, 2),
    @stock INT,
    @category_id INT,
    @image_url VARCHAR(255) = NULL,
    @discount DECIMAL(5, 2) = 0
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if product exists
    IF NOT EXISTS (SELECT 1 FROM products WHERE id = @product_id)
    BEGIN
        SELECT 'fail' AS status, 'Product not found.' AS message;
        RETURN;
    END
    
    -- Check if category exists
    IF NOT EXISTS (SELECT 1 FROM categories WHERE id = @category_id)
    BEGIN
        SELECT 'fail' AS status, 'Category not found.' AS message;
        RETURN;
    END
    
    -- Validate price and stock
    IF @price <= 0
    BEGIN
        SELECT 'fail' AS status, 'Price must be greater than zero.' AS message;
        RETURN;
    END
    
    IF @stock < 0
    BEGIN
        SELECT 'fail' AS status, 'Stock cannot be negative.' AS message;
        RETURN;
    END
    
    -- Check if product name already exists for a different product
    IF EXISTS (SELECT 1 FROM products WHERE product_name = @product_name AND id != @product_id)
    BEGIN
        SELECT 'fail' AS status, 'Product name already exists.' AS message;
        RETURN;
    END
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Update product
        UPDATE products
        SET 
            product_name = @product_name,
            product_description = @description,
            price = @price,
            stock = @stock,
            category_id = @category_id,
            discount = @discount
        WHERE id = @product_id;
        
        -- Update image_url only if provided
        IF @image_url IS NOT NULL AND @image_url != ''
        BEGIN
            UPDATE products
            SET image_url = @image_url
            WHERE id = @product_id;
        END
        
        COMMIT TRANSACTION;
        
        -- Return updated product details
        SELECT 
            'success' AS status, 
            'Product updated successfully.' AS message,
            p.id,
            p.product_name,
            p.product_description AS description,
            p.price,
            p.stock,
            p.category_id,
            c.category_name,
            p.image_url,
            p.discount
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = @product_id;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        SELECT 
            'fail' AS status, 
            'Error updating product: ' + ERROR_MESSAGE() AS message;
    END CATCH
END;
GO
-- ################################################################# SearchProduct ###############################################

CREATE PROCEDURE SearchProduct
    @ProductName VARCHAR(100) = NULL,
    @CategoryName VARCHAR(100) = NULL,
    @MinPrice DECIMAL(10, 2) = NULL,
    @MaxPrice DECIMAL(10, 2) = NULL,
    @MinDiscount DECIMAL(5, 2) = 0,        -- Minimum discount allowed
    @OnlyDiscounted BIT = 0,                -- If set to 1, only fetch products with discount > 0
    @SortBy VARCHAR(20) = 'price',          -- Options: 'price', 'product_name', 'discount'
    @SortOrder VARCHAR(4) = 'ASC',          -- Options: 'ASC', 'DESC'
    @RowLimit INT = 100                     -- Limit the number of returned rows
AS
BEGIN
    -- Validate SortBy and SortOrder
    DECLARE @SafeSortBy NVARCHAR(20) = CASE @SortBy
        WHEN 'price' THEN 'P.price'
        WHEN 'product_name' THEN 'P.product_name'
        WHEN 'discount' THEN 'P.discount'
        ELSE 'P.price'
    END;
    DECLARE @SafeSortOrder NVARCHAR(4) = CASE @SortOrder
        WHEN 'ASC' THEN 'ASC'
        WHEN 'DESC' THEN 'DESC'
        ELSE 'ASC'
    END;

    DECLARE @Query NVARCHAR(MAX);

    SET @Query = N'
    SELECT TOP (' + CAST(@RowLimit AS NVARCHAR) + ')
        P.product_name,
        P.product_description,
        P.price,
        P.stock,
        P.discount,
        P.image_url,
        C.category_name
    FROM products P
    JOIN categories C ON P.category_id = C.id
    WHERE 
        (@ProductName IS NULL OR P.product_name LIKE ''%'' + @ProductName + ''%'')
        AND (@CategoryName IS NULL OR C.category_name = @CategoryName)
        AND (@MinPrice IS NULL OR P.price >= @MinPrice)
        AND (@MaxPrice IS NULL OR P.price <= @MaxPrice)
        AND (P.discount >= @MinDiscount) ';

    -- Add filter for discounted products if required
    IF @OnlyDiscounted = 1
    BEGIN
        SET @Query += ' AND P.discount > 0 ';
    END;

    -- Add sorting condition
    SET @Query += ' ORDER BY ' + @SafeSortBy + ' ' + @SafeSortOrder + ';';
    
    EXEC sp_executesql @Query,
        N'@ProductName VARCHAR(100), @CategoryName VARCHAR(100), @MinPrice DECIMAL(10, 2), 
          @MaxPrice DECIMAL(10, 2), @MinDiscount DECIMAL(5, 2)',
        @ProductName, @CategoryName, @MinPrice, @MaxPrice, @MinDiscount;
END;
GO
-- ################################################################# UpdateProductStock ###############################################
CREATE PROCEDURE UpdateProductStock
    @ProductName VARCHAR(100),
    @NewStock INT,
    @AddToExisting BIT = 1  -- 1: Add to existing inventory, 0: Replace existing inventory.
AS
BEGIN
    DECLARE @ExistingProductID BIGINT;
    DECLARE @CurrentStock INT;

    -- Check that the new quantity is positive
    IF @NewStock <= 0
    BEGIN
        SELECT 'Invalid stock value. New stock must be greater than zero.' AS Message;
        RETURN;
    END

    -- Check the presence of the product in the database
    SELECT @ExistingProductID = id, @CurrentStock = stock
    FROM products
    WHERE product_name = @ProductName;

    IF @ExistingProductID IS NULL
    BEGIN
        SELECT 'Product not found.' AS Message;
        RETURN;
    END

    -- Update inventory based on selected addition method
    IF @AddToExisting = 1
    BEGIN
        UPDATE products
        SET stock = stock + @NewStock
        WHERE id = @ExistingProductID;
        
        SELECT 'Product stock successfully updated by adding the new quantity.' AS Message;
    END
    ELSE
    BEGIN
        UPDATE products
        SET stock = @NewStock
        WHERE id = @ExistingProductID;
        
        SELECT 'Product stock successfully updated by replacing the old quantity.' AS Message;
    END
END;
GO

-- ################################################################# GetAllReviews ###############################################
CREATE PROCEDURE GetAllReviews
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if there are any reviews
    IF NOT EXISTS (SELECT 1 FROM product_reviews)
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'No reviews found.' AS message;
        RETURN;
    END

    -- Return all reviews with product and user details
    SELECT 
        pr.product_id AS ProductID,
        p.product_name AS ProductName,
        pr.user_id AS UserID,
        u.username AS Username,
        u.full_name AS FullName,
        pr.rating AS Rating,
        pr.review_text AS ReviewText,
        pr.review_date AS ReviewDate
    FROM product_reviews pr
    JOIN products p ON pr.product_id = p.id
    JOIN users u ON pr.user_id = u.id
    ORDER BY pr.review_date DESC;

    -- Return status row
    SELECT 
        'success' AS status,
        0 AS StatusCode,
        'Reviews retrieved successfully.' AS message;
END
GO
-- ################################################################# DeleteUser ###############################################

CREATE PROCEDURE DeleteUser
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Check the user's presence
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = @UserID)
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'User not found.' AS message;
        RETURN;
    END

    -- Prevent the deletion of admins
    IF EXISTS (SELECT 1 FROM users WHERE id = @UserID AND user_role = 'Admin')
    BEGIN
        SELECT 
            'fail' AS status,
            2 AS StatusCode,
            'Cannot delete an admin user.' AS message;
        RETURN;
    END

    -- Make sure the phantom user is there
    IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'deleted_user')
    BEGIN
        INSERT INTO users (username, email, pass_word, full_name, user_role, phone_number, user_address)
        VALUES ('deleted_user', 'deleted@gmail.com', 'N/A', 'Deleted User', 'Admin', 'N/A', 'N/A');
    END

    -- Get Fake User ID
    DECLARE @deleteduserid INT;
    SELECT @deleteduserid = id FROM users WHERE username = 'deleted_user';

    -- Transfer of orders
    UPDATE orders 
    SET user_id = @deleteduserid 
    WHERE user_id = @UserID;

    -- Transfer of ratings
    UPDATE product_reviews 
    SET user_id = @deleteduserid 
    WHERE user_id = @UserID;

	-- Delete card data
    DELETE FROM cart 
    WHERE user_id = @UserID;

    -- Delete the original user
    DELETE FROM users 
    WHERE id = @UserID;

    -- Success Message
    SELECT 
        'success' AS status,
        0 AS StatusCode,
        'User deleted successfully, orders and reviews preserved.' AS message;
END
GO
-- ################################################################# GetUserProfile ###############################################

CREATE PROCEDURE GetUserProfile
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if user exists
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = @UserID)
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'User not found.' AS message,
            CAST(NULL AS INT) AS UserID,
            CAST(NULL AS NVARCHAR(255)) AS Username,
            CAST(NULL AS NVARCHAR(255)) AS FullName,
            CAST(NULL AS NVARCHAR(255)) AS Email,
            CAST(NULL AS NVARCHAR(255)) AS PhoneNumber,
            CAST(NULL AS NVARCHAR(255)) AS Address,
            CAST(NULL AS NVARCHAR(255)) AS Role;
        RETURN;
    END

    -- Return user data with success status
    SELECT 
        'success' AS status,
        0 AS StatusCode,
        'User profile retrieved successfully.' AS message,
        id AS UserID,
        username AS Username,
        full_name AS FullName,
        email AS Email,
        phone_number AS PhoneNumber,
        user_address AS Address,
        user_role AS Role
    FROM users
    WHERE id = @UserID;
END
GO
-- ################################################################# ChangePassword ###############################################

CREATE PROCEDURE ChangePassword
    @RequesterID INT,              -- ID of the user making the request
    @TargetUserID INT,             -- ID of the user whose password is being changed
    @NewPasswordHash NVARCHAR(255) -- The new password hash
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- Check if the requester exists
        IF NOT EXISTS (SELECT 1 FROM users WHERE id = @RequesterID)
        BEGIN
            SELECT 
                'fail' AS status,
                4 AS StatusCode,
                'Requester user not found.' AS message;
            RETURN;
        END

        -- Check if the target user exists
        IF NOT EXISTS (SELECT 1 FROM users WHERE id = @TargetUserID)
        BEGIN
            SELECT 
                'fail' AS status,
                1 AS StatusCode,
                'Target user not found.' AS message;
            RETURN;
        END

        -- Check if the requester is admin
        DECLARE @IsAdmin BIT;
        SELECT @IsAdmin = CASE WHEN user_role = 'Admin' THEN 1 ELSE 0 END
        FROM users WHERE id = @RequesterID;

        -- If requester is not admin and trying to change someone else's password
        IF @IsAdmin = 0 AND @RequesterID <> @TargetUserID
        BEGIN
            SELECT 
                'fail' AS status,
                2 AS StatusCode,
                'You are not authorized to change another user''s password.' AS message;
            RETURN;
        END

        -- Perform password update
        UPDATE users
        SET pass_word = @NewPasswordHash
        WHERE id = @TargetUserID;

        -- Success response
        SELECT 
            'success' AS status,
            0 AS StatusCode,
            'Password changed successfully.' AS message;
    END TRY
    BEGIN CATCH
        -- Return error if something goes wrong
        SELECT 
            'fail' AS status,
            ERROR_NUMBER() AS StatusCode,
            ERROR_MESSAGE() AS message;
    END CATCH
END;
GO
-- ################################################################# GetReviewsForSpecificProduct ###############################################


CREATE PROCEDURE GetReviewsForSpecificProduct
    @ProductName VARCHAR(100),
    @Page INT = 1,
    @PerPage INT = 10
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ProductID INT;

    -- Check for empty input
    IF LTRIM(RTRIM(@ProductName)) = ''
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'Product name cannot be empty.' AS message;
        RETURN;
    END

    -- Check for valid pagination parameters
    IF @Page < 1 OR @PerPage < 1
    BEGIN
        SELECT 
            'fail' AS status,
            4 AS StatusCode,
            'Invalid pagination parameters.' AS message;
        RETURN;
    END

    -- Get product ID
    SELECT @ProductID = id
    FROM products
    WHERE product_name = @ProductName;

    IF @ProductID IS NULL
    BEGIN
        SELECT 
            'fail' AS status,
            2 AS StatusCode,
            'Product not found.' AS message;
        RETURN;
    END

    -- Get reviews
    SELECT 
        pr.product_id,
        p.product_name,
        pr.user_id,
        u.full_name AS username,
        pr.rating,
        pr.review_text,
        pr.review_date,
        p.image_url AS photo_url
    FROM product_reviews pr
    JOIN products p ON pr.product_id = p.id
    JOIN users u ON pr.user_id = u.id
    WHERE pr.product_id = @ProductID
    ORDER BY pr.review_date DESC
    OFFSET (@Page - 1) * @PerPage ROWS
    FETCH NEXT @PerPage ROWS ONLY;

    IF @@ROWCOUNT = 0
    BEGIN
        SELECT 
            'fail' AS status,
            3 AS StatusCode,
            'No reviews found for this product.' AS message;
        RETURN;
    END

    -- Return success status
    SELECT 
        'success' AS status,
        0 AS StatusCode,
        'Reviews retrieved successfully.' AS message;
END;
GO
-- ################################################################# GetProductDetails ###############################################

CREATE PROCEDURE GetProductDetails
    @ProductName VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    -- Check for empty input
    IF LTRIM(RTRIM(@ProductName)) = ''
    BEGIN
        SELECT 
            'fail' AS status,
            1 AS StatusCode,
            'Product name cannot be empty.' AS message;
        RETURN;
    END

    -- Check if product exists
    IF NOT EXISTS (SELECT 1 FROM products WHERE product_name = @ProductName)
    BEGIN
        SELECT 
            'fail' AS status,
            2 AS StatusCode,
            'Product not found.' AS message;
        RETURN;
    END

    -- Get product details
    SELECT 
        p.id AS product_id,
        p.product_name,
        p.product_description,
        p.price,
        p.stock,
        c.category_name,
        p.image_url,
        p.discount
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.id
    WHERE p.product_name = @ProductName;

    -- Return success status
    SELECT 
        'success' AS status,
        0 AS StatusCode,
        'Product details retrieved successfully.' AS message;
END
GO
-- ################################################################# CancelOrder ###############################################
-- CancelOrder for users
CREATE PROCEDURE CancelOrder
    @order_id INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @status VARCHAR(50);
    DECLARE @message NVARCHAR(255);

    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM orders WHERE id = @order_id)
        BEGIN
            SET @status = 'fail';
            SET @message = 'Order not found.';
            SELECT @status AS status, @message AS message;
            RETURN;
        END

        DECLARE @current_status VARCHAR(50);
        SELECT @current_status = status FROM orders WHERE id = @order_id;
        IF @current_status IN ('shipped', 'delivered')
        BEGIN
            SET @status = 'fail';
            SET @message = 'Cannot cancel order in this status.';
            SELECT @status AS status, @message AS message;
            RETURN;
        END

        SET @status = 'success';
        SET @message = 'Order canceled successfully.';
        SELECT @status AS status, @message AS message;

    END TRY
    BEGIN CATCH
        SET @status = 'fail';
        SET @message = 'An error occurred while canceling the order: ' + ERROR_MESSAGE();
        SELECT @status AS status, @message AS message;
    END CATCH
END
GO
-- ################################################################# ToggleProductVisibility ###############################################
-- Drop the procedure if it exists
DROP PROCEDURE IF EXISTS ToggleProductVisibility;
GO

-- Create the ToggleProductVisibility procedure
CREATE PROCEDURE ToggleProductVisibility
    @product_id INT,
    @is_active BIT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if product exists
    IF NOT EXISTS (SELECT 1 FROM products WHERE id = @product_id)
    BEGIN
        SELECT 'fail' AS status, 'Product not found.' AS message;
        RETURN;
    END
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- First, check if the is_active column exists
        IF NOT EXISTS (
            SELECT 1 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'products' AND COLUMN_NAME = 'is_active'
        )
        BEGIN
            -- Add the column if it doesn't exist
            ALTER TABLE products
            ADD is_active BIT NOT NULL DEFAULT 1;
        END
        
        -- Update product visibility
        UPDATE products
        SET is_active = @is_active
        WHERE id = @product_id;
        
        COMMIT TRANSACTION;
        
        -- Return success message
        SELECT 
            'success' AS status, 
            CASE WHEN @is_active = 1 
                THEN 'Product activated successfully.' 
                ELSE 'Product deactivated successfully.' 
            END AS message;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        SELECT 
            'fail' AS status, 
            'Error toggling product visibility: ' + ERROR_MESSAGE() AS message;
    END CATCH
END;
GO


CREATE OR ALTER PROCEDURE UpdateProduct
    @product_id INT,
    @product_name VARCHAR(100) = NULL,
    @product_description TEXT = NULL,
    @price DECIMAL(10, 2) = NULL,
    @stock INT = NULL,
    @category_id INT = NULL,
    @image_url VARCHAR(255) = NULL,
    @discount DECIMAL(5, 2) = NULL,
    @is_active BIT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE products
    SET
        product_name = COALESCE(@product_name, product_name),
        product_description = COALESCE(@product_description, product_description),
        price = COALESCE(@price, price),
        stock = COALESCE(@stock, stock),
        category_id = COALESCE(@category_id, category_id),
        image_url = COALESCE(@image_url, image_url),
        discount = COALESCE(@discount, discount),
        is_active = COALESCE(@is_active, is_active)
    WHERE id = @product_id;
END;
GO


-- mahmoud elqalini
-- mahmoud ramadan
-- habiba abdelmalik