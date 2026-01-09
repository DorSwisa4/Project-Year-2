from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import date
from classes import RegisteredCustomer
from utils import add_to_sql, check_login

app = Flask(__name__)

app.secret_key = 'SwisBoy'

# --- 1. Database Configuration ---
# Update these details to match your MySQL Workbench setup
db_config = {
    'user': 'root',  # Your MySQL username
    'password': 'password',  # Your MySQL password
    'host': 'localhost',
    'database': 'AirlineDB'
}

# --- 2. The Home Route ---
# This serves your HTML page when you open the site
@app.route('/')
def home():
    return render_template('home_page.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign-up.html')

    if request.method == 'POST':
        # 1. Create the Object (Now including phones!)
        new_customer = RegisteredCustomer(
            email=request.form['email'],
            first_name_en=request.form['first_name'],
            last_name_en=request.form['last_name'],
            registration_date=date.today(),
            passport_num=request.form['passport_num'],
            password=request.form['password'],
            birth_date=request.form['birth_date'],
            phones=request.form.getlist('phones')  # Pass the list directly
        )

        # 2. Call the smart function
        success, message = add_to_sql(new_customer)

        # 3. Handle Result
        if success:
            # Auto-login session setup
            session['user_email'] = new_customer.email
            session['user_name'] = new_customer.first_name_en

            flash(message)  # "Registration successful!"
            return redirect(url_for('home'))
        else:
            flash(message)  # e.g., "Error: Manager phone found"
            return redirect(url_for('signup'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Just showing the form
    if request.method == 'GET':
        return render_template('login.html')

    # 2. Processing the Login
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Call our helper function
        user_name = check_login(email, password)

        if user_name:
            # SUCCESS: Create the "Session" (The digital wristband)
            session['user_email'] = email
            session['user_name'] = user_name

            flash(f"Welcome back, {user_name}!")
            return redirect(url_for('home'))
        else:
            # FAILURE
            flash("Invalid email or password. Please try again.")
            return redirect(url_for('login'))


# --- LOGOUT ROUTE (Crucial!) ---
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)