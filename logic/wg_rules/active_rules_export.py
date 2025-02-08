import logging
from logic_bank.logic_bank import DeclareRule, Rule, LogicBank
from database.models import *
from decimal import Decimal
from datetime import date, datetime

log = logging.getLogger(__name__)

def declare_logic():
    """
        declare_logic - declare rules
        this function is called from logic/declare_logic.py
    """
    log.info("declare_logic - active rules")
    
    # Exported Rules:
    # Customer Balance Constraint 
    # Ensures the customer's balance is aligned with the credit limit.
    Rule.constraint(validate=Customer,
                    as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg='Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})')
    
    # Customer Balance Derivation 
    # Calculates the customer's balance as the sum of orders' amount_total where date_shipped is null.
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
    
    # Order Amount Total Derivation 
    # Calculates order's amount_total as the sum of item amounts.
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
    
    # Item Amount Derivation 
    # Calculates item amount as quantity multiplied by unit price.
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    
    # Copy Item Unit Price 
    # Copies the product's unit price to the item.
    Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
    
    # Order Kafka Integration 
    # Sends the order to Kafka topic 'order_shipping' if the date shipped is not None.
    Rule.after_flush_row_event(on_class=Order, calling=kafka_producer.send_row_to_kafka, if_condition=lambda row: row.date_shipped is not None, with_args={"topic": "order_shipping"})
    