from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import date
from classes import RegisteredCustomer
from utils import add_to_sql, check_login, is_signup_valid, get_flights, check_manager_login

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
    # CHANGE 1: Get all active flights from DB when loading the page
    all_flights = get_flights()
    # Pass the 'flights' data to the HTML template
    return render_template('home_page.html', flights=all_flights)


@app.route('/search', methods=['POST'])
def search_results():
    search_params = {
        'source_country': request.form.get('source_country'),
        'source_city': request.form.get('source_city'),
        'source_airport': request.form.get('source_airport'),
        'dest_country': request.form.get('dest_country'),
        'dest_city': request.form.get('dest_city'),
        'dest_airport': request.form.get('dest_airport'),
        'date': request.form.get('exit_date')
    }

    clean_params = {k: v for k, v in search_params.items() if v and v.strip() != ""}
    results = get_flights(clean_params)

    no_results_found = False

    # השינוי: אם אין תוצאות, טען את כל הטיסות הפעילות
    if not results:
        results = get_flights()  # מביא הכל
        no_results_found = True  # מדליק דגל כדי שנוכל להציג הודעה מתאימה

    # שולחים ל-HTML גם את הטיסות וגם את הדגל
    return render_template('home_page.html', flights=results, scroll_to_results=True, no_results_found=no_results_found)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign-up.html')

    if request.method == 'POST':
        new_customer = RegisteredCustomer(
            email=request.form['email'],
            first_name_en=request.form['first_name'],
            last_name_en=request.form['last_name'],
            registration_date=date.today(),
            passport_num=request.form['passport_num'],
            password=request.form['password'],
            birth_date=request.form['birth_date'],
            phones=request.form.getlist('phones')
        )

        is_valid, error_message = is_signup_valid(new_customer)

        if not is_valid:
            flash(error_message)
            return redirect(url_for('signup'))

        success, message = add_to_sql(new_customer)

        if success:
            session['user_email'] = new_customer.email
            session['user_name'] = new_customer.first_name_en
            flash(message)
            return redirect(url_for('home'))
        else:
            flash(message)
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

            return redirect(url_for('home'))
        else:
            # FAILURE
            flash("Invalid email or password. Please try again.")
            return redirect(url_for('login'))

@app.route('/manager_login', methods = ['GET', 'POST'])
def manager_login():
    if request.method == 'GET':
        return render_template('manager_login.html')

    if request.method =='POST':
        id_num = request.form['id_num']
        password = request.form['password']

        manager_name = check_manager_login(id_num, password)

        if manager_name:
            # Create a Manager Session
            session['user_name'] = manager_name
            session['user_id'] = id_num
            session['is_manager'] = True  # specific flag to distinguish from customers

            return redirect(url_for('manager_dashboard'))
        else:
            flash("Invalid Manager ID or Password")
            return redirect(url_for('manager_login'))




# --- LOGOUT ROUTE (Crucial!) ---
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    return redirect(url_for('home'))


@app.errorhandler(404)
def error(e):
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)