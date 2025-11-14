from app import app, db
from sqlalchemy import text

with app.app_context():
    # Using raw SQL to add column if not exists
    db.session.execute(text('ALTER TABLE toko ADD COLUMN image_peta VARCHAR(200)'))

print("Kolom image_peta berhasil ditambahkan ke tabel Toko.")
