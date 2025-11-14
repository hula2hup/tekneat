from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tekneat.db'  # Sesuaikan dengan URI di app.py Anda
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def add_missing_columns():
    with app.app_context():
        with db.engine.connect() as conn:
            # Tambahkan kolom ke tabel toko jika belum ada
            try:
                conn.execute(text('ALTER TABLE toko ADD COLUMN image_peta VARCHAR(200)'))
                print("Kolom image_peta ditambahkan ke tabel toko.")
            except Exception as e:
                print(f"Kolom image_peta sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE toko ADD COLUMN image_peta2 VARCHAR(200)'))
                print("Kolom image_peta2 ditambahkan ke tabel toko.")
            except Exception as e:
                print(f"Kolom image_peta2 sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE toko ADD COLUMN image_peta3 VARCHAR(200)'))
                print("Kolom image_peta3 ditambahkan ke tabel toko.")
            except Exception as e:
                print(f"Kolom image_peta3 sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE toko ADD COLUMN queue_counter INTEGER DEFAULT 0'))
                print("Kolom queue_counter ditambahkan ke tabel toko.")
            except Exception as e:
                print(f"Kolom queue_counter sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE toko ADD COLUMN use_categories BOOLEAN DEFAULT 1'))
                print("Kolom use_categories ditambahkan ke tabel toko.")
            except Exception as e:
                print(f"Kolom use_categories sudah ada atau error: {e}")

            # Tambahkan kolom ke tabel menu jika belum ada
            try:
                conn.execute(text('ALTER TABLE menu ADD COLUMN max_order INTEGER DEFAULT 20'))
                print("Kolom max_order ditambahkan ke tabel menu.")
            except Exception as e:
                print(f"Kolom max_order sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE menu ADD COLUMN stock INTEGER DEFAULT 100'))
                print("Kolom stock ditambahkan ke tabel menu.")
            except Exception as e:
                print(f"Kolom stock sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE menu ADD COLUMN category_id INTEGER REFERENCES category(id)'))
                print("Kolom category_id ditambahkan ke tabel menu.")
            except Exception as e:
                print(f"Kolom category_id sudah ada atau error: {e}")

            # Tambahkan kolom ke tabel user jika belum ada
            try:
                conn.execute(text('ALTER TABLE user ADD COLUMN toko_id INTEGER REFERENCES toko(id)'))
                print("Kolom toko_id ditambahkan ke tabel user.")
            except Exception as e:
                print(f"Kolom toko_id sudah ada atau error: {e}")

            # Tambahkan kolom ke tabel pesanan jika belum ada
            try:
                conn.execute(text('ALTER TABLE pesanan ADD COLUMN nama_pembeli TEXT'))
                print("Kolom nama_pembeli ditambahkan ke tabel pesanan.")
            except Exception as e:
                print(f"Kolom nama_pembeli sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE pesanan ADD COLUMN telepon TEXT'))
                print("Kolom telepon ditambahkan ke tabel pesanan.")
            except Exception as e:
                print(f"Kolom telepon sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE pesanan ADD COLUMN nomor_antrean INTEGER'))
                print("Kolom nomor_antrean ditambahkan ke tabel pesanan.")
            except Exception as e:
                print(f"Kolom nomor_antrean sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE pesanan ADD COLUMN status_pembayaran TEXT DEFAULT "belum"'))
                print("Kolom status_pembayaran ditambahkan ke tabel pesanan.")
            except Exception as e:
                print(f"Kolom status_pembayaran sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE pesanan ADD COLUMN waktu_pesan DATETIME'))
                print("Kolom waktu_pesan ditambahkan ke tabel pesanan.")
            except Exception as e:
                print(f"Kolom waktu_pesan sudah ada atau error: {e}")

            try:
                conn.execute(text('ALTER TABLE pesanan ADD COLUMN waktu_bayar DATETIME'))
                print("Kolom waktu_bayar ditambahkan ke tabel pesanan.")
            except Exception as e:
                print(f"Kolom waktu_bayar sudah ada atau error: {e}")

            conn.commit()
            print("Migrasi selesai. Semua kolom yang hilang telah ditambahkan.")

if __name__ == "__main__":
    add_missing_columns()
