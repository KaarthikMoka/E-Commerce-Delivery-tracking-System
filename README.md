# 🛒 E-Commerce Order Tracking System

## 📘 Overview
The **E-Commerce Order Tracking System** is a MySQL-based Database Management System project designed to manage and automate order tracking, inventory control, and customer transactions.  
It demonstrates advanced SQL concepts including **triggers**, **stored procedures**, **functions**, **nested queries**, and **aggregate operations**.

---

## 🧩 Project Features
- Manage products, customers, orders, and shipments  
- Automatically update stock after orders  
- Prevent negative stock using triggers  
- Generate sales reports using stored procedures  
- Calculate customer lifetime value and product revenue  
- Handle returns and update inventory automatically  
- Support analytical queries (Group By, Nested, Correlated)

---

## 🧠 Database Objects
| Type | Count | Purpose |
|------|--------|----------|
| **Triggers** | 4 | Stock updates, validations, order total, returns |
| **Procedures** | 3 | Order history, returns, sales reports |
| **Functions** | 3 | Revenue, lifetime value, average rating |

---

## ⚙️ Technologies Used
- **Database:** MySQL  
- **Tools:** MySQL Shell / MySQL Workbench  
- **Language:** SQL  
- **Platform:** Windows / Linux  

---

## 🚀 Example Operations

### 1️⃣ Update Operation
```sql
UPDATE ORDERS SET status = 'Delivered' WHERE order_id = 105;
```
2️⃣ Delete Operation
```sql
DELETE FROM RETURNS WHERE return_id = 3;
```
3️⃣ Group By + Aggregate Query
```sql
SELECT product_id, SUM(quantity) AS total_sold 
FROM ORDER_DETAILS 
GROUP BY product_id;
```
4️⃣ Nested Query
```sql
SELECT name, price 
FROM PRODUCTS 
WHERE price > (SELECT AVG(price) FROM PRODUCTS);
```
---
📊 Example Output
|Order ID|	Customer|	Status	|Total Amount|
|------|--------|----------|----------|
|101	|201	|Delivered	|2500.00|
|102	|202	|Pending|	1400.00|
---
🏁 Conclusion

The E-Commerce Order Tracking System improves order management efficiency by automating key business logic within the database layer.
With robust SQL structures—triggers, procedures, and functions—it ensures real-time data consistency, reporting, and performance for modern e-commerce operations.
