
from logic_bank.logic_bank import Rule
from database.models import *
import integration.kafka.kafka_producer as kafka_producer

def init_rule():
  Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
