def add_to_sql(obj):
    """
    מקבלת אובייקט, מזהה את סוגו ומכניסה אותו לטבלה המתאימה ב-DB.
    """

    # הגדרות התחברות ל-DB (שנה את הסיסמה לסיסמה שלך)
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'airlinedb'
    }

    sql = None
    values = None

    # זיהוי סוג האובייקט והכנת השאילתה
    if isinstance(obj, Manager):
        sql = """INSERT INTO Managers (id_num, first_name, last_name, phone, city, street, house_number, start_date, password)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (
        obj.id_num, obj.first_name, obj.last_name, obj.phone, obj.city, obj.street, obj.house_number, obj.start_date,
        obj.password)

    elif isinstance(obj, Pilot):
        sql = """INSERT INTO Pilots (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (
        obj.id_num, obj.first_name, obj.last_name, obj.phone, obj.city, obj.street, obj.house_number, obj.start_date,
        obj.long_flight_training)

    elif isinstance(obj, Attendant):
        sql = """INSERT INTO Attendants (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (
        obj.id_num, obj.first_name, obj.last_name, obj.phone, obj.city, obj.street, obj.house_number, obj.start_date,
        obj.long_flight_training)

    elif isinstance(obj, GuestCustomer):
        sql = """INSERT INTO GuestCustomers (email, first_name_en, last_name_en) VALUES (%s, %s, %s)"""
        values = (obj.email, obj.first_name_en, obj.last_name_en)

    elif isinstance(obj, RegisteredCustomer):
        sql = """INSERT INTO RegisteredCustomers (email, first_name_en, last_name_en, registration_date, passport_num, password, birth_date)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (obj.email, obj.first_name_en, obj.last_name_en, obj.registration_date, obj.passport_num, obj.password,
                  obj.birth_date)

    elif isinstance(obj, Plane):
        sql = """INSERT INTO Planes (plane_id, manufacturer, purchase_date, size) VALUES (%s, %s, %s, %s)"""
        values = (obj.plane_id, obj.manufacturer, obj.purchase_date, obj.size)

    elif isinstance(obj, FlightClass):
        # שים לב: ב-SQL הטבלה נקראת Classes
        sql = """INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats) VALUES (%s, %s, %s, %s, %s)"""
        values = (obj.plane_id, obj.class_type, obj.num_columns, obj.num_rows, obj.total_seats)

    elif isinstance(obj, Seat):
        sql = """INSERT INTO Seats (plane_id, class_type, row_num, col_num) VALUES (%s, %s, %s, %s)"""
        values = (obj.plane_id, obj.class_type, obj.row_num, obj.col_num)

    elif isinstance(obj, OperatingLine):
        sql = """INSERT INTO OperatingLines (src_country, src_city, src_airport, dst_country, dst_city, dst_airport, flight_duration)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (obj.src_country, obj.src_city, obj.src_airport, obj.dst_country, obj.dst_city, obj.dst_airport,
                  obj.flight_duration)

    elif isinstance(obj, Flight):
        sql = """INSERT INTO Flights (flight_id, plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, status)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (
        obj.flight_id, obj.plane_id, obj.src_country, obj.src_city, obj.src_airport, obj.dst_country, obj.dst_city,
        obj.dst_airport, obj.departure_time, obj.landing_time, obj.status)

    elif isinstance(obj, Order):
        sql = """INSERT INTO Orders (order_code, total_cost, status, guest_email, registered_email)
                 VALUES (%s, %s, %s, %s, %s)"""
        values = (obj.order_code, obj.total_cost, obj.status, obj.guest_email, obj.registered_email)

    elif isinstance(obj, Ticket):
        sql = """INSERT INTO Tickets (ticket_number, flight_id, plane_id, class_type, row_num, col_num, order_code, guest_email, registered_email, price)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (
        obj.ticket_number, obj.flight_id, obj.plane_id, obj.class_type, obj.row_num, obj.col_num, obj.order_code,
        obj.guest_email, obj.registered_email, obj.price)

    else:
        print(f"Error: Unknown object type {type(obj)}")
        return

    # ביצוע ההוספה בפועל
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        print(f"Successfully added {type(obj).__name__} to DB!")
    except mysql.connector.Error as err:
        print(f"Error inserting to SQL: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()