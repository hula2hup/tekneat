from app import app, db, Toko

def test_reset_queue():
    with app.app_context():
        # Get first toko
        toko = Toko.query.first()
        if not toko:
            print("No toko found.")
            return

        print(f"Toko: {toko.nama}")
        print(f"Initial queue_counter: {toko.queue_counter}")

        # Simulate reset
        toko.queue_counter = 0
        db.session.commit()
        print(f"After reset - queue_counter: {toko.queue_counter}")

        # Simulate increment after reset
        toko.queue_counter += 1
        nomor_antrean = toko.queue_counter
        print(f"After increment - queue_counter: {toko.queue_counter}, nomor_antrean: {nomor_antrean}")

if __name__ == "__main__":
    test_reset_queue()
