#--------------------------------------------IMPORTS----------------------------------------------#

from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import select, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from typing import List
import datetime 

#--------------------------------------------------------------------------------------------------------------#
#------------------------------------------Connect DB------------------------------------------------------#

app = Flask(__name__) # Create a Flask application
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:OmenisbehindU!@localhost/e_commerce_api" # Database URI
app.json.sort_keys = False # Prevents jsonify from sorting the keys

#---------------------------------------------------------------------------------------------------------------------#
#------------------------------------------Create Base Class------------------------------------------------------#

class Base(DeclarativeBase): # Base class for all models
    pass

db = SQLAlchemy(app, model_class=Base) # Initialize the database
ma = Marshmallow(app) # Initialize Marshmallow

class Customer(Base): # Customer model
    __tablename__ = "Customers" # Table name
    customer_id: Mapped[int] = mapped_column(primary_key=True) # Customer ID
    name: Mapped[str] = mapped_column(db.String(255), nullable = False) # Customer Name
    email: Mapped[str] = mapped_column(db.String(320)) # Customer Email
    phone: Mapped[str] = mapped_column(db.String(15)) # Customer Phone Number
 
    orders: Mapped[List["Order"]] = db.relationship(back_populates="customer") # Relationship with Order model

# association (join) table for managing many-to-many relationships
order_product = db.Table(
    "Order_Product", 
    Base.metadata, 
    db.Column("order_id", db.ForeignKey("Orders.order_id"), primary_key=True), # Foreign key to Orders table
    db.Column("product_id", db.ForeignKey("Products.product_id"), primary_key=True) # Foreign key to Products table
)

class Order(Base): # Order model
    __tablename__ = "Orders" # Table name
    order_id: Mapped[int] = mapped_column(primary_key=True) # Order ID
    date: Mapped[datetime.date] = mapped_column(db.Date, nullable=False) # Order Date

    customer_id: Mapped[int] = mapped_column(db.ForeignKey('Customers.customer_id')) # Foreign key to Customers table

    customer: Mapped["Customer"] = db.relationship(back_populates="orders") # Relationship with Customer model
    products: Mapped[List["Product"]] = db.relationship(secondary=order_product) # Relationship with Product model

class Product(Base): # Product model
    __tablename__ = "Products" # Table name
    product_id: Mapped[int] = mapped_column(primary_key=True) # Product ID
    name: Mapped[str] = mapped_column(db.String(255), nullable = False) # Product Name
    price: Mapped[float] = mapped_column(db.Float, nullable = False) # Product Price

# Initialize the database and create tables
with app.app_context(): 
    # db.drop_all() # Drop tables
    db.create_all() # Create tables

#---------------------------------------------------------------------------------------------------------------------#
#------------------------------------------Create Schemas-----------------------------------------------------------#

#--------------------Customer Schema---------------------#
# Schema for a single customer with optional id
class CustomerSchema(ma.Schema): # Customer schema
    customer_id = fields.Integer(required=False) # Customer ID
    name = fields.String(required=True) # Customer Name
    email = fields.String(required=True) # Customer Email
    phone = fields.String(required=True) # Customer Phone Number

    class Meta: # Fields to include in the schema
        fields = ("customer_id", "name", "email", "phone") 

# Schema for a list of customers with a required id
class CustomersSchema(ma.Schema): # Customers schema
    customer_id = fields.Integer(required=True) # Customer ID
    name = fields.String(required=True) # Customer Name
    email = fields.String(required=True) # Customer Email
    phone = fields.String(required=True) # Customer Phone Number

    class Meta: # Fields to include in the schema
        fields = ("customer_id", "name", "email", "phone")

customer_schema = CustomerSchema() # Initialize the customer schema
customers_schema = CustomersSchema(many=True) # Initialize the customers schema for multiple customers

#--------------------Product Schema---------------------#
class ProductSchema(ma.Schema): # Product schema
    product_id = fields.Integer(required=False) # Product ID
    name = fields.String(required=True) # Product Name
    price = fields.Float(required=True) # Product Price

    class Meta: # Fields to include in the schema
        fields = ("product_id", "name", "price")

product_schema = ProductSchema() # Initialize the product schema
products_schema = ProductSchema(many=True) # Initialize the products schema for multiple products

#--------------------Order Schema---------------------#
class OrderSchema(ma.Schema): # Order schema
    order_id = fields.Integer(required=False) # Order ID
    date = fields.Date(required=True) # Order Date
    customer_id = fields.Integer(required=True) # Customer ID

    class Meta: # Fields to include in the schema
        fields = ("order_id", "date", "customer_id") 

order_schema = OrderSchema() # Initialize the order schema
orders_schema = OrderSchema(many=True) # Initialize the orders schema for multiple orders

#---------------------------------------------------------------------------------------------------------------------#
#------------------------------------------Create Customer Routes-----------------------------------------------------------#
@app.route("/") 
def home(): # Home route
    return "Hello there, welcome and thanks for stopping by!"

#--------------------Get All Customers---------------------#
@app.route("/customers", methods=["GET"]) # Get all customers
def get_customers(): # Function to get all customers
    query = select(Customer) # Query to select all customers
    result = db.session.execute(query).scalars() # Execute the query
    print(result) # Print the result
    customers = result.all() # Get all customers
    return customers_schema.jsonify(customers) # Return the customers as JSON

#--------------------Get Customer By ID---------------------#
@app.route("/customers/<int:id>", methods=["GET"]) # Get a customer by ID
def get_customer_by_id(id): # Function to get a customer by ID
    query = select(Customer).filter(Customer.customer_id==id) # Query to select a customer by ID
    customer = db.session.execute(query).scalars().first() # Execute the query

    if customer: # If the customer exists
        return customer_schema.jsonify(customer)
    else: # If the customer does not exist
        return jsonify({"message": "Customer not found"}), 404 
    
#--------------------Create Customer---------------------#
@app.route("/customers", methods=["POST"]) # Create a new customer
def add_customer(): # Function to add a new customer
    try: 
        customer_data = customer_schema.load(request.json) # Load the customer data
        print(customer_data) # Print the customer data
    
    except ValidationError as err: # If there is a validation error
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session: # Create a session
        new_customer = Customer(name=customer_data["name"], email=customer_data["email"], phone=customer_data["phone"]) # Create a new customer
        session.add(new_customer) # Add the new customer to the session
        session.commit() # Commit the session

    return jsonify({"message": "New customer added succesfully"}), 201

#---------------------Update a Customer---------------------#
@app.route("/customers/<int:id>", methods=["PUT"]) # Update a customer
def update_customer(id): # Function to update a customer
    with Session(db.engine) as session: # Create a session
        with session.begin(): # Begin the session
            query = select(Customer).filter(Customer.customer_id == id) # Query to select a customer by ID
            result = session.execute(query).scalars().first() # Execute the query
            if result is None: # If the customer does not exist
                return jsonify({"error": "Customer Not Found"}), 404
            customer = result # Get the customer

            try: # Try to load the customer data
                customer_data = customer_schema.load(request.json) # Load the customer data
            except ValidationError as err:
                return jsonify(err.messages), 400
            
            for field, value in customer_data.items(): # Update the customer data
                setattr(customer, field, value) # Set the customer field to the value

            session.commit() # Commit the session
            return jsonify({"message": "Customer details updated succesfully"}), 200

#---------------------Delete a Customer---------------------#
@app.route("/customers/<int:id>", methods=["DELETE"]) # Delete a customer
def delete_customer(id): # Function to delete a customer
    delete_statement = delete(Customer).where(Customer.customer_id == id) # Delete statement
    with db.session.begin():  # Begin the session
        result = db.session.execute(delete_statement)  # Execute the delete statement
        print(result) # Print the result
        if result.rowcount == 0: # If the customer does not exist
            return jsonify({"error": "Customer not found"}), 404
        
        return jsonify({"message": "Customer removed successfully"}), 200
    
#---------------------------------------------------------------------------------------------------------------------#
#------------------------------------------Create Product Routes-----------------------------------------------------------#

#--------------------Get All Products---------------------#
@app.route("/products", methods=["GET"]) # Get all products
def get_products(): # Function to get all products
    query = select(Product) # Query to select all products
    result = db.session.execute(query).scalars() # Execute the query
    products = result.all() # Get all products

    return products_schema.jsonify(products) # Return the products as JSON

#--------------------Get Product by name---------------------#
@app.route("/products/by-name/<string:name>", methods = ["GET"]) # Get a product by name
def get_product_by_name(name): # Function to get a product by name
    search = f"%{name}%" # Search query
    query = select(Product).where(Product.name.like(search)).order_by(Product.price.asc()) # Query to select a product by name
    products = db.session.execute(query).scalars().all() # Execute the query

    return products_schema.jsonify(products) # Return the products as JSON

#--------------------Create Product---------------------#
@app.route('/products', methods=["POST"]) # Create a new product
def add_product(): # Function to add a new product
    try:  # Try to load the product data
        product_data = product_schema.load(request.json) # Load the product data

    except ValidationError as err: # If there is a validation error
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session: # Create a session
        with session.begin(): # Begin the session
            new_product = Product(name=product_data['name'], price=product_data['price'] ) # Create a new product
            session.add(new_product) # Add the new product to the session
            session.commit() # Commit the session

    return jsonify({"message": "Product added successfully"}), 201 # Return a success message

#--------------------Update Product---------------------#
@app.route("/products/<int:id>", methods=["PUT"]) # Update a product
def update_product(id): # Function to update a product
    with Session(db.engine) as session: # Create a session
        with session.begin(): # Begin the session
            query = select(Product).filter(Product.product_id==id) # Query to select a product by ID
            result = session.execute(query).scalars().first() # Execute the query
            if result is None: # If the product does not exist
                return jsonify({"error": "Product not found"}), 404 
            product = result # Get the product

            try: # Try to load the product data
                product_data = product_schema.load(request.json) # Load the product data
            except ValidationError as err: # If there is a validation error
                return jsonify(err.messages), 400
            
            for field, value in product_data.items(): # Update the product data
                setattr(product, field, value ) # Set the product field to the value
            
            session.commit() # Commit the session
            return jsonify({"message": "Product successfully updated!"}), 200

#--------------------Delete Product---------------------#
@app.route("/products/<int:id>", methods=["DELETE"]) # Delete a product
def delete_product(id): # Function to delete a product
    delete_statement = delete(Product).where(Product.product_id==id) # Delete statement
    with db.session.begin(): # Begin the session
        result = db.session.execute(delete_statement) # Execute the delete statement
        if result.rowcount == 0: # If the product does not exist
            return jsonify({"error": "Product Not found"}), 404
        
        return jsonify({"message": "Product removed successfully"}), 200 # Return a success message

#---------------------------------------------------------------------------------------------------------------------#
#------------------------------------------Create Order Routes-----------------------------------------------------------#

#---------------------Get All Orders---------------------#
@app.route("/orders", methods=["GET"]) # Get all orders
def get_orders(): # Function to get all orders
    query = select(Order) # Query to select all orders
    result = db.session.execute(query).scalars() # Execute the query
    orders = result.all() # Get all orders

    return orders_schema.jsonify(orders) # Return the orders as JSON

#---------------------Get Order By Customer ID---------------------#
@app.route("/orders/<int:customer_id>", methods = ["GET"]) # Get orders by customer ID
def get_order_by_customer(customer_id): # Function to get orders by customer ID
    query = select(Order).where(Order.customer_id==customer_id) # Query to select orders by customer ID
    orders = db.session.execute(query).scalars() # Execute the query
    
    return orders_schema.jsonify(orders) # Return the orders as JSON

#---------------------Create Order---------------------#
@app.route("/orders", methods=["POST"]) # Create a new order
def add_order(): # Function to add a new order
    try: # Try to load the order data
        order_data = order_schema.load(request.json) # Load the order data
    except ValidationError as err: # If there is a validation error
        return jsonify(err.messages), 400 
    
    with Session(db.engine) as session: # Create a session
        with session.begin(): # Begin the session
            new_order = Order(date=order_data['date'], customer_id=order_data['customer_id']) # Create a new order
            session.add(new_order) # Add the new order to the session

            session.commit() # Commit the session
            return jsonify({"message": "New order has been added successfully"}), 201 # Return a success message

#---------------------Update Order---------------------#
@app.route("/orders/<int:id>", methods=["PUT"]) # Update an order
def update_order(id): # Function to update an order
    with Session(db.engine) as session: # Create a session
        with session.begin(): # Begin the session
            query = select(Order).filter(Order.order_id==id) # Query to select an order by ID
            result = session.execute(query).scalars().first() # Execute the query
            if result is None: # If the order does not exist
                return jsonify({"error": "Order not found"}), 404 
            order = result # Get the order

            try: # Try to load the order data
                order_data = order_schema.load(request.json) # Load the order data
            except ValidationError as err: # If there is a validation error
                return jsonify(err.messages), 400
            
            for field, value in order_data.items(): # Update the order data
                setattr(order, field, value ) # Set the order field to the value
            
            session.commit() # Commit the session
            return jsonify({"message": "Order successfully updated!"}), 200 # Return a success message

#---------------------Delete Order---------------------#
@app.route("/orders/<int:id>", methods=["DELETE"]) # Delete an order
def delete_order(id): # Function to delete an order
    delete_statement = delete(Order).where(Order.order_id==id) # Delete statement
    with db.session.begin(): # Begin the session
        result = db.session.execute(delete_statement) # Execute the delete statement
        if result.rowcount == 0: # If the order does not exist
            return jsonify({"error": "Order Not found"}), 404 # Return an error message
        
        return jsonify({"message": "Order removed successfully"}), 200 # Return a success message

#---------------------------------------------------------------------------------------------------------------------#

#-----------------Run--------------------#
if __name__ == "__main__": # Run the application
    app.run(debug=True)