# ==========================================
# 1. עובדים (Employees) - כאן יש ירושה
# ==========================================

# מחלקת בסיס (הורה) - מכילה את השדות המשותפים לכל העובדים
class Employee:
    def __init__(self, id_num, first_name, last_name, phone, city, street, house_number, start_date):
        self.id_num = id_num
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.city = city
        self.street = street
        self.house_number = house_number
        self.start_date = start_date

# מנהל - יורש מעובד ומוסיף סיסמה
class Manager(Employee):
    def __init__(self, id_num, first_name, last_name, phone, city, street, house_number, start_date, password):
        # קריאה לבנאי של האבא (Employee) כדי למלא את הפרטים הרגילים
        super().__init__(id_num, first_name, last_name, phone, city, street, house_number, start_date)
        self.password = password

# דייל - יורש מעובד ומוסיף הכשרה
class Attendant(Employee):
    def __init__(self, id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training=False):
        super().__init__(id_num, first_name, last_name, phone, city, street, house_number, start_date)
        self.long_flight_training = long_flight_training

# טייס - יורש מעובד ומוסיף הכשרה
class Pilot(Employee):
    def __init__(self, id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training=False):
        super().__init__(id_num, first_name, last_name, phone, city, street, house_number, start_date)
        self.long_flight_training = long_flight_training



class GuestCustomer:
    def __init__(self, email, first_name_en, last_name_en):
        self.email = email
        self.first_name_en = first_name_en
        self.last_name_en = last_name_en
        self.phones = []  # מקום לשמור רשימת טלפונים אם תשלוף אותם

class RegisteredCustomer:
    def __init__(self, email, first_name_en, last_name_en, registration_date, passport_num, password, birth_date):
        self.email = email
        self.first_name_en = first_name_en
        self.last_name_en = last_name_en
        self.registration_date = registration_date
        self.passport_num = passport_num
        self.password = password
        self.birth_date = birth_date
        self.phones = []  # מקום לשמור רשימת טלפונים

# ==========================================
# 3. מטוסים ומושבים (Planes)
# ==========================================

class Plane:
    def __init__(self, plane_id, manufacturer, purchase_date, size):
        self.plane_id = plane_id
        self.manufacturer = manufacturer
        self.purchase_date = purchase_date
        self.size = size

class FlightClass:
    def __init__(self, plane_id, class_type, num_columns, num_rows):
        self.plane_id = plane_id
        self.class_type = class_type
        self.num_columns = num_columns
        self.num_rows = num_rows
        self.total_seats = num_columns * num_rows

class Seat:
    def __init__(self, plane_id, class_type, row_num, col_num):
        self.plane_id = plane_id
        self.class_type = class_type
        self.row_num = row_num
        self.col_num = col_num

# ==========================================
# 4. תפעול וטיסות (Operations)
# ==========================================

class OperatingLine:
    def __init__(self, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, flight_duration):
        self.src_country = src_country
        self.src_city = src_city
        self.src_airport = src_airport
        self.dst_country = dst_country
        self.dst_city = dst_city
        self.dst_airport = dst_airport
        self.flight_duration = flight_duration

class Flight:
    def __init__(self, flight_id, plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, status='Active'):
        self.flight_id = flight_id
        self.plane_id = plane_id
        self.src_country = src_country
        self.src_city = src_city
        self.src_airport = src_airport
        self.dst_country = dst_country
        self.dst_city = dst_city
        self.dst_airport = dst_airport
        self.departure_time = departure_time
        self.landing_time = landing_time
        self.status = status

# ==========================================
# 5. הזמנות וכרטיסים (Orders & Tickets)
# ==========================================

class Order:
    def __init__(self, order_code, total_cost, status='Active', guest_email=None, registered_email=None):
        self.order_code = order_code
        self.guest_email = guest_email
        self.registered_email = registered_email
        self.total_cost = total_cost
        self.status = status

class Ticket:
    def __init__(self, ticket_number, flight_id, plane_id, class_type, row_num, col_num, order_code, price, guest_email=None, registered_email=None):
        self.ticket_number = ticket_number
        self.flight_id = flight_id
        self.plane_id = plane_id
        self.class_type = class_type
        self.row_num = row_num
        self.col_num = col_num
        self.order_code = order_code
        self.guest_email = guest_email
        self.registered_email = registered_email
        self.price = price