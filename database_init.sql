-- Initialize database for Hospital Monitoring System
-- This script should be run against the RDS instance to create the initial schema

-- Use the specified database
USE `database-1`;

-- Create Users table
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(64) NOT NULL UNIQUE,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password_hash` VARCHAR(128) NOT NULL,
  `first_name` VARCHAR(64) NOT NULL,
  `last_name` VARCHAR(64) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'nurse',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `last_login` DATETIME,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create User Sessions table
CREATE TABLE IF NOT EXISTS `user_sessions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `session_id` VARCHAR(128) NOT NULL UNIQUE,
  `ip_address` VARCHAR(45),
  `user_agent` VARCHAR(255),
  `login_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_activity` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
);

-- Create Patients table
CREATE TABLE IF NOT EXISTS `patients` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `first_name` VARCHAR(64) NOT NULL,
  `last_name` VARCHAR(64) NOT NULL,
  `date_of_birth` DATE NOT NULL,
  `gender` VARCHAR(10) NOT NULL,
  `blood_type` VARCHAR(5),
  `phone` VARCHAR(20),
  `email` VARCHAR(120),
  `address` TEXT,
  `admission_date` DATE NOT NULL,
  `doctor_id` INT,
  `height` FLOAT,
  `weight` FLOAT,
  `allergies` TEXT,
  `medical_history` TEXT,
  `current_medications` TEXT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Patient Locations table
CREATE TABLE IF NOT EXISTS `patient_locations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `room_number` VARCHAR(10) NOT NULL,
  `bed_number` VARCHAR(10),
  `department` VARCHAR(50),
  `start_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end_time` DATETIME,
  `is_current` BOOLEAN NOT NULL DEFAULT TRUE,
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE
);

-- Create Patient Vital Signs table
CREATE TABLE IF NOT EXISTS `patient_vital_signs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `heart_rate` INT,
  `bp_systolic` INT,
  `bp_diastolic` INT,
  `respiratory_rate` INT,
  `spo2` FLOAT,
  `temperature` FLOAT,
  `blood_glucose` FLOAT,
  `recorded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `recorded_by` INT,
  `anomaly_score` FLOAT DEFAULT 0,
  `is_anomaly` BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`recorded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
);

-- Create Patient Medical History table
CREATE TABLE IF NOT EXISTS `patient_medical_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `entry_type` VARCHAR(20) NOT NULL,
  `entry_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `description` TEXT NOT NULL,
  `recorded_by` INT,
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`recorded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
);

-- Create Emergency Contacts table
CREATE TABLE IF NOT EXISTS `emergency_contacts` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `name` VARCHAR(128) NOT NULL,
  `relationship` VARCHAR(64),
  `phone` VARCHAR(20) NOT NULL,
  `address` TEXT,
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE
);

-- Create an initial admin user (password: admin)
-- In production, change this password immediately!
INSERT INTO `users` (`username`, `email`, `password_hash`, `first_name`, `last_name`, `role`) 
VALUES ('admin', 'admin@hospital.com', '$2b$12$lW.reQiB5JXivrL0g.MQPObAzGrOQRY/S89Yl5YS8vw5heXjUz1lW', 'System', 'Administrator', 'admin');

-- Create sample patients (optional)
INSERT INTO `patients` (`first_name`, `last_name`, `date_of_birth`, `gender`, `blood_type`, `admission_date`)
VALUES 
('John', 'Doe', '1975-05-15', 'male', 'A+', CURDATE()),
('Jane', 'Smith', '1982-09-23', 'female', 'O-', CURDATE()),
('Robert', 'Johnson', '1968-11-03', 'male', 'B+', CURDATE());

-- Add sample locations for patients
INSERT INTO `patient_locations` (`patient_id`, `room_number`, `bed_number`, `department`)
VALUES 
(1, '101', 'A', 'Cardiology'),
(2, '102', 'B', 'General'),
(3, '103', 'A', 'Pulmonology');