import sqlite3
import pandas as pd
import json
from datetime import datetime
from contextlib import contextmanager

class DatabaseHandler:
    def __init__(self, db_path='food_recommendation.db'):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a SQL query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                return cursor.fetchall()
            conn.commit()
    
    def get_user_food_logs(self, user_id, days=7):
        """Get user's food logs for specified days"""
        query = """
        SELECT * FROM user_food_logs 
        WHERE user_id = ? AND date(timestamp) >= date('now', ?)
        ORDER BY timestamp DESC
        """
        params = (user_id, f'-{days} days')
        return self.execute_query(query, params, fetch=True)
    
    def get_user_stats(self, user_id):
        """Get user's nutrition statistics"""
        query = """
        SELECT 
            SUM(calories) as total_calories,
            SUM(protein) as total_protein,
            SUM(carbs) as total_carbs,
            SUM(fat) as total_fat,
            COUNT(*) as meal_count
        FROM user_food_logs 
        WHERE user_id = ? AND date(timestamp) = date('now')
        """
        result = self.execute_query(query, (user_id,), fetch=True)
        return dict(result[0]) if result else {}
    
    def get_foods_by_category(self, category, limit=50):
        """Get foods by category"""
        query = """
        SELECT * FROM foods 
        WHERE category = ? 
        ORDER BY health_score DESC 
        LIMIT ?
        """
        return self.execute_query(query, (category, limit), fetch=True)
    
    def search_foods(self, search_term, limit=20):
        """Search for foods"""
        query = """
        SELECT * FROM foods 
        WHERE name LIKE ? OR ingredients LIKE ?
        ORDER BY health_score DESC 
        LIMIT ?
        """
        search_param = f"%{search_term}%"
        return self.execute_query(query, (search_param, search_param, limit), fetch=True)
    
    def add_food_log(self, user_id, food_data):
        """Add a food log entry"""
        query = """
        INSERT INTO user_food_logs 
        (user_id, food_name, calories, protein, carbs, fat, meal_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user_id,
            food_data['food_name'],
            food_data['calories'],
            food_data.get('protein', 0),
            food_data.get('carbs', 0),
            food_data.get('fat', 0),
            food_data.get('meal_type', 'other')
        )
        self.execute_query(query, params)
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile"""
        fields = []
        params = []
        
        for field, value in profile_data.items():
            if value is not None:
                fields.append(f"{field} = ?")
                params.append(value)
        
        if fields:
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
            params.append(user_id)
            self.execute_query(query, params)
    
    def get_popular_foods(self, user_id=None, limit=10):
        """Get popular foods (most logged by users)"""
        query = """
        SELECT food_name, COUNT(*) as log_count,
               AVG(calories) as avg_calories
        FROM user_food_logs
        GROUP BY food_name
        ORDER BY log_count DESC
        LIMIT ?
        """
        return self.execute_query(query, (limit,), fetch=True)

# Initialize database handler
db_handler = DatabaseHandler()