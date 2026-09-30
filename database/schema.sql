-- Database Schema for Human-Centered AI in Smart Farming

CREATE DATABASE IF NOT EXISTS smart_farming_db;
USE smart_farming_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(100),
    farm_size DECIMAL(10, 2), -- in Acres/Hectares
    soil_type VARCHAR(50),
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Farms Table
CREATE TABLE IF NOT EXISTS farms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    farm_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    total_area DECIMAL(10, 2),
    soil_type VARCHAR(50),
    irrigation_type VARCHAR(50),
    current_crop VARCHAR(50),
    previous_crop VARCHAR(50),
    farming_experience INT, -- in years
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Digital Twin Fields Table
CREATE TABLE IF NOT EXISTS fields (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    crop VARCHAR(50),
    area DECIMAL(10, 2),
    soil_moisture DECIMAL(5, 2),
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    irrigation_status VARCHAR(50) DEFAULT 'Optimal',
    growth_stage VARCHAR(50) DEFAULT 'Vegetative',
    health_status VARCHAR(50) DEFAULT 'Healthy',
    data_source VARCHAR(20) DEFAULT 'manual', -- manual or sensor_demo
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE
);

-- 4. Soil Records Table
CREATE TABLE IF NOT EXISTS soil_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nitrogen DECIMAL(8, 2),
    phosphorus DECIMAL(8, 2),
    potassium DECIMAL(8, 2),
    ph_level DECIMAL(4, 2),
    moisture DECIMAL(5, 2),
    soil_type VARCHAR(50),
    health_status VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. AI Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    prediction_type VARCHAR(50) DEFAULT 'crop_recommendation',
    input_data JSON, -- stores N, P, K, temp, humidity, pH, rainfall
    predicted_crop VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(5, 2) NOT NULL, -- e.g. 95.50%
    reliability_level VARCHAR(20) DEFAULT 'High', -- High, Medium, Low
    top_alternatives JSON, -- e.g. ["Maize", "Cotton", "Jute"]
    feature_influences JSON, -- e.g. {"Rainfall": "High", "Humidity": "High"}
    simple_explanation TEXT,
    technical_explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Recommendations Table (Fertilizer & Irrigation)
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    rec_type VARCHAR(50), -- fertilizer or irrigation
    crop VARCHAR(50),
    suggested_action TEXT,
    reasoning TEXT,
    advisory_notice TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Farmer Feedback Table (Human-Centered AI Loop)
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    prediction_id INT,
    usefulness VARCHAR(20) NOT NULL, -- Yes, Partially, No
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE SET NULL
);

-- 8. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'Medium', -- Low, Medium, High
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 9. Disease Predictions Table
CREATE TABLE IF NOT EXISTS disease_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image_filename VARCHAR(255),
    predicted_disease VARCHAR(100),
    confidence_score DECIMAL(5, 2),
    health_status VARCHAR(50),
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. Weather Records Table
CREATE TABLE IF NOT EXISTS weather_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    rain_probability DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    forecast_summary VARCHAR(255),
    is_live_api BOOLEAN DEFAULT FALSE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
