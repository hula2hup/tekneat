from app import app, db
from sqlalchemy import text

with app.app_context():
    # Using raw SQL to add columns if not exists
    db.session.execute(text('ALTER TABLE toko ADD COLUMN image_peta2 VARCHAR(200)'))
    db.session.execute(text('ALTER TABLE toko ADD COLUMN image_peta3 VARCHAR(200)'))

print("Kolom image_peta2 dan image_peta3 berhasil ditambahkan ke tabel Toko.")
