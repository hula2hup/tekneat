from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tekneat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model with the new column
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='user')
    toko_id = db.Column(db.Integer, db.ForeignKey('toko.id'), nullable=True)  # New column

with app.app_context():
    # Add the column to the database
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE user ADD COLUMN toko_id INTEGER REFERENCES toko(id)"))
        conn.commit()
    print("Column 'toko_id' added to 'user' table.")
