from app import db, app
from sqlalchemy import text

with app.app_context():
    # Add qris_image column to Toko table
    db.session.execute(text('ALTER TABLE toko ADD COLUMN qris_image VARCHAR(200)'))
    db.session.commit()
    print("Column qris_image added to Toko table.")
