import requests
from getmac import get_mac_address

def register_user(cardholder_name, card_no, password):
    mac_address = get_mac_address()
    response = requests.post('http://localhost:5000/register', json={
        'cardholder_name': cardholder_name,
        'card_no': card_no,
        'password': password,
        'mac_address': mac_address
    })
    print(response.json())

def perform_transaction(card_no, password):
    mac_address = get_mac_address()
    response = requests.post('http://localhost:5000/transaction', json={
        'card_no': card_no,
        'password': password,
        'mac_address': mac_address
    })
    print(response.json())

# Example usage
register_user('John Doe', '1234567890', 'password123')
perform_transaction('1234567890', 'password123')
