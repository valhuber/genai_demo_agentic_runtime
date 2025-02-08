
from logic_bank.logic_bank import Rule
from database.models import *
import integration.kafka.kafka_producer as kafka_producer

def init_rule():
  Rule.constraint(validate=Customer,
                  as_condition=lambda row: row.balance <= row.credit_limit,
                  error_msg='Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})')
