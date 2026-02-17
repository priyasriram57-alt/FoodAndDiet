from app import app, db, User, UserPreferences
import json

def seed_database():
    with app.app_context():
        # Check if user already exists
        if User.query.filter_by(username='testuser').first():
            print("User 'testuser' already exists.")
            return

        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com',
            age=30,
            gender='male',
            weight=75.0,
            height=175.0,
            activity_level='moderate',
            dietary_goal='maintain',
            health_conditions=json.dumps([])
        )
        user.set_password('password123')
        
        db.session.add(user)
        db.session.commit()
        
        # Create user preferences
        prefs = UserPreferences(
            user_id=user.id,
            preferred_cuisines=json.dumps(['Italian', 'Asian']),
            allergies=json.dumps([]),
            disliked_foods=json.dumps([]),
            favorite_foods=json.dumps(['Pizza', 'Sushi'])
        )
        db.session.add(prefs)
        db.session.commit()
        
        print("Test user created successfully!")
        print("Username: testuser")
        print("Password: password123")

if __name__ == '__main__':
    seed_database()
