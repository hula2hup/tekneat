import logging
logging.basicConfig(level=logging.DEBUG)
from app import app, Toko, Menu, Penjualan

with app.app_context():
    try:
        toko_list = Toko.query.all()
        print('Toko list loaded:', len(toko_list))
        for toko in toko_list[:3]:
            print(f'Toko: {toko.nama}, ID: {toko.id}')
            menus = Menu.query.filter_by(toko_id=toko.id).all()
            print(f'  Menus: {len(menus)}')
            for menu in menus[:2]:
                print(f'    Menu: {menu.name}, ID: {menu.id}, category_id: {menu.category_id}')
        print('Query successful')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
