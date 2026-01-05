CREATE DATABASE IF NOT EXISTS AirlineDB;
USE AirlineDB;

-- ==========================================
-- 1. עובדים (Employees)
-- ==========================================
CREATE TABLE Managers (
    id_num VARCHAR(9) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50),
    street VARCHAR(50),
    house_number VARCHAR(10),
    start_date DATE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Attendants (
    id_num VARCHAR(9) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50),
    street VARCHAR(50),
    house_number VARCHAR(10),
    start_date DATE,
    long_flight_training BOOLEAN DEFAULT 0
);

CREATE TABLE Pilots (
    id_num VARCHAR(9) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50),
    street VARCHAR(50),
    house_number VARCHAR(10),
    start_date DATE,
    long_flight_training BOOLEAN DEFAULT 0
);

-- ==========================================
-- 2. מטוסים (Planes)
-- ==========================================
CREATE TABLE Planes (
    plane_id VARCHAR(20) PRIMARY KEY,
    manufacturer VARCHAR(50),
    purchase_date DATE,
    size ENUM('Big', 'Small') NOT NULL 
);

CREATE TABLE FlightClass (
    plane_id VARCHAR(20),
    class_type ENUM('Business', 'Economy'),
    num_columns INT,
    num_rows INT,
    total_seats INT,
    PRIMARY KEY (plane_id, class_type),
    FOREIGN KEY (plane_id) REFERENCES Planes(plane_id) ON DELETE CASCADE
);

CREATE TABLE Seats (
    plane_id VARCHAR(20),
    class_type ENUM('Business', 'Economy'),
    row_num INT,
    col_num VARCHAR(5),
    PRIMARY KEY (plane_id, class_type, row_num, col_num),
    FOREIGN KEY (plane_id, class_type) REFERENCES FlightClass(plane_id, class_type) ON DELETE CASCADE
);

-- ==========================================
-- 3. תפעול וטיסות (Flights) - עם הסטטוס החדש
-- ==========================================
CREATE TABLE OperatingLines (
    src_country VARCHAR(50), src_city VARCHAR(50), src_airport VARCHAR(50),
    dst_country VARCHAR(50), dst_city VARCHAR(50), dst_airport VARCHAR(50),
    flight_duration TIME,
    PRIMARY KEY (src_country, src_city, src_airport, dst_country, dst_city, dst_airport)
);

CREATE TABLE Flights (
    flight_id VARCHAR(20) PRIMARY KEY,
    plane_id VARCHAR(20),
    src_country VARCHAR(50), src_city VARCHAR(50), src_airport VARCHAR(50),
    dst_country VARCHAR(50), dst_city VARCHAR(50), dst_airport VARCHAR(50),
    departure_time DATETIME,
    landing_time DATETIME,
    
    -- >>> דרישה 1: סטאטוס טיסה <<<
    -- Active = פעילה
    -- Full = תפוסה מלאה
    -- Landed = התקיימה (נחתה)
    -- Cancelled = בוטלה
    status ENUM('Active', 'Full', 'Landed', 'Cancelled') DEFAULT 'Active',
    
    FOREIGN KEY (plane_id) REFERENCES Planes(plane_id),
    FOREIGN KEY (src_country, src_city, src_airport, dst_country, dst_city, dst_airport) 
        REFERENCES OperatingLines(src_country, src_city, src_airport, dst_country, dst_city, dst_airport)
);

CREATE TABLE AttendantsOnFlights (
    attendant_id VARCHAR(9), flight_id VARCHAR(20),
    PRIMARY KEY (attendant_id, flight_id),
    FOREIGN KEY (attendant_id) REFERENCES Attendants(id_num),
    FOREIGN KEY (flight_id) REFERENCES Flights(flight_id)
);

CREATE TABLE PilotsOnFlights (
    pilot_id VARCHAR(9), flight_id VARCHAR(20),
    PRIMARY KEY (pilot_id, flight_id),
    FOREIGN KEY (pilot_id) REFERENCES Pilots(id_num),
    FOREIGN KEY (flight_id) REFERENCES Flights(flight_id)
);

-- ==========================================
-- 4. לקוחות וטלפונים (Phones Split) - הפיצול
-- ==========================================

-- לקוחות אורחים
CREATE TABLE GuestCustomers (
    email VARCHAR(100) PRIMARY KEY, 
    first_name_en VARCHAR(50),
    last_name_en VARCHAR(50)
);

-- לקוחות רשומים
CREATE TABLE RegisteredCustomers (
    email VARCHAR(100) PRIMARY KEY,
    first_name_en VARCHAR(50),      
    last_name_en VARCHAR(50),       
    registration_date DATE,
    passport_num VARCHAR(20),
    password VARCHAR(255),
    birth_date DATE
);

-- >>> דרישה 3: פיצול טבלאות טלפונים <<<

-- טבלת טלפונים לאורחים
CREATE TABLE GuestPhones (
    email VARCHAR(100),
    phone_number VARCHAR(20),
    
    PRIMARY KEY (email, phone_number),
    FOREIGN KEY (email) REFERENCES GuestCustomers(email) ON DELETE CASCADE
);

-- טבלת טלפונים לרשומים
CREATE TABLE RegisteredPhones (
    email VARCHAR(100),
    phone_number VARCHAR(20),
    
    PRIMARY KEY (email, phone_number),
    FOREIGN KEY (email) REFERENCES RegisteredCustomers(email) ON DELETE CASCADE
);

-- ==========================================
-- 5. הזמנות (Orders) - עם הסטטוס החדש
-- ==========================================
CREATE TABLE Orders (
    order_code VARCHAR(20), 
    
    guest_email VARCHAR(100) NULL,
    registered_email VARCHAR(100) NULL,
    
    total_cost DECIMAL(10, 2),
    
    -- >>> דרישה 2: סטאטוס הזמנה <<<
    -- Active = פעילה
    -- Completed = בוצע (שולם/נסגר)
    -- CancelledByCustomer = ביטול לקוח
    -- CancelledBySystem = ביטול מערכת
    status ENUM('Active', 'Completed', 'CancelledByCustomer', 'CancelledBySystem') DEFAULT 'Active',
    
    PRIMARY KEY (order_code), 
    FOREIGN KEY (guest_email) REFERENCES GuestCustomers(email),
    FOREIGN KEY (registered_email) REFERENCES RegisteredCustomers(email)
);

-- ==========================================
-- 6. כרטיסים (Tickets)
-- ==========================================
CREATE TABLE Tickets (
    ticket_number VARCHAR(20) PRIMARY KEY,
    
    flight_id VARCHAR(20),
    plane_id VARCHAR(20),
    class_type ENUM('Business', 'Economy'),
    row_num INT,
    col_num VARCHAR(5),
    
    order_code VARCHAR(20),
    
    -- המיילים המפוצלים (לצורך תיעוד בכרטיס)
    guest_email VARCHAR(100) NULL,
    registered_email VARCHAR(100) NULL,
    
    price DECIMAL(10, 2),
    
    FOREIGN KEY (flight_id) REFERENCES Flights(flight_id),
    FOREIGN KEY (order_code) REFERENCES Orders(order_code) ON DELETE CASCADE,
    
    FOREIGN KEY (guest_email) REFERENCES GuestCustomers(email),
    FOREIGN KEY (registered_email) REFERENCES RegisteredCustomers(email),
    
    FOREIGN KEY (plane_id, class_type, row_num, col_num) 
        REFERENCES Seats(plane_id, class_type, row_num, col_num)
);
