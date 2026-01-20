import mysql.connector
from classes import *
from datetime import date

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
                sql = """INSERT INTO Orders (order_code, total_cost, status, guest_email, registered_email)
                         VALUES (%s, %s, %s, %s, %s)"""
                values = (obj.order_code, obj.total_cost, obj.status, obj.guest_email, obj.registered_email)

            elif isinstance(obj, Ticket):
                sql = """INSERT INTO Tickets (ticket_number, flight_id, plane_id, class_type, row_num, col_num, order_code, guest_email, registered_email, price)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (obj.ticket_number, obj.flight_id, obj.plane_id, obj.class_type, obj.row_num, obj.col_num,
                          obj.order_code, obj.guest_email, obj.registered_email, obj.price)

            else:
                print(f"Error: Unknown object type {type(obj)}")
                return False, f"Unknown object type {type(obj)}"

            # Execute the standard SQL prepared above
            cursor.execute(sql, values)
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
            flight['price_economy'] = 150  # Base price example
            flight['price_business'] = 400 if flight['size'] == 'Big' else 0

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


# --- REPORT 1: LOAD FACTOR ---
def get_load_factor_stats():
    """
    Returns a list of flights with their capacity, tickets sold, and occupancy %.
    """
    conn = None
    cursor = None
    results = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # This query calculates capacity (from Classes) and sold tickets (from Tickets)
        query = """
            SELECT 
                f.flight_id, 
                f.src_city, 
                f.dst_city, 
                DATE_FORMAT(f.departure_time, '%Y-%m-%d %H:%i') as dept_time,
                p.manufacturer,

                -- Subquery for Total Capacity
                (SELECT IFNULL(SUM(total_seats), 0) FROM Classes c WHERE c.plane_id = f.plane_id) as capacity,

                -- Subquery for Tickets Sold
                (SELECT COUNT(*) FROM Tickets t WHERE t.flight_id = f.flight_id) as tickets_sold

            FROM Flights f
            JOIN Planes p ON f.plane_id = p.plane_id
            WHERE f.status != 'Cancelled'
            ORDER BY f.departure_time DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # Calculate Percentage in Python to be safe
        for row in data:
            cap = row['capacity']
            sold = row['tickets_sold']
            percentage = round((sold / cap * 100), 1) if cap > 0 else 0

            row['occupancy'] = percentage
            results.append(row)

    except mysql.connector.Error as err:
        print(f"Report Error: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return results


# --- REPORT 2: REVENUE ---
def get_revenue_stats():
    """ Returns total revenue grouped by Month. """
    conn = None
    cursor = None
    results = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Group by Year-Month
        query = """
            SELECT 
                DATE_FORMAT(f.departure_time, '%Y-%m') as month,
                SUM(t.price) as total_revenue
            FROM Tickets t
            JOIN Flights f ON t.flight_id = f.flight_id
            GROUP BY month
            ORDER BY month ASC
        """
        cursor.execute(query)
        results = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Report Error: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return results


# --- REPORT 3: POPULAR ROUTES ---
def get_popular_routes_stats():
    """ Returns top destinations by ticket sales. """
    conn = None
    cursor = None
    results = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                f.dst_city, 
                COUNT(t.ticket_number) as ticket_count
            FROM Tickets t
            JOIN Flights f ON t.flight_id = f.flight_id
            GROUP BY f.dst_city
            ORDER BY ticket_count DESC
            LIMIT 5
        """
        cursor.execute(query)
        results = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Report Error: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return results


# --- REPORT 4: OPERATIONAL HEALTH (orders) ---
def get_order_status_stats():
    """ Returns count of Orders grouped by their status. """
    conn = None
    cursor = None
    results = {
        'Active': 0,
        'Completed': 0,
        'CancelledByCustomer': 0,
        'CancelledBySystem': 0
    }
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT status, COUNT(*) as count FROM Orders GROUP BY status"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            if row['status'] in results:
                results[row['status']] = row['count']

    except mysql.connector.Error as err:
        print(f"Report Error: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return results

def assign_crew_to_flight(flight_id, pilot_ids, attendant_ids):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert Pilots
        sql_pilot = "INSERT INTO PilotsOnFlights (pilot_id, flight_id) VALUES (%s, %s)"
        for p_id in pilot_ids:
            cursor.execute(sql_pilot, (p_id, flight_id))

        # Insert Attendants
        sql_att = "INSERT INTO AttendantsOnFlights (attendant_id, flight_id) VALUES (%s, %s)"
        for a_id in attendant_ids:
            cursor.execute(sql_att, (a_id, flight_id))

        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error assigning crew: {err}")
        return False
    finally:
        if conn: conn.close()


def get_available_resources_for_flight(src_country, query_date_str):
    """
    Finds resources available in src_country at the specific query_date.

    Logic:
    1. Subqueries find the 'last_dst' (destination of last flight) and 'last_landing' time.
    2. HAVING clause checks:
       - (last_dst IS NULL): resource has NEVER flown -> Available anywhere (Global).
       - OR (last_dst = src_country AND last_landing <= query_date): resource is currently here.
    """
    is_long_flight = False
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # --- 1. PLANES ---
        sql_planes = """
            SELECT 
                P.plane_id, P.manufacturer, P.size,
                (
                    SELECT dst_country 
                    FROM Flights F 
                    WHERE F.plane_id = P.plane_id 
                      AND F.departure_time < %s 
                    ORDER BY F.departure_time DESC LIMIT 1
                ) as last_dst,
                (
                    SELECT landing_time 
                    FROM Flights F 
                    WHERE F.plane_id = P.plane_id 
                      AND F.departure_time < %s 
                    ORDER BY F.departure_time DESC LIMIT 1
                ) as last_landing
            FROM Planes P
            HAVING (last_dst IS NULL) 
                OR (last_dst = %s AND last_landing <= %s)
        """
        cursor.execute(sql_planes, (query_date_str, query_date_str, src_country, query_date_str))
        valid_planes = [(p['plane_id'], p['manufacturer'], p['size']) for p in cursor.fetchall()]

        # --- 2. PILOTS ---
        sql_pilots = """
            SELECT 
                P.id_num, P.first_name, P.last_name, P.long_flight_training,
                (
                    SELECT F.dst_country 
                    FROM Flights F 
                    JOIN PilotsOnFlights POF ON F.flight_id = POF.flight_id
                    WHERE POF.pilot_id = P.id_num 
                      AND F.departure_time < %s 
                    ORDER BY F.departure_time DESC LIMIT 1
                ) as last_dst,
                (
                    SELECT F.landing_time 
                    FROM Flights F 
                    JOIN PilotsOnFlights POF ON F.flight_id = POF.flight_id
                    WHERE POF.pilot_id = P.id_num 
                      AND F.departure_time < %s 
                    ORDER BY F.departure_time DESC LIMIT 1
                ) as last_landing
            FROM Pilots P
            HAVING (last_dst IS NULL) 
                OR (last_dst = %s AND last_landing <= %s)
        """
        cursor.execute(sql_pilots, (query_date_str, query_date_str, src_country, query_date_str))
        valid_pilots = [(p['id_num'], p['first_name'], p['last_name'], p['long_flight_training']) for p in
                        cursor.fetchall()]

        # --- 3. ATTENDANTS ---
        sql_attendants = """
            SELECT 
                A.id_num, A.first_name, A.last_name, A.long_flight_training,
                (
                    SELECT F.dst_country 
                    FROM Flights F 
                    JOIN AttendantsOnFlights AOF ON F.flight_id = AOF.flight_id
                    WHERE AOF.attendant_id = A.id_num 
                      AND F.departure_time < %s 
                    ORDER BY F.departure_time DESC LIMIT 1
                ) as last_dst,
                (
                    SELECT F.landing_time 
                    FROM Flights F 
                    JOIN AttendantsOnFlights AOF ON F.flight_id = AOF.flight_id
                    WHERE AOF.attendant_id = A.id_num 
                      AND F.departure_time < %s 
                    ORDER BY F.departure_time DESC LIMIT 1
                ) as last_landing
            FROM Attendants A
            HAVING (last_dst IS NULL) 
                OR (last_dst = %s AND last_landing <= %s)
        """
        cursor.execute(sql_attendants, (query_date_str, query_date_str, src_country, query_date_str))
        valid_attendants = [(a['id_num'], a['first_name'], a['last_name'], a['long_flight_training']) for a in
                            cursor.fetchall()]

    except mysql.connector.Error as err:
        print(f"Error fetching resources: {err}")
        return {'error': str(err)}
    finally:
        if conn: conn.close()

    return {
        'is_long_flight': is_long_flight,
        'planes': valid_planes,
        'pilots': valid_pilots,
        'attendants': valid_attendants
    }