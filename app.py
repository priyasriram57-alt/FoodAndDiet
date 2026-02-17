from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from deep_learning.food_recommender import FoodRecommender
from deep_learning.nutrition_calculator import NutritionCalculator
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load models
recommender = FoodRecommender()
nutrition_calc = NutritionCalculator()

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    activity_level = db.Column(db.String(20))
    dietary_goal = db.Column(db.String(50))
    health_conditions = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserFoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_name = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    meal_type = db.Column(db.String(20))  # breakfast, lunch, dinner, snack

class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    preferred_cuisines = db.Column(db.String(200))
    allergies = db.Column(db.String(200))
    disliked_foods = db.Column(db.String(200))
    favorite_foods = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.json
            logger.info(f"Registering user: {data.get('username')}")
            
            username = data.get('username')
            email = data.get('email', '').lower()
            password = data.get('password')
            
            if not username or not email or not password:
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Validate numeric fields
            age = data.get('age')
            weight = data.get('weight')
            height = data.get('height')
            
            if age is None or weight is None or height is None:
                 return jsonify({'error': 'Age, weight and height are required'}), 400
            
            if User.query.filter(db.func.lower(User.username) == username.lower()).first():
                return jsonify({'error': 'Username already exists'}), 400
            
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already exists'}), 400
            
            user = User(
                username=username,
                email=email,
                age=age,
                gender=data.get('gender', 'other'),
                weight=weight,
                height=height,
                activity_level=data.get('activity_level', 'moderate'),
                dietary_goal=data.get('dietary_goal', 'maintain'),
                health_conditions=json.dumps(data.get('health_conditions', []))
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush() # Get user ID before committing
            
            # Create user preferences
            preferences = UserPreferences(
                user_id=user.id,
                preferred_cuisines=json.dumps(data.get('preferred_cuisines', [])),
                allergies=json.dumps(data.get('allergies', [])),
                disliked_foods=json.dumps(data.get('disliked_foods', [])),
                favorite_foods=json.dumps(data.get('favorite_foods', []))
            )
            db.session.add(preferences)
            db.session.commit()
            
            login_user(user)
            return jsonify({'message': 'Registration successful', 'redirect': '/dashboard'})
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during registration: {str(e)}")
            return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Case-insensitive username search
        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'message': 'Login successful', 'redirect': '/dashboard'})
        
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({'error': 'An internal error occurred'}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's nutrition stats
    daily_stats = nutrition_calc.calculate_daily_nutrition(current_user)
    
    # Get recent food logs
    recent_foods = UserFoodLog.query.filter_by(user_id=current_user.id)\
        .order_by(UserFoodLog.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         user=current_user,
                         stats=daily_stats,
                         recent_foods=recent_foods)

@app.route('/recommendations')
@login_required
def recommendations():
    return render_template('recommendations.html', user=current_user)

@app.route('/meal-plans')
@login_required
def meal_plans():
    return render_template('meal_plan.html', user=current_user)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/get_recommendations', methods=['POST'])
@login_required
def get_recommendations():
    data = request.json
    meal_type = data.get('meal_type', 'all')
    preferences = UserPreferences.query.filter_by(user_id=current_user.id).first()
    
    # Convert preferences to dict
    user_prefs = {
        'preferred_cuisines': json.loads(preferences.preferred_cuisines) if preferences.preferred_cuisines else [],
        'allergies': json.loads(preferences.allergies) if preferences.allergies else [],
        'disliked_foods': json.loads(preferences.disliked_foods) if preferences.disliked_foods else [],
        'favorite_foods': json.loads(preferences.favorite_foods) if preferences.favorite_foods else []
    }
    
    # Get recommendations
    recommendations = recommender.get_recommendations(
        user_id=current_user.id,
        user_data=current_user,
        meal_type=meal_type,
        preferences=user_prefs
    )
    
    # Add is_favorite flag
    favorites = user_prefs['favorite_foods']
    for rec in recommendations:
        rec['is_favorite'] = rec['name'] in favorites
    
    return jsonify({'recommendations': recommendations})

@app.route('/log_food', methods=['POST'])
@login_required
def log_food():
    data = request.json
    food_log = UserFoodLog(
        user_id=current_user.id,
        food_name=data['food_name'],
        calories=data['calories'],
        protein=data.get('protein', 0),
        carbs=data.get('carbs', 0),
        fat=data.get('fat', 0),
        meal_type=data.get('meal_type', 'other')
    )
    
    db.session.add(food_log)
    db.session.commit()
    
    return jsonify({'message': 'Food logged successfully'})

@app.route('/generate_meal_plan', methods=['POST'])
@login_required
def generate_meal_plan():
    data = request.json
    days = data.get('days', 7)
    
    meal_plan = recommender.generate_weekly_meal_plan(
        user_id=current_user.id,
        user_data=current_user,
        days=days
    )
    
    # Calculate nutrition summary
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    day_count = len(meal_plan)
    
    if day_count > 0:
        for day, meals in meal_plan.items():
            for meal_type, meal in meals.items():
                total_calories += meal.get('calories', 0)
                total_protein += meal.get('protein', 0)
                total_carbs += meal.get('carbs', 0)
                total_fat += meal.get('fat', 0)
        
        nutrition_summary = {
            'avg_calories': round(total_calories / day_count),
            'avg_protein': round(total_protein / day_count),
            'avg_carbs': round(total_carbs / day_count),
            'avg_fat': round(total_fat / day_count),
            'total_calories': round(total_calories)
        }
    else:
        nutrition_summary = {}

    return jsonify({
        'meal_plan': meal_plan,
        'nutrition_summary': nutrition_summary
    })

@app.route('/save_day_plan', methods=['POST'])
@login_required
def save_day_plan():
    try:
        data = request.json
        plan = data.get('plan')
        
        if not plan:
            return jsonify({'error': 'No meal plan provided'}), 400
            
        # Iterate through meals in the plan (breakfast, lunch, dinner, snack)
        for meal_type, meal_data in plan.items():
            if not meal_data:
                continue
                
            food_log = UserFoodLog(
                user_id=current_user.id,
                food_name=meal_data['name'],
                calories=meal_data['calories'],
                protein=meal_data['protein'],
                carbs=meal_data['carbs'],
                fat=meal_data['fat'],
                meal_type=meal_type
            )
            db.session.add(food_log)
        
        db.session.commit()
        return jsonify({'message': 'Day plan logged successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving day plan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/nutrition_analysis')
@login_required
def nutrition_analysis():
    # Get nutrition analysis for the user
    analysis = nutrition_calc.analyze_user_nutrition(current_user.id)
    return jsonify(analysis)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    
    # Update user data
    if 'weight' in data:
        current_user.weight = data['weight']
    if 'height' in data:
        current_user.height = data['height']
    if 'activity_level' in data:
        current_user.activity_level = data['activity_level']
    if 'dietary_goal' in data:
        current_user.dietary_goal = data['dietary_goal']
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    data = request.json
    food_name = data.get('food_name')
    if not food_name:
        return jsonify({'error': 'Food name required'}), 400
        
    prefs = UserPreferences.query.filter_by(user_id=current_user.id).first()
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.session.add(prefs)
        
    favorites = json.loads(prefs.favorite_foods) if prefs.favorite_foods else []
    
    if food_name in favorites:
        favorites.remove(food_name)
        action = 'removed'
    else:
        favorites.append(food_name)
        action = 'added'
        
    prefs.favorite_foods = json.dumps(favorites)
    db.session.commit()
    
    return jsonify({'message': f'Food {action} to favorites', 'action': action})

@app.route('/get_favorites', methods=['GET'])
@login_required
def get_favorites():
    try:
        prefs = UserPreferences.query.filter_by(user_id=current_user.id).first()
        favorites = json.loads(prefs.favorite_foods) if prefs and prefs.favorite_foods else []
        return jsonify({'favorites': favorites})
    except Exception as e:
        logger.error(f"Error fetching favorites: {str(e)}")
        return jsonify({'favorites': []})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)