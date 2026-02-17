-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    weight REAL,
    height REAL,
    activity_level VARCHAR(20),
    dietary_goal VARCHAR(50),
    health_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User food logs
CREATE TABLE IF NOT EXISTS user_food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_name VARCHAR(200) NOT NULL,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meal_type VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    preferred_cuisines TEXT,
    allergies TEXT,
    disliked_foods TEXT,
    favorite_foods TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Food database
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    cuisine VARCHAR(50),
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL,
    fiber REAL,
    sugar REAL,
    prep_time INTEGER,
    complexity VARCHAR(20),
    health_score REAL,
    ingredients TEXT,
    allergens TEXT,
    meal_type VARCHAR(20)
);

-- Create indexes for performance
CREATE INDEX idx_user_food_logs_user_id ON user_food_logs(user_id);
CREATE INDEX idx_user_food_logs_timestamp ON user_food_logs(timestamp);
CREATE INDEX idx_foods_category ON foods(category);
CREATE INDEX idx_foods_meal_type ON foods(meal_type);