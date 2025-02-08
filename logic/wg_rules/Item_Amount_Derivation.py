
from logic_bank.logic_bank import Rule
from database.models import *
import integration.kafka.kafka_producer as kafka_producer

def init_rule():
  Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
