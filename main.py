from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import date
from classes import RegisteredCustomer, EmployeeFactory, Plane
from utils import add_to_sql, check_login, is_signup_valid, get_flights, get_unique_locations, check_manager_login, get_flight_details, get_user_details, is_manager_phone

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
    if session.get('is_manager'):
        return redirect(url_for('manager_dashboard'))
    else:
        all_flights = get_flights()
        return render_template('home_page.html', flights=all_flights)


@app.route('/search', methods=['POST'])
def search_results():
    search_params = {
        'flight_id': request.form.get('flight_num'),
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


@app.route('/api/get-options')
def get_options():
    request_type = request.args.get('type')
    parent_val = request.args.get('parent_val')
    location_side = request.args.get('side')

    data = []

    if request_type == 'country':
        data = get_unique_locations('country', location_type=location_side)

    elif request_type == 'city':
        data = get_unique_locations('city', 'country', parent_val, location_type=location_side)

    elif request_type == 'airport':
        data = get_unique_locations('airport', 'city', parent_val, location_type=location_side)

    return jsonify(data)


@app.route('/order/<flight_id>', methods=['GET', 'POST'])
def order_page(flight_id):
    if request.method == 'GET':
        flight = get_flight_details(flight_id)
        if not flight:
            flash("Flight not found.")
            return redirect(url_for('home'))

        user = None
        if 'user_email' in session:
            user = get_user_details(session['user_email'])

        return render_template('booking.html', flight=flight, user=user)

    if request.method == 'POST':
        phones = request.form.getlist('phones[]')

        for phone in phones:
            clean_phone = phone.strip()
            if clean_phone and is_manager_phone(clean_phone):
                flash(
                    f"The phone number {clean_phone} is associated with a Manager account and cannot be used for booking.")
                return redirect(url_for('order_page', flight_id=flight_id))

        booking_data = {
            'flight_id': flight_id,
            'email': request.form.get('email'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phones': phones,
            'tickets_economy': int(request.form.get('tickets_economy', 0)),
            'tickets_business': int(request.form.get('tickets_business', 0))
        }

        if booking_data['tickets_economy'] == 0 and booking_data['tickets_business'] == 0:
            flash("You must select at least one ticket.")
            return redirect(url_for('order_page', flight_id=flight_id))

        session['temp_booking'] = booking_data

        return "Redirecting to Seat Selection Page... (Next Step)"

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
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_name = check_login(email, password)

        if user_name:
            session['user_email'] = email
            session['user_name'] = user_name

            return redirect(url_for('home'))
        else:
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


@app.route('/manager-dashboard', methods=['GET', 'POST'])
def manager_dashboard():
    if not session.get('is_manager'):
        flash("Access Denied. Managers only.")
        return redirect(url_for('manager_login'))

    if request.method == 'GET':
        return render_template('manager_dashboard.html')

    return render_template('manager_dashboard.html')

@app.route('/manager-dashboard/add-employee', methods=['GET', 'POST'])
def add_employee():
    if request.method =='GET':
        return render_template('add-employee.html')

    if request.method == 'POST':
        employee_data = {
            'id_num' : request.form.get('id_num'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phone': request.form.get('phone'),
            'city': request.form.get('city'),
            'street': request.form.get('street'),
            'house_number': request.form.get('house_number'),
            'start_date': date.today(),
            'password': request.form.get('password'),
            'long_flight_training': request.form.get('long_flight_training')

        }

        role = request.form.get('role')

        new_employee = EmployeeFactory.create_employee(role, employee_data)

        success, message = add_to_sql(new_employee)

        if success:
            flash(f"Success! Added {role} named {employee_data['first_name']} ")
            return redirect(url_for('add_employee'))

        else:
            flash(f"Error: {message}")
            return redirect(url_for('add_employee'))

@app.route('/manager-dashboard/add-plane', methods=['GET','POST'])
def add_plane():
    if request.method == 'GET':
        return render_template('add-plane.html')

    if request.method == 'POST':
        counter = 1
        new_plane = Plane(
            plane_id = counter,
            manufacturer = request.form.get('manufacturer'),
            purchase_date = request.form.get('purchase_date'),
            size = request.form.get('size')
        )

    success, message = add_to_sql(new_plane)

    if success:
        flash(f"Success! Added a new plane: manufacturer: {request.form.get('manufacturer')} serial number: {counter}")
        flash(message)
        counter += 1
        return redirect(url_for('add_plane'))
    else:
        flash(f"Error: {message}")
        return redirect(url_for('add_plane'))




# --- LOGOUT ROUTE (Crucial!) ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.errorhandler(404)
def error(e):
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

