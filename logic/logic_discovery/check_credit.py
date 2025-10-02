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
            return row.product.unit_price  # No change if no supplier
        # #als: triggered inserts - https://apilogicserver.github.io/Docs/Logic-Use/#in-logic TODO: fix
        sys_supplier_req_logic_row : models.SysSupplierReq = logic_row.new_logic_row(models.SysSupplierReq)
        sys_supplier_req = sys_supplier_req_logic_row.row
        sys_supplier_req_logic_row.link(to_parent=logic_row)
        sys_supplier_req.product_id = row.product_id
        sys_supplier_req.item_id = row.id
        # this calls choose_supplier_for_item_with_ai, which sets chosen_supplier_id and chosen_unit_price
        sys_supplier_req_logic_row.insert(reason="Supplier Svc Request ", row=sys_supplier_req)  # triggers rules...
        return sys_supplier_req.chosen_unit_price
    
    ''' proposed by GPT (unused)
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

    def choose_supplier_for_item_with_ai(row: models.SysSupplierReq, old_row: models.SysSupplierReq, logic_row: LogicRow):
        '''  Choose a supplier for the SysSupplierReq using AI (simulated here).
             Sets chosen_supplier_id and chosen_unit_price on the SysSupplierReq row.
        '''
        if logic_row.is_inserted():
            # Call AI service to choose supplier based on payload and top_n
            # For demonstration, we'll just pick the first from top_n if available
            for each_supplier in row.product.ProductSupplierList:
                logic_row.log(f"SysSupplierReq {row.id} has supplier candidate {each_supplier.supplier_id} ")
                if row.chosen_supplier is None:
                    row.chosen_supplier_id = each_supplier.supplier_id
                    row.chosen_unit_price = each_supplier.unit_cost
                    logic_row.log(f"Chosen supplier {row.chosen_supplier_id} for SysSupplierReq {row.id} by default (first candidate)")
            ''' proposed by GPT
            if row.top_n and isinstance(row.top_n, list) and len(row.top_n) > 0:
                chosen = row.top_n[0]  # In real case, call AI to choose
                row.chosen_supplier_id = chosen.get("supplier_id")
                logic_row.debug(f"Chosen supplier {row.chosen_supplier_id} for SysSupplierReq {row.id} using AI")
            else:
                logic_row.debug(f"No candidates in top_n to choose from for SysSupplierReq {row.id}")
            '''

    Rule.early_row_event(models.SysSupplierReq, calling=choose_supplier_for_item_with_ai)

