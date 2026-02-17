import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

class FoodRecommendationModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        
    def build_model(self, input_shape, num_foods=100):
        """Build a hybrid recommendation model using neural networks"""
        
        # User features input
        user_input = layers.Input(shape=(input_shape,), name='user_features')
        
        # Food features input
        food_input = layers.Input(shape=(10,), name='food_features')  # 10 food features
        
        # User embedding
        user_dense = layers.Dense(64, activation='relu')(user_input)
        user_dense = layers.Dropout(0.2)(user_dense)
        user_dense = layers.Dense(32, activation='relu')(user_dense)
        
        # Food embedding
        food_dense = layers.Dense(32, activation='relu')(food_input)
        food_dense = layers.Dropout(0.2)(food_dense)
        food_dense = layers.Dense(16, activation='relu')(food_dense)
        
        # Concatenate user and food embeddings
        merged = layers.Concatenate()([user_dense, food_dense])
        
        # Deep layers for interaction
        merged = layers.Dense(64, activation='relu')(merged)
        merged = layers.Dropout(0.3)(merged)
        merged = layers.Dense(32, activation='relu')(merged)
        merged = layers.Dropout(0.2)(merged)
        
        # Output layer for ranking score
        output = layers.Dense(1, activation='sigmoid', name='ranking_score')(merged)
        
        # Create model
        self.model = keras.Model(
            inputs=[user_input, food_input],
            outputs=output
        )
        
        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        return self.model
    
    def prepare_features(self, user_data, food_data):
        """Prepare features for the model"""
        
        # Prepare user features
        user_features = self._extract_user_features(user_data)
        
        # Prepare food features
        food_features = self._extract_food_features(food_data)
        
        return user_features, food_features
    
    def _extract_user_features(self, user_data):
        """Extract and encode user features"""
        features = []
        
        # Age (normalized)
        features.append(user_data['age'] / 100)
        
        # Gender (encoded)
        if 'gender' not in self.label_encoders:
            self.label_encoders['gender'] = LabelEncoder()
            self.label_encoders['gender'].fit(['male', 'female', 'other'])
        gender_encoded = self.label_encoders['gender'].transform([user_data['gender']])[0]
        features.append(gender_encoded / 2)  # Normalize to 0-1
        
        # BMI
        bmi = user_data['weight'] / ((user_data['height'] / 100) ** 2)
        features.append(bmi / 50)  # Normalize
        
        # Activity level
        activity_mapping = {'sedentary': 0, 'light': 0.25, 'moderate': 0.5, 'active': 0.75, 'very_active': 1}
        features.append(activity_mapping.get(user_data['activity_level'], 0.5))
        
        # Dietary goal encoding
        goal_mapping = {
            'weight_loss': 0, 'weight_gain': 1, 'maintenance': 0.5,
            'muscle_gain': 0.75, 'health_maintenance': 0.5
        }
        features.append(goal_mapping.get(user_data['dietary_goal'], 0.5))
        
        return np.array(features).reshape(1, -1)
    
    def _extract_food_features(self, food_data):
        """Extract food features"""
        features = []
        
        # Nutritional features (normalized)
        features.append(food_data['calories'] / 1000)
        features.append(food_data['protein'] / 100)
        features.append(food_data['carbs'] / 200)
        features.append(food_data['fat'] / 100)
        features.append(food_data['fiber'] / 50 if 'fiber' in food_data else 0.1)
        features.append(food_data['sugar'] / 100 if 'sugar' in food_data else 0.05)
        
        # Food category encoding
        if 'category' not in self.label_encoders:
            self.label_encoders['category'] = LabelEncoder()
        category_encoded = self.label_encoders['category'].transform([food_data['category']])[0]
        features.append(category_encoded / 20)  # Assuming max 20 categories
        
        # Health score (if available)
        features.append(food_data.get('health_score', 0.5))
        
        # Preparation time (normalized)
        features.append(min(food_data.get('prep_time', 30) / 120, 1))
        
        # Complexity score
        features.append(food_data.get('complexity', 0.5))
        
        return np.array(features).reshape(1, -1)
    
    def predict_preference(self, user_data, food_data):
        """Predict user's preference for a food item"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        user_features, food_features = self.prepare_features(user_data, food_data)
        
        # Scale features if scaler is fitted
        if hasattr(self.scaler, 'mean_'):
            user_features = self.scaler.transform(user_features)
        
        prediction = self.model.predict([user_features, food_features])
        return prediction[0][0]
    
    def save_model(self, path='models/food_recommender.h5'):
        """Save the trained model"""
        self.model.save(path)
        joblib.dump(self.scaler, 'models/scaler.pkl')
        joblib.dump(self.label_encoders, 'models/label_encoders.pkl')
    
    def load_model(self, path='models/food_recommender.h5'):
        """Load a trained model"""
        self.model = keras.models.load_model(path)
        self.scaler = joblib.load('models/scaler.pkl')
        self.label_encoders = joblib.load('models/label_encoders.pkl')