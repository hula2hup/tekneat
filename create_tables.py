import os
print("Current directory:", os.getcwd())
from app import app, db

with app.app_context():
    db.create_all()
    db.session.commit()
    print("Tables created.")
