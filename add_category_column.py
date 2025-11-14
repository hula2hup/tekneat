from app import app, db

with app.app_context():
    # Add category_id column to menu table
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE menu ADD COLUMN category_id INTEGER REFERENCES category(id)"))
        conn.commit()

    print("Added category_id column to menu table")
