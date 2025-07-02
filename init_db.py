from app import app, db  # make sure to import your app instance too

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")
