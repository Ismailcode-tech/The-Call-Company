import utils.luhn
import datetime
 
def check_card_number(card_number):
    card_number = card_number.replace(' ', '')
    if len(card_number) != 16:
        return False, 'Card number must be 16 digits'
    if not card_number.isdigit():
        return False, 'Card number must only contain numbers'
    if not utils.luhn.luhn_check(card_number):
        return False, 'Card number is not valid'
    return True, 'OK'
 
def check_expiry(month, year):
    try:
        month = int(month)
        year = int(year)
    except:
        return False, 'Expiry date must be numbers'
    if month < 1 or month > 12:
        return False, 'Month must be between 1 and 12'
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year % 100
    if year < current_year:
        return False, 'This card has expired'
    if year == current_year and month < current_month:
        return False, 'This card has expired'
    return True, 'OK'
 
def check_cvc(cvc):
    cvc = cvc.strip()
    if len(cvc) != 3:
        return False, 'CVC must be 3 digits'
    if not cvc.isdigit():
        return False, 'CVC must only contain numbers'
    return True, 'OK'
 
def validate_card(card_number, exp_month, exp_year, cvc):
    errors = []
    number_ok, number_msg = check_card_number(card_number)
    expiry_ok, expiry_msg = check_expiry(exp_month, exp_year)
    cvc_ok, cvc_msg = check_cvc(cvc)
    if not number_ok:
        errors.append(number_msg)
    if not expiry_ok:
        errors.append(expiry_msg)
    if not cvc_ok:
        errors.append(cvc_msg)
    if len(errors) == 0:
        return True, 'Card is valid'
    else:
        return False, errors
if __name__ == '__main__':
    print(validate_card('4539578763621486', '12', '26', '123'))
    print(validate_card('1234567890123456', '12', '26', '123'))
    print(validate_card('4539578763621486', '01', '23', '12'))
