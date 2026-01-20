from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import date
from classes import *
from utils import *
import mysql.connector

app = Flask(__name__)

app.secret_key = 'SwisBoy'

# --- 1. Database Configuration ---
# Update these details to match your MySQL Workbench setup
db_config = {
    'user': 'root',  # Your MySQL username
    'password': 'root',  # Your MySQL password
    'host': 'localhost',
    'database': 'airlinedb'
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


# Add this to main.py

@app.route('/my-bookings')
def my_bookings():
    # 1. Security Check
    if 'user_email' not in session:
        flash("Please login to view your bookings.")
        return redirect(url_for('login'))

    if session.get('is_manager'):
        return redirect(url_for('manager_dashboard'))

    # 2. Fetch Data
    user_email = session['user_email']
    orders = get_customer_orders_history(user_email)

    return render_template('my-bookings-history.html', orders=orders)


@app.route('/cancel-order/<int:order_code>/<int:flight_id>')
def cancel_order(order_code, flight_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # 1. Re-validate the 36-hour rule on the server side (Security)
    flight = get_flight_details(flight_id)  # Using existing util function
    if not flight:
        flash("Flight not found.")
        return redirect(url_for('my_bookings'))

    flight_time = flight['departure_time']
    # If departure_time is a string, convert it. If datetime object, use directly.
    if isinstance(flight_time, str):
        flight_time = datetime.strptime(flight_time, '%Y-%m-%d %H:%M:%S')

    time_diff = flight_time - datetime.now()

    if time_diff < timedelta(hours=36):
        flash("Error: Cannot cancel. Less than 36 hours remaining to flight.")
        return redirect(url_for('my_bookings'))

    # 2. Perform Cancellation
    success = cancel_order_by_user(order_code)

    if success:
        flash("Order cancelled successfully. You have been charged 5% of the total cost.")
    else:
        flash("Error occurred while cancelling order.")

    return redirect(url_for('my_bookings'))


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

        return redirect(url_for('seat_selection'))

@app.route('/seat-selection', methods=['GET', 'POST'])
def seat_selection():
    if 'temp_booking' not in session:
        return redirect(url_for('home'))

    booking_data = session['temp_booking']
    flight_id = booking_data['flight_id']

    total_needed = int(booking_data['tickets_economy']) + int(booking_data['tickets_business'])

    if request.method == 'GET':
        flight = get_flight_details(flight_id)
        layout = get_plane_layout(flight['plane_id'])
        occupied_seats = get_occupied_seats(flight_id)

        col_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        return render_template('seat_selection.html',
                               flight=flight,
                               layout=layout,
                               occupied_seats=occupied_seats,
                               booking=booking_data,
                               col_letters=col_letters,
                               total_needed=total_needed)

    if request.method == 'POST':
        selected_seats = request.form.getlist('selected_seats')

        if len(selected_seats) != total_needed:
            flash(f"Almost there! You selected {len(selected_seats)} seats — please select exactly {total_needed} seats to continue.")
            return redirect(url_for('seat_selection'))

        session['temp_booking']['selected_seats'] = selected_seats
        session.modified = True

        flash("Great choice! Your seats have been selected. Let’s move on to payment.")
        return redirect(url_for('payment_page'))


@app.route('/payment', methods=['GET', 'POST'])
def payment_page():
    if 'temp_booking' not in session:
        return redirect(url_for('home'))

    booking_data = session['temp_booking']
    flight_id = booking_data['flight_id']
    flight = get_flight_details(flight_id)

    total_price = (int(booking_data['tickets_economy']) * flight['price_economy']) + \
                  (int(booking_data['tickets_business']) * flight['price_business'])

    if request.method == 'GET':
        return render_template('payment.html', price=total_price, booking=booking_data, flight=flight)

    if request.method == 'POST':
        email = booking_data['email']

        is_registered = is_email_registered(email)

        guest_email_val = None
        registered_email_val = None

        if is_registered:
            registered_email_val = email
        else:
            guest_email_val = email
            ensure_guest_exists(
                email,
                booking_data['first_name'],
                booking_data['last_name'],
                booking_data['phones']
            )

        new_order = Order(
            order_code=None,
            total_cost=total_price,
            status='Active',
            guest_email=guest_email_val,
            registered_email=registered_email_val
        )

        success, msg = add_to_sql(new_order)  # זה יעדכן את new_order.order_code
        if not success:
            flash("Error processing order.")
            return redirect(url_for('payment_page'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            for seat_code in booking_data['selected_seats']:
                parts = seat_code.split('-')
                row_str = parts[0]
                col_str = parts[1]

                # המרה ל-INT חשובה כדי למנוע אי תאימות מול ה-DB
                row_num = int(row_str)

                # שליפת פרטי המושב
                query_seat = """SELECT class_type, price_supplement FROM Seats 
                                        WHERE plane_id = %s AND row_num = %s AND col_num = %s"""
                cursor.execute(query_seat, (flight['plane_id'], row_num, col_str))
                seat_info = cursor.fetchone()

                # בדיקה קריטית 1: האם המושב נמצא?
                if not seat_info:
                    print(f"CRITICAL ERROR: Seat {seat_code} not found for plane {flight['plane_id']}!")
                    continue  # מדלג למושב הבא כדי לא לקרוס

                final_ticket_price = flight['base_price'] + seat_info['price_supplement']

                new_ticket = Ticket(
                    ticket_number=None,
                    flight_id=flight_id,
                    plane_id=flight['plane_id'],
                    class_type=seat_info['class_type'],
                    row_num=row_num,
                    col_num=col_str,
                    order_code=new_order.order_code,
                    price=final_ticket_price,
                    guest_email=guest_email_val,
                    registered_email=registered_email_val
                )

                # בדיקה קריטית 2: האם הכרטיס נשמר?
                success_t, msg_t = add_to_sql(new_ticket)
                if not success_t:
                    print(f"SQL INSERT FAILED for seat {seat_code}: {msg_t}")
                    # כאן תראה במסך השחור למטה בדיוק למה זה נכשל (למשל Foreign Key)
                else:
                    print(f"Ticket for seat {seat_code} saved successfully.")

        except Exception as e:
            print(f"EXCEPTION in ticket creation loop: {e}")

        finally:
            cursor.close()
            conn.close()

        check_and_update_flight_status(flight_id)

        session.pop('temp_booking', None)
        return render_template('confirmation.html',
                               order_id=new_order.order_code,
                               flight=flight,
                               booking=booking_data,
                               price=total_price)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('is_manager'):
        return redirect(url_for('manager_dashboard'))

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
    if session.get('is_manager'):
        session.clear()
        return redirect(url_for('login'))

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

    flights_data = get_manager_flight_history()

    if request.method == 'GET':
        return render_template('manager_dashboard.html', flights=flights_data)

    return render_template('manager_dashboard.html', flights=flights_data)


@app.route('/manager-dashboard/add-employee', methods=['GET', 'POST'])
def add_employee():
    if not session.get('is_manager'):
        flash("Access Denied. Managers only.")
        return redirect(url_for('manager_login'))

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


@app.route('/manager-dashboard/add-plane', methods=['GET', 'POST'])
def add_plane():
    if not session.get('is_manager'):
        flash("Access Denied. Managers only.")
        return redirect(url_for('manager_login'))

    if request.method == 'GET':
        return render_template('add-plane.html')

    if request.method == 'POST':
        # 1. Create the Plane Object
        new_plane = Plane(
            manufacturer=request.form.get('manufacturer'),
            purchase_date=request.form.get('purchase_date'),
            size=request.form.get('size'),
            plane_id=None
        )

        success = add_to_sql(new_plane)

        if not success:
            flash(f"Error adding plane")
            return redirect(url_for('add_plane'))

        create_classes_and_seats(new_plane.plane_id, new_plane.size, request.form)

        flash(f"Success! Plane {new_plane.plane_id} by {new_plane.manufacturer} has been added to the company's fleet.")
        return redirect(url_for('add_plane'))

@app.route('/manager-dashboard/add-operating-line', methods=['GET', 'POST'])
def new_operating_line():
    if not session.get('is_manager'):
        flash("Access Denied. Managers only.")
        return redirect(url_for('manager_login'))

    if request.method == 'GET':
        return render_template('add-operating-line.html')

    if request.method == 'POST':
        new_line = OperatingLine(
            src_country=request.form.get('src_country'),
            src_city=request.form.get('src_city'),
            src_airport=request.form.get('src_airport'),
            dst_country=request.form.get('dst_country'),
            dst_city=request.form.get('dst_city'),
            dst_airport=request.form.get('dst_airport'),
            flight_duration= request.form.get('flight_duration')
        )

        success, message = add_to_sql(new_line)

        if not success:
            flash(f"Error creating new operating line: {message}")
            return redirect(url_for('new_operating_line'))

        else:
            flash(f"Success! A new line from {new_line.src_country}, {new_line.src_city} to {new_line.dst_country}, {new_line.dst_city} has been created!")
            return redirect(url_for('new_operating_line'))


@app.route('/api/schedule-data', methods=['POST'])
def api_schedule_data():
    try:
        request_data = request.json
        action = request_data.get('action')

        # 1. Fetch Operating Lines (Routes) for the Dropdowns
        if action == 'get_lines':
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM OperatingLines")
            lines = cursor.fetchall()

            # Convert 'flight_duration' (TimeDelta) to string so JSON can read it
            for line in lines:
                if 'flight_duration' in line and line['flight_duration'] is not None:
                    line['flight_duration'] = str(line['flight_duration'])

            cursor.close()
            conn.close()
            return jsonify(lines)

        # 2. Fetch Available Resources (Planes/Crew) based on History
        elif action == 'get_resources':
            src_country = request_data.get('src_country')
            dept_date = request_data.get('dept_date')
            dept_time = request_data.get('dept_time')

            if not dept_date or not dept_time:
                return jsonify({'error': 'Date and Time are required'}), 400

            full_date_str = f"{dept_date} {dept_time}:00"

            # Call the function from utils.py
            resources = get_available_resources_for_flight(src_country, full_date_str)

            return jsonify(resources)

    except Exception as e:
        print(f"API ERROR: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/manager-dashboard/schedule-flight', methods=['GET', 'POST'])
def schedule_flight():
    if not session.get('is_manager'):
        flash("Access Denied.")
        return redirect(url_for('manager_login'))

    if request.method == 'GET':
        return render_template('schedule-flight.html')

    if request.method == 'POST':
        # 1. Extract Basic Flight Details
        src_country = request.form.get('src_country')
        src_city = request.form.get('src_city')
        src_airport = request.form.get('src_airport')
        dst_country = request.form.get('dst_country')
        dst_city = request.form.get('dst_city')
        dst_airport = request.form.get('dst_airport')
        base_price = request.form.get('base_price')

        # 2. Date & Time
        dept_date = request.form.get('dept_date')
        dept_time = request.form.get('dept_time')
        landing_datetime = request.form.get('landing_datetime')  # Calculated by JS

        # Create the full datetime string for the DB
        departure_dt = f"{dept_date} {dept_time}"

        # 3. Resources (IDs)
        plane_id = request.form.get('selected_plane')
        pilot_ids = request.form.getlist('selected_pilots')
        attendant_ids = request.form.getlist('selected_attendants')

        # 4. Create Flight Object
        new_flight = Flight(
            plane_id=plane_id,
            src_country=src_country, src_city=src_city, src_airport=src_airport,
            dst_country=dst_country, dst_city=dst_city, dst_airport=dst_airport,
            departure_time=departure_dt,
            landing_time=landing_datetime,
            status='Active'
        )
        # Manually attach base_price (assuming your DB insert logic handles it)
        new_flight.base_price = base_price

        # 5. Insert Flight into DB
        success, msg = add_to_sql(new_flight)

        if success:
            # 6. Assign Crew to the new Flight ID
            assign_success = assign_crew_to_flight(new_flight.flight_id, pilot_ids, attendant_ids)

            if assign_success:
                flash("Success! Flight scheduled successfully.")
                return redirect(url_for('manager_dashboard'))
            else:
                flash("Flight created, but error assigning crew.")
                return redirect(url_for('manager_dashboard'))
        else:
            flash(f"Database Error: {msg}")
            return redirect(url_for('schedule_flight'))

@app.route('/manager-dashboard/report/load-factor')
def report_load_factor():
    if not session.get('is_manager'):
        flash("Access Denied. Managers only.")
        return redirect(url_for('manager_login'))

    data = get_load_factor_stats()
    return render_template('report_load_factor.html', report_data=data)

@app.route('/manager-dashboard/report/revenue')
def report_revenue():
    if not session.get('is_manager'):
        flash("Access Denied. Managers only.")
        return redirect(url_for('manager_login'))

    data = get_revenue_stats()

    labels = [row['month'] for row in data]
    values = [float(row['total_revenue']) for row in data]

    return render_template('report_revenue.html', labels=labels, values=values)

@app.route('/manager-dashboard/report/popular-routes')
def report_popular_routes():
    if not session.get('is_manager'):
        flash("Access Denied. Managers only.")
        return redirect(url_for('manager_login'))

    data = get_popular_routes_stats()
    labels = [row['dst_city'] for row in data]
    values = [row['ticket_count'] for row in data]

    return render_template('report_routes.html', labels=labels, values=values)


@app.route('/manager-dashboard/report/cancellations')
def report_cancellations():
    if not session.get('is_manager'):
        flash("Access Denied. Managers only.")
        return redirect(url_for('manager_login'))

    data = get_order_status_stats()

    # Prepare data for Chart.js
    labels = ['Active', 'Completed', 'Cancelled (Customer)', 'Cancelled (System)']
    values = [
        data['Active'],
        data['Completed'],
        data['CancelledByCustomer'],
        data['CancelledBySystem']
    ]

    return render_template('report_health.html', labels=labels, values=values)


# --- LOGOUT ROUTE (Crucial!) ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))




@app.errorhandler(404)
def error(e):
    return redirect(url_for('home'))


@app.route('/seat-selection', methods=['GET', 'POST'])
def seat_selection():
    if 'temp_booking' not in session:
        return redirect(url_for('home'))

    booking_data = session['temp_booking']
    flight_id = booking_data['flight_id']

    total_needed = int(booking_data['tickets_economy']) + int(booking_data['tickets_business'])

    if request.method == 'GET':
        flight = get_flight_details(flight_id)
        layout = get_plane_layout(flight['plane_id'])
        occupied_seats = get_occupied_seats(flight_id)

        col_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        return render_template('seat_selection.html',
                               flight=flight,
                               layout=layout,
                               occupied_seats=occupied_seats,
                               booking=booking_data,
                               col_letters=col_letters,
                               total_needed=total_needed)

    if request.method == 'POST':
        selected_seats = request.form.getlist('selected_seats')

        if len(selected_seats) != total_needed:
            flash(f"Almost there! You selected {len(selected_seats)} seats — please select exactly {total_needed} seats to continue.")
            return redirect(url_for('seat_selection'))

        session['temp_booking']['selected_seats'] = selected_seats
        session.modified = True

        flash("Great choice! Your seats have been selected. Let’s move on to payment.")
        return redirect(url_for('payment_page'))


@app.route('/payment', methods=['GET', 'POST'])
def payment_page():
    if 'temp_booking' not in session:
        return redirect(url_for('home'))

    booking_data = session['temp_booking']
    flight_id = booking_data['flight_id']
    flight = get_flight_details(flight_id)

    total_price = (int(booking_data['tickets_economy']) * flight['price_economy']) + \
                  (int(booking_data['tickets_business']) * flight['price_business'])

    if request.method == 'GET':
        return render_template('payment.html', price=total_price, booking=booking_data, flight=flight)

    if request.method == 'POST':
        email = booking_data['email']

        is_registered = is_email_registered(email)

        guest_email_val = None
        registered_email_val = None

        if is_registered:
            registered_email_val = email
        else:
            guest_email_val = email
            ensure_guest_exists(
                email,
                booking_data['first_name'],
                booking_data['last_name'],
                booking_data['phones']
            )

        new_order = Order(
            order_code=None,
            total_cost=total_price,
            status='Active',
            guest_email=guest_email_val,
            registered_email=registered_email_val
        )

        success, msg = add_to_sql(new_order)  # זה יעדכן את new_order.order_code
        if not success:
            flash("Error processing order.")
            return redirect(url_for('payment_page'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            for seat_code in booking_data['selected_seats']:
                parts = seat_code.split('-')
                row_str = parts[0]
                col_str = parts[1]

                # המרה ל-INT חשובה כדי למנוע אי תאימות מול ה-DB
                row_num = int(row_str)

                # שליפת פרטי המושב
                query_seat = """SELECT class_type, price_supplement FROM Seats 
                                        WHERE plane_id = %s AND row_num = %s AND col_num = %s"""
                cursor.execute(query_seat, (flight['plane_id'], row_num, col_str))
                seat_info = cursor.fetchone()

                # בדיקה קריטית 1: האם המושב נמצא?
                if not seat_info:
                    print(f"CRITICAL ERROR: Seat {seat_code} not found for plane {flight['plane_id']}!")
                    continue  # מדלג למושב הבא כדי לא לקרוס

                final_ticket_price = flight['base_price'] + seat_info['price_supplement']

                new_ticket = Ticket(
                    ticket_number=None,
                    flight_id=flight_id,
                    plane_id=flight['plane_id'],
                    class_type=seat_info['class_type'],
                    row_num=row_num,
                    col_num=col_str,
                    order_code=new_order.order_code,
                    price=final_ticket_price,
                    guest_email=guest_email_val,
                    registered_email=registered_email_val
                )

                # בדיקה קריטית 2: האם הכרטיס נשמר?
                success_t, msg_t = add_to_sql(new_ticket)
                if not success_t:
                    print(f"SQL INSERT FAILED for seat {seat_code}: {msg_t}")
                    # כאן תראה במסך השחור למטה בדיוק למה זה נכשל (למשל Foreign Key)
                else:
                    print(f"Ticket for seat {seat_code} saved successfully.")

        except Exception as e:
            print(f"EXCEPTION in ticket creation loop: {e}")

        finally:
            cursor.close()
            conn.close()

        check_and_update_flight_status(flight_id)

        session.pop('temp_booking', None)
        return render_template('confirmation.html',
                               order_id=new_order.order_code,
                               flight=flight,
                               booking=booking_data,
                               price=total_price)
if __name__ == '__main__':
    app.run(debug=True)


