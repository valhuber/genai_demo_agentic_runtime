import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import logging

app_logger = logging.getLogger(__name__)


def declare_logic():
    """
    Check Credit Use Case Logic
    
    Natural Language Requirements:
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
    """
    
    # 1. The Customer's balance is less than the credit limit
    Rule.constraint(validate=models.Customer,
                   as_condition=lambda row: row.balance <= row.credit_limit,
                   error_msg="Customer balance exceeds credit limit")
    
    # 2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    Rule.sum(derive=models.Customer.balance, 
             as_sum_of=models.Order.amount_total,
             where=lambda row: row.date_shipped is None)
    
    # 3. The Order's amount_total is the sum of the Item amount
    Rule.sum(derive=models.Order.amount_total, 
             as_sum_of=models.Item.amount)
    
    # 4. The Item amount is the quantity * unit_price
    Rule.formula(derive=models.Item.amount, 
                 as_expression=lambda row: row.quantity * row.unit_price)
    
    ''' item.unit_price copy rule disabled - superceded by supplier rules
    # 5. The Item unit_price is copied from the Product unit_price
    Rule.copy(derive=models.Item.unit_price, 
              from_parent=models.Product.unit_price)
    '''


    # New rules for Supplier and ProductSupplier

    # count indicates products has suppliers - and we must choose one (via AI)
    Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)

    def ItemUnitPriceFromSupplier(row: models.Item, old_row: models.Item, logic_row: LogicRow):
        if row.product.count_suppliers == 0:
            logic_row.debug(f"Item {row.id} has no order or order has no supplier; unit_price not set from supplier")
            return row.unit_price  # No change if no supplier
        '''
        supplier_id = row.order.supplier_id
        product_id = row.product_id
        ps = session.query(models.ProductSupplier).filter_by(supplier_id=supplier_id, product_id=product_id).first()
        if ps and ps.last_quote is not None:
            app_logger.debug(f"Item {item.id} unit_price set from supplier {supplier_id} last_quote {ps.last_quote}")
            return ps.last_quote
        else:
            app_logger.debug(f"Item {item.id} has no matching ProductSupplier for supplier {supplier_id}; unit_price not changed")
            return item.unit_price  # No change if no matching ProductSupplier
        '''
    
    Rule.formula(derive=models.Item.unit_price, calling=ItemUnitPriceFromSupplier)

