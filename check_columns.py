from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tekneat.db'
db = SQLAlchemy(app)

with app.app_context():
    inspector = inspect(db.engine)
    print('Tabel toko kolom:', [col['name'] for col in inspector.get_columns('toko')])
    print('Tabel menu kolom:', [col['name'] for col in inspector.get_columns('menu')])
    print('Tabel user kolom:', [col['name'] for col in inspector.get_columns('user')])
    print('Tabel pesanan kolom:', [col['name'] for col in inspector.get_columns('pesanan')])
