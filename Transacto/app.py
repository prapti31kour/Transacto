from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import socket
import traceback
import uuid


app = Flask(__name__)
app.config.from_object('config.Config')

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    cardholder_name = request.form['username']
    card_no = request.form['card_no']
    password = generate_password_hash(request.form['password'])
    mac_address = get_mac_address()

    conn = get_db_connection()
    if conn is None:
        flash('Database connection error. Please try again later.', 'danger')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cards (cardholder_name, card_no, password, mac_address) VALUES (%s, %s, %s, %s)', (cardholder_name, card_no, password, mac_address))
        conn.commit()
        flash('Registration successful!', 'success')
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        flash('An error occurred while registering. Please try again.', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('transaction'))

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if request.method == 'POST':
        card_no = request.form['card_no']
        password = request.form['password']
        mac_address = get_mac_address()

        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('transaction'))

        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cards WHERE card_no = %s', (card_no,))
            user = cursor.fetchone()

            if user and check_password_hash(user[3], password):
                if user[4] == mac_address:
                    flash('Transaction Successful!', 'success')
                else:
                    flash('Transaction Failed: Invalid MAC address.', 'danger')
            else:
                flash('Invalid Card No or Password.', 'danger')

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            flash('An error occurred while processing the transaction. Please try again.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('transaction.html')


def get_mac_address():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)])

if __name__ == '__main__':
    app.run(debug=True)
