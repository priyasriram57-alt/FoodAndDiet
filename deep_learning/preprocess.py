import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

class FoodDataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoders = {}
        
    def load_and_clean_data(self, filepath):
        """Load and clean the food dataset"""
        df = pd.read_csv(filepath)
        
        # Handle missing values
        numeric_cols = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        # Create derived features
        df['calorie_density'] = df['calories'] / 100  # per 100g
        df['protein_ratio'] = df['protein'] / (df['protein'] + df['carbs'] + df['fat'] + 1e-10)
        df['health_score'] = self.calculate_health_score(df)
        
        return df
    
    def calculate_health_score(self, df):
        """Calculate health score for foods"""
        scores = []
        
        for _, row in df.iterrows():
            score = 0
            
            # Higher protein is good
            if row['protein'] > 20:
                score += 0.3
            elif row['protein'] > 10:
                score += 0.15
            
            # Lower sugar is good
            if 'sugar' in row:
                if row['sugar'] < 10:
                    score += 0.3
                elif row['sugar'] < 20:
                    score += 0.15
            
            # Fiber is good
            if 'fiber' in row and row['fiber'] > 5:
                score += 0.2
            
            # Balanced calories
            if 200 < row['calories'] < 500:
                score += 0.2
            
            scores.append(min(score, 1.0))  # Cap at 1.0
        
        return scores
    
    def prepare_training_data(self, df, user_interactions=None):
        """Prepare data for model training"""
        # Prepare features
        feature_cols = [
            'calories', 'protein', 'carbs', 'fat',
            'calorie_density', 'protein_ratio', 'health_score'
        ]
        
        # Add categorical features
        categorical_cols = ['category', 'cuisine', 'meal_type']
        for col in categorical_cols:
            if col in df.columns:
                self.encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.encoders[col].fit_transform(df[col])
                feature_cols.append(f'{col}_encoded')
        
        # Select features
        X = df[feature_cols].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Create labels (simulated for training)
        # In real scenario, these would come from user interactions
        if user_interactions is None:
            # Simulate user preferences
            np.random.seed(42)
            y = np.random.randint(0, 2, size=len(df))
        else:
            y = user_interactions
        
        return X_scaled, y
    
    def split_data(self, X, y, test_size=0.2, val_size=0.1):
        """Split data into train, validation, and test sets"""
        # First split: train+val vs test
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Second split: train vs val
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=val_ratio, random_state=42
        )
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def save_preprocessor(self, path='models/preprocessor.pkl'):
        """Save the preprocessor for later use"""
        joblib.dump({
            'scaler': self.scaler,
            'encoders': self.encoders
        }, path)
    
    def load_preprocessor(self, path='models/preprocessor.pkl'):
        """Load a saved preprocessor"""
        data = joblib.load(path)
        self.scaler = data['scaler']
        self.encoders = data['encoders']