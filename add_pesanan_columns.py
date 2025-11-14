import sqlite3

def add_columns():
    conn = sqlite3.connect('tekneat.db')
    cursor = conn.cursor()

    # Add new columns to pesanan table
    try:
        cursor.execute("ALTER TABLE pesanan ADD COLUMN nama_pembeli TEXT")
        print("Added nama_pembeli column")
    except sqlite3.OperationalError as e:
        print(f"nama_pembeli column already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE pesanan ADD COLUMN telepon TEXT")
        print("Added telepon column")
    except sqlite3.OperationalError as e:
        print(f"telepon column already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE pesanan ADD COLUMN nomor_antrean INTEGER")
        print("Added nomor_antrean column")
    except sqlite3.OperationalError as e:
        print(f"nomor_antrean column already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE pesanan ADD COLUMN status_pembayaran TEXT DEFAULT 'belum'")
        print("Added status_pembayaran column")
    except sqlite3.OperationalError as e:
        print(f"status_pembayaran column already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE pesanan ADD COLUMN waktu_pesan DATETIME")
        print("Added waktu_pesan column")
    except sqlite3.OperationalError as e:
        print(f"waktu_pesan column already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE pesanan ADD COLUMN waktu_bayar DATETIME")
        print("Added waktu_bayar column")
    except sqlite3.OperationalError as e:
        print(f"waktu_bayar column already exists or error: {e}")

    conn.commit()
    conn.close()
    print("Database updated successfully.")

if __name__ == "__main__":
    add_columns()
