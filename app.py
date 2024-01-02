from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import random
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db'
app.secret_key = 'njcv87vbcvb8778bvcvbcv9889vbcvbvc'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(16), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    current_amount = db.Column(db.Float, default=1000.0)

def generate_account_number():
    return ''.join(str(random.randint(0, 9)) for _ in range(16))


def encrypt_password(password):
    key = get_random_bytes(8)
    cipher = DES.new(key, DES.MODE_ECB)
    padded_password = password + ' ' * (8 - len(password) % 8)
    encrypted_password = cipher.encrypt(padded_password.encode())
    return b64encode(key + encrypted_password).decode()

def decrypt_password(encrypted_password):
    data = b64decode(encrypted_password.encode())
    key = data[:8]
    encrypted_password = data[8:]
    cipher = DES.new(key, DES.MODE_ECB)
    decrypted_password = cipher.decrypt(encrypted_password).decode().rstrip()
    return decrypted_password


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        return redirect(url_for("index"))
    return render_template("index.html")

account_number = generate_account_number()
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        password = request.form['password']
        encrypted_password = encrypt_password(password)
        session['account_number'] = account_number
        new_user = User(account_number=account_number, password=encrypted_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login', account_number=account_number))

    return render_template('signup.html', account_number=account_number)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_account_number = request.form['accountNumber']
        entered_password = request.form['password']
        user = User.query.filter_by(account_number=entered_account_number).first()

        if user and decrypt_password(user.password) == entered_password:
            session['account_number'] = user.account_number
            return redirect(url_for('dashboard'))
        else:
            error_message = 'Invalid account number or password. Please try again.'
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])


def dashboard():
    account_number = session.get('account_number')
    if not account_number:
        return redirect(url_for('index'))

    user = User.query.filter_by(account_number=account_number).first()
    if not user:
        return redirect(url_for('index'))

    return render_template("dashboard.html", user=user)

@app.route('/fund_transfer', methods=['GET', 'POST'])
def fund_transfer():
    if request.method == 'POST':
        amount_to_transfer = float(request.form['amount'])
        recipient_account_number = request.form['accountNumber']
        sender_password = request.form['password']

        sender_account_number = session.get('account_number')
        sender = User.query.filter_by(account_number=sender_account_number).first()

        if sender and decrypt_password(sender.password) == sender_password:
            recipient = User.query.filter_by(account_number=recipient_account_number).first()

            if recipient:
                if sender.current_amount >= amount_to_transfer:
                    sender.current_amount -= amount_to_transfer
                    recipient.current_amount += amount_to_transfer
                    db.session.commit()
                    print("Transfer successful")
                    return redirect(url_for('dashboard'))
                else:
                    error_message = 'Insufficient funds for the transfer.'
            else:
                error_message = 'Recipient account not found.'
        else:
            error_message = 'Invalid password. Please try again.'

        print(f"Error: {error_message}")

        return render_template('fund_transfer.html', error_message=error_message)

    return render_template('fund_transfer.html')

@app.route('/process_transfer', methods=['POST'])
def process_transfer():
    account_number = session.get('account_number')
    user = User.query.filter_by(account_number=account_number).first()

    if user:
        amount_to_transfer = float(request.form.get('amount', 0))
        recipient_account_number = request.form.get('accountNumber')
        sender_password = request.form.get('password')

        if decrypt_password(user.password) == sender_password:
            if user.current_amount >= amount_to_transfer:
                user.current_amount -= amount_to_transfer

                recipient = User.query.filter_by(account_number=recipient_account_number).first()

                if recipient:
                    recipient.current_amount += amount_to_transfer
                    db.session.commit()

                    flash('Fund transfer successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Recipient account not found.', 'error')
            else:
                flash('Insufficient funds for the transfer.', 'error')
        else:
            flash('Invalid password. Please try again.', 'error')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
