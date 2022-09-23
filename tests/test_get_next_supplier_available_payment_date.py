from utils.utils import *
from datetime import datetime

def test_get_next_supplier_available_payment_date_in_same_year():
    current_payment_date = datetime.strptime("23-09-22", '%d-%m-%y')
    new_payment_date = get_next_supplier_available_payment_date(current_payment_date)
    assert new_payment_date == "11-10-2022"

def test_get_next_supplier_available_payment_date_between_changing_years():
    current_payment_date = datetime.strptime("23-12-22", '%d-%m-%y')
    new_payment_date = get_next_supplier_available_payment_date(current_payment_date)
    assert new_payment_date == "10-01-2023"