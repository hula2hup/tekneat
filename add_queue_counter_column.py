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
    best_seller_menu_id = db.Column(db.Integer, nullable=True)
    nmid = db.Column(db.String(20), nullable=True)
    qris_string = db.Column(db.Text, nullable=True)
    qris_image = db.Column(db.String(200), nullable=True)
    queue_counter = db.Column(db.Integer, default=0)  # New column

with app.app_context():
    # Add the new column
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE toko ADD COLUMN queue_counter INTEGER DEFAULT 0"))
        conn.commit()
    print("Kolom queue_counter berhasil ditambahkan ke tabel toko.")
