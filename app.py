from flask import Flask, jsonify, request
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import AddressNotFound

app = Flask(__name__)
tron = Tron()

# Создание нового кошелька
@app.route('/create_wallet/', methods=['POST'])
def create_wallet():
    private_key = PrivateKey.random()
    address = private_key.public_key.to_base58check_address()
    return jsonify({"address": address, "private_key": private_key.to_base58()})

# Получение баланса
@app.route('/get_balance/<address>', methods=['GET'])
def get_balance(address):
    try:
        balance = tron.get_account_balance(address)
        return jsonify({"balance": balance})
    except AddressNotFound:
        return jsonify({"detail": "Address not found"}), 404

# Отправка TRX
@app.route('/send_trx/', methods=['POST'])
def send_trx():
    request_data = request.get_json()
    from_address = request_data.get('from_address')
    to_address = request_data.get('to_address')
    amount = request_data.get('amount')

    if not all([from_address, to_address, amount]):
        return jsonify({"detail": "Missing parameters"}), 400

    try:
        # Проверка, что достаточно средств на счету
        balance = tron.get_account_balance(from_address)
        if balance < amount:
            return jsonify({"detail": "Insufficient funds"}), 400

        # Создание и подписка транзакции
        txn = (
            tron.trx.transfer(from_address, to_address, amount)
            .build()
            .sign(from_address.private_key)  # Здесь вам нужно передать приватный ключ
        )
        txn.broadcast()  # Отправка транзакции
        return jsonify({"status": "Transaction sent successfully"})
    except AddressNotFound:
        return jsonify({"detail": "Address not found"}), 404
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
