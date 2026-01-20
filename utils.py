import mysql.connector
from classes import *
from datetime import datetime, timedelta

# DB Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # Your password
    'database': 'airlinedb'
}


def add_to_sql(obj):
    """
    Receives an object.
    If it is a RegisteredCustomer, it performs all specific validations (Email check, Manager Phone check, Guest cleanup).
    For other objects, it performs a standard INSERT.

    Returns: (Boolean, String) -> (Success?, Message)
    """

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # ==============================================================================
        # SPECIAL LOGIC FOR REGISTERED CUSTOMER (Validations + Transaction)
        # ==============================================================================
        if isinstance(obj, RegisteredCustomer):

            # 1. Check if user is already signed up (Email check)
            cursor.execute("SELECT email FROM RegisteredCustomers WHERE email = %s", (obj.email,))
            if cursor.fetchone():
                return False, "Error: This email is already registered."

            # 2. Check if any phone belongs to a Manager
            # We assume obj.phones is a list of strings inside the object
            for phone in obj.phones:
                if phone.strip():  # Skip empty strings
                    cursor.execute("SELECT id_num FROM Managers WHERE phone = %s", (phone,))
                    if cursor.fetchone():
                        return False, f"Error: The phone number {phone} belongs to a Manager. Cannot register."

            # 3. If email exists in GuestCustomers, delete it
            cursor.execute("DELETE FROM GuestCustomers WHERE email = %s", (obj.email,))

            # 4. Add to RegisteredCustomers DB
            sql_user = """INSERT INTO RegisteredCustomers 
                          (email, first_name_en, last_name_en, registration_date, passport_num, password, birth_date)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            val_user = (obj.email, obj.first_name_en, obj.last_name_en, obj.registration_date,
                        obj.passport_num, obj.password, obj.birth_date)
            cursor.execute(sql_user, val_user)

            # 5. Add to RegisteredPhones DB
            sql_phone = "INSERT INTO RegisteredPhones (email, phone_number) VALUES (%s, %s)"
            for phone in obj.phones:
                if phone.strip():
                    cursor.execute(sql_phone, (obj.email, phone))

            # Commit the whole transaction
            conn.commit()
            print(f"Successfully registered user {obj.email}")
            return True, ""

        # ==============================================================================
        # LOGIC FOR OTHER CLASSES (Standard Insert)
        # ==============================================================================
        else:
            sql = None
            values = None

            if isinstance(obj, Manager):
                sql = """INSERT INTO Managers (id_num, first_name, last_name, phone, city, street, house_number, start_date, password)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (obj.id_num, obj.first_name, obj.last_name, obj.phone, obj.city, obj.street, obj.house_number,
                          obj.start_date, obj.password)

            elif isinstance(obj, Pilot):
                sql = """INSERT INTO Pilots (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (obj.id_num, obj.first_name, obj.last_name, obj.phone, obj.city, obj.street, obj.house_number,
                          obj.start_date, obj.long_flight_training)

            elif isinstance(obj, Attendant):
                sql = """INSERT INTO Attendants (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (obj.id_num, obj.first_name, obj.last_name, obj.phone, obj.city, obj.street, obj.house_number,
                          obj.start_date, obj.long_flight_training)

            elif isinstance(obj, GuestCustomer):
                sql = """INSERT INTO GuestCustomers (email, first_name_en, last_name_en) VALUES (%s, %s, %s)"""
                values = (obj.email, obj.first_name_en, obj.last_name_en)


            elif isinstance(obj, Plane):

                sql = """INSERT INTO Planes (manufacturer, purchase_date, size) VALUES (%s, %s, %s)"""

                values = (obj.manufacturer, obj.purchase_date, obj.size)

                cursor.execute(sql, values)

                new_id = cursor.lastrowid

                obj.plane_id = new_id

            elif isinstance(obj, FlightClass):
                sql = """INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats) VALUES (%s, %s, %s, %s, %s)"""
                values = (obj.plane_id, obj.class_type, obj.num_columns, obj.num_rows, obj.total_seats)

            elif isinstance(obj, Seat):
                sql = """INSERT INTO Seats (plane_id, class_type, row_num, col_num) VALUES (%s, %s, %s, %s)"""
                values = (obj.plane_id, obj.class_type, obj.row_num, obj.col_num)

            elif isinstance(obj, OperatingLine):
                sql = """INSERT INTO OperatingLines (src_country, src_city, src_airport, dst_country, dst_city, dst_airport, flight_duration)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                values = (
                obj.src_country, obj.src_city, obj.src_airport, obj.dst_country, obj.dst_city, obj.dst_airport,
                obj.flight_duration)

            elif isinstance(obj, Flight):
                sql = """INSERT INTO Flights (flight_id, plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, status)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (obj.flight_id, obj.plane_id, obj.src_country, obj.src_city, obj.src_airport, obj.dst_country,
                          obj.dst_city, obj.dst_airport, obj.departure_time, obj.landing_time, obj.status)

                cursor.execute(sql, values)

                obj.flight_id = cursor.lastrowid

            elif isinstance(obj, Order):
                sql = """INSERT INTO Orders (total_cost, status, guest_email, registered_email)
                                     VALUES (%s, %s, %s, %s)"""
                values = (obj.total_cost, obj.status, obj.guest_email, obj.registered_email)

            elif isinstance(obj, Ticket):
                sql = """INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, guest_email, registered_email, price)
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (obj.flight_id, obj.plane_id, obj.class_type, obj.row_num, obj.col_num,
                          obj.order_code, obj.guest_email, obj.registered_email, obj.price)

            else:
                print(f"Error: Unknown object type {type(obj)}")
                return False, f"Unknown object type {type(obj)}"

            # Execute the standard SQL prepared above
            cursor.execute(sql, values)
            if isinstance(obj, Order):
                obj.order_code = cursor.lastrowid

            if isinstance(obj,Plane):
                obj.plane_id = cursor.lastrowid
            conn.commit()
            print(f"Successfully added {type(obj).__name__} to DB!")
            return True, f"Successfully added {type(obj).__name__} to DB!"

    except mysql.connector.Error as err:
        # If anything fails (in RegisteredCustomer or others), we rollback
        if conn: conn.rollback()
        print(f"Error inserting to SQL: {err}")
        return False, f"Database Error: {err}"

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def check_login(email, password):
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # The Query: Find a user where BOTH email AND password match
        query = "SELECT first_name_en FROM RegisteredCustomers WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))

        result = cursor.fetchone()  # Get the first result (if any)

        if result:
            return result[0]
        else:
            return None  # No match found

    except mysql.connector.Error as err:
        print(f"Login Error: {err}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def is_signup_valid(customer):
    """
    Checks requirements for a user sign-up.
    """

    # 1. First/Last Name: English letters only
    if not (customer.first_name_en.isalpha() and customer.first_name_en.isascii()):
        return False, "First name must contain only English letters."

    if not (customer.last_name_en.isalpha() and customer.last_name_en.isascii()):
        return False, "Last name must contain only English letters."

    # 2. Passport: At least 6 characters (Length check)
    if len(customer.passport_num) < 6:
        return False, "Passport number must be at least 6 characters."

    # 3. Password: At least 6 chars, English or numbers only
    if len(customer.password) < 6:
        return False, "Password must be at least 6 characters."

    # .isalnum() checks for letters OR numbers
    if not (customer.password.isalnum() and customer.password.isascii()):
        return False, "Password must contain only English letters or numbers."

    # 4. Phones: 10 digits exactly
    if not customer.phones:
        return False, "At least one phone number is required."

    for phone in customer.phones:
        # .isdigit() ensures 0-9 only
        if not (phone.isdigit() and len(phone) == 10):
            return False, f"Phone number '{phone}' is invalid. It must be exactly 10 digits."

    return True, ""

def get_flights(criteria=None):
    if criteria is None:
        criteria = {}

    conn = None
    cursor = None
    flights_data = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT flight_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, 
                   departure_time, landing_time, status 
            FROM Flights 
            WHERE status = 'Active'
        """
        params = []

        if criteria.get('source_country'):
            query += " AND src_country = %s"
            params.append(criteria['source_country'])

        if criteria.get('source_city'):
            query += " AND src_city = %s"
            params.append(criteria['source_city'])

        if criteria.get('source_airport'):
            query += " AND src_airport = %s"
            params.append(criteria['source_airport'])

        if criteria.get('dest_country'):
            query += " AND dst_country = %s"
            params.append(criteria['dest_country'])

        if criteria.get('dest_city'):
            query += " AND dst_city = %s"
            params.append(criteria['dest_city'])

        if criteria.get('dest_airport'):
            query += " AND dst_airport = %s"
            params.append(criteria['dest_airport'])

        if criteria.get('date'):
            query += " AND DATE(departure_time) = %s"
            params.append(criteria['date'])

        if criteria.get('flight_id'):
            query += " AND flight_id = %s"
            params.append(criteria['flight_id'])

        query += " ORDER BY departure_time ASC"

        cursor.execute(query, tuple(params))
        flights_data = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error fetching flights: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return flights_data



def get_unique_locations(column, filter_col=None, filter_val=None, location_type='source'):
    """
    שולפת ערכים ייחודיים (מדינות/ערים/שדות) מטבלת קווי התפעול.
    column: העמודה המבוקשת (למשל 'city')
    filter_col: העמודה שלפיה מסננים (למשל 'country')
    filter_val: הערך לסינון (למשל 'Israel')
    location_type: 'source' (מוצא) או 'dest' (יעד)
    """
    conn = None
    cursor = None
    results = []

    prefix = "src" if location_type == 'source' else "dst"
    target_col = f"{prefix}_{column}"

    query = f"SELECT DISTINCT {target_col} FROM OperatingLines"
    params = []

    if filter_col and filter_val:
        filter_column_name = f"{prefix}_{filter_col}"
        query += f" WHERE {filter_column_name} = %s"
        params.append(filter_val)

    query += f" ORDER BY {target_col}"

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))

        results = [row[0] for row in cursor.fetchall()]

    except mysql.connector.Error as err:
        print(f"Error fetching locations: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return results

def check_manager_login(id_num, password):
    """
    Checks if a manager exists with the given ID and Password.
    Returns the Manager's first name if valid, None otherwise.
    """
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT first_name FROM Managers WHERE id_num = %s AND password = %s"
        cursor.execute(query, (id_num, password))

        result = cursor.fetchone()

        if result:
            return result[0]  # Return the first name
        else:
            return None

    except mysql.connector.Error as err:
        print(f"Manager Login Error: {err}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_flight_details(flight_id):
    conn = None
    cursor = None
    flight = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Join Flights with Planes to know the plane size (Big/Small)
        query = """
            SELECT F.*, P.size, P.manufacturer 
            FROM Flights F
            JOIN Planes P ON F.plane_id = P.plane_id
            WHERE F.flight_id = %s
        """
        cursor.execute(query, (flight_id,))
        flight = cursor.fetchone()

        # Mocking prices for now (as requested)
        if flight:

            flight['price_economy'] = flight['base_price']
            flight['price_business'] = 0  # ברירת מחדל

            if flight['size'] == 'Big':
                query_supp = """
                            SELECT price_supplement 
                            FROM Seats 
                            WHERE plane_id = %s AND class_type = 'Business' 
                            LIMIT 1
                        """
                cursor.execute(query_supp, (flight['plane_id'],))
                result = cursor.fetchone()

                if result:
                    # המרה ל-float/decimal כדי לחבר מחירים
                    supplement = result['price_supplement']
                    flight['price_business'] = flight['base_price'] + supplement

    except mysql.connector.Error as err:
        print(f"Error fetching flight details: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return flight


def get_user_details(email):
    conn = None
    cursor = None
    user_data = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get basic info
        query_user = """
            SELECT email, first_name_en, last_name_en 
            FROM RegisteredCustomers 
            WHERE email = %s
        """
        cursor.execute(query_user, (email,))
        user_data = cursor.fetchone()

        if user_data:
            # Get phones
            query_phones = "SELECT phone_number FROM RegisteredPhones WHERE email = %s"
            cursor.execute(query_phones, (email,))
            phones_result = cursor.fetchall()  # Returns list of dicts [{'phone_number': '...'}, ...]

            # Convert to simple list
            user_data['phones'] = [p['phone_number'] for p in phones_result]

    except mysql.connector.Error as err:
        print(f"Error fetching user details: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return user_data


def is_manager_phone(phone_number):
    """
    Checks if a given phone number belongs to a Manager in the database.
    Ignores hyphens in both the input and the database record.
    Returns True if it exists, False otherwise.
    """
    conn = None
    cursor = None
    exists = False

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        clean_input = phone_number.replace('-', '').strip()

        query = "SELECT id_num FROM Managers WHERE REPLACE(phone, '-', '') = %s"
        cursor.execute(query, (clean_input,))

        if cursor.fetchone():
            exists = True

    except mysql.connector.Error as err:
        print(f"Error checking manager phone: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return exists


def get_manager_flight_history():
    """
    Fetches all flights with status, seat occupancy, and total capacity.
    """
    conn = None
    cursor = None
    results = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                f.flight_id, 
                f.src_city, f.src_airport, 
                f.dst_city, f.dst_airport, 
                f.departure_time, 
                f.status,

                -- Calculate Total Seats (Capacity)
                (SELECT IFNULL(SUM(total_seats), 0) FROM Classes c WHERE c.plane_id = f.plane_id) as total_seats,

                -- Calculate Occupied Seats (Tickets Sold)
                (SELECT COUNT(*) FROM Tickets t WHERE t.flight_id = f.flight_id) as occupied_seats

            FROM Flights f
            ORDER BY f.departure_time DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error fetching manager flights: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return results

def create_classes_and_seats(plane_id, plane_size, form_data):
    """
    Generates FlightClass and Seat objects for a given plane and inserts them into SQL.

    Args:
        plane_id: The ID of the newly created plane.
        plane_size: 'Big' or 'Small'.
        form_data: The request.form dictionary containing row/col counts.
    """

    # 1. Define what classes to build based on size
    classes_to_create = []

    # Economy (Always exists)
    try:
        eco_rows = int(form_data.get('eco_rows'))
        eco_cols = int(form_data.get('eco_cols'))
        classes_to_create.append(('Economy', eco_rows, eco_cols))
    except (ValueError, TypeError):
        print("Error reading Economy configuration.")
        return False

    # Business (Only if Big)
    if plane_size == 'Big':
        try:
            bus_rows = int(form_data.get('bus_rows', 0))
            bus_cols = int(form_data.get('bus_cols', 0))
            if bus_rows > 0 and bus_cols > 0:
                classes_to_create.append(('Business', bus_rows, bus_cols))
        except (ValueError, TypeError):
            # Not critical if empty, just skip business
            pass

    # 2. Loop through config, create objects, and save to SQL
    col_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for class_name, rows, cols in classes_to_create:
        # A. Create & Save FlightClass
        flight_class = FlightClass(
            plane_id=plane_id,
            class_type=class_name,
            num_rows=rows,
            num_columns=cols
        )
        add_to_sql(flight_class)

        # B. Generate & Save Seats
        for r in range(1, rows + 1):
            for c in range(cols):
                # Safety check for column limits (A-Z)
                if c >= len(col_letters):
                    break

                col_char = col_letters[c]

                new_seat = Seat(
                    plane_id=plane_id,
                    class_type=class_name,
                    row_num=r,
                    col_num=col_char
                )
                add_to_sql(new_seat)

    return True


def get_plane_layout(plane_id):

    conn = None
    cursor = None
    layout = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT class_type, num_rows, num_columns 
            FROM Classes 
            WHERE plane_id = %s 
            ORDER BY class_type ASC
        """
        cursor.execute(query, (plane_id,))
        layout = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error fetching layout: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return layout


def get_occupied_seats(flight_id):

    conn = None
    cursor = None
    occupied = set()
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT row_num, col_num FROM Tickets WHERE flight_id = %s"
        cursor.execute(query, (flight_id,))

        for (r, c) in cursor.fetchall():
            occupied.add(f"{r}-{c}")  # format: "5-A"

    except mysql.connector.Error as err:
        print(f"Error fetching occupied seats: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return occupied



def is_email_registered(email):
    conn = None
    cursor = None
    exists = False
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM RegisteredCustomers WHERE email = %s", (email,))
        if cursor.fetchone():
            exists = True
    except mysql.connector.Error as err:
        print(f"Error checking email: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return exists


def ensure_guest_exists(email, first_name, last_name, phones):

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1. בדיקה אם קיים
        cursor.execute("SELECT email FROM GuestCustomers WHERE email = %s", (email,))
        if not cursor.fetchone():
            # הוספה לטבלת אורחים
            cursor.execute(
                "INSERT INTO GuestCustomers (email, first_name_en, last_name_en) VALUES (%s, %s, %s)",
                (email, first_name, last_name)
            )

        for phone in phones:
            if phone.strip():
                cursor.execute("SELECT * FROM GuestPhones WHERE email=%s AND phone_number=%s", (email, phone))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO GuestPhones (email, phone_number) VALUES (%s, %s)", (email, phone))

        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error ensuring guest: {err}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def check_and_update_flight_status(flight_id):

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1. כמה מושבים יש סך הכל במטוס של הטיסה הזו?
        # אנו צריכים את ה-plane_id מתוך הטיסה, ואז לסכום את ה-total_seats מ-Classes
        query_total = """
            SELECT SUM(C.total_seats) 
            FROM Classes C
            JOIN Flights F ON F.plane_id = C.plane_id
            WHERE F.flight_id = %s
        """
        cursor.execute(query_total, (flight_id,))
        result = cursor.fetchone()
        total_capacity = result[0] if result and result[0] else 0

        cursor.execute("SELECT COUNT(*) FROM Tickets WHERE flight_id = %s", (flight_id,))
        sold_count = cursor.fetchone()[0]

        if sold_count >= total_capacity:
            cursor.execute("UPDATE Flights SET status = 'Full' WHERE flight_id = %s", (flight_id,))
            conn.commit()
            print(f"Flight {flight_id} is now FULL.")

    except mysql.connector.Error as err:
        print(f"Error updating flight status: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return {
        'is_long_flight': is_long_flight,
        'planes': valid_planes,
        'pilots': valid_pilots,
        'attendants': valid_attendants
    }


def get_customer_orders_history(email):
    """
    Fetches all orders for a specific registered customer.
    Calculates the 'Actual Paid' amount based on status.
    Determines if cancellation is allowed (Time > 36 hours).
    """
    conn = None
    cursor = None
    orders = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # We join Orders -> Tickets -> Flights to get location and time data
        # We Group By Order Code to count tickets per order
        query = """
            SELECT 
                O.order_code, 
                O.total_cost, 
                O.status as order_status,
                F.src_city,
                F.dst_city,
                F.departure_time,
                F.flight_id,
                COUNT(T.ticket_number) as ticket_count
            FROM Orders O
            JOIN Tickets T ON O.order_code = T.order_code
            JOIN Flights F ON T.flight_id = F.flight_id
            WHERE O.registered_email = %s
            GROUP BY O.order_code, O.total_cost, O.status, F.src_city, F.dst_city, F.departure_time, F.flight_id
            ORDER BY F.departure_time DESC
        """

        cursor.execute(query, (email,))
        results = cursor.fetchall()

        now = datetime.now()

        for row in results:
            # 1. Calculate "Actual Paid" logic
            status = row['order_status']
            cost = float(row['total_cost'])

            if status == 'CancelledBySystem':
                row['actual_paid'] = 0
            elif status == 'CancelledByCustomer':
                row['actual_paid'] = cost * 0.05  # Customer pays 5% penalty
            else:
                row['actual_paid'] = cost

            # 2. Check 36 Hours Rule for Cancellation Button
            # Calculate time difference
            flight_time = row['departure_time']
            time_diff = flight_time - now

            # Button is active ONLY if:
            # 1. Status is Active
            # 2. Time to flight is more than 36 hours
            if status == 'Active' and time_diff > timedelta(hours=36):
                row['can_cancel'] = True
            else:
                row['can_cancel'] = False

            orders.append(row)

    except mysql.connector.Error as err:
        print(f"Error fetching history: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return orders


def cancel_order_by_user(order_code):
    """
    Updates order status to 'CancelledByCustomer'.
    Does NOT delete the row, just updates status.
    """
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = "UPDATE Orders SET status = 'CancelledByCustomer' WHERE order_code = %s"
        cursor.execute(sql, (order_code,))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error canceling order: {err}")
        return False
    finally:
        if conn: conn.close()

def get_plane_layout(plane_id):

    conn = None
    cursor = None
    layout = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT class_type, num_rows, num_columns 
            FROM Classes 
            WHERE plane_id = %s 
            ORDER BY class_type ASC
        """
        cursor.execute(query, (plane_id,))
        layout = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error fetching layout: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return layout


def get_occupied_seats(flight_id):

    conn = None
    cursor = None
    occupied = set()
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT row_num, col_num FROM Tickets WHERE flight_id = %s"
        cursor.execute(query, (flight_id,))

        for (r, c) in cursor.fetchall():
            occupied.add(f"{r}-{c}")  # format: "5-A"

    except mysql.connector.Error as err:
        print(f"Error fetching occupied seats: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return occupied



def is_email_registered(email):
    conn = None
    cursor = None
    exists = False
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM RegisteredCustomers WHERE email = %s", (email,))
        if cursor.fetchone():
            exists = True
    except mysql.connector.Error as err:
        print(f"Error checking email: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return exists


def ensure_guest_exists(email, first_name, last_name, phones):

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1. בדיקה אם קיים
        cursor.execute("SELECT email FROM GuestCustomers WHERE email = %s", (email,))
        if not cursor.fetchone():
            # הוספה לטבלת אורחים
            cursor.execute(
                "INSERT INTO GuestCustomers (email, first_name_en, last_name_en) VALUES (%s, %s, %s)",
                (email, first_name, last_name)
            )

        for phone in phones:
            if phone.strip():
                cursor.execute("SELECT * FROM GuestPhones WHERE email=%s AND phone_number=%s", (email, phone))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO GuestPhones (email, phone_number) VALUES (%s, %s)", (email, phone))

        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error ensuring guest: {err}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def check_and_update_flight_status(flight_id):

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1. כמה מושבים יש סך הכל במטוס של הטיסה הזו?
        # אנו צריכים את ה-plane_id מתוך הטיסה, ואז לסכום את ה-total_seats מ-Classes
        query_total = """
            SELECT SUM(C.total_seats) 
            FROM Classes C
            JOIN Flights F ON F.plane_id = C.plane_id
            WHERE F.flight_id = %s
        """
        cursor.execute(query_total, (flight_id,))
        result = cursor.fetchone()
        total_capacity = result[0] if result and result[0] else 0

        cursor.execute("SELECT COUNT(*) FROM Tickets WHERE flight_id = %s", (flight_id,))
        sold_count = cursor.fetchone()[0]

        if sold_count >= total_capacity:
            cursor.execute("UPDATE Flights SET status = 'Full' WHERE flight_id = %s", (flight_id,))
            conn.commit()
            print(f"Flight {flight_id} is now FULL.")

    except mysql.connector.Error as err:
        print(f"Error updating flight status: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

