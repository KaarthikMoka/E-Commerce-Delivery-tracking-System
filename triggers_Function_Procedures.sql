-- ============================================================
--  E-COMMERCE ORDER TRACKING SYSTEM
--  Database Management System Project
--  Student IDs: PES2UG23CS250, PES2UG23CS255
-- ============================================================

-- ============================================================
-- 1. TRIGGERS
-- ============================================================

-- ------------------------------------------------------------
-- TRIGGER 1: update_stock_after_order
-- PURPOSE:
-- Automatically updates the product stock quantity whenever
-- a new order detail is inserted (i.e., an order is placed).
-- ------------------------------------------------------------
DELIMITER //
CREATE TRIGGER update_stock_after_order
AFTER INSERT ON ORDER_DETAILS
FOR EACH ROW
BEGIN
    UPDATE PRODUCTS
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END//
DELIMITER ;
-- EXAMPLE:
-- Before: stock_quantity = 80
-- After inserting order detail (quantity = 5), stock_quantity = 75
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- TRIGGER 2: prevent_negative_stock
-- PURPOSE:
-- Prevents any product stock quantity from becoming negative.
-- If an update tries to reduce stock below zero, raises an error.
-- ------------------------------------------------------------
DELIMITER //
CREATE TRIGGER prevent_negative_stock
BEFORE UPDATE ON PRODUCTS
FOR EACH ROW
BEGIN
    IF NEW.stock_quantity < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Stock quantity cannot be negative';
    END IF;
END//
DELIMITER ;
-- EXAMPLE:
-- Attempt to set stock_quantity = -5 produces:
-- "Error: Stock quantity cannot be negative."
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- TRIGGER 3: update_order_total
-- PURPOSE:
-- Automatically recalculates and updates total_amount in ORDERS
-- when new order details are inserted or changed.
-- ------------------------------------------------------------
DELIMITER //
CREATE TRIGGER update_order_total
AFTER INSERT ON ORDER_DETAILS
FOR EACH ROW
BEGIN
    UPDATE ORDERS
    SET total_amount = (
        SELECT SUM(quantity * price)
        FROM ORDER_DETAILS
        WHERE order_id = NEW.order_id
    )
    WHERE order_id = NEW.order_id;
END//
DELIMITER ;
-- EXAMPLE:
-- Adding new items to order automatically updates total_amount.
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- TRIGGER 4: log_return_request
-- PURPOSE:
-- When a return request is approved, restores the product stock.
-- ------------------------------------------------------------
DELIMITER //
CREATE TRIGGER log_return_request
AFTER INSERT ON RETURNS
FOR EACH ROW
BEGIN
    IF NEW.status = 'Approved' THEN
        UPDATE PRODUCTS p
        INNER JOIN ORDER_DETAILS od ON p.product_id = od.product_id
        SET p.stock_quantity = p.stock_quantity + od.quantity
        WHERE od.order_id = NEW.order_id 
        AND od.product_id = NEW.product_id;
    END IF;
END//
DELIMITER ;
-- EXAMPLE:
-- Approved return increases stock_quantity from 18 → 19
-- ------------------------------------------------------------



-- ============================================================
-- 2. STORED PROCEDURES
-- ============================================================

-- ------------------------------------------------------------
-- PROCEDURE 1: get_customer_order_history
-- PURPOSE:
-- Retrieves full order history of a customer, including product,
-- order, and shipment details.
-- ------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE get_customer_order_history(IN cust_id INT)
BEGIN
    SELECT 
        o.order_id,
        o.order_date,
        o.status,
        o.total_amount,
        p.name AS product_name,
        od.quantity,
        od.price,
        s.tracking_number,
        s.delivery_date
    FROM ORDERS o
    INNER JOIN ORDER_DETAILS od ON o.order_id = od.order_id
    INNER JOIN PRODUCTS p ON od.product_id = p.product_id
    LEFT JOIN SHIPMENTS s ON o.order_id = s.order_id
    WHERE o.customer_id = cust_id
    ORDER BY o.order_date DESC;
END//
DELIMITER ;
-- EXAMPLE:
-- CALL get_customer_order_history(101);
-- Returns all order, product & shipment details for the customer.
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- PROCEDURE 2: process_product_return
-- PURPOSE:
-- Handles product return requests, updates status, and restores stock
-- if the return is approved.
-- ------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE process_product_return(
    IN p_return_id INT,
    IN p_new_status VARCHAR(20)
)
BEGIN
    DECLARE v_order_id INT;
    DECLARE v_product_id INT;
    DECLARE v_quantity INT;
    
    -- Fetch order and product from return record
    SELECT order_id, product_id INTO v_order_id, v_product_id
    FROM RETURNS WHERE return_id = p_return_id;
    
    -- Get ordered quantity
    SELECT quantity INTO v_quantity
    FROM ORDER_DETAILS WHERE order_id = v_order_id AND product_id = v_product_id;
    
    -- Update return status
    UPDATE RETURNS SET status = p_new_status WHERE return_id = p_return_id;
    
    -- If approved, restore product stock
    IF p_new_status = 'Approved' THEN
        UPDATE PRODUCTS SET stock_quantity = stock_quantity + v_quantity WHERE product_id = v_product_id;
    END IF;
    
    SELECT CONCAT('Return #', p_return_id, ' processed successfully. Status: ', p_new_status) AS message;
END//
DELIMITER ;
-- EXAMPLE:
-- CALL process_product_return(2, 'Approved');
-- Return processed, stock restored.
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- PROCEDURE 3: generate_sales_report
-- PURPOSE:
-- Generates a detailed sales summary between given dates.
-- Includes order count, customers, revenue, and average order value.
-- ------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE generate_sales_report(
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    SELECT 
        DATE(o.order_date) AS sale_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        SUM(od.quantity) AS total_items_sold,
        SUM(od.quantity * od.price) AS total_revenue,
        AVG(o.total_amount) AS avg_order_value
    FROM ORDERS o
    INNER JOIN ORDER_DETAILS od ON o.order_id = od.order_id
    WHERE DATE(o.order_date) BETWEEN start_date AND end_date
    AND o.status != 'Cancelled'
    GROUP BY DATE(o.order_date)
    ORDER BY sale_date DESC;
END//
DELIMITER ;
-- EXAMPLE:
-- CALL generate_sales_report('2025-01-01', '2025-01-31');
-- Returns daily summary with revenue and metrics.
-- ------------------------------------------------------------



-- ============================================================
-- 3. FUNCTIONS
-- ============================================================

-- ------------------------------------------------------------
-- FUNCTION 1: calculate_product_revenue
-- PURPOSE:
-- Calculates total revenue generated by a specific product,
-- excluding cancelled orders.
-- ------------------------------------------------------------
DELIMITER //
CREATE FUNCTION calculate_product_revenue(prod_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_revenue DECIMAL(10,2);
    SELECT COALESCE(SUM(od.quantity * od.price), 0)
    INTO total_revenue
    FROM ORDER_DETAILS od
    INNER JOIN ORDERS o ON od.order_id = o.order_id
    WHERE od.product_id = prod_id
    AND o.status != 'Cancelled';
    RETURN total_revenue;
END//
DELIMITER ;
-- EXAMPLE:
-- SELECT calculate_product_revenue(101);
-- Output: 2500.00
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- FUNCTION 2: calculate_customer_ltv
-- PURPOSE:
-- Calculates a customer's lifetime value (sum of all valid orders).
-- ------------------------------------------------------------
DELIMITER //
CREATE FUNCTION calculate_customer_ltv(cust_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE lifetime_value DECIMAL(10,2);
    SELECT COALESCE(SUM(total_amount), 0) INTO lifetime_value
    FROM ORDERS WHERE customer_id = cust_id AND status != 'Cancelled';
    RETURN lifetime_value;
END//
DELIMITER ;
-- EXAMPLE:
-- SELECT calculate_customer_ltv(201);
-- Output: Total purchase value of customer.
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- FUNCTION 3: get_average_rating
-- PURPOSE:
-- Calculates average customer rating for a specific product.
-- ------------------------------------------------------------
DELIMITER //
CREATE FUNCTION get_average_rating(prod_id INT)
RETURNS DECIMAL(3,2)
DETERMINISTIC
BEGIN
    DECLARE avg_rating DECIMAL(3,2);
    SELECT COALESCE(AVG(rating), 0) INTO avg_rating
    FROM REVIEWS WHERE product_id = prod_id;
    RETURN avg_rating;
END//
DELIMITER ;
-- EXAMPLE:
-- SELECT get_average_rating(101);
-- Output: 4.50
-- ------------------------------------------------------------



-- ============================================================
-- DATABASE OBJECTS SUMMARY
-- ============================================================
-- Total Triggers: 4
-- Total Procedures: 3
-- Total Functions: 3
-- ------------------------------------------------------------

-- ============================================================
-- CONCLUSION
-- ============================================================
-- This SQL implementation of the E-Commerce Order Tracking System
-- demonstrates advanced database automation and analytics:
-- • Triggers ensure data integrity and automatic updates.
-- • Procedures provide reusable business logic for reporting and operations.
-- • Functions support analytical calculations (revenue, LTV, ratings).
-- Together, they form a robust, intelligent backend for e-commerce.
-- ============================================================
