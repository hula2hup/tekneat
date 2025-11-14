from app import app, db, User, Toko, Menu, Penjualan, Pesanan
from flask import session
import tempfile
import os

def test_reset_sales():
    # Use a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()

        # Create central admin
        central_admin = User(username='central', password='123', role='admin')
        db.session.add(central_admin)

        # Create toko admin
        toko_admin = User(username='toko_admin', password='123', role='admin', toko_id=1)
        db.session.add(toko_admin)

        # Create toko
        toko1 = Toko(nama='Toko 1')
        toko2 = Toko(nama='Toko 2')
        db.session.add(toko1)
        db.session.add(toko2)
        db.session.commit()

        # Create menu for toko1
        menu1 = Menu(name='Menu 1', price=10000, toko_id=toko1.id)
        menu2 = Menu(name='Menu 2', price=20000, toko_id=toko2.id)
        db.session.add(menu1)
        db.session.add(menu2)
        db.session.commit()

        # Create penjualan
        penjualan1 = Penjualan(menu_id=menu1.id, quantity=5)
        penjualan2 = Penjualan(menu_id=menu2.id, quantity=3)
        db.session.add(penjualan1)
        db.session.add(penjualan2)

        # Create pesanan (paid and unpaid)
        pesanan1 = Pesanan(toko_id=toko1.id, menu_id=menu1.id, quantity=2, nama_pembeli='Buyer1', telepon='08123456789', nomor_antrean=1, status_pembayaran='paid')
        pesanan2 = Pesanan(toko_id=toko1.id, menu_id=menu1.id, quantity=1, nama_pembeli='Buyer2', telepon='08123456780', nomor_antrean=2, status_pembayaran='unpaid')
        pesanan3 = Pesanan(toko_id=toko2.id, menu_id=menu2.id, quantity=4, nama_pembeli='Buyer3', telepon='08123456781', nomor_antrean=1, status_pembayaran='paid')
        db.session.add(pesanan1)
        db.session.add(pesanan2)
        db.session.add(pesanan3)
        db.session.commit()

        print("Data awal:")
        print(f"Penjualan: {Penjualan.query.count()}")
        print(f"Pesanan: {Pesanan.query.count()}")

        with app.test_client() as client:
            # Test 1: Reset untuk toko tertentu oleh admin pusat
            with client:
                # Login as central admin
                client.post('/login', data={'username': 'central', 'password': '123'})
                response = client.post('/reset_sales', data={'toko_id': str(toko1.id)})
                print(f"Response status: {response.status_code}")
                print(f"Penjualan setelah reset toko1: {Penjualan.query.count()}")
                print(f"Pesanan setelah reset toko1: {Pesanan.query.count()}")
                # Should have 1 penjualan left (for toko2), 1 pesanan left (for toko2)

            # Test 2: Reset semua oleh admin pusat
            with client:
                client.post('/login', data={'username': 'central', 'password': '123'})
                response = client.post('/reset_sales', data={})
                print(f"Response status setelah reset semua: {response.status_code}")
                print(f"Penjualan setelah reset semua: {Penjualan.query.count()}")
                print(f"Pesanan setelah reset semua: {Pesanan.query.count()}")
                # Should be 0

            # Recreate data for next test
            penjualan3 = Penjualan(menu_id=menu1.id, quantity=5)
            pesanan4 = Pesanan(toko_id=toko1.id, menu_id=menu1.id, quantity=2, nama_pembeli='Buyer4', telepon='08123456782', nomor_antrean=1, status_pembayaran='paid')
            db.session.add(penjualan3)
            db.session.add(pesanan4)
            db.session.commit()

            # Test 3: Reset untuk toko sendiri oleh admin toko
            with client:
                client.post('/login', data={'username': 'toko_admin', 'password': '123'})
                response = client.post('/reset_sales', data={'toko_id': str(toko1.id)})
                print(f"Response status admin toko reset sendiri: {response.status_code}")
                print(f"Penjualan setelah admin toko reset: {Penjualan.query.count()}")
                print(f"Pesanan setelah admin toko reset: {Pesanan.query.count()}")

            # Test 4: Admin toko mencoba reset toko lain (should fail)
            with client:
                client.post('/login', data={'username': 'toko_admin', 'password': '123'})
                response = client.post('/reset_sales', data={'toko_id': str(toko2.id)})
                print(f"Response status admin toko reset lain: {response.status_code}")
                # Should be redirect or error

            # Test 5: Admin toko mencoba reset semua (should fail)
            with client:
                client.post('/login', data={'username': 'toko_admin', 'password': '123'})
                response = client.post('/reset_sales', data={})
                print(f"Response status admin toko reset semua: {response.status_code}")
                # Should be redirect or error

    os.close(db_fd)
    os.unlink(db_path)

if __name__ == '__main__':
    test_reset_sales()
