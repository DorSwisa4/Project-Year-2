Drop Database if exists airlinedb;
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
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
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

USE AirlineDB;

-- ==========================================================
-- 3. DATA POPULATION
-- ==========================================================

-- --- Requirement 3: Create exactly 3 specific Managers (Tweak 4) ---
-- Phone numbers format fixed (Tweak 2)
INSERT INTO Managers (id_num, first_name, last_name, phone, city, street, house_number, start_date, password) VALUES
('111111111', 'Dor', 'Jacob Haruv', '0501111111', 'Tel Aviv', 'Rothschild', '1', '2020-01-01', 'admin1'),
('222222222', 'Dor', 'David Swisa', '0502222222', 'Haifa', 'Herzl', '2', '2021-02-01', 'admin2'),
('333333333', 'Eran', 'Daniel Dgani', '0503333333', 'Jerusalem', 'Jaffa', '3', '2019-03-01', 'admin3');

-- --- Requirement 6: Create Planes (Max 15) ---
-- Tweak 6: Total 15 planes. 
-- Tweak 3: Only Boeing, Airbus, Dassault.
-- Planes 1-8: BIG (For long flights)
INSERT INTO Planes (manufacturer, purchase_date, size) VALUES
('Boeing', '2018-01-01', 'Big'), ('Airbus', '2019-05-10', 'Big'),
('Boeing', '2020-03-15', 'Big'), ('Airbus', '2017-11-20', 'Big'),
('Dassault', '2021-01-05', 'Big'), ('Boeing', '2018-06-06', 'Big'),
('Airbus', '2022-01-01', 'Big'), ('Dassault', '2019-09-09', 'Big');

-- Planes 9-15: SMALL (Economy Only)
INSERT INTO Planes (manufacturer, purchase_date, size) VALUES
('Boeing', '2018-01-01', 'Small'), ('Airbus', '2019-05-10', 'Small'),
('Dassault', '2020-03-15', 'Small'), ('Airbus', '2017-11-20', 'Small'),
('Dassault', '2021-01-05', 'Small'), ('Boeing', '2018-06-06', 'Small'),
('Airbus', '2022-01-01', 'Small');

-- --- Configure Classes and Seats ---
-- BIG PLANES (1-8): Business (4x5=20 seats) + Economy (6x20=120 seats). Total 140.
INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats)
SELECT plane_id, 'Business', 4, 5, 20 FROM Planes WHERE size='Big';

INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats)
SELECT plane_id, 'Economy', 6, 20, 120 FROM Planes WHERE size='Big';

-- SMALL PLANES (9-15): Economy Only (6x20=120 seats). Total 120.
INSERT INTO Classes (plane_id, class_type, num_columns, num_rows, total_seats)
SELECT plane_id, 'Economy', 6, 20, 120 FROM Planes WHERE size='Small';

-- --- Generating ACTUAL SEATS ---
DROP TABLE IF EXISTS TempNums;
CREATE TEMPORARY TABLE TempNums (n INT);
INSERT INTO TempNums VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10),(11),(12),(13),(14),(15),(16),(17),(18),(19),(20),(21),(22),(23),(24),(25);

DROP TABLE IF EXISTS TempCols;
CREATE TEMPORARY TABLE TempCols (c CHAR(1), idx INT);
INSERT INTO TempCols VALUES ('A',1),('B',2),('C',3),('D',4),('E',5),('F',6);

-- Tweak 1: Business Price = 100
INSERT INTO Seats (plane_id, class_type, row_num, col_num, price_supplement)
SELECT p.plane_id, 'Business', tn.n, tc.c, 100.00
FROM Planes p
JOIN TempNums tn ON tn.n <= 5
JOIN TempCols tc ON tc.idx <= 4
WHERE p.size = 'Big';

-- Tweak 1: Economy Price = 0
INSERT INTO Seats (plane_id, class_type, row_num, col_num, price_supplement)
SELECT p.plane_id, 'Economy', tn.n + 5, tc.c, 0.00
FROM Planes p
JOIN TempNums tn ON tn.n <= 20
JOIN TempCols tc ON tc.idx <= 6
WHERE p.size = 'Big';

-- Tweak 1: Economy Price = 0 (Small planes)
INSERT INTO Seats (plane_id, class_type, row_num, col_num, price_supplement)
SELECT p.plane_id, 'Economy', tn.n, tc.c, 0.00
FROM Planes p
JOIN TempNums tn ON tn.n <= 20
JOIN TempCols tc ON tc.idx <= 6
WHERE p.size = 'Small';

-- --- Requirement 5: Create Crew (Limited) ---
DELIMITER $$
CREATE PROCEDURE FillCrew()
BEGIN
    DECLARE i INT DEFAULT 1;
    -- Tweak 6: Max 50 Attendants
    WHILE i <= 50 DO
        INSERT INTO Attendants (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training)
        VALUES (
            CONCAT('4000000', LPAD(i, 2, '0')), 
            CONCAT('Attendant', i), 
            'Worker', 
            -- Tweak 2: 10 digits, no dashes
            CONCAT('05200000', LPAD(i, 2, '0')), 
            'Tel Aviv', 'Street', '1', CURDATE(), 
            IF(i % 2 = 0, 1, 0)
        );
        SET i = i + 1;
    END WHILE;
    
    SET i = 1;
    -- Tweak 6: Max 30 Pilots
    WHILE i <= 30 DO
        INSERT INTO Pilots (id_num, first_name, last_name, phone, city, street, house_number, start_date, long_flight_training)
        VALUES (
            CONCAT('6000000', LPAD(i, 2, '0')), 
            CONCAT('Pilot', i), 
            'Flyer', 
            -- Tweak 2: 10 digits, no dashes
            CONCAT('05400000', LPAD(i, 2, '0')), 
            'Haifa', 'Ave', '1', CURDATE(), 
            IF(i % 2 = 0, 1, 0)
        );
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;
CALL FillCrew();
DROP PROCEDURE FillCrew;


-- --- Operating Lines ---
-- Tweak 7: Add routes not connected to Israel, maintain symmetry
INSERT INTO OperatingLines VALUES 
-- Israel Routes
('Israel', 'Tel Aviv', 'TLV', 'USA', 'New York', 'JFK', '11:00:00'),
('USA', 'New York', 'JFK', 'Israel', 'Tel Aviv', 'TLV', '11:00:00'),
('Israel', 'Tel Aviv', 'TLV', 'Thailand', 'Bangkok', 'BKK', '10:30:00'),
('Thailand', 'Bangkok', 'BKK', 'Israel', 'Tel Aviv', 'TLV', '10:30:00'),
('Israel', 'Tel Aviv', 'TLV', 'UK', 'London', 'LHR', '05:30:00'),
('UK', 'London', 'LHR', 'Israel', 'Tel Aviv', 'TLV', '05:30:00'),
('Israel', 'Tel Aviv', 'TLV', 'France', 'Paris', 'CDG', '04:50:00'),
('France', 'Paris', 'CDG', 'Israel', 'Tel Aviv', 'TLV', '04:50:00'),

-- Non-Israel Routes (New)
('UK', 'London', 'LHR', 'USA', 'New York', 'JFK', '07:30:00'),
('USA', 'New York', 'JFK', 'UK', 'London', 'LHR', '07:30:00'),
('France', 'Paris', 'CDG', 'Greece', 'Athens', 'ATH', '03:15:00'),
('Greece', 'Athens', 'ATH', 'France', 'Paris', 'CDG', '03:15:00');


-- --- Customers ---
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
        -- Tweak 2: Phone format 10 digits
        INSERT INTO RegisteredPhones VALUES (
            CONCAT('reg', i, '@mail.com'),
            CONCAT('050', LPAD(i, 7, '0')) 
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
        -- Insert Guest Phones immediately
        INSERT IGNORE INTO GuestPhones VALUES (CONCAT('guest', i, '@mail.com'), CONCAT('055', LPAD(i, 7, '0')));
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;
CALL FillCustomers();
DROP PROCEDURE FillCustomers;


-- ==========================================================
-- REAL LIFE SIMULATION: FLIGHTS & ORDERS
-- ==========================================================
-- This procedure generates flights (past/future) and fills them with random orders
-- respecting capacity limits and plane sizes.

DELIMITER $$
CREATE PROCEDURE GenerateTraffic()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE rnd_plane INT;
    DECLARE is_long BOOLEAN;
    DECLARE flight_date DATETIME;
    DECLARE flight_status VARCHAR(20);
    DECLARE new_flight_id INT;
    DECLARE max_seats INT;
    DECLARE seats_sold INT;
    DECLARE seats_to_sell INT;
    DECLARE j INT;
    DECLARE ticket_type INT; -- 1=Business, 2=Economy
    DECLARE rnd_customer_email VARCHAR(100);
    DECLARE is_reg INT;
    DECLARE new_order_id INT;
    DECLARE flight_base_price DECIMAL(10,2);
    
    -- Create 60 Flights
    WHILE i <= 60 DO
        -- 1. Pick Plane (1-15)
        SET rnd_plane = FLOOR(1 + (RAND() * 15));
        
        -- 2. Determine if Long Flight (Planes 1-8 are Big/Long)
        IF rnd_plane <= 8 THEN
            SET is_long = TRUE;
            SET max_seats = 140; -- 20 Biz + 120 Eco
        ELSE
            SET is_long = FALSE;
            SET max_seats = 120; -- 120 Eco
        END IF;

        -- 3. Determine Date (Between 2 months ago and 2 months future)
        SET flight_date = DATE_ADD(NOW(), INTERVAL FLOOR(-60 + (RAND() * 120)) DAY);
        
        IF flight_date < NOW() THEN
            SET flight_status = 'Landed';
        ELSE
            SET flight_status = 'Active';
        END IF;

        -- 4. Create Flight based on plane type (Long/Short)
        IF is_long THEN
            -- Long Flight (e.g., TLV-JFK or LHR-JFK)
             IF RAND() > 0.5 THEN
                INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
                VALUES (rnd_plane, 'Israel', 'Tel Aviv', 'TLV', 'USA', 'New York', 'JFK', flight_date, DATE_ADD(flight_date, INTERVAL 11 HOUR), 1200, flight_status);
             ELSE
                INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
                VALUES (rnd_plane, 'UK', 'London', 'LHR', 'USA', 'New York', 'JFK', flight_date, DATE_ADD(flight_date, INTERVAL 8 HOUR), 900, flight_status);
             END IF;
        ELSE
            -- Short Flight (e.g., TLV-LHR, TLV-CDG, CDG-ATH)
            SET flight_base_price = 300;
            IF RAND() < 0.33 THEN
                INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
                VALUES (rnd_plane, 'Israel', 'Tel Aviv', 'TLV', 'UK', 'London', 'LHR', flight_date, DATE_ADD(flight_date, INTERVAL 5 HOUR), flight_base_price, flight_status);
            ELSEIF RAND() < 0.66 THEN
                INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
                VALUES (rnd_plane, 'France', 'Paris', 'CDG', 'Greece', 'Athens', 'ATH', flight_date, DATE_ADD(flight_date, INTERVAL 3 HOUR), flight_base_price, flight_status);
            ELSE
                 INSERT INTO Flights (plane_id, src_country, src_city, src_airport, dst_country, dst_city, dst_airport, departure_time, landing_time, base_price, status)
                VALUES (rnd_plane, 'Israel', 'Tel Aviv', 'TLV', 'France', 'Paris', 'CDG', flight_date, DATE_ADD(flight_date, INTERVAL 4 HOUR), flight_base_price, flight_status);
            END IF;
        END IF;

        SET new_flight_id = LAST_INSERT_ID();

        -- 5. Assign Crew (Respect limits: 30 pilots, 50 attendants)
        -- Assign 2 Pilots (Random from 1-30)
        INSERT IGNORE INTO PilotsOnFlights (pilot_id, flight_id) VALUES 
        (CONCAT('6000000', LPAD(FLOOR(1 + RAND() * 30), 2, '0')), new_flight_id),
        (CONCAT('6000000', LPAD(FLOOR(1 + RAND() * 30), 2, '0')), new_flight_id);

        -- Assign 3 Attendants (Random from 1-50)
        INSERT IGNORE INTO AttendantsOnFlights (attendant_id, flight_id) VALUES 
        (CONCAT('4000000', LPAD(FLOOR(1 + RAND() * 50), 2, '0')), new_flight_id),
        (CONCAT('4000000', LPAD(FLOOR(1 + RAND() * 50), 2, '0')), new_flight_id),
        (CONCAT('4000000', LPAD(FLOOR(1 + RAND() * 50), 2, '0')), new_flight_id);

        -- 6. Generate Orders/Tickets (Tweak 5: Respect Capacity)
        -- Determine how many tickets to sell (0 up to Max Seats)
        SET seats_to_sell = FLOOR(RAND() * max_seats);
        SET j = 1;

        WHILE j <= seats_to_sell DO
            SET is_reg = FLOOR(RAND() * 2); -- 0 or 1
            
            -- Pick Customer
            IF is_reg = 1 THEN
                 SET rnd_customer_email = CONCAT('reg', FLOOR(1 + (RAND() * 100)), '@mail.com');
                 INSERT INTO Orders (registered_email, total_cost, status) VALUES (rnd_customer_email, 0, IF(flight_status='Landed', 'Completed', 'Active'));
            ELSE
                 SET rnd_customer_email = CONCAT('guest', FLOOR(1 + (RAND() * 100)), '@mail.com');
                 INSERT INTO Orders (guest_email, total_cost, status) VALUES (rnd_customer_email, 0, IF(flight_status='Landed', 'Completed', 'Active'));
            END IF;
            
            SET new_order_id = LAST_INSERT_ID();

            -- Seat Assignment Logic (Simplified to avoid collision)
            -- We assume simple filling: if j <= 20 and plane is big, it's business. Else Economy.
            -- Note: Real logic would require checking seat availability, but for bulk insert we approximate.
            
            IF is_long AND j <= 20 THEN
                -- Business Ticket (Price + 100)
                INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, registered_email, guest_email, price)
                VALUES (new_flight_id, rnd_plane, 'Business', CEIL(j/4), CHAR(65 + ((j-1)%4)), new_order_id, 
                        IF(is_reg=1, rnd_customer_email, NULL), IF(is_reg=0, rnd_customer_email, NULL), 
                        (SELECT base_price FROM Flights WHERE flight_id=new_flight_id) + 100);
                        
                UPDATE Orders SET total_cost = (SELECT base_price FROM Flights WHERE flight_id=new_flight_id) + 100 WHERE order_code = new_order_id;
            ELSE
                -- Economy Ticket (Price + 0)
                -- Row logic approximation for bulk insert
                INSERT INTO Tickets (flight_id, plane_id, class_type, row_num, col_num, order_code, registered_email, guest_email, price)
                VALUES (new_flight_id, rnd_plane, 'Economy', 6 + FLOOR(j/6), CHAR(65 + ((j-1)%6)), new_order_id, 
                        IF(is_reg=1, rnd_customer_email, NULL), IF(is_reg=0, rnd_customer_email, NULL), 
                        (SELECT base_price FROM Flights WHERE flight_id=new_flight_id));
                
                UPDATE Orders SET total_cost = (SELECT base_price FROM Flights WHERE flight_id=new_flight_id) WHERE order_code = new_order_id;
            END IF;

            SET j = j + 1;
        END WHILE;

        -- If we sold max seats, mark flight as full
        IF seats_to_sell >= max_seats AND flight_status = 'Active' THEN
            UPDATE Flights SET status = 'Full' WHERE flight_id = new_flight_id;
        END IF;

        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL GenerateTraffic();
DROP PROCEDURE GenerateTraffic;

-- Cleanup Helpers
DROP TABLE TempNums;
DROP TABLE TempCols;