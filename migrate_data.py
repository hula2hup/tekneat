from app import app, db, Toko, Menu, Category

with app.app_context():
    # Get all existing menus
    menus = Menu.query.all()

    # Group menus by toko and create categories based on menu names
    toko_categories = {}
    for menu in menus:
        toko_id = menu.toko_id
        if toko_id not in toko_categories:
            toko_categories[toko_id] = {}

        # Extract category from menu name (simple heuristic: first word or common patterns)
        name_lower = menu.name.lower()
        if 'nasi' in name_lower or 'ayam' in name_lower or 'goreng' in name_lower:
            category_name = 'Nasi Goreng'
        elif 'mie' in name_lower or 'kwetiaw' in name_lower:
            category_name = 'Mie & Kwetiaw'
        elif 'soto' in name_lower:
            category_name = 'Soto'
        elif 'bakso' in name_lower:
            category_name = 'Bakso'
        elif 'kebab' in name_lower:
            category_name = 'Kebab'
        elif 'telur' in name_lower:
            category_name = 'Telur'
        elif 'gurame' in name_lower or 'ikan' in name_lower:
            category_name = 'Ikan'
        elif 'batagor' in name_lower:
            category_name = 'Batagor'
        else:
            category_name = 'Lainnya'

        if category_name not in toko_categories[toko_id]:
            # Check if category already exists
            existing_cat = Category.query.filter_by(name=category_name, toko_id=toko_id).first()
            if existing_cat:
                toko_categories[toko_id][category_name] = existing_cat.id
            else:
                new_cat = Category(name=category_name, toko_id=toko_id)
                db.session.add(new_cat)
                db.session.flush()  # Get the ID
                toko_categories[toko_id][category_name] = new_cat.id

        # Assign menu to category
        menu.category_id = toko_categories[toko_id][category_name]

    db.session.commit()

print("Data migration completed!")
