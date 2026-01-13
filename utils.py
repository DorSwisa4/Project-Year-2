import mysql.connector
from classes import *

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
                sql = """INSERT INTO Planes (plane_id, manufacturer, purchase_date, size) VALUES (%s, %s, %s, %s)"""
                values = (obj.plane_id, obj.manufacturer, obj.purchase_date, obj.size)

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

        # שאילתה בסיסית - מביאה הכל
        query = """
            SELECT flight_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, 
                   departure_time, landing_time, status 
            FROM Flights 
            WHERE status = 'Active'
        """
        params = []

        # --- הוספת כל אפשרויות הסינון ---

        # 1. מדינת מוצא
        if criteria.get('source_country'):
            query += " AND src_country = %s"
            params.append(criteria['source_country'])

        # 2. עיר מוצא (חדש!)
        if criteria.get('source_city'):
            query += " AND src_city = %s"
            params.append(criteria['source_city'])

        # 3. שדה תעופה מוצא (חדש!)
        if criteria.get('source_airport'):
            query += " AND src_airport = %s"
            params.append(criteria['source_airport'])

        # 4. מדינת יעד
        if criteria.get('dest_country'):
            query += " AND dst_country = %s"
            params.append(criteria['dest_country'])

        # 5. עיר יעד (חדש!)
        if criteria.get('dest_city'):
            query += " AND dst_city = %s"
            params.append(criteria['dest_city'])

        # 6. שדה תעופה יעד (חדש!)
        if criteria.get('dest_airport'):
            query += " AND dst_airport = %s"
            params.append(criteria['dest_airport'])

        # 7. תאריך
        if criteria.get('date'):
            query += " AND DATE(departure_time) = %s"
            params.append(criteria['date'])

        query += " ORDER BY departure_time ASC"

        cursor.execute(query, tuple(params))
        flights_data = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error fetching flights: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return flights_data


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
