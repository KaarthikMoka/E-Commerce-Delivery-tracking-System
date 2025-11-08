-- Create the CUSTOMERS table
CREATE TABLE CUSTOMERS (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL
);

-- Create the PRODUCTS table
CREATE TABLE PRODUCTS (
    product_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0));
    


-- Create the ORDERS table
CREATE TABLE ORDERS (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    CONSTRAINT fk_orders_customers FOREIGN KEY (customer_id)
        REFERENCES CUSTOMERS (customer_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Create the ORDER_DETAILS table
CREATE TABLE ORDER_DETAILS (
    order_detail_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    CONSTRAINT fk_orderdetails_orders FOREIGN KEY (order_id)
        REFERENCES ORDERS(order_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_orderdetails_products FOREIGN KEY (product_id)
        REFERENCES PRODUCTS(product_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Create the SHIPMENTS table
CREATE TABLE SHIPMENTS (
    shipment_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    shipment_date DATE NOT NULL,
    delivery_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'Shipped',
    tracking_number VARCHAR(50) UNIQUE,
    CONSTRAINT fk_shipments_orders FOREIGN KEY (order_id)
        REFERENCES ORDERS(order_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Create the RETURNS table
CREATE TABLE RETURNS (
    return_id INT PRIMARY KEY,
    order_id INT NULL,
    product_id INT NULL,
    return_date DATE NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Processing',
    CONSTRAINT fk_returns_orders FOREIGN KEY (order_id)
        REFERENCES ORDERS(order_id)
        ON DELETE CASCADE
        ON UPDATE SET NULL,
    CONSTRAINT fk_returns_products FOREIGN KEY (product_id)
        REFERENCES PRODUCTS(product_id)
        ON DELETE SET NULL
        ON UPDATE SET NULL
);

-- Create the REVIEWS table
CREATE TABLE REVIEWS (
    review_id INT PRIMARY KEY,
    product_id INT NULL,
    customer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    review_date DATE NOT NULL,
    CONSTRAINT fk_reviews_products FOREIGN KEY (product_id)
        REFERENCES PRODUCTS(product_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_reviews_customers FOREIGN KEY (customer_id)
        REFERENCES CUSTOMERS(customer_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- CUSTOMERS
INSERT INTO CUSTOMERS VALUES
(1, 'Amit Sharma', 'amit.sharma@email.com', '9876543210', 'Bangalore, India'),
(2, 'Pooja Singh', 'pooja.singh@email.com', '9876501234', 'Delhi, India'),
(3, 'Rahul Kumar', 'rahul.kumar@email.com', '9812345678', 'Mumbai, India'),
(4, 'Sneha Patel', 'sneha.patel@email.com', '9123456789', 'Ahmedabad, India'),
(5, 'Vikas Roy', 'vikas.roy@email.com', '9001122334', 'Kolkata, India');

-- PRODUCTS (Assuming category_id as 1 for all)
INSERT INTO PRODUCTS VALUES
(1, 'Wireless Mouse', 'Ergonomic Wireless Mouse', 550.00, 80),
(2, 'Mechanical Keyboard', 'RGB Backlit Mechanical Keyboard', 2500.00, 50),
(3, '16GB Pen Drive', 'USB 3.1 High Speed Pen Drive', 700.00, 120),
(4, 'Laptop Stand', 'Adjustable Laptop Stand', 900.00, 40),
(5, 'Bluetooth Speaker', 'Portable Bluetooth Speaker', 1200.00, 60);

-- ORDERS
INSERT INTO ORDERS VALUES
(1, 1, '2025-08-01', 'Shipped', 3200.00),
(2, 2, '2025-08-02', 'Delivered', 1450.00),
(3, 3, '2025-08-03', 'Processing', 900.00),
(4, 4, '2025-08-04', 'Cancelled', 2500.00),
(5, 5, '2025-08-05', 'Shipped', 1950.00);

-- ORDER_DETAILS
INSERT INTO ORDER_DETAILS VALUES
(1, 1, 2, 1, 2500.00),
(2, 1, 5, 1, 1200.00),
(3, 2, 1, 1, 550.00),
(4, 2, 3, 2, 700.00),
(5, 3, 4, 1, 900.00);

-- SHIPMENTS
INSERT INTO SHIPMENTS VALUES
(1, 1, '2025-08-02', '2025-08-05', 'Delivered', 'TRK001'),
(2, 2, '2025-08-03', '2025-08-06', 'Delivered', 'TRK002'),
(3, 3, '2025-08-04', NULL, 'Shipped', 'TRK003'),
(4, 4, '2025-08-06', NULL, 'Cancelled', 'TRK004'),
(5, 5, '2025-08-07', NULL, 'Shipped', 'TRK005');

-- RETURNS
INSERT INTO RETURNS VALUES
(1, 2, 3, '2025-08-09', 'Defective item', 'Processed'),
(2, 1, 5, '2025-08-10', 'Not as described', 'Processing'),
(3, 1, 2, '2025-08-10', 'Wrong item sent', 'Processing'),
(4, 2, 1, '2025-08-11', 'Damaged in transit', 'Processed'),
(5, 3, 4, '2025-08-12', 'Changed mind', 'Pending');

-- REVIEWS
INSERT INTO REVIEWS VALUES
(1, 1, 1, 4, 'Works well, satisfied!', '2025-08-06'),
(2, 3, 2, 5, 'Very fast data transfer.', '2025-08-07'),
(3, 5, 1, 2, 'Poor sound quality.', '2025-08-08'),
(4, 4, 5, 5, 'Sturdy and versatile stand!', '2025-08-09'),
(5, 2, 3, 3, 'Good keyboard, average keys.', '2025-08-10');