from app import app, db, User, Toko

with app.app_context():
    db.create_all()
    if not User.query.first():
        # Central admin
        admin = User(username='galuh', password='123', role='admin', toko_id=None)
        db.session.add(admin)
        # Store-specific admins for each toko
        tokos = Toko.query.all()
        for toko in tokos:
            store_admin = User(username=f'admin_{toko.nama.lower().replace(" ", "_")}', password='123', role='admin', toko_id=toko.id)
            db.session.add(store_admin)
        db.session.commit()
    print('Database initialized successfully.')
