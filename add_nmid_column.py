from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///d:/Kuliah/Pengantar Desain Teknik/Prototype/tekneat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Toko model with the new column
class Toko(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    best_seller_menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=True)
    nmid = db.Column(db.String(20), nullable=True)  # New column for NMID QRIS

with app.app_context():
    # Add the column to the database
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE toko ADD COLUMN nmid VARCHAR(20)"))
        conn.commit()
    print("Column 'nmid' added to 'toko' table.")
