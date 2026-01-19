DROP DATABASE IF EXISTS AirlineDB;
CREATE DATABASE AirlineDB;
USE AirlineDB;

-- ==========================================
-- 1. עובדים (Employees)
-- ==========================================
CREATE TABLE Managers (
    id_num VARCHAR(9) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
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
    phone VARCHAR(20) NOT NULL,
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
    phone VARCHAR(20) NOT NULL,
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
    plane_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer VARCHAR(50),
    purchase_date DATE,
    size ENUM('Big', 'Small') NOT NULL 
);

CREATE TABLE Classes (
    plane_id INT,
    class_type ENUM('Business', 'Economy'),
    num_columns INT,
    num_rows INT,
    total_seats INT,
    PRIMARY KEY (plane_id, class_type),
    FOREIGN KEY (plane_id) REFERENCES Planes(plane_id) ON DELETE CASCADE
);

CREATE TABLE Seats (
    plane_id INT,
    class_type ENUM('Business', 'Economy'),
    row_num INT,
    col_num VARCHAR(5),
    price_supplement DECIMAL(10,2) DEFAULT 0,
    PRIMARY KEY (plane_id, class_type, row_num, col_num),
    FOREIGN KEY (plane_id, class_type) REFERENCES Classes(plane_id, class_type) ON DELETE CASCADE
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
    flight_id INT AUTO_INCREMENT PRIMARY KEY,
    plane_id INT,
    src_country VARCHAR(50), src_city VARCHAR(50), src_airport VARCHAR(50),
    dst_country VARCHAR(50), dst_city VARCHAR(50), dst_airport VARCHAR(50),
    departure_time DATETIME,
    landing_time DATETIME,
    base_price DECIMAL(10,2) DEFAULT 0,
    
    status ENUM('Active', 'Full', 'Landed', 'Cancelled') DEFAULT 'Active',
    
    FOREIGN KEY (plane_id) REFERENCES Planes(plane_id),
    FOREIGN KEY (src_country, src_city, src_airport, dst_country, dst_city, dst_airport) 
        REFERENCES OperatingLines(src_country, src_city, src_airport, dst_country, dst_city, dst_airport)
);

CREATE TABLE AttendantsOnFlights (
    attendant_id VARCHAR(9), flight_id INT,
    PRIMARY KEY (attendant_id, flight_id),
    FOREIGN KEY (attendant_id) REFERENCES Attendants(id_num),
    FOREIGN KEY (flight_id) REFERENCES Flights(flight_id)
);

CREATE TABLE PilotsOnFlights (
    pilot_id VARCHAR(9), flight_id INT,
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
    order_code INT AUTO_INCREMENT, 
    
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
    ticket_number INT AUTO_INCREMENT PRIMARY KEY,
    
    flight_id INT,
    plane_id INT,
    class_type ENUM('Business', 'Economy'),
    row_num INT,
    col_num VARCHAR(5),
    
    order_code INT,
    
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

USE AirlineDB;


USE AirlineDB;



-- ==========================================
-- 1. עובדים
-- ==========================================

INSERT INTO Managers (id_num, first_name, last_name, phone, city, street, house_number, start_date, password) VALUES
('111111111', 'Dor', 'Jacob Haruv', '050-1000001', 'Tel Aviv', 'Rothschild', '1', '2020-01-01', 'admin1'),
('222222222', 'Dor', 'David Swisa', '050-1000002', 'Haifa', 'Herzl', '2', '2021-02-01', 'admin2'),
('333333333', 'Eran', 'Daniel Dgani', '050-1000003', 'Jerusalem', 'Jaffa', '3', '2019-03-01', 'admin3');

INSERT INTO Attendants (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training) VALUES
('400000001', 'Noa', 'Cohen', '052-2000001', 'Eilat', 'Yam', '10', '2022-01-01', 1),
('400000002', 'Yael', 'Levi', '052-2000002', 'Holon', 'Kugel', '20', '2023-05-01', 0),
('400000003', 'Dana', 'Friedman', '052-2000003', 'Tel Aviv', 'Allenby', '30', '2021-08-15', 1),
('400000004', 'Michal', 'Katz', '052-2000004', 'Rishon', 'Herzl', '40', '2024-01-01', 0);

INSERT INTO Pilots (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training) VALUES
('600000001', 'Ron', 'Shachar', '054-3000001', 'Tel Aviv', 'Dizengoff', '100', '2018-01-01', 1),
('600000002', 'Gal', 'Malka', '054-3000002', 'Ramat Gan', 'Bialik', '12', '2020-06-01', 0),
('600000003', 'Omer', 'Bar', '054-3000003', 'Haifa', 'Moriah', '55', '2015-11-20', 1),
('600000004', 'Ido', 'Golan', '054-3000004', 'Herzliya', 'Sokolov', '8', '2022-03-10', 0);


-- ==========================================
-- 2. מטוסים
-- ==========================================
INSERT INTO Planes (manufacturer, purchase_date, size) VALUES
('Boeing', '2015-01-01', 'Big'),    -- Plane 1
('Boeing', '2018-06-15', 'Small'),  -- Plane 2
('Airbus', '2019-01-01', 'Big'),    -- Plane 3
('Airbus', '2020-02-20', 'Small'),  -- Plane 4
('Embraer', '2021-03-10', 'Small'), -- Plane 5
('Bombardier', '2022-04-05', 'Small'); -- Plane 6

INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats) VALUES
(1, 'Business', 4, 5, 20), (1, 'Economy', 9, 30, 270),
(2, 'Business', 4, 2, 8),  (2, 'Economy', 6, 20, 120),
(3, 'Business', 6, 10, 60), (3, 'Economy', 10, 40, 400),
(4, 'Economy', 6, 25, 150),
(5, 'Economy', 4, 20, 80),
(6, 'Economy', 4, 18, 72);

INSERT INTO Seats (plane_id, class_type, row_num, col_num, price_supplement) VALUES
(1, 'Business', 1, 'A', 100), (1, 'Business', 1, 'B', 100),
(1, 'Economy', 10, 'A', 0),   (1, 'Economy', 10, 'B', 0),
(2, 'Business', 1, 'A', 100),
(2, 'Economy', 5, 'A', 0), (2, 'Economy', 5, 'B', 0),
(3, 'Business', 1, 'A', 100),
(3, 'Economy', 20, 'A', 0),
(4, 'Economy', 1, 'A', 0), (4, 'Economy', 1, 'B', 0),
(5, 'Economy', 1, 'A', 0),
(6, 'Economy', 1, 'A', 0);


-- ==========================================
-- 3. קווי תפעול
-- ==========================================
INSERT INTO OperatingLines (src_country, src_city, src_airport, dst_country, dst_city, dst_airport, flight_duration) VALUES
('Israel', 'Tel Aviv', 'TLV', 'USA', 'New York', 'JFK', '11:00:00'),
('Israel', 'Tel Aviv', 'TLV', 'UK', 'London', 'LHR', '05:30:00'),
('Israel', 'Tel Aviv', 'TLV', 'France', 'Paris', 'CDG', '04:50:00'),
('Israel', 'Tel Aviv', 'TLV', 'Greece', 'Athens', 'ATH', '02:00:00'),
('Israel', 'Tel Aviv', 'TLV', 'Thailand', 'Bangkok', 'BKK', '10:30:00'),
('USA', 'New York', 'JFK', 'Israel', 'Tel Aviv', 'TLV', '10:45:00');


-- ==========================================
-- 4. טיסות (ללא manager_id) !!!
-- ==========================================
INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status) VALUES
-- חודש הנוכחי
(1, 'Israel', 'Tel Aviv', 'TLV', 'USA', 'New York', 'JFK', NOW() + INTERVAL 5 HOUR, NOW() + INTERVAL 16 HOUR, 1000, 'Active'),
(2, 'Israel', 'Tel Aviv', 'TLV', 'UK', 'London', 'LHR', NOW() + INTERVAL 10 HOUR, NOW() + INTERVAL 15 HOUR, 600, 'Active'),
(3, 'Israel', 'Tel Aviv', 'TLV', 'France', 'Paris', 'CDG', NOW() + INTERVAL 20 HOUR, NOW() + INTERVAL 25 HOUR, 500, 'Active'),
(4, 'Israel', 'Tel Aviv', 'TLV', 'Greece', 'Athens', 'ATH', NOW() + INTERVAL 5 DAY, NOW() + INTERVAL 5 DAY + INTERVAL 2 HOUR, 200, 'Active'),

-- לפני חודש
(1, 'USA', 'New York', 'JFK', 'Israel', 'Tel Aviv', 'TLV', DATE_SUB(NOW(), INTERVAL 1 MONTH), DATE_SUB(NOW(), INTERVAL 1 MONTH) + INTERVAL 11 HOUR, 900, 'Landed'),
(5, 'Israel', 'Tel Aviv', 'TLV', 'Greece', 'Athens', 'ATH', DATE_SUB(NOW(), INTERVAL 1 MONTH), DATE_SUB(NOW(), INTERVAL 1 MONTH) + INTERVAL 2 HOUR, 150, 'Landed'),

-- לפני חודשיים
(2, 'Israel', 'Tel Aviv', 'TLV', 'UK', 'London', 'LHR', DATE_SUB(NOW(), INTERVAL 2 MONTH), DATE_SUB(NOW(), INTERVAL 2 MONTH) + INTERVAL 5 HOUR, 550, 'Landed'),
(6, 'Israel', 'Tel Aviv', 'TLV', 'Greece', 'Athens', 'ATH', DATE_SUB(NOW(), INTERVAL 2 MONTH), DATE_SUB(NOW(), INTERVAL 2 MONTH) + INTERVAL 2 HOUR, 180, 'Cancelled'),

-- לפני 3 חודשים
(3, 'Israel', 'Tel Aviv', 'TLV', 'Thailand', 'Bangkok', 'BKK', DATE_SUB(NOW(), INTERVAL 3 MONTH), DATE_SUB(NOW(), INTERVAL 3 MONTH) + INTERVAL 10 HOUR, 800, 'Landed'),
(4, 'Israel', 'Tel Aviv', 'TLV', 'France', 'Paris', 'CDG', DATE_SUB(NOW(), INTERVAL 3 MONTH), DATE_SUB(NOW(), INTERVAL 3 MONTH) + INTERVAL 5 HOUR, 450, 'Landed'),

-- לפני 4 חודשים
(1, 'Israel', 'Tel Aviv', 'TLV', 'USA', 'New York', 'JFK', DATE_SUB(NOW(), INTERVAL 4 MONTH), DATE_SUB(NOW(), INTERVAL 4 MONTH) + INTERVAL 11 HOUR, 950, 'Landed'),
(5, 'Israel', 'Tel Aviv', 'TLV', 'Greece', 'Athens', 'ATH', DATE_SUB(NOW(), INTERVAL 4 MONTH), DATE_SUB(NOW(), INTERVAL 4 MONTH) + INTERVAL 2 HOUR, 140, 'Cancelled');


-- ==========================================
-- 5. שיבוץ צוות
-- ==========================================
INSERT INTO AttendantsOnFlights (attendant_id, flight_id) VALUES 
('400000001', 1), ('400000001', 5),
('400000002', 2), ('400000002', 6),
('400000003', 3), ('400000003', 9),
('400000004', 4), ('400000004', 10);

INSERT INTO PilotsOnFlights (pilot_id, flight_id) VALUES
('600000001', 1), ('600000001', 5),
('600000002', 2), ('600000002', 6),
('600000003', 3), ('600000003', 9),
('600000004', 4), ('600000004', 10);


-- ==========================================
-- 6. לקוחות
-- ==========================================
INSERT INTO GuestCustomers (email, first_name_en, last_name_en) VALUES
('g1@test.com', 'John', 'Doe'), ('g2@test.com', 'Jane', 'Smith'),
('g3@test.com', 'Bob', 'Dylan'), ('g4@test.com', 'Alice', 'Wonder'),
('g5@test.com', 'Charlie', 'Chaplin');

INSERT INTO RegisteredCustomers (email, first_name_en, last_name_en, registration_date, passport_num, password, birth_date) VALUES
('r1@test.com', 'Moshe', 'Cohen', '2020-01-01', 'P1', '123', '1990-01-01'),
('r2@test.com', 'Sarah', 'Levi', '2021-01-01', 'P2', '123', '1992-02-02'),
('r3@test.com', 'David', 'Ben', '2022-01-01', 'P3', '123', '1985-05-05'),
('r4@test.com', 'Rina', 'Mat', '2023-01-01', 'P4', '123', '1999-09-09'),
('r5@test.com', 'Yossi', 'Gagin', '2019-01-01', 'P5', '123', '1980-08-08');


-- ==========================================
-- 7. הזמנות וכרטיסים
-- ==========================================
INSERT INTO Orders (guest_email, total_cost, status) VALUES 
('g1@test.com', 1100, 'Active'),
('g2@test.com', 600, 'Active'),
('g3@test.com', 500, 'Active');

INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, guest_email, price) VALUES
(1, 1, 'Business', 1, 'A', 1, 'g1@test.com', 1100),
(2, 2, 'Economy', 5, 'A', 2, 'g2@test.com', 600),
(3, 3, 'Economy', 20, 'A', 3, 'g3@test.com', 500);

INSERT INTO Orders (registered_email, total_cost, status) VALUES
('r1@test.com', 1000, 'Completed'),
('r2@test.com', 180, 'Completed'),
('r3@test.com', 800, 'Completed');

INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, registered_email, price) VALUES
(5, 1, 'Economy', 10, 'A', 4, 'r1@test.com', 1000),
(6, 5, 'Economy', 1, 'A', 5, 'r2@test.com', 180),
(9, 3, 'Economy', 20, 'A', 6, 'r3@test.com', 800);

INSERT INTO Orders (registered_email, total_cost, status) VALUES
('r4@test.com', 950, 'CancelledByCustomer'),
('r5@test.com', 550, 'CancelledByCustomer');

INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, registered_email, price) VALUES
(11, 1, 'Economy', 10, 'B', 7, 'r4@test.com', 950),
(7, 2, 'Economy', 5, 'B', 8, 'r5@test.com', 550);

INSERT INTO Orders (guest_email, total_cost, status) VALUES ('g4@test.com', 200, 'Active');
INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, guest_email, price) VALUES
(4, 4, 'Economy', 1, 'A', 9, 'g4@test.com', 200);
