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
            return True, "Registration successful!"

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
            # result is a tuple like ('John',)
            return result[0]  # Return the name 'John'
        else:
            return None  # No match found

    except mysql.connector.Error as err:
        print(f"Login Error: {err}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()