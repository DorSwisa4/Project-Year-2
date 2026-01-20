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
    def __init__(self, email, first_name_en, last_name_en, registration_date, passport_num, password, birth_date,
                 phones=None):
        self.email = email
        self.first_name_en = first_name_en
        self.last_name_en = last_name_en
        self.registration_date = registration_date
        self.passport_num = passport_num
        self.password = password
        self.birth_date = birth_date
        # If phones are provided, save them. If not, create an empty list.
        self.phones = phones if phones else []

# ==========================================
# 3. מטוסים ומושבים (Planes)
# ==========================================

class Plane:
    def __init__(self, manufacturer, purchase_date, size, plane_id = None):
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
    def __init__(self, total_cost, status='Active', guest_email=None, registered_email=None, order_code = None):
        self.order_code = order_code
        self.guest_email = guest_email
        self.registered_email = registered_email
        self.total_cost = total_cost
        self.status = status

class Ticket:
    def __init__(self, flight_id, plane_id, class_type, row_num, col_num, order_code, price, guest_email=None, registered_email=None, ticket_number=None):
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

class EmployeeFactory:
    """ a factory class that helps us create a new employee
    (manager, pilot, attendant) it gets a role and a dictionary with
    all the relevant attributes"""
    @staticmethod
    def create_employee(role, data):
        args = [
            data.get('id_num'),
            data.get('first_name'),
            data.get('last_name'),
            data.get('phone'),
            data.get('city'),
            data.get('street'),
            data.get('house_number'),
            data.get('start_date')
        ]

        training = data.get('long_training_flight')
        training_val = 1 if training =='Yes' else 0

        if role == 'Manager':
            return Manager(*args, password=data.get('password'))

        elif role == 'Pilot':
            return Pilot(*args, long_flight_training=training_val)

        elif role == 'Attendant':
            return Attendant(*args, long_flight_training=training_val)

        else:
            return None


from classes import Pilot, Attendant  # Ensure these are imported


class Location:
    # 1. Specific Location Dictionaries
    # Structure: {'Israel': [(id, name, last), ...], 'USA': [...]}
    attendants_by_country = {}
    pilots_by_country = {}

    # 2. "Global Pool" lists for fresh employees (Available from ANY country)
    new_attendants = []
    new_pilots = []

    # 3. Lookup to track where everyone is (for fast moving)
    # Structure: {id_num: 'CountryName'} OR {id_num: 'Global'}
    current_locations = {}

    @staticmethod
    def add_new_employee(employee):
        """
        Adds a new employee to the 'Global Pool'.
        They are available for flights departing from ANY country.
        """
        # Create the tuple: (id, first_name, last_name)
        emp_tuple = (employee.id_num, employee.first_name, employee.last_name)

        if isinstance(employee, Attendant):
            Location.new_attendants.append(emp_tuple)

        elif isinstance(employee, Pilot):
            Location.new_pilots.append(emp_tuple)

        # Mark them as 'Global' in the lookup
        Location.current_locations[employee.id_num] = 'Global'

    @staticmethod
    def get_available_crew(country, role_type):
        """
        Returns a combined list of:
        1. Crew specifically in the requested 'country'.
        2. New crew from the 'Global' list.
        """
        specific_crew = []
        global_crew = []

        if role_type == 'Pilot':
            specific_crew = Location.pilots_by_country.get(country, [])
            global_crew = Location.new_pilots
        elif role_type == 'Attendant':
            specific_crew = Location.attendants_by_country.get(country, [])
            global_crew = Location.new_attendants

        # Return the combined list
        return specific_crew + global_crew

    @staticmethod
    def move_crew_to_destination(flight, crew_employee_objects):
        """
        Moves crew members to the flight's destination.
        Handles moving them from 'Global' -> 'Country' OR 'Country A' -> 'Country B'.
        """
        destination = flight.dst_country

        for emp in crew_employee_objects:
            emp_id = emp.id_num
            emp_tuple = (emp.id_num, emp.first_name, emp.last_name)

            # A. Find where they are currently
            current_loc = Location.current_locations.get(emp_id)

            # B. Remove from old location
            if current_loc == 'Global':
                # Remove from the "New" lists
                if isinstance(emp, Attendant):
                    if emp_tuple in Location.new_attendants:
                        Location.new_attendants.remove(emp_tuple)
                elif isinstance(emp, Pilot):
                    if emp_tuple in Location.new_pilots:
                        Location.new_pilots.remove(emp_tuple)

            elif current_loc and current_loc != 'Global':
                # Remove from specific country list
                if isinstance(emp, Attendant):
                    if current_loc in Location.attendants_by_country:
                        if emp_tuple in Location.attendants_by_country[current_loc]:
                            Location.attendants_by_country[current_loc].remove(emp_tuple)
                elif isinstance(emp, Pilot):
                    if current_loc in Location.pilots_by_country:
                        if emp_tuple in Location.pilots_by_country[current_loc]:
                            Location.pilots_by_country[current_loc].remove(emp_tuple)

            # C. Add to NEW destination country
            if isinstance(emp, Attendant):
                if destination not in Location.attendants_by_country:
                    Location.attendants_by_country[destination] = []
                Location.attendants_by_country[destination].append(emp_tuple)

            elif isinstance(emp, Pilot):
                if destination not in Location.pilots_by_country:
                    Location.pilots_by_country[destination] = []
                Location.pilots_by_country[destination].append(emp_tuple)

            # D. Update lookup to the new real country
            Location.current_locations[emp_id] = destination



