# **E-Commerce API**

Welcome! This provides a quick overview of the E-Commerce API and how to get started using it.

## ·Features· 


**♡ Customer Management:** *Create, retrieve, update, and delete customer information.*

**♡ Product Management:** *Add, view, update, and remove product listings.*

**♡ Order Management:** *Create, view, update, and cancel orders.*

**♡ Database Interaction:** *Utilizes SQLAlchemy to interact with the database efficiently.*

**♡ Validation:** *Implements data validation using Marshmallow to ensure data integrity.*

**♡ Error Handling:** *Provides detailed error messages and proper HTTP status codes for better debugging and user experience.*

**♡ Flexibility:** *Supports various database backends, including MySQL.*

**♡ Easy Integration:** *Simple to integrate with existing systems or frontend applications.*
<br />


## ·Prerequisites·
**♡ *Python 3.x***

**♡ *Flask***

**♡ *SQLAlchemy***

**♡ *Flask-SQLAlchemy***

**♡ *Flask-Marshmallow***


## ·Usage·
***The API provides endpoints for managing customers, products, and orders.***

<br />

**♡ Customers:**

**`/customers`**: Get all customers.

**`/customers/<customer_id>`**: Get a customer by ID.

**`/customers`**: Create a new customer.

**`/customers/<customer_id>`**: Update a customer.

**`/customers/<customer_id>`**: Delete a customer.

**♡ Products:** 

**`/products`**: Get all products.

**`/products/by-name/<product_name>`**: Get products by name.

**`/products`**: Create a new product.

**`/products/<product_id>`**: Update a product.

**`/products/<product_id>`**: Delete a product.

**♡ Orders:** 

**`/orders`**: Get all orders.

**`/orders/<customer_id>`**: Get orders by customer ID.

**`/orders`**: Create a new order.

**`/orders/<order_id>`**: Update an order.

**`/orders/<order_id>`**: Delete an order.

<br />

*Refer to the API documentation for detailed usage instructions.*


## ·Error Handling·

**♡* The API provides detailed error messages and appropriate HTTP status codes to handle various scenarios such as invalid requests, missing data, or database errors. Error responses are formatted in JSON for easy interpretation by client applications.**

