# deep_learning/data/create_dataset.py
import pandas as pd
import numpy as np
import random
from faker import Faker

def create_sample_dataset(n_samples=1000, output_path='deep_learning/data/food_dataset.csv'):
    """Create a sample food dataset"""
    fake = Faker()
    
    # Food categories and types
    categories = ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert', 'Salad', 'Soup', 'Main Course', 'Side Dish']
    cuisines = ['Italian', 'Indian', 'Chinese', 'Mexican', 'Mediterranean', 'American', 'Japanese', 'Thai', 'French']
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    complexities = ['easy', 'medium', 'hard']
    allergens = ['none', 'dairy', 'nuts', 'gluten', 'seafood', 'eggs', 'soy']
    
    # Common food items by category
    food_templates = {
        'Breakfast': ['Oatmeal', 'Scrambled Eggs', 'Pancakes', 'Yogurt Parfait', 'Smoothie Bowl', 'Avocado Toast'],
        'Lunch': ['Chicken Salad', 'Vegetable Wrap', 'Quinoa Bowl', 'Soup', 'Sandwich', 'Pasta Salad'],
        'Dinner': ['Grilled Salmon', 'Vegetable Stir Fry', 'Chicken Curry', 'Lentil Stew', 'Beef Tacos', 'Pizza'],
        'Snack': ['Apple Slices', 'Protein Bar', 'Mixed Nuts', 'Greek Yogurt', 'Hummus with Veggies'],
        'Dessert': ['Fruit Salad', 'Dark Chocolate', 'Berry Sorbet', 'Chia Pudding', 'Baked Apple'],
        'Salad': ['Greek Salad', 'Caesar Salad', 'Quinoa Salad', 'Spinach Salad', 'Coleslaw'],
        'Soup': ['Tomato Soup', 'Lentil Soup', 'Chicken Noodle', 'Minestrone', 'Butternut Squash Soup']
    }
    
    data = []
    
    for i in range(n_samples):
        # Randomly select category
        category = random.choice(categories)
        
        # Get appropriate food name
        if category in food_templates:
            base_name = random.choice(food_templates[category])
            variation = fake.word()
            name = f"{base_name} with {variation}"
        else:
            name = fake.word().title() + " " + fake.word().title()
        
        # Generate nutritional values based on category
        if category in ['Breakfast', 'Snack']:
            calories = random.randint(100, 400)
            protein = random.uniform(5, 25)
            carbs = random.uniform(10, 60)
            fat = random.uniform(2, 20)
        elif category in ['Lunch', 'Dinner', 'Main Course']:
            calories = random.randint(300, 800)
            protein = random.uniform(15, 50)
            carbs = random.uniform(20, 100)
            fat = random.uniform(10, 40)
        else:
            calories = random.randint(50, 300)
            protein = random.uniform(1, 20)
            carbs = random.uniform(5, 40)
            fat = random.uniform(1, 15)
        
        # Create food item
        food_item = {
            'food_id': i + 1,
            'name': name,
            'category': category,
            'cuisine': random.choice(cuisines),
            'calories': round(calories, 1),
            'protein': round(protein, 1),
            'carbs': round(carbs, 1),
            'fat': round(fat, 1),
            'fiber': round(random.uniform(0, 15), 1),
            'sugar': round(random.uniform(0, 30), 1),
            'sodium': round(random.uniform(0, 1000), 1),
            'prep_time': random.randint(5, 120),
            'complexity': random.choice(complexities),
            'health_score': round(random.uniform(0.3, 1.0), 2),
            'ingredients': ', '.join([fake.word() for _ in range(5)]),
            'allergens': random.choice(allergens),
            'meal_type': random.choice(meal_types),
            'vegetarian': random.choice([True, False]),
            'vegan': random.choice([True, False]),
            'gluten_free': random.choice([True, False]),
            'dairy_free': random.choice([True, False])
        }
        
        # Adjust health score based on nutrition
        if food_item['sugar'] < 10 and food_item['fiber'] > 5:
            food_item['health_score'] = min(food_item['health_score'] + 0.2, 1.0)
        if food_item['fat'] > 30:
            food_item['health_score'] = max(food_item['health_score'] - 0.1, 0.1)
        
        data.append(food_item)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Created dataset with {n_samples} samples at {output_path}")
    
    return df

if __name__ == "__main__":
    create_sample_dataset(2000)