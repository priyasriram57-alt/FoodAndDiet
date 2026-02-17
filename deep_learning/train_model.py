import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import os

from deep_learning.model import FoodRecommendationModel
from deep_learning.data.preprocess import FoodDataPreprocessor

class ModelTrainer:
    def __init__(self, data_path='deep_learning/data/food_dataset.csv'):
        self.data_path = data_path
        self.preprocessor = FoodDataPreprocessor()
        self.model = FoodRecommendationModel()
        
    def prepare_data(self):
        """Prepare data for training"""
        # Load and clean data
        df = self.preprocessor.load_and_clean_data(self.data_path)
        
        # Prepare training data
        X, y = self.preprocessor.prepare_training_data(df)
        
        # Split data
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.preprocessor.split_data(X, y)
        
        return X_train, X_val, X_test, y_train, y_val, y_test, df
    
    def train_model(self, epochs=50, batch_size=32):
        """Train the recommendation model"""
        # Prepare data
        X_train, X_val, X_test, y_train, y_val, y_test, df = self.prepare_data()
        
        # Build model
        input_shape = X_train.shape[1]
        self.model.build_model(input_shape)
        
        # Setup callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            ),
            keras.callbacks.ModelCheckpoint(
                filepath='models/best_model.h5',
                monitor='val_accuracy',
                save_best_only=True
            )
        ]
        
        # Train model
        print("Training model...")
        history = self.model.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save model
        self.model.save_model('models/food_recommender.h5')
        self.preprocessor.save_preprocessor('models/preprocessor.pkl')
        
        return history, X_test, y_test
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        print("\nEvaluating model...")
        
        # Make predictions
        y_pred = self.model.model.predict(X_test)
        y_pred_binary = (y_pred > 0.5).astype(int)
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        accuracy = accuracy_score(y_test, y_pred_binary)
        precision = precision_score(y_test, y_pred_binary)
        recall = recall_score(y_test, y_pred_binary)
        f1 = f1_score(y_test, y_pred_binary)
        
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred_binary))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred_binary)
        self.plot_confusion_matrix(cm)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def plot_confusion_matrix(self, cm):
        """Plot confusion matrix"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig('models/confusion_matrix.png')
        plt.show()
    
    def plot_training_history(self, history):
        """Plot training history"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Plot accuracy
        ax1.plot(history.history['accuracy'], label='Train Accuracy')
        ax1.plot(history.history['val_accuracy'], label='Val Accuracy')
        ax1.set_title('Model Accuracy')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Accuracy')
        ax1.legend()
        
        # Plot loss
        ax2.plot(history.history['loss'], label='Train Loss')
        ax2.plot(history.history['val_loss'], label='Val Loss')
        ax2.set_title('Model Loss')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('models/training_history.png')
        plt.show()

def main():
    """Main training function"""
    print("Starting model training...")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Train model
    history, X_test, y_test = trainer.train_model(epochs=30)
    
    # Evaluate model
    metrics = trainer.evaluate_model(X_test, y_test)
    
    # Plot training history
    trainer.plot_training_history(history)
    
    print("\nTraining completed successfully!")
    print(f"Model saved to: models/food_recommender.h5")
    
    return metrics

if __name__ == "__main__":
    main()