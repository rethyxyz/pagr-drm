-- Create the DRM database
CREATE DATABASE IF NOT EXISTS pagr_drm;

USE pagr_drm;

-- Table to store DRM keys
CREATE TABLE drm_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drm_key VARCHAR(128) NOT NULL UNIQUE,
    max_devices INT NOT NULL DEFAULT 1
);

-- Table to store device registrations
CREATE TABLE registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drm_key VARCHAR(64) NOT NULL,
    hardware_id VARCHAR(64) NOT NULL,
    registration_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (drm_key) REFERENCES drm_keys(drm_key)
);

-- Indexes for faster lookup
CREATE INDEX idx_drm_key ON registrations(drm_key);
CREATE INDEX idx_hardware_id ON registrations(hardware_id);

-- USED TO ADD NEW DRM KEYS INTO THE DATABASE.
