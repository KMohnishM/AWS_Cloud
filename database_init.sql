SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `patient_medical_history`;
DROP TABLE IF EXISTS `patient_vital_signs`;
DROP TABLE IF EXISTS `patient_locations`;
DROP TABLE IF EXISTS `user_sessions`;
DROP TABLE IF EXISTS `patients`;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;
-- Initialize database for Hospital Monitoring System
-- This script should be run against the RDS instance to create the initial schema

USE `healthcare`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `password_hash` VARCHAR(256) NOT NULL,
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `role` VARCHAR(20) NOT NULL,
  `department` VARCHAR(50),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `last_login` DATETIME,
  `is_active` BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS `user_sessions` (
  `session_id` VARCHAR(128) PRIMARY KEY,
  `user_id` INT NOT NULL,
  `ip_address` VARCHAR(45),
  `user_agent` VARCHAR(256),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `expires_at` DATETIME,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `patients` (
  `patient_id` INT AUTO_INCREMENT PRIMARY KEY,
  `mrn` VARCHAR(20) NOT NULL UNIQUE,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `date_of_birth` DATE NOT NULL,
  `gender` VARCHAR(10) NOT NULL,
  `blood_type` VARCHAR(3),
  `address` VARCHAR(255),
  `phone` VARCHAR(20),
  `email` VARCHAR(100),
  `emergency_contact` VARCHAR(100),
  `emergency_phone` VARCHAR(20),
  `admission_date` DATETIME,
  `discharge_date` DATETIME,
  `status` VARCHAR(20) NOT NULL,
  `notes` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `patient_locations` (
  `location_id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `hospital` VARCHAR(50) NOT NULL,
  `department` VARCHAR(50) NOT NULL,
  `ward` VARCHAR(50) NOT NULL,
  `bed` VARCHAR(20),
  `assigned_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `active` BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `patient_vital_signs` (
  `vital_id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `heart_rate` FLOAT,
  `spo2` FLOAT,
  `bp_systolic` FLOAT,
  `bp_diastolic` FLOAT,
  `respiratory_rate` FLOAT,
  `temperature` FLOAT,
  `etco2` FLOAT,
  `recorded_by` INT,
  `recorded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE,
  FOREIGN KEY (`recorded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS `patient_medical_history` (
  `history_id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `condition` VARCHAR(100) NOT NULL,
  `diagnosis_date` DATE,
  `treatment` TEXT,
  `medication` VARCHAR(255),
  `notes` TEXT,
  `recorded_by` INT,
  `recorded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE,
  FOREIGN KEY (`recorded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
);


INSERT INTO `users` (`username`, `email`, `password_hash`, `first_name`, `last_name`, `role`, `is_active`)
VALUES ('admin', 'admin@hospital.com', '$2b$12$lW.reQiB5JXivrL0g.MQPObAzGrOQRY/S89Yl5YS8vw5heXjUz1lW', 'System', 'Administrator', 'admin', TRUE);

INSERT INTO `patients` (`mrn`, `first_name`, `last_name`, `date_of_birth`, `gender`, `blood_type`, `admission_date`, `status`)
VALUES 
('MRN001', 'John', 'Doe', '1975-05-15', 'male', 'A+', CURDATE(), 'admitted'),
('MRN002', 'Jane', 'Smith', '1982-09-23', 'female', 'O-', CURDATE(), 'admitted'),
('MRN003', 'Robert', 'Johnson', '1968-11-03', 'male', 'B+', CURDATE(), 'admitted');

INSERT INTO `patient_locations` (`patient_id`, `hospital`, `department`, `ward`, `bed`)
VALUES 
(1, 'Main Hospital', 'Cardiology', 'Ward A', '101A'),
(2, 'Main Hospital', 'General', 'Ward B', '102B'),
(3, 'Main Hospital', 'Pulmonology', 'Ward A', '103A');