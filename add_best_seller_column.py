from app import app, db

with app.app_context():
    # Add best_seller_menu_id column to Toko table
    with db.engine.connect() as conn:
        conn.execute(db.text('ALTER TABLE toko ADD COLUMN best_seller_menu_id INTEGER REFERENCES menu(id)'))
        conn.commit()
    print("Column added.")
