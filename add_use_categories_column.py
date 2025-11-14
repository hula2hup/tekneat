from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Tambah kolom use_categories ke tabel toko
        db.session.execute(text('ALTER TABLE toko ADD COLUMN use_categories BOOLEAN DEFAULT 1'))
        db.session.commit()
        print('Kolom use_categories berhasil ditambahkan ke tabel toko.')
    except Exception as e:
        print(f'Error: {e}')
