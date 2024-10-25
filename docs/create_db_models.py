# created from response - used to create database and project
#  should run without error
#  if not, check for decimal, indent, or import issues

import decimal

import logging



logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

import sqlalchemy



from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py

from logic_bank.logic_bank import Rule

# SQLAlchemy database setup and model creation

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Base for declarative models
Base = declarative_base()

# Database Engine
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Session = sessionmaker(bind=engine)
session = Session()

class Customer(Base):
    """description: Table representing customers, storing their balance and credit limit."""
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    credit_limit = Column(Float, nullable=False, default=5000.0)

class Order(Base):
    """description: Table representing customer orders, including a note and shipping date."""
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date_ordered = Column(DateTime, default=datetime.datetime.utcnow)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    amount_total = Column(Float, nullable=False, default=0.0)

class Product(Base):
    """description: Table representing available products with their unit price."""
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)

class Item(Base):
    """description: Table representing items in an order, with quantity and price details."""
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    amount = Column(Float, nullable=False, default=0.0)
    unit_price = Column(Float, nullable=False)

# Create tables
Base.metadata.create_all(engine)

# Insert sample data
customer1 = Customer(name="Alice", balance=0.0, credit_limit=3000.0)
customer2 = Customer(name="Bob", balance=0.0, credit_limit=5000.0)

product1 = Product(name="Laptop", unit_price=1500.0)
product2 = Product(name="Mouse", unit_price=50.0)

order1 = Order(customer_id=1, date_ordered=datetime.datetime.now(), amount_total=0.0, notes="First order")
order2 = Order(customer_id=2, date_ordered=datetime.datetime.now(), date_shipped=datetime.datetime.now(), amount_total=0.0, notes="Second order")

item1 = Item(order_id=1, product_id=1, quantity=1, unit_price=1500.0, amount=1500.0)
item2 = Item(order_id=2, product_id=2, quantity=2, unit_price=50.0, amount=100.0)

# Manually calculate and set derived attributes
order1.amount_total = item1.amount
order2.amount_total = item2.amount

customer1.balance = order1.amount_total
customer2.balance = 0.0  # No unshipped orders for Bob

# Add data to session and commit
session.add_all([customer1, customer2, product1, product2, order1, order2, item1, item2])
session.commit()

# LogicBank rules creation
def declare_logic():
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
    Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
