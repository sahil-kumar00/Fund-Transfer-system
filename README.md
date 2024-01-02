Fund Transfer System

Overview:
The Flask Fund Transfer system App is a web application built with Flask and SQLAlchemy to provide users with a basic fund transfer experience experience. Users can sign up, log in, view their dashboard, and transfer funds to other accounts.

Features:
User Authentication: Secure user authentication using DES password encryption.
User Dashboard: View account information and current balance.
Fund Transfer: Transfer funds securely between accounts.

Installation:
1. Download the repository to your device.
2. cd Fund-Transfer-system
3. pip install flask flask-sqlalchemy pycryptodome

Usage:
1. Run app.py file.
2. Open your browser and go to http://localhost:5000/
3. Sign up for a new account or log in with an existing account.
4. You can only signup with one account at a time. To get another account number, you have to rerun the app.py file.
5. If it shows "ModuleNotFound Crypto" error while running the script you should change the name 'Crypto' to 'Cryptodome'.
