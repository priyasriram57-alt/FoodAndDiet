import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from datetime import datetime, timedelta
import random

class FoodRecommender:
    def __init__(self, data_path='deep_learning/data/food_dataset.csv'):
        self.food_data = self.load_food_data(data_path)
        self.user_preferences = {}
        self.model = None
        
    def load_food_data(self, path):
        """Load and prepare food dataset"""
        try:
            df = pd.read_csv(path)
        except FileNotFoundError:
            
            # Create sample dataset if file doesn't exist
            df = self.create_sample_dataset()
            df.to_csv(path, index=False)
        
        return df

    def create_sample_dataset(self):
        """Create a sample food dataset"""
        categories = ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert', 'Salad', 'Soup', 'Main Course']
        cuisines = ['Italian', 'Indian', 'Chinese', 'Mexican', 'Mediterranean', 'American', 'Japanese']
        
        data = []
        for i in range(1000):
            food = {
                'food_id': i,
                'name': f'Food Item {i}',
                'category': random.choice(categories),
                'cuisine': random.choice(cuisines),
                'calories': random.randint(50, 800),
                'protein': round(random.uniform(1, 40), 1),
                'carbs': round(random.uniform(10, 100), 1),
                'fat': round(random.uniform(1, 50), 1),
                'fiber': round(random.uniform(0, 15), 1),
                'sugar': round(random.uniform(0, 50), 1),
                'prep_time': random.randint(5, 120),
                'complexity': random.choice(['easy', 'medium', 'hard']),
                'health_score': round(random.uniform(0.3, 1.0), 2),
                'ingredients': ['ingredient1', 'ingredient2', 'ingredient3'],
                'allergens': random.choice(['none', 'dairy', 'nuts', 'gluten', 'seafood']),
                'meal_type': random.choice(['breakfast', 'lunch', 'dinner', 'snack'])
            }
            data.append(food)
        
        return pd.DataFrame(data)
    
    def get_recommendations(self, user_id, user_data, meal_type='all', preferences=None, top_n=10):
        """Get personalized food recommendations"""
        
        # Filter by meal type if specified
        if meal_type != 'all':
            filtered_foods = self.food_data[self.food_data['meal_type'] == meal_type]
        else:
            filtered_foods = self.food_data
        
        # Apply dietary restrictions
        if preferences and 'allergies' in preferences:
            filtered_foods = self.filter_allergies(filtered_foods, preferences['allergies'])
        
        # Apply disliked foods filter
        if preferences and 'disliked_foods' in preferences:
            filtered_foods = self.filter_disliked_foods(filtered_foods, preferences['disliked_foods'])
        
        # Calculate scores for each food
        recommendations = []
        for _, food in filtered_foods.iterrows():
            score = self.calculate_food_score(food, user_data, preferences)
            
            if score > 0:  # Only include foods with positive score
                recommendations.append({
                    'food_id': int(food['food_id']),
                    'name': food['name'],
                    'category': food['category'],
                    'calories': float(food['calories']),
                    'protein': float(food['protein']),
                    'carbs': float(food['carbs']),
                    'fat': float(food['fat']),
                    'health_score': float(food['health_score']),
                    'prep_time': int(food['prep_time']),
                    'score': float(score),
                    'meal_suitability': food['meal_type']
                })
        
        # Sort by score and return top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_n]
    
    def calculate_food_score(self, food, user_data, preferences=None):
        """Calculate personalized score for a food item"""
        score = 0
        
        # 1. Nutritional scoring based on user goals
        score += self.nutritional_score(food, user_data)
        
        # 2. Preference scoring
        if preferences:
            score += self.preference_score(food, preferences)
        
        # 3. Health score
        score += food['health_score'] * 0.3
        
        # 4. Meal type suitability
        if user_data.activity_level == 'very_active' and food['calories'] > 400:
            score += 0.2
        elif user_data.activity_level == 'sedentary' and food['calories'] < 300:
            score += 0.2
        
        return max(0, score)
    
    def nutritional_score(self, food, user_data):
        """Calculate nutritional score based on user profile"""
        score = 0
        
        # Calculate BMI
        bmi = user_data.weight / ((user_data.height / 100) ** 2)
        
        # Adjust scores based on dietary goals
        if user_data.dietary_goal == 'weight_loss':
            # Lower calories, higher protein
            if food['calories'] < 400:
                score += 0.3
            if food['protein'] > 20:
                score += 0.2
            if food['fat'] < 15:
                score += 0.1
        
        elif user_data.dietary_goal == 'weight_gain':
            # Higher calories, balanced macros
            if food['calories'] > 500:
                score += 0.2
            if food['protein'] > 25:
                score += 0.2
            if 20 < food['carbs'] < 80:
                score += 0.1
        
        elif user_data.dietary_goal == 'muscle_gain':
            # Very high protein
            if food['protein'] > 30:
                score += 0.4
            if food['calories'] > 400:
                score += 0.2
        
        # Activity level adjustment
        if user_data.activity_level in ['active', 'very_active']:
            if food['carbs'] > 40:
                score += 0.1
        
        return score
    
    def preference_score(self, food, preferences):
        """Score based on user preferences"""
        score = 0
        
        # Preferred cuisines
        if 'preferred_cuisines' in preferences and food['cuisine'] in preferences['preferred_cuisines']:
            score += 0.3
        
        # Favorite foods (partial matching)
        if 'favorite_foods' in preferences:
            for fav in preferences['favorite_foods']:
                if fav.lower() in food['name'].lower():
                    score += 0.4
                    break
        
        return score
    
    def filter_allergies(self, foods, allergies):
        """Filter out foods containing allergens"""
        if not allergies:
            return foods
        
        filtered = foods.copy()
        for allergy in allergies:
            filtered = filtered[~filtered['allergens'].str.contains(allergy, case=False, na=False)]
        
        return filtered
    
    def filter_disliked_foods(self, foods, disliked_foods):
        """Filter out disliked foods"""
        if not disliked_foods:
            return foods
        
        filtered = foods.copy()
        for disliked in disliked_foods:
            filtered = filtered[~filtered['name'].str.contains(disliked, case=False, na=False)]
        
        return filtered
    
    def generate_weekly_meal_plan(self, user_id, user_data, days=7):
        """Generate a weekly meal plan"""
        meal_plan = {}
        
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        total_calories_needed = self.calculate_daily_calories(user_data)
        
        for day in range(days):
            day_plan = {}
            day_calories = 0
            
            for meal_type in meal_types:
                # Get recommendations for this meal type
                recommendations = self.get_recommendations(
                    user_id, user_data, meal_type, top_n=5
                )
                
                if recommendations:
                    # Select a recommendation (could be random or based on score)
                    selected = random.choice(recommendations[:3])
                    day_plan[meal_type] = selected
                    day_calories += selected['calories']
            
            # Adjust if calories are too high or low
            day_plan = self.adjust_meal_calories(day_plan, total_calories_needed)
            
            meal_plan[f'Day {day + 1}'] = day_plan
        
        return meal_plan
    
    def calculate_daily_calories(self, user_data):
        """Calculate daily calorie needs using Harris-Benedict formula"""
        if user_data.gender.lower() == 'male':
            bmr = 88.362 + (13.397 * user_data.weight) + (4.799 * user_data.height) - (5.677 * user_data.age)
        else:
            bmr = 447.593 + (9.247 * user_data.weight) + (3.098 * user_data.height) - (4.330 * user_data.age)
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(user_data.activity_level, 1.2)
        
        # Adjust based on goal
        if user_data.dietary_goal == 'weight_loss':
            return tdee * 0.8  # 20% deficit
        elif user_data.dietary_goal == 'weight_gain':
            return tdee * 1.2  # 20% surplus
        elif user_data.dietary_goal == 'muscle_gain':
            return tdee * 1.1  # 10% surplus
        
        return tdee  # Maintenance
    
    def adjust_meal_calories(self, day_plan, target_calories):
        """Adjust meal calories to meet target"""
        total_calories = sum(meal['calories'] for meal in day_plan.values())
        
        if total_calories == 0:
            return day_plan
        
        # Calculate adjustment factor
        adjustment = target_calories / total_calories if total_calories > 0 else 1
        
        # Adjust portion sizes (simulated)
        for meal_type, meal in day_plan.items():
            meal['adjusted_calories'] = meal['calories'] * adjustment
            meal['portion_size'] = f"{adjustment:.1f}x"
        
        return day_plan