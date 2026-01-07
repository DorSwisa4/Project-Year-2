from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import date
from classes import RegisteredCustomer
from utils import add_to_sql

app = Flask(__name__)

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
            return redirect(url_for('dashboard'))
        else:
            flash(message)  # e.g., "Error: Manager phone found"
            return redirect(url_for('signup'))


@app.route('/dashboard')
def dashboard():
    return "Dashboard"  # Placeholder


if __name__ == '__main__':
    app.run(debug=True)

# --- 4. Run the App ---
if __name__ == '__main__':
    app.run(debug=True)