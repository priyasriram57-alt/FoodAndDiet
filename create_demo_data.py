from app import app, db, User, UserFoodLog, UserPreferences
from deep_learning.food_recommender import FoodRecommender
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import json

def create_rich_food_dataset():
    """Create a rich food dataset for demo purposes"""
    print("Creating rich food dataset...")
    
    foods = [
        # Breakfast Items
        {"name": "Oatmeal with Berries", "category": "Breakfast", "meal_type": "breakfast", "cuisine": "American", "calories": 350, "protein": 12, "fat": 6, "carbs": 60, "health_score": 0.9, "prep_time": 10},
        {"name": "Scrambled Eggs on Toast", "category": "Breakfast", "meal_type": "breakfast", "cuisine": "American", "calories": 400, "protein": 20, "fat": 22, "carbs": 30, "health_score": 0.8, "prep_time": 15},
        {"name": "Greek Yogurt Parfait", "category": "Breakfast", "meal_type": "breakfast", "cuisine": "Mediterranean", "calories": 300, "protein": 15, "fat": 5, "carbs": 45, "health_score": 0.9, "prep_time": 5},
        {"name": "Avocado Toast", "category": "Breakfast", "meal_type": "breakfast", "cuisine": "Australian", "calories": 320, "protein": 8, "fat": 20, "carbs": 35, "health_score": 0.9, "prep_time": 10},
        {"name": "Protein Pancakes", "category": "Breakfast", "meal_type": "breakfast", "cuisine": "American", "calories": 450, "protein": 25, "fat": 10, "carbs": 55, "health_score": 0.7, "prep_time": 20},
        
        # Lunch Items
        {"name": "Grilled Chicken Salad", "category": "Lunch", "meal_type": "lunch", "cuisine": "American", "calories": 450, "protein": 40, "fat": 20, "carbs": 15, "health_score": 0.9, "prep_time": 20},
        {"name": "Quinoa Buddha Bowl", "category": "Lunch", "meal_type": "lunch", "cuisine": "Mediterranean", "calories": 500, "protein": 18, "fat": 18, "carbs": 65, "health_score": 1, "prep_time": 25},
        {"name": "Turkey Wrap", "category": "Lunch", "meal_type": "lunch", "cuisine": "American", "calories": 420, "protein": 25, "fat": 12, "carbs": 45, "health_score": 0.7, "prep_time": 10},
        {"name": "Lentil Soup", "category": "Lunch", "meal_type": "lunch", "cuisine": "Mediterranean", "calories": 300, "protein": 15, "fat": 5, "carbs": 45, "health_score": 0.9, "prep_time": 30},
        {"name": "Tuna Sandwich", "category": "Lunch", "meal_type": "lunch", "cuisine": "American", "calories": 400, "protein": 28, "fat": 15, "carbs": 35, "health_score": 0.7, "prep_time": 10},
        {"name": "Sushi Roll Set", "category": "Lunch", "meal_type": "lunch", "cuisine": "Japanese", "calories": 480, "protein": 18, "fat": 10, "carbs": 75, "health_score": 0.8, "prep_time": 15},
        {"name": "Caesar Salad", "category": "Lunch", "meal_type": "lunch", "cuisine": "Italian", "calories": 350, "protein": 15, "fat": 25, "carbs": 10, "health_score": 0.6, "prep_time": 15},

        # Dinner Items
        {"name": "Salmon with Asparagus", "category": "Dinner", "meal_type": "dinner", "cuisine": "International", "calories": 550, "protein": 35, "fat": 30, "carbs": 10, "health_score": 0.9, "prep_time": 25},
        {"name": "Chicken Stir Fry", "category": "Dinner", "meal_type": "dinner", "cuisine": "Asian", "calories": 480, "protein": 30, "fat": 15, "carbs": 55, "health_score": 0.8, "prep_time": 30},
        {"name": "Vegetable Curry with Rice", "category": "Dinner", "meal_type": "dinner", "cuisine": "Indian", "calories": 520, "protein": 12, "fat": 20, "carbs": 70, "health_score": 0.8, "prep_time": 40},
        {"name": "Beef Tacos", "category": "Dinner", "meal_type": "dinner", "cuisine": "Mexican", "calories": 600, "protein": 30, "fat": 30, "carbs": 45, "health_score": 0.6, "prep_time": 30},
        {"name": "Pasta Primavera", "category": "Dinner", "meal_type": "dinner", "cuisine": "Italian", "calories": 580, "protein": 15, "fat": 20, "carbs": 80, "health_score": 0.7, "prep_time": 25},
        {"name": "Grilled Steak with Veggies", "category": "Dinner", "meal_type": "dinner", "cuisine": "American", "calories": 700, "protein": 50, "fat": 40, "carbs": 15, "health_score": 0.8, "prep_time": 30},
        
        # Snacks
        {"name": "Apple with Almond Butter", "category": "Snack", "meal_type": "snack", "cuisine": "American", "calories": 200, "protein": 4, "fat": 12, "carbs": 22, "health_score": 0.9, "prep_time": 5},
        {"name": "Protein Bar", "category": "Snack", "meal_type": "snack", "cuisine": "American", "calories": 250, "protein": 20, "fat": 8, "carbs": 25, "health_score": 0.7, "prep_time": 0},
        {"name": "Trail Mix", "category": "Snack", "meal_type": "snack", "cuisine": "American", "calories": 300, "protein": 8, "fat": 20, "carbs": 25, "health_score": 0.8, "prep_time": 0},
        {"name": "Carrot Sticks with Hummus", "category": "Snack", "meal_type": "snack", "cuisine": "Mediterranean", "calories": 150, "protein": 5, "fat": 8, "carbs": 15, "health_score": 0.9, "prep_time": 5},
        {"name": "Dark Chocolate", "category": "Snack", "meal_type": "snack", "cuisine": "International", "calories": 180, "protein": 2, "fat": 12, "carbs": 15, "health_score": 0.6, "prep_time": 0},
        {"name": "Banana", "category": "Snack", "meal_type": "snack", "cuisine": "Tropical", "calories": 105, "protein": 1.3, "fat": 0.4, "carbs": 27, "health_score": 1.0, "prep_time": 0},
    ]
    
    # Add food_id
    for i, food in enumerate(foods, 1):
        food['food_id'] = i
        
    df = pd.DataFrame(foods)
    
    # Ensure directory exists
    os.makedirs('deep_learning/data', exist_ok=True)
    df.to_csv('deep_learning/data/food_dataset.csv', index=False)
    print(f"Created dataset with {len(df)} items.")
    return df

def seed_user_history():
    """Seed user history for dashboard demo"""
    print("Seeding user history...")
    
    with app.app_context():
        # Get test user
        user = User.query.filter_by(username='testuser').first()
        if not user:
            print("User 'testuser' not found. Please run seed_db.py first.")
            return

        # Update user preferences to ensure valid JSON
        pref = UserPreferences.query.filter_by(user_id=user.id).first()
        if pref:
            # Ensure valid JSON
            try:
                if not pref.preferred_cuisines or not pref.preferred_cuisines.startswith('['):
                    pref.preferred_cuisines = json.dumps([])
                if not pref.allergies or not pref.allergies.startswith('['):
                    pref.allergies = json.dumps([])
                if not pref.disliked_foods or not pref.disliked_foods.startswith('['):
                    pref.disliked_foods = json.dumps([])
                if not pref.favorite_foods or not pref.favorite_foods.startswith('['):
                    pref.favorite_foods = json.dumps([])
                db.session.commit()
            except:
                pass

        # Clear existing logs for a clean demo
        UserFoodLog.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # Add random logs for the last 3 days
        today = datetime.utcnow()
        foods = pd.read_csv('deep_learning/data/food_dataset.csv').to_dict('records')
        
        history_logs = []
        
        # Log food for last 3 days
        for i in range(3):
            date = today - timedelta(days=i)
            
            # Breakfast
            bf = next((f for f in foods if f['category'] == 'Breakfast'), None)
            if bf:
                history_logs.append(UserFoodLog(
                    user_id=user.id,
                    food_name=bf['name'],
                    calories=bf['calories'],
                    protein=bf['protein'],
                    carbs=bf['carbs'],
                    fat=bf['fat'],
                    meal_type='breakfast',
                    timestamp=date.replace(hour=8, minute=30)
                ))
            
            # Lunch
            lunch = next((f for f in foods if f['category'] == 'Lunch'), None)
            if lunch:
                history_logs.append(UserFoodLog(
                    user_id=user.id,
                    food_name=lunch['name'],
                    calories=lunch['calories'],
                    protein=lunch['protein'],
                    carbs=lunch['carbs'],
                    fat=lunch['fat'],
                    meal_type='lunch',
                    timestamp=date.replace(hour=13, minute=0)
                ))
                
            # Dinner
            dinner = next((f for f in foods if f['category'] == 'Dinner'), None)
            if dinner:
                history_logs.append(UserFoodLog(
                    user_id=user.id,
                    food_name=dinner['name'],
                    calories=dinner['calories'],
                    protein=dinner['protein'],
                    carbs=dinner['carbs'],
                    fat=dinner['fat'],
                    meal_type='dinner',
                    timestamp=date.replace(hour=19, minute=0)
                ))
        
        # Add them to session
        for log in history_logs:
            db.session.add(log)
            
        db.session.commit()
        print(f"Added {len(history_logs)} food logs for history.")

if __name__ == '__main__':
    create_rich_food_dataset()
    seed_user_history()
