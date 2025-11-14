from app import app, db, Pesanan, Menu, Penjualan, Toko
from datetime import datetime

def test_confirm_payment():
    with app.app_context():
        # Create test data
        toko = Toko.query.first()
        if not toko:
            toko = Toko(nama='Test Toko', queue_counter=5)
            db.session.add(toko)
            db.session.commit()

        menu1 = Menu.query.filter_by(toko_id=toko.id).first()
        if not menu1:
            menu1 = Menu(name='Test Menu 1', price=10000, stock=10, toko_id=toko.id)
            db.session.add(menu1)
            db.session.commit()

        menu2 = Menu.query.filter_by(toko_id=toko.id).all()
        if len(menu2) < 2:
            menu2 = Menu(name='Test Menu 2', price=15000, stock=5, toko_id=toko.id)
            db.session.add(menu2)
            db.session.commit()
        else:
            menu2 = menu2[1]

        # Create orders with same nomor_antrean
        nomor_antrean = 100
        order1 = Pesanan(toko_id=toko.id, menu_id=menu1.id, quantity=2, nama_pembeli='Test Buyer', telepon='08123456789', nomor_antrean=nomor_antrean)
        order2 = Pesanan(toko_id=toko.id, menu_id=menu2.id, quantity=1, nama_pembeli='Test Buyer', telepon='08123456789', nomor_antrean=nomor_antrean)
        db.session.add(order1)
        db.session.add(order2)
        db.session.commit()

        # Record initial stock
        initial_stock1 = menu1.stock
        initial_stock2 = menu2.stock
        initial_sales_count = Penjualan.query.count()

        # Call confirm_payment (simulate by calling the function directly)
        from flask import request
        # Since it's a GET route, we can call it directly
        with app.test_request_context(f'/confirm_payment/{order1.id}'):
            from app import confirm_payment
            confirm_payment(order1.id)

        # Verify changes
        order1_refreshed = Pesanan.query.get(order1.id)
        order2_refreshed = Pesanan.query.get(order2.id)
        menu1_refreshed = Menu.query.get(menu1.id)
        menu2_refreshed = Menu.query.get(menu2.id)
        final_sales_count = Penjualan.query.count()

        print("Test confirm_payment:")
        print(f"Order1 status: {order1_refreshed.status_pembayaran}, waktu_bayar: {order1_refreshed.waktu_bayar}")
        print(f"Order2 status: {order2_refreshed.status_pembayaran}, waktu_bayar: {order2_refreshed.waktu_bayar}")
        print(f"Menu1 stock: {initial_stock1} -> {menu1_refreshed.stock}")
        print(f"Menu2 stock: {initial_stock2} -> {menu2_refreshed.stock}")
        print(f"Sales count: {initial_sales_count} -> {final_sales_count}")

        # Assertions
        assert order1_refreshed.status_pembayaran == 'paid'
        assert order2_refreshed.status_pembayaran == 'paid'
        assert order1_refreshed.waktu_bayar is not None
        assert order2_refreshed.waktu_bayar is not None
        assert menu1_refreshed.stock == initial_stock1 - 2
        assert menu2_refreshed.stock == initial_stock2 - 1
        assert final_sales_count == initial_sales_count + 2  # Two sales records

        print("confirm_payment test PASSED")

def test_expire_payment():
    with app.app_context():
        # Create test data
        toko = Toko.query.first()
        if not toko:
            toko = Toko(nama='Test Toko', queue_counter=5)
            db.session.add(toko)
            db.session.commit()

        menu1 = Menu.query.filter_by(toko_id=toko.id).first()
        if not menu1:
            menu1 = Menu(name='Test Menu 1', price=10000, stock=10, toko_id=toko.id)
            db.session.add(menu1)
            db.session.commit()

        # Create order
        nomor_antrean = 101
        order = Pesanan(toko_id=toko.id, menu_id=menu1.id, quantity=3, nama_pembeli='Test Buyer', telepon='08123456789', nomor_antrean=nomor_antrean)
        db.session.add(order)
        db.session.commit()

        # Record initial values
        initial_stock = menu1.stock
        initial_queue_counter = toko.queue_counter

        # Call expire_payment
        with app.test_request_context(f'/expire_payment/{order.id}'):
            from app import expire_payment
            expire_payment(order.id)

        # Verify changes
        order_refreshed = Pesanan.query.get(order.id)
        menu_refreshed = Menu.query.get(menu1.id)
        toko_refreshed = Toko.query.get(toko.id)

        print("Test expire_payment:")
        print(f"Order status: {order_refreshed.status_pembayaran}")
        print(f"Menu stock: {initial_stock} -> {menu_refreshed.stock}")
        print(f"Toko queue_counter: {initial_queue_counter} -> {toko_refreshed.queue_counter}")

        # Assertions
        assert order_refreshed.status_pembayaran == 'expired'
        assert menu_refreshed.stock == initial_stock + 3
        assert toko_refreshed.queue_counter == initial_queue_counter - 1

        print("expire_payment test PASSED")

if __name__ == '__main__':
    test_confirm_payment()
    test_expire_payment()
    print("All tests passed!")
