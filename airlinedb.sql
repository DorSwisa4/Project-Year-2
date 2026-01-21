CREATE DATABASE AirlineDB;
USE AirlineDB;

-- ==========================================================
-- 2. SCHEMA CREATION (Based on your provided file)
-- ==========================================================

-- 1. Employees
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

-- 2. Planes
CREATE TABLE Planes (
    plane_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer ENUM('Boeing','Airbus','Dassault'),
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

-- 3. Operations
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

-- 4. Customers
CREATE TABLE GuestCustomers (
    email VARCHAR(100) PRIMARY KEY, 
    first_name_en VARCHAR(50),
    last_name_en VARCHAR(50)
);

CREATE TABLE RegisteredCustomers (
    email VARCHAR(100) PRIMARY KEY,
    first_name_en VARCHAR(50),      
    last_name_en VARCHAR(50),       
    registration_date DATE,
    passport_num VARCHAR(20),
    password VARCHAR(255),
    birth_date DATE
);

CREATE TABLE GuestPhones (
    email VARCHAR(100),
    phone_number VARCHAR(20),
    PRIMARY KEY (email, phone_number),
    FOREIGN KEY (email) REFERENCES GuestCustomers(email) ON DELETE CASCADE
);

CREATE TABLE RegisteredPhones (
    email VARCHAR(100),
    phone_number VARCHAR(20),
    PRIMARY KEY (email, phone_number),
    FOREIGN KEY (email) REFERENCES RegisteredCustomers(email) ON DELETE CASCADE
);

-- 5. Orders & Tickets
CREATE TABLE Orders (
    order_code INT AUTO_INCREMENT, 
    guest_email VARCHAR(100) NULL,
    registered_email VARCHAR(100) NULL,
    total_cost DECIMAL(10, 2),
    status ENUM('Active', 'Completed', 'CancelledByCustomer', 'CancelledBySystem') DEFAULT 'Active',
    PRIMARY KEY (order_code), 
    FOREIGN KEY (guest_email) REFERENCES GuestCustomers(email),
    FOREIGN KEY (registered_email) REFERENCES RegisteredCustomers(email)
);

CREATE TABLE Tickets (
    ticket_number INT AUTO_INCREMENT PRIMARY KEY,
    flight_id INT,
    plane_id INT,
    class_type ENUM('Business', 'Economy'),
    row_num INT,
    col_num VARCHAR(5),
    order_code INT,
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

-- ==========================================================
-- 3. DATA POPULATION
-- ==========================================================

-- --- Requirement 3: Create exactly 3 specific Managers ---
INSERT INTO Managers (id_num, first_name, last_name, phone, city, street, house_number, start_date, password) VALUES
('111111111', 'Dor', 'Jacob Haruv', '050-1111111', 'Tel Aviv', 'Rothschild', '1', '2020-01-01', 'admin1'),
('222222222', 'Dor', 'David Swisa', '050-2222222', 'Haifa', 'Herzl', '2', '2021-02-01', 'admin2'),
('333333333', 'Eran', 'Daniel Dgani', '050-3333333', 'Jerusalem', 'Jaffa', '3', '2019-03-01', 'admin3');

-- --- Requirement 6: Create at least 20 planes (Boeing, Airbus, Dassault) ---
-- Planes 1-10: BIG (For long flights)
INSERT INTO Planes (manufacturer, purchase_date, size) VALUES
('Boeing', '2018-01-01', 'Big'), ('Airbus', '2019-05-10', 'Big'),
('Boeing', '2020-03-15', 'Big'), ('Airbus', '2017-11-20', 'Big'),
('Dassault', '2021-01-05', 'Big'), ('Boeing', '2018-06-06', 'Big'),
('Airbus', '2022-01-01', 'Big'), ('Dassault', '2019-09-09', 'Big'),
('Boeing', '2020-02-02', 'Big'), ('Airbus', '2021-12-12', 'Big');

-- Planes 11-20: SMALL (Economy Only)
INSERT INTO Planes (manufacturer, purchase_date, size) VALUES
('Boeing', '2018-01-01', 'Small'), ('Airbus', '2019-05-10', 'Small'),
('Dassault', '2020-03-15', 'Small'), ('Airbus', '2017-11-20', 'Small'),
('Dassault', '2021-01-05', 'Small'), ('Boeing', '2018-06-06', 'Small'),
('Airbus', '2022-01-01', 'Small'), ('Dassault', '2019-09-09', 'Small'),
('Boeing', '2020-02-02', 'Small'), ('Airbus', '2021-12-12', 'Small');


-- --- Requirement 7 & 4: Configure Classes and Create Seats ---
-- BIG PLANES (1-10): Have Business (Row 1-5, Col A-D) and Economy (Row 6-25, Col A-F)
INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats)
SELECT plane_id, 'Business', 4, 5, 20 FROM Planes WHERE size='Big';

INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats)
SELECT plane_id, 'Economy', 6, 20, 120 FROM Planes WHERE size='Big';

-- SMALL PLANES (11-20): Economy Only (Row 1-20, Col A-F)
INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats)
SELECT plane_id, 'Economy', 6, 20, 120 FROM Planes WHERE size='Small';

-- --- Generating ACTUAL SEATS for all planes (Requirement 4) ---
-- We use a temporary helper mechanism to generate rows and columns without Python
DROP TABLE IF EXISTS TempNums;
CREATE TEMPORARY TABLE TempNums (n INT);
INSERT INTO TempNums VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10),(11),(12),(13),(14),(15),(16),(17),(18),(19),(20),(21),(22),(23),(24),(25);

DROP TABLE IF EXISTS TempCols;
CREATE TEMPORARY TABLE TempCols (c CHAR(1), idx INT);
INSERT INTO TempCols VALUES ('A',1),('B',2),('C',3),('D',4),('E',5),('F',6);

-- Insert Business Seats (Big Planes, Rows 1-5, Cols A-D)
INSERT INTO Seats (plane_id, class_type, row_num, col_num, price_supplement)
SELECT p.plane_id, 'Business', tn.n, tc.c, 100.00
FROM Planes p
JOIN TempNums tn ON tn.n <= 5
JOIN TempCols tc ON tc.idx <= 4
WHERE p.size = 'Big';

-- Insert Economy Seats (Big Planes, Rows 6-25, Cols A-F)
INSERT INTO Seats (plane_id, class_type, row_num, col_num, price_supplement)
SELECT p.plane_id, 'Economy', tn.n + 5, tc.c, 0.00
FROM Planes p
JOIN TempNums tn ON tn.n <= 20
JOIN TempCols tc ON tc.idx <= 6
WHERE p.size = 'Big';

-- Insert Economy Seats (Small Planes, Rows 1-20, Cols A-F)
INSERT INTO Seats (plane_id, class_type, row_num, col_num, price_supplement)
SELECT p.plane_id, 'Economy', tn.n, tc.c, 0.00
FROM Planes p
JOIN TempNums tn ON tn.n <= 20
JOIN TempCols tc ON tc.idx <= 6
WHERE p.size = 'Small';


-- --- Requirement 5: Create 80 Attendants and 50 Pilots ---
-- (We use a procedure to loop insert to avoid 130 lines of code, then drop it)
DELIMITER $$
CREATE PROCEDURE FillCrew()
BEGIN
    DECLARE i INT DEFAULT 1;
    -- 80 Attendants
    WHILE i <= 80 DO
        INSERT INTO Attendants (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training)
        VALUES (
            CONCAT('4000000', LPAD(i, 2, '0')), 
            CONCAT('Attendant', i), 
            'Worker', 
            CONCAT('052-00000', LPAD(i, 2, '0')), 
            'Tel Aviv', 'Street', '1', CURDATE(), 
            IF(i % 2 = 0, 1, 0) -- Half have long training
        );
        SET i = i + 1;
    END WHILE;
    
    SET i = 1;
    -- 50 Pilots
    WHILE i <= 50 DO
        INSERT INTO Pilots (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training)
        VALUES (
            CONCAT('6000000', LPAD(i, 2, '0')), 
            CONCAT('Pilot', i), 
            'Flyer', 
            CONCAT('054-00000', LPAD(i, 2, '0')), 
            'Haifa', 'Ave', '1', CURDATE(), 
            IF(i % 2 = 0, 1, 0) -- Half have long training
        );
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;
CALL FillCrew();
DROP PROCEDURE FillCrew;


-- --- Requirement 10: Operating Lines (Symmetric) ---
-- Long Lines (> 6 hours)
INSERT INTO OperatingLines VALUES 
('Israel', 'Tel Aviv', 'TLV', 'USA', 'New York', 'JFK', '11:00:00'),
('USA', 'New York', 'JFK', 'Israel', 'Tel Aviv', 'TLV', '11:00:00'), -- Symmetric

('Israel', 'Tel Aviv', 'TLV', 'Thailand', 'Bangkok', 'BKK', '10:30:00'),
('Thailand', 'Bangkok', 'BKK', 'Israel', 'Tel Aviv', 'TLV', '10:30:00'); -- Symmetric

-- Short Lines (< 6 hours)
INSERT INTO OperatingLines VALUES 
('Israel', 'Tel Aviv', 'TLV', 'UK', 'London', 'LHR', '05:30:00'),
('UK', 'London', 'LHR', 'Israel', 'Tel Aviv', 'TLV', '05:30:00'),

('Israel', 'Tel Aviv', 'TLV', 'France', 'Paris', 'CDG', '04:50:00'),
('France', 'Paris', 'CDG', 'Israel', 'Tel Aviv', 'TLV', '04:50:00'),

('Israel', 'Tel Aviv', 'TLV', 'Greece', 'Athens', 'ATH', '02:00:00'),
('Greece', 'Athens', 'ATH', 'Israel', 'Tel Aviv', 'TLV', '02:00:00'),

('Israel', 'Tel Aviv', 'TLV', 'Cyprus', 'Larnaca', 'LCA', '01:00:00'),
('Cyprus', 'Larnaca', 'LCA', 'Israel', 'Tel Aviv', 'TLV', '01:00:00');


-- --- Requirement 8 & 9: Create Flights (Logic check) ---
-- Requirement 9: Only Big planes on > 6 hours.
-- Requirement 8: Crew logic handles in assignment later.

-- Flight 1: Long (TLV -> JFK). Needs Big Plane (ID 1).
INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
VALUES (1, 'Israel', 'Tel Aviv', 'TLV', 'USA', 'New York', 'JFK', NOW() + INTERVAL 1 DAY, NOW() + INTERVAL 1 DAY + INTERVAL 11 HOUR, 1200, 'Active');

-- Flight 2: Long (JFK -> TLV). Needs Big Plane (ID 2).
INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
VALUES (2, 'USA', 'New York', 'JFK', 'Israel', 'Tel Aviv', 'TLV', NOW() + INTERVAL 2 DAY, NOW() + INTERVAL 2 DAY + INTERVAL 11 HOUR, 1100, 'Active');

-- Flight 3: Short (TLV -> ATH). Small Plane (ID 11) OK.
INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
VALUES (11, 'Israel', 'Tel Aviv', 'TLV', 'Greece', 'Athens', 'ATH', NOW() + INTERVAL 5 HOUR, NOW() + INTERVAL 7 HOUR, 200, 'Active');

-- Flight 4: Short (ATH -> TLV). Small Plane (ID 11) OK.
INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
VALUES (11, 'Greece', 'Athens', 'ATH', 'Israel', 'Tel Aviv', 'TLV', NOW() + INTERVAL 10 HOUR, NOW() + INTERVAL 12 HOUR, 180, 'Active');

-- Flight 5: Long (TLV -> BKK). Big Plane (ID 3).
INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
VALUES (3, 'Israel', 'Tel Aviv', 'TLV', 'Thailand', 'Bangkok', 'BKK', NOW() + INTERVAL 3 DAY, NOW() + INTERVAL 3 DAY + INTERVAL 10 HOUR, 900, 'Active');

-- Flight 6 (Past): Short. Small Plane (ID 12). Landed.
INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
VALUES (12, 'Israel', 'Tel Aviv', 'TLV', 'Cyprus', 'Larnaca', 'LCA', NOW() - INTERVAL 10 DAY, NOW() - INTERVAL 10 DAY + INTERVAL 1 HOUR, 100, 'Landed');

-- ... Adding more flights to reach variety ...
INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
VALUES 
(4, 'Israel', 'Tel Aviv', 'TLV', 'UK', 'London', 'LHR', NOW() + INTERVAL 5 DAY, NOW() + INTERVAL 5 DAY + INTERVAL 5 HOUR, 500, 'Active'),
(5, 'UK', 'London', 'LHR', 'Israel', 'Tel Aviv', 'TLV', NOW() + INTERVAL 6 DAY, NOW() + INTERVAL 6 DAY + INTERVAL 5 HOUR, 450, 'Active'),
(13, 'Israel', 'Tel Aviv', 'TLV', 'France', 'Paris', 'CDG', NOW() + INTERVAL 12 HOUR, NOW() + INTERVAL 17 HOUR, 400, 'Active'),
(14, 'France', 'Paris', 'CDG', 'Israel', 'Tel Aviv', 'TLV', NOW() + INTERVAL 20 HOUR, NOW() + INTERVAL 25 HOUR, 400, 'Active');


-- --- Requirement 8: Assign Crew (Long flights need training) ---
-- Pilots with ID ending in Even numbers (02, 04, ...) have Long Flight Training (See proc above).

-- Flight 1 (Long): Assign trained pilots/attendants
INSERT INTO PilotsOnFlights VALUES ('600000002', 1), ('600000004', 1);
INSERT INTO AttendantsOnFlights VALUES ('400000002', 1), ('400000004', 1), ('400000006', 1);

-- Flight 3 (Short): Can assign anyone
INSERT INTO PilotsOnFlights VALUES ('600000001', 3); -- Untrained OK for short
INSERT INTO AttendantsOnFlights VALUES ('400000001', 3);

-- Flight 5 (Long): Needs trained
INSERT INTO PilotsOnFlights VALUES ('600000006', 5);
INSERT INTO AttendantsOnFlights VALUES ('400000008', 5);


-- --- Requirement 13: Create 200 Customers (100 Reg, 100 Guest) ---
DELIMITER $$
CREATE PROCEDURE FillCustomers()
BEGIN
    DECLARE i INT DEFAULT 1;
    -- 100 Registered
    WHILE i <= 100 DO
        INSERT INTO RegisteredCustomers VALUES (
            CONCAT('reg', i, '@mail.com'), 
            CONCAT('RegName', i), 
            'Family', 
            CURDATE(), 
            CONCAT('P', i + 10000), 
            'password123', 
            '1990-01-01'
        );
        -- Requirement 11: Registered phone
        INSERT INTO RegisteredPhones VALUES (
            CONCAT('reg', i, '@mail.com'),
            CONCAT('050-', LPAD(i, 7, '0'))
        );
        SET i = i + 1;
    END WHILE;

    SET i = 1;
    -- 100 Guests
    WHILE i <= 100 DO
        INSERT INTO GuestCustomers VALUES (
            CONCAT('guest', i, '@mail.com'),
            CONCAT('GuestName', i),
            'Visitor'
        );
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;
CALL FillCustomers();
DROP PROCEDURE FillCustomers;


-- --- Requirement 14 & 12: Create 100 Orders & Tickets ---
-- We will loop to create orders.
-- Half for guests (add phone to GuestPhones), Half for registered.
DELIMITER $$
CREATE PROCEDURE FillOrders()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE o_id INT;
    
    WHILE i <= 50 DO
        -- 1. Guest Order
        INSERT INTO Orders (guest_email, total_cost, status) 
        VALUES (CONCAT('guest', i, '@mail.com'), 500, 'Active');
        SET o_id = LAST_INSERT_ID();
        
        -- Requirement 12: Guest with order must have phone
        INSERT IGNORE INTO GuestPhones VALUES (CONCAT('guest', i, '@mail.com'), CONCAT('055-', LPAD(i, 7, '0')));
        
        -- Create Ticket for Guest (Flight 3, Plane 11 (Small), Eco)
        INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, guest_email, price)
        VALUES (3, 11, 'Economy', 1, 'A', o_id, CONCAT('guest', i, '@mail.com'), 200);

        -- 2. Registered Order
        INSERT INTO Orders (registered_email, total_cost, status) 
        VALUES (CONCAT('reg', i, '@mail.com'), 1200, 'Active');
        SET o_id = LAST_INSERT_ID();
        
        -- Create Ticket for Registered (Flight 1, Plane 1 (Big), Business)
        INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, registered_email, price)
        VALUES (1, 1, 'Business', 1, 'A', o_id, CONCAT('reg', i, '@mail.com'), 1200);

        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;
CALL FillOrders();
DROP PROCEDURE FillOrders;

-- Cleanup
DROP TABLE TempNums;
DROP TABLE TempCols;



USE AirlineDB;

-- ==========================================================
-- 1. יצירת לקוחות עבר (Registered + Guests) + טלפונים בהתאמה
-- ==========================================================

DELIMITER $$
CREATE PROCEDURE AddPastCustomers()
BEGIN
    DECLARE i INT DEFAULT 200; -- מתחילים מ-200 כדי לא להתנגש עם הנתונים הקודמים
    
    WHILE i < 250 DO
        -- 1. לקוחות רשומים
        INSERT INTO RegisteredCustomers (email, first_name_en, last_name_en, registration_date, passport_num, password, birth_date)
        VALUES (
            CONCAT('past_reg', i, '@mail.com'), 
            CONCAT('OldReg', i), 
            'Smith', 
            '2015-01-01', -- נרשמו בעבר
            CONCAT('P99', i), 
            'oldpass', 
            '1985-05-05'
        );
        
        -- חובה: טלפון ללקוח רשום מיד לאחר היצירה
        INSERT INTO RegisteredPhones (email, phone_number)
        VALUES (CONCAT('past_reg', i, '@mail.com'), CONCAT('050-999', i));

        -- 2. לקוחות אורחים
        INSERT INTO GuestCustomers (email, first_name_en, last_name_en)
        VALUES (CONCAT('past_guest', i, '@mail.com'), CONCAT('OldGuest', i), 'Cohen');

        -- חובה: טלפון ללקוח אורח מיד לאחר היצירה (דרישה 12)
        INSERT INTO GuestPhones (email, phone_number)
        VALUES (CONCAT('past_guest', i, '@mail.com'), CONCAT('054-888', i));
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;
CALL AddPastCustomers();
DROP PROCEDURE AddPastCustomers;

-- ==========================================================
-- 2. יצירת טיסות עבר (Landed) - שימוש במטוסים קיימים בלבד
-- ==========================================================

INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
VALUES 
-- טיסה 1: ארוכה, מטוס גדול (ID 1)
(1, 'USA', 'New York', 'JFK', 'Israel', 'Tel Aviv', 'TLV', '2022-01-10 10:00:00', '2022-01-10 21:00:00', 800, 'Landed'),

-- טיסה 2: קצרה, מטוס קטן (ID 15)
(15, 'UK', 'London', 'LHR', 'Israel', 'Tel Aviv', 'TLV', '2022-02-15 14:00:00', '2022-02-15 19:30:00', 300, 'Landed'),

-- טיסה 3: ארוכה, מטוס גדול (ID 5)
(5, 'Thailand', 'Bangkok', 'BKK', 'Israel', 'Tel Aviv', 'TLV', '2021-11-20 08:00:00', '2021-11-20 18:30:00', 600, 'Landed'),

-- טיסה 4: קצרה, מטוס קטן (ID 18)
(18, 'France', 'Paris', 'CDG', 'Israel', 'Tel Aviv', 'TLV', '2023-05-05 12:00:00', '2023-05-05 16:50:00', 250, 'Landed'),

-- טיסה 5: קצרה, מטוס קטן (ID 20)
(20, 'Greece', 'Athens', 'ATH', 'Israel', 'Tel Aviv', 'TLV', '2023-06-01 09:00:00', '2023-06-01 11:00:00', 150, 'Landed');

-- ==========================================================
-- 3. שיבוץ צוות לטיסות העבר (כדי למנוע שגיאות FK)
-- ==========================================================
INSERT INTO PilotsOnFlights (pilot_id, flight_id) VALUES 
('600000002', (SELECT flight_id FROM Flights WHERE status='Landed' LIMIT 1));

INSERT INTO AttendantsOnFlights (attendant_id, flight_id) VALUES 
('400000002', (SELECT flight_id FROM Flights WHERE status='Landed' LIMIT 1));


-- ==========================================================
-- 4. יצירת הזמנות וכרטיסים לטיסות העבר (סטטוס Completed)
-- ==========================================================
DELIMITER $$
CREATE PROCEDURE CreatePastOrders()
BEGIN
    DECLARE i INT DEFAULT 200;
    DECLARE past_flight_id INT;
    DECLARE order_id INT;
    
    -- בוחרים אחת מטיסות העבר שיצרנו למעלה
    SELECT flight_id INTO past_flight_id FROM Flights WHERE status='Landed' ORDER BY flight_id ASC LIMIT 1;

    WHILE i < 230 DO
        -- 1. הזמנה ללקוח רשום
        INSERT INTO Orders (registered_email, total_cost, status) 
        VALUES (CONCAT('past_reg', i, '@mail.com'), 900, 'Completed');
        
        SET order_id = LAST_INSERT_ID();

        -- כרטיס (Business)
        INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, registered_email, price)
        VALUES (past_flight_id, 1, 'Business', 2, 'A', order_id, CONCAT('past_reg', i, '@mail.com'), 900);

        -- 2. הזמנה ללקוח אורח
        INSERT INTO Orders (guest_email, total_cost, status) 
        VALUES (CONCAT('past_guest', i, '@mail.com'), 800, 'Completed');
        
        SET order_id = LAST_INSERT_ID();

        -- כרטיס (Economy)
        INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, guest_email, price)
        VALUES (past_flight_id, 1, 'Economy', 10, 'A', order_id, CONCAT('past_guest', i, '@mail.com'), 800);

        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;
CALL CreatePastOrders();
DROP PROCEDURE CreatePastOrders;


USE AirlineDB;

DELIMITER $$

DROP PROCEDURE IF EXISTS GenerateLastYearData$$

CREATE PROCEDURE GenerateLastYearData()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE rnd_plane INT;
    DECLARE rnd_month INT;
    DECLARE flight_id_new INT;
    DECLARE order_id_new INT;
    DECLARE customer_email VARCHAR(100);
    DECLARE is_long BOOLEAN;
    
    -- לולאה ליצירת 50 טיסות שבוצעו בשנה האחרונה
    WHILE i <= 50 DO
        
        -- הגרלת חודש אחורה (בין 1 ל-12 חודשים אחורה)
        SET rnd_month = FLOOR(1 + (RAND() * 12));
        
        -- החלטה אם הטיסה ארוכה או קצרה (50% סיכוי)
        IF (RAND() > 0.5) THEN
            -- טיסה ארוכה (דורש מטוס גדול 1-10)
            SET rnd_plane = FLOOR(1 + (RAND() * 10));
            SET is_long = TRUE;
            
            INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
            VALUES (
                rnd_plane, 
                'Israel', 'Tel Aviv', 'TLV', 
                'USA', 'New York', 'JFK', 
                DATE_SUB(NOW(), INTERVAL rnd_month MONTH), 
                DATE_ADD(DATE_SUB(NOW(), INTERVAL rnd_month MONTH), INTERVAL 11 HOUR), 
                1000 + FLOOR(RAND()*500), 
                'Landed'
            );
        ELSE
            -- טיסה קצרה (מטוס קטן 11-20)
            SET rnd_plane = FLOOR(11 + (RAND() * 10));
            SET is_long = FALSE;
            
            INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
            VALUES (
                rnd_plane, 
                'Israel', 'Tel Aviv', 'TLV', 
                'Cyprus', 'Larnaca', 'LCA', 
                DATE_SUB(NOW(), INTERVAL rnd_month MONTH), 
                DATE_ADD(DATE_SUB(NOW(), INTERVAL rnd_month MONTH), INTERVAL 1 HOUR), 
                100 + FLOOR(RAND()*100), 
                'Landed'
            );
        END IF;

        SET flight_id_new = LAST_INSERT_ID();
        
        -- === יצירת הזמנות לטיסה זו ===
        -- ניצור 3 הזמנות לכל טיסה כדי לא להעמיס מדי, אבל שיהיה מידע
        
        -- הזמנה 1: לקוח רשום (מחלקת עסקים אם המטוס גדול, אחרת תיירים)
        SET customer_email = CONCAT('reg', FLOOR(1 + (RAND() * 50)), '@mail.com'); -- בוחר לקוח רשום קיים רנדומלי
        
        INSERT INTO Orders (registered_email, total_cost, status) VALUES (customer_email, 0, 'Completed');
        SET order_id_new = LAST_INSERT_ID();
        
        IF (is_long IS TRUE) THEN
            -- מטוס גדול -> יש ביזנס
            INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, registered_email, price)
            VALUES (flight_id_new, rnd_plane, 'Business', 1, 'A', order_id_new, customer_email, 1500);
            UPDATE Orders SET total_cost = 1500 WHERE order_code = order_id_new;
        ELSE
            -- מטוס קטן -> רק אקונומי
            INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, registered_email, price)
            VALUES (flight_id_new, rnd_plane, 'Economy', 1, 'A', order_id_new, customer_email, 200);
            UPDATE Orders SET total_cost = 200 WHERE order_code = order_id_new;
        END IF;

        -- הזמנה 2: לקוח אורח (תיירים)
        SET customer_email = CONCAT('guest', FLOOR(1 + (RAND() * 50)), '@mail.com'); -- בוחר אורח קיים
        
        INSERT INTO Orders (guest_email, total_cost, status) VALUES (customer_email, 0, 'Completed');
        SET order_id_new = LAST_INSERT_ID();
        
        INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, guest_email, price)
        VALUES (flight_id_new, rnd_plane, 'Economy', 5, 'C', order_id_new, customer_email, 400);
        UPDATE Orders SET total_cost = 400 WHERE order_code = order_id_new;

        -- שיבוץ טייסים (כדי למנוע חורים בנתונים, נשבץ טייס רנדומלי)
        INSERT INTO PilotsOnFlights (pilot_id, flight_id) 
        VALUES (CONCAT('6000000', LPAD(FLOOR(1 + RAND() * 10), 2, '0')), flight_id_new);

        SET i = i + 1;
    END WHILE;

END$$

DELIMITER ;

-- הרצת הפרוצדורה
CALL GenerateLastYearData();

-- מחיקת הפרוצדורה בסיום
DROP PROCEDURE GenerateLastYearData;