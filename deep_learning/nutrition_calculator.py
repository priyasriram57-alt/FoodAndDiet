import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class NutritionCalculator:
    def __init__(self):
        self.nutrient_requirements = self.load_nutrient_requirements()
        
    def load_nutrient_requirements(self):
        """Load standard nutrient requirements by age and gender"""
        return {
            'calories': {'male': 2500, 'female': 2000},
            'protein': {'male': 56, 'female': 46},  # grams
            'carbs': {'male': 300, 'female': 250},  # grams
            'fat': {'male': 83, 'female': 66},  # grams
            'fiber': {'male': 38, 'female': 25},  # grams
            'sugar': {'male': 36, 'female': 25},  # grams (max)
            'calcium': {'male': 1000, 'female': 1000},  # mg
            'iron': {'male': 8, 'female': 18},  # mg
            'vitamin_c': {'male': 90, 'female': 75},  # mg
            'vitamin_d': {'male': 15, 'female': 15}  # mcg
        }
    
    def calculate_daily_nutrition(self, user):
        """Calculate user's daily nutrition needs"""
        # Default values to prevent crashes if user data is missing
        weight = user.weight if user.weight is not None else 70.0
        height = user.height if user.height is not None else 170.0
        age = user.age if user.age is not None else 30
        gender = user.gender.lower() if user.gender else 'male'
        activity = user.activity_level if user.activity_level else 'moderate'
        
        # Calculate BMR and TDEE
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity, 1.2)
        
        # Adjust based on goal
        if user.dietary_goal == 'weight_loss':
            calories = tdee * 0.8
        elif user.dietary_goal == 'weight_gain':
            calories = tdee * 1.2
        elif user.dietary_goal == 'muscle_gain':
            calories = tdee * 1.1
        else:  # maintenance
            calories = tdee
        
        # Calculate macronutrients based on goal
        if user.dietary_goal == 'weight_loss':
            protein = (calories * 0.35) / 4  # 35% protein
            carbs = (calories * 0.40) / 4    # 40% carbs
            fat = (calories * 0.25) / 9      # 25% fat
        elif user.dietary_goal == 'muscle_gain':
            protein = (calories * 0.40) / 4  # 40% protein
            carbs = (calories * 0.40) / 4    # 40% carbs
            fat = (calories * 0.20) / 9      # 20% fat
        else:
            protein = (calories * 0.30) / 4  # 30% protein
            carbs = (calories * 0.50) / 4    # 50% carbs
            fat = (calories * 0.20) / 9      # 20% fat
        
        return {
            'daily_calories': round(calories),
            'daily_protein': round(protein, 1),
            'daily_carbs': round(carbs, 1),
            'daily_fat': round(fat, 1),
            'bmi': round(user.weight / ((user.height / 100) ** 2), 1),
            'bmr': round(bmr),
            'tdee': round(tdee)
        }
    
    def analyze_user_nutrition(self, user_id):
        """Analyze user's nutrition intake patterns"""
        # This would typically query the database for user's food logs
        # For now, return sample analysis
        
        return {
            'nutrition_score': 78,
            'balance_score': 82,
            'protein_sufficiency': 95,
            'carb_quality': 65,
            'fat_balance': 88,
            'micronutrient_diversity': 72,
            'meal_timing': 85,
            'hydration': 90,
            'recommendations': [
                'Increase fiber intake by adding more vegetables',
                'Consider reducing added sugars in snacks',
                'Try to include protein in every meal',
                'Drink water before each meal'
            ],
            'improvement_areas': [
                'Vitamin D intake is below recommended levels',
                'Omega-3 fatty acids could be increased'
            ]
        }
    
    def calculate_nutrient_deficiencies(self, food_logs):
        """Calculate nutrient deficiencies from food logs"""
        nutrients = {
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'calcium': 0,
            'iron': 0,
            'vitamin_c': 0,
            'vitamin_d': 0
        }
        
        # Sum nutrients from food logs
        for log in food_logs:
            nutrients['protein'] += log.protein or 0
            nutrients['carbs'] += log.carbs or 0
            nutrients['fat'] += log.fat or 0
        
        # Calculate deficiencies (simplified)
        deficiencies = {}
        requirements = self.nutrient_requirements
        
        for nutrient, value in nutrients.items():
            if nutrient in requirements:
                required = requirements[nutrient]['male']  # Simplified
                percentage = (value / required) * 100 if required > 0 else 100
                deficiencies[nutrient] = {
                    'intake': value,
                    'required': required,
                    'percentage': round(percentage, 1),
                    'status': 'adequate' if percentage >= 90 else 'deficient' if percentage < 70 else 'moderate'
                }
        
        return deficiencies