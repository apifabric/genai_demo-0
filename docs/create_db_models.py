import decimal

import logging



logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

import sqlalchemy



from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py

from logic_bank.logic_bank import Rule

import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Create engine and base
Base = declarative_base()
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Session = sessionmaker(bind=engine)
session = Session()
class Customer(Base):
    """
    description: represent a customer with orders, balance and credit limit.
    """
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0)
    credit_limit = Column(Float, nullable=False)
    
class Order(Base):
    """
    description: represent an order made by a customer, includes notes.
    """
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    amount_total = Column(Float, default=0)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String)
    customer = relationship('Customer')

class Product(Base):
    """
    description: represent a product with a price, can be in multiple items.
    """
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)

class Item(Base):
    """
    description: represent an item in an order, includes quantity and amount.
    """
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, default=0)
    order = relationship('Order')
    product = relationship('Product')

# Optional additional tables, placeholder for demonstrating relationships
class Supplier(Base):
    """
    description: represent a supplier providing products.
    """
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Inventory(Base):
    """
    description: represent inventory records for products.
    """
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    product = relationship('Product')

class Shipment(Base):
    """
    description: represent a shipment containing orders.
    """
    __tablename__ = 'shipments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_date = Column(DateTime, default=datetime.datetime.now)

class Payment(Base):
    """
    description: represent a payment for an order.
    """
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    order = relationship('Order')

class Category(Base):
    """
    description: represent a category for products.
    """
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Location(Base):
    """
    description: represent a location for shipping orders.
    """
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False)

class Employee(Base):
    """
    description: represent an employee interacting with customers.
    """
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Review(Base):
    """
    description: represent a review of a product by a customer.
    """
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    product = relationship('Product')
    customer = relationship('Customer')
# Create all tables
Base.metadata.create_all(engine)
# Insert sample data
def populate_data(session):
    # Create Customers
    customer1 = Customer(name='Customer One', credit_limit=1000)
    customer2 = Customer(name='Customer Two', credit_limit=1200)
    
    # Create Products
    product1 = Product(name='Product Alpha', unit_price=20)
    product2 = Product(name='Product Beta', unit_price=30)
    
    # Create Orders
    order1 = Order(customer=customer1, amount_total=80)
    order2 = Order(customer=customer2, amount_total=150, date_shipped=datetime.datetime.now())
    
    # Create Items
    item1 = Item(order=order1, product=product1, quantity=2, unit_price=20, amount=40)
    item2 = Item(order=order1, product=product2, quantity=2, unit_price=30, amount=60)
    item3 = Item(order=order2, product=product1, quantity=1, unit_price=20, amount=20)
    item4 = Item(order=order2, product=product2, quantity=3, unit_price=30, amount=90)
    
    # Additional data to demonstrate completeness
    supplier = Supplier(name='Supplier One')
    inventory = Inventory(product=product1, quantity=100)
    shipment = Shipment(shipment_date=datetime.datetime.now())
    payment = Payment(amount=100, order=order1)
    category = Category(name='Gadgets')
    location = Location(address='123 Test St.')
    employee = Employee(name='Employee One')
    review = Review(product=product1, customer=customer1, rating=5, comment='Great product!')

    # Adding all records to session
    session.add_all([customer1, customer2, product1, product2,
                     order1, order2, item1, item2, item3, item4,
                     supplier, inventory, shipment, payment,
                     category, location, employee, review])

    # Commit the transaction
    session.commit()

populate_data(session)
# from logic_bank.logic_bank import LogicBank
# from logic_bank.rule_bank.rules import Rule

def activate_logic():
    def declare_logic():
        Rule.constraint(
            validate=Customer,
            as_condition=lambda row: row.balance <= row.credit_limit,
            error_msg="Customer {row.name} balance ({row.balance}) exceeds credit limit ({row.credit_limit})"
        )
        Rule.sum(
            derive=Customer.balance,
            as_sum_of=Order.amount_total,
            where=lambda row: row.date_shipped is None
        )
        Rule.sum(
            derive=Order.amount_total,
            as_sum_of=Item.amount
        )
        Rule.formula(
            derive=Item.amount,
            as_expression=lambda row: row.quantity * row.unit_price
        )
        Rule.copy(
            derive=Item.unit_price,
            from_parent=Product.unit_price
        )

    # LogicBank.activate(session=session, activator=declare_logic)

# Note: LogicBank usage is contextual and requires specific database integration
