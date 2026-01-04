-- 1. Create Database
DROP DATABASE IF EXISTS campus_ar_db;
CREATE DATABASE campus_ar_db;
USE campus_ar_db;

-- 2. Create Buildings Table
CREATE TABLE Buildings (
    building_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL
);

-- 3. Create Rooms Table
CREATE TABLE Rooms (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    building_id INT,
    name VARCHAR(100) NOT NULL,
    room_number VARCHAR(20),
    FOREIGN KEY (building_id) REFERENCES Buildings(building_id)
);

-- 4. Create Faculty Table
CREATE TABLE Faculty (
    faculty_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    office_room_id INT,
    FOREIGN KEY (office_room_id) REFERENCES Rooms(room_id)
);

-- 5. Create Events Table
CREATE TABLE Events (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    room_id INT,
    start_time DATETIME,
    end_time DATETIME,
    description TEXT,
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
);

-- 6. Create Markers Table (Linked directly to Room)
CREATE TABLE Markers (
    marker_id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50), 
    room_id INT,
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
);

-- --- INSERT DUMMY DATA ---
INSERT INTO Buildings (name) VALUES ('ISE Department');
INSERT INTO Rooms (building_id,name, room_number) VALUES (1,'ISE Seminar Hall', '001'); 
INSERT INTO Markers (type, room_id) VALUES ('hall_entry', 1);
INSERT INTO Events (name, room_id, start_time, end_time, description) 
VALUES ('DBMS Guest Talk', 1, NOW(), DATE_ADD(NOW(), INTERVAL 3 HOUR), 'Information about DBMS systems in industry');