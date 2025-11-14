from app import app, db, Toko, Pesanan, Menu

def test_queue_counter():
    with app.app_context():
        # Get first toko
        toko = Toko.query.first()
        if not toko:
            print("No toko found. Please add a toko first.")
            return

        print(f"Toko: {toko.nama}")
        print(f"Initial queue_counter: {toko.queue_counter}")

        # Simulate checkout logic
        toko.queue_counter += 1
        nomor_antrean = toko.queue_counter
        print(f"After increment - queue_counter: {toko.queue_counter}, nomor_antrean: {nomor_antrean}")

        # Create a dummy order to test
        menu = Menu.query.filter_by(toko_id=toko.id).first()
        if menu:
            pesanan = Pesanan(
                toko_id=toko.id,
                menu_id=menu.id,
                quantity=1,
                nama_pembeli="Test User",
                telepon="08123456789",
                nomor_antrean=nomor_antrean
            )
            db.session.add(pesanan)
            db.session.commit()
            print(f"Pesanan created with nomor_antrean: {pesanan.nomor_antrean}")

            # Test another increment
            toko.queue_counter += 1
            nomor_antrean2 = toko.queue_counter
            print(f"Second increment - queue_counter: {toko.queue_counter}, nomor_antrean: {nomor_antrean2}")

            pesanan2 = Pesanan(
                toko_id=toko.id,
                menu_id=menu.id,
                quantity=1,
                nama_pembeli="Test User 2",
                telepon="08123456789",
                nomor_antrean=nomor_antrean2
            )
            db.session.add(pesanan2)
            db.session.commit()
            print(f"Second pesanan created with nomor_antrean: {pesanan2.nomor_antrean}")

            # Verify uniqueness
            orders = Pesanan.query.filter_by(toko_id=toko.id).order_by(Pesanan.nomor_antrean.desc()).limit(5).all()
            print("Recent orders nomor_antrean:", [o.nomor_antrean for o in orders])

        else:
            print("No menu found in toko.")

if __name__ == "__main__":
    test_queue_counter()
