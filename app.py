from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
from sqlalchemy import func
import qrcode
import io
import base64
from pyzbar.pyzbar import decode
from PIL import Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tekneat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['SECRET_KEY'] = 'your_secret_key'  # Ganti dengan kunci rahasia unik Anda
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Model Database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)  # Simpan password plain untuk sederhana
    role = db.Column(db.String(50), default='user')  # Role: admin or user
    toko_id = db.Column(db.Integer, db.ForeignKey('toko.id'), nullable=True)  # Toko yang dikelola admin, None untuk central admin

    def __repr__(self):
        return f'<User {self.username}>'

class Toko(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    best_seller_menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=True)
    nmid = db.Column(db.String(20), nullable=True)  # NMID untuk QRIS
    qris_string = db.Column(db.Text, nullable=True)  # Custom QRIS string
    qris_image = db.Column(db.String(200), nullable=True)  # Path to QRIS image
    image_peta = db.Column(db.String(200), nullable=True)  # Path to peta image 1
    image_peta2 = db.Column(db.String(200), nullable=True)  # Path to peta image 2
    image_peta3 = db.Column(db.String(200), nullable=True)  # Path to peta image 3
    queue_counter = db.Column(db.Integer, default=0)  # Counter untuk nomor antrean
    use_categories = db.Column(db.Boolean, default=True)  # Apakah toko menggunakan kategori menu
    best_seller_menu = db.relationship('Menu', foreign_keys=[best_seller_menu_id], uselist=False)

    def __repr__(self):
        return f'<Toko {self.nama}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    toko_id = db.Column(db.Integer, db.ForeignKey('toko.id'), nullable=False)
    toko = db.relationship('Toko', backref=db.backref('categories', lazy=True))

    def __repr__(self):
        return f'<Category {self.name} in Toko {self.toko_id}>'

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    in_stock = db.Column(db.Boolean, default=True)
    max_order = db.Column(db.Integer, default=20)  # Batasan maksimal porsi per menu
    stock = db.Column(db.Integer, default=100)  # Stok yang tersedia
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('menus', lazy=True, cascade="all, delete-orphan"))
    toko_id = db.Column(db.Integer, db.ForeignKey('toko.id'), nullable=False)  # Keep for compatibility
    toko = db.relationship('Toko', foreign_keys=[toko_id], backref=db.backref('menus', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Menu {self.name} in Category {self.category_id}>'

class Penjualan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Penjualan {self.menu_id} on {self.date}>'

class Pesanan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    toko_id = db.Column(db.Integer, db.ForeignKey('toko.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')
    nama_pembeli = db.Column(db.String(100), nullable=False)
    telepon = db.Column(db.String(20), nullable=False)
    nomor_antrean = db.Column(db.Integer, nullable=False)
    status_pembayaran = db.Column(db.String(50), default='unpaid')  # unpaid, paid, expired
    waktu_pesan = db.Column(db.DateTime, default=datetime.utcnow)
    waktu_bayar = db.Column(db.DateTime, nullable=True)
    menu = db.relationship('Menu', backref=db.backref('pesanan', lazy=True))

    def __repr__(self):
        return f'<Pesanan {self.menu_id} for Toko {self.toko_id}>'

class Peta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image1 = db.Column(db.String(200), nullable=True)  # Path to peta image 1
    image2 = db.Column(db.String(200), nullable=True)  # Path to peta image 2
    image3 = db.Column(db.String(200), nullable=True)  # Path to peta image 3

    def __repr__(self):
        return f'<Peta {self.id}>'

with app.app_context():
    db.create_all()
    # Create default central admin user if not exists
    if not User.query.filter_by(username='galuh').first():
        admin = User(username='galuh', password='123', role='admin')
        db.session.add(admin)
        db.session.commit()
    # Create admin accounts for each toko if not exists
    toko_list = Toko.query.all()
    for toko in toko_list:
        username = toko.nama
        if not User.query.filter_by(username=username).first():
            toko_admin = User(username=username, password='123', role='admin', toko_id=toko.id)
            db.session.add(toko_admin)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()  # Cek username dan password
        if user:
            login_user(user)
            flash('Login berhasil! Selamat datang, admin.')
            return redirect(url_for('admin'))
        flash('Login gagal. Cek username dan password.')
    return render_template('login.html')  # Buat template login.html baru

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toko_list')
def toko_list():
    toko_list = Toko.query.all()
    best_sellers = {}
    for toko in toko_list:
        if toko.best_seller_menu_id:
            best_menu = Menu.query.get(toko.best_seller_menu_id)
            best_sellers[toko.id] = best_menu.image_url if best_menu else None
        else:
            menus = Menu.query.filter_by(toko_id=toko.id).all()
            if menus:
                max_sales = 0
                best_menu = None
                for menu in menus:
                    sales_count = Penjualan.query.filter_by(menu_id=menu.id).count()
                    if sales_count > max_sales:
                        max_sales = sales_count
                        best_menu = menu
                if best_menu:
                    best_sellers[toko.id] = best_menu.image_url
            else:
                best_sellers[toko.id] = None
    return render_template('toko_list.html', toko_list=toko_list, best_sellers=best_sellers)

@app.route('/all_menus')
def all_menus():
    toko_list = Toko.query.all()
    best_menus = []
    for toko in toko_list:
        if toko.best_seller_menu_id:
            best_menu = Menu.query.get(toko.best_seller_menu_id)
            if best_menu:
                best_menus.append((best_menu, toko))
        else:
            menus = Menu.query.filter_by(toko_id=toko.id).all()
            if menus:
                max_sales = 0
                best_menu = None
                for menu in menus:
                    sales_count = Penjualan.query.filter_by(menu_id=menu.id).count()
                    if sales_count > max_sales:
                        max_sales = sales_count
                        best_menu = menu
                if best_menu:
                    best_menus.append((best_menu, toko))
    return render_template('all_menus.html', all_menus=best_menus)

@app.route('/peta')
def peta():
    toko_list = Toko.query.all()
    peta = Peta.query.first()
    return render_template('peta.html', toko_list=toko_list, peta=peta)

@app.route('/toko/<int:toko_id>')
def toko_detail(toko_id):
    toko = Toko.query.get_or_404(toko_id)
    cart_toko_id = session.get('cart_toko_id')
    if cart_toko_id and cart_toko_id != toko_id:
        # Kosongkan keranjang jika berpindah ke toko berbeda
        session.pop('cart', None)
        session.pop('cart_toko_id', None)
        flash('Keranjang dikosongkan karena Anda berpindah ke toko yang berbeda.')
    menus = Menu.query.filter_by(toko_id=toko_id).all()
    best_menu = None
    if toko.best_seller_menu_id:
        best_menu = Menu.query.get(toko.best_seller_menu_id)
    else:
        if menus:
            max_sales = 0
            for menu in menus:
                sales_count = Penjualan.query.filter_by(menu_id=menu.id).count()
                if sales_count > max_sales:
                    max_sales = sales_count
                    best_menu = menu
    # Calculate total_ordered for each menu
    for menu in menus:
        menu.total_ordered = db.session.query(func.sum(Pesanan.quantity)).filter_by(menu_id=menu.id).scalar() or 0
    return render_template('toko_detail.html', toko=toko, menus=menus, best_menu=best_menu)

@app.route('/add_toko', methods=['GET', 'POST'])
@login_required  # Hanya central admin
def add_toko():
    if current_user.role != 'admin' or current_user.toko_id is not None:
        flash('Akses ditolak. Hanya admin pusat yang dapat menambah toko.')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        nama = request.form['nama'].strip()
        if not nama:
            flash('Nama toko harus diisi.')
            return redirect(url_for('add_toko'))
        if Toko.query.filter_by(nama=nama).first():
            flash('Toko dengan nama tersebut sudah ada.')
            return redirect(url_for('add_toko'))
        new_toko = Toko(nama=nama)
        db.session.add(new_toko)
        db.session.commit()
        # Create admin user for the toko
        toko_admin = User(username=nama, password='123', role='admin', toko_id=new_toko.id)
        db.session.add(toko_admin)
        db.session.commit()
        flash(f'Toko "{nama}" berhasil ditambahkan dengan admin user "{nama}".')
        return redirect(url_for('admin'))
    return render_template('add_toko.html')

@app.route('/add_category', methods=['GET', 'POST'])
@login_required  # Hanya admin
def add_category():
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat menambah kategori.')
        return redirect(url_for('admin'))
    # Filter toko berdasarkan toko_id user, atau semua jika central admin
    if current_user.toko_id is None:
        toko_list = Toko.query.all()
    else:
        toko_list = Toko.query.filter_by(id=current_user.toko_id).all()
    if request.method == 'POST':
        nama = request.form['nama']
        toko_id = int(request.form['toko_id'])
        # Cek apakah toko_id sesuai dengan akses user
        if current_user.toko_id is not None and toko_id != current_user.toko_id:
            flash('Akses ditolak. Anda hanya dapat menambah kategori untuk toko Anda sendiri.')
            return redirect(url_for('admin'))
        new_category = Category(name=nama, toko_id=toko_id)
        db.session.add(new_category)
        db.session.commit()
        flash('Kategori berhasil ditambahkan.')
        return redirect(url_for('admin'))
    return render_template('add_category.html', toko_list=toko_list)

@app.route('/add_menu', methods=['GET', 'POST'])
@login_required  # Hanya admin
def add_menu():
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat menambah menu.')
        return redirect(url_for('admin'))
    # Filter toko berdasarkan toko_id user, atau semua jika central admin
    if current_user.toko_id is None:
        toko_list = Toko.query.all()
    else:
        toko_list = Toko.query.filter_by(id=current_user.toko_id).all()
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        in_stock = 'in_stock' in request.form
        stock = int(request.form['stock'])
        toko_id = int(request.form['toko_id'])
        # Cek apakah toko_id sesuai dengan akses user
        if current_user.toko_id is not None and toko_id != current_user.toko_id:
            flash('Akses ditolak. Anda hanya dapat menambah menu untuk toko Anda sendiri.')
            return redirect(url_for('admin'))
        toko = Toko.query.get(toko_id)
        category_id = request.form.get('category_id')
        if category_id and toko.use_categories:
            category_id = int(category_id)
        else:
            category_id = None
        image = request.files.get('image')
        image_url = None
        if image:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            image_url = f"images/{image_filename}"
        new_menu = Menu(name=name, price=price, image_url=image_url, in_stock=in_stock, stock=stock, category_id=category_id, toko_id=toko_id)
        db.session.add(new_menu)
        db.session.commit()
        return redirect(url_for('admin'))
    # Get categories for the selected toko
    categories = []
    if toko_list:
        categories = Category.query.filter_by(toko_id=toko_list[0].id).all()
    return render_template('add_menu.html', toko_list=toko_list, categories=categories)



@app.route('/edit_toko/<int:toko_id>', methods=['GET', 'POST'])
@login_required  # Hanya admin
def edit_toko(toko_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengedit toko.')
        return redirect(url_for('admin'))
    # Cek akses: hanya central admin atau admin toko sendiri
    if current_user.toko_id is not None and current_user.toko_id != toko_id:
        flash('Akses ditolak. Anda hanya dapat mengedit toko Anda sendiri.')
        return redirect(url_for('admin'))
    toko = Toko.query.get_or_404(toko_id)
    menus = Menu.query.filter_by(toko_id=toko_id).all()
    categories = Category.query.filter_by(toko_id=toko_id).all()
    if request.method == 'POST':
        toko.nama = request.form['nama']
        # Handle QRIS image upload
        qris_image = request.files.get('qris_image')
        if qris_image:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_filename = qris_image.filename
            qris_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            toko.qris_image = f"images/{image_filename}"
            try:
                img = Image.open(qris_image)
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                decoded_objects = decode(img)
                if decoded_objects:
                    extracted_qris_string = decoded_objects[0].data.decode('utf-8')
                    toko.qris_string = extracted_qris_string
                    flash('QRIS string berhasil diekstrak dari gambar.')
                else:
                    flash('Tidak dapat mendeteksi QR code dalam gambar. Pastikan gambar berisi QR code yang jelas.')
            except Exception as e:
                flash(f'Error memproses gambar: {str(e)}')
        # Handle image peta uploads (removed from edit_toko)
        best_seller_menu_id = request.form.get('best_seller_menu_id')
        if best_seller_menu_id and best_seller_menu_id != 'none':
            toko.best_seller_menu_id = int(best_seller_menu_id)
        else:
            toko.best_seller_menu_id = None

        # Handle use_categories
        toko.use_categories = 'use_categories' in request.form

        # Handle queue reset
        if request.form.get('reset_queue') == 'yes':
            toko.queue_counter = 0
            flash('Nomor antrean berhasil direset ke 0.')

        db.session.commit()
        flash('Toko berhasil diperbarui.')
        return redirect(url_for('admin'))
    return render_template('edit_toko.html', toko=toko, menus=menus, categories=categories)

@app.route('/edit_menu/<int:menu_id>', methods=['GET', 'POST'])
@login_required  # Hanya admin
def edit_menu(menu_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengedit menu.')
        return redirect(url_for('admin'))
    menu = Menu.query.get_or_404(menu_id)
    # Cek akses: hanya central admin atau admin toko sendiri
    if current_user.toko_id is not None and current_user.toko_id != menu.toko_id:
        flash('Akses ditolak. Anda hanya dapat mengedit menu untuk toko Anda sendiri.')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        menu.name = request.form['name']
        menu.price = float(request.form['price'])
        menu.in_stock = 'in_stock' in request.form
        menu.stock = int(request.form['stock'])
        toko = Toko.query.get(menu.toko_id)
        category_id = request.form.get('category_id')
        if category_id and toko.use_categories:
            menu.category_id = int(category_id)
        else:
            menu.category_id = None
        image = request.files.get('image')
        if image:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            menu.image_url = f"images/{image_filename}"
        db.session.commit()
        return redirect(url_for('toko_detail', toko_id=menu.toko_id))
    # Get categories for the menu's toko
    categories = Category.query.filter_by(toko_id=menu.toko_id).all()
    toko = Toko.query.get(menu.toko_id)
    return render_template('edit_menu.html', menu=menu, categories=categories, toko=toko)

@app.route('/delete_menu/<int:menu_id>', methods=['POST'])
@login_required  # Hanya admin
def delete_menu(menu_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat menghapus menu.')
        return redirect(url_for('admin'))
    menu = Menu.query.get_or_404(menu_id)
    # Cek akses: hanya central admin atau admin toko sendiri
    if current_user.toko_id is not None and current_user.toko_id != menu.toko_id:
        flash('Akses ditolak. Anda hanya dapat menghapus menu untuk toko Anda sendiri.')
        return redirect(url_for('admin'))
    # Hapus penjualan terkait
    Penjualan.query.filter_by(menu_id=menu_id).delete()
    db.session.commit()
    # Hapus menu
    db.session.delete(menu)
    db.session.commit()
    flash(f'Menu "{menu.name}" berhasil dihapus!')
    return redirect(url_for('admin'))

@app.route('/delete_toko/<int:toko_id>', methods=['POST'])
@login_required  # Hanya admin
def delete_toko(toko_id):
    if current_user.role != 'admin' or current_user.toko_id is not None:
        flash('Akses ditolak. Hanya admin pusat yang dapat menghapus toko.')
        return redirect(url_for('admin'))
    toko = Toko.query.get_or_404(toko_id)
    # Hapus data terkait dalam urutan yang benar untuk menghindari foreign key errors
    # Hapus pesanan terkait
    Pesanan.query.filter_by(toko_id=toko_id).delete()
    # Hapus penjualan terkait menu di toko ini
    menus = Menu.query.filter_by(toko_id=toko_id).all()
    for menu in menus:
        Penjualan.query.filter_by(menu_id=menu.id).delete()
        # Hapus gambar menu jika ada
        if menu.image_url:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(menu.image_url))
            if os.path.exists(image_path):
                os.remove(image_path)
    # Hapus menu
    Menu.query.filter_by(toko_id=toko_id).delete()
    # Hapus kategori terkait
    Category.query.filter_by(toko_id=toko_id).delete()
    # Hapus user admin toko
    User.query.filter_by(toko_id=toko_id).delete()
    # Hapus gambar qris_image jika ada
    if toko.qris_image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(toko.qris_image))
        if os.path.exists(image_path):
            os.remove(image_path)
    # Hapus toko
    db.session.delete(toko)
    db.session.commit()
    flash(f'Toko "{toko.nama}" dan semua data terkait berhasil dihapus!')
    return redirect(url_for('admin'))

@app.route('/add_to_cart/<int:menu_id>', methods=['POST'])
def add_to_cart(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        flash('Jumlah porsi harus lebih dari 0.')
        return redirect(url_for('toko_detail', toko_id=menu.toko_id))
    if quantity > menu.max_order:
        flash(f'Maksimal pesanan per orang adalah {menu.max_order} porsi.')
        return redirect(url_for('toko_detail', toko_id=menu.toko_id))
    if not menu.in_stock:
        flash('Menu ini sedang tidak tersedia.')
        return redirect(url_for('toko_detail', toko_id=menu.toko_id))
    if quantity > menu.stock:
        flash(f'Stok tidak mencukupi. Stok tersedia: {menu.stock} porsi.')
        return redirect(url_for('toko_detail', toko_id=menu.toko_id))

    cart = session.get('cart', [])
    cart_toko_id = session.get('cart_toko_id')
    if cart_toko_id and cart_toko_id != menu.toko_id:
        flash('Keranjang hanya untuk satu toko. Silakan checkout atau kosongkan keranjang terlebih dahulu.')
        return redirect(url_for('toko_detail', toko_id=menu.toko_id))
    session['cart_toko_id'] = menu.toko_id

    # Check if menu already in cart
    for item in cart:
        if item['menu_id'] == menu_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'toko_id': menu.toko_id, 'menu_id': menu_id, 'quantity': quantity})
    session['cart'] = cart
    flash(f'{quantity} porsi {menu.name} ditambahkan ke keranjang.')
    return redirect(url_for('toko_detail', toko_id=menu.toko_id))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    cart_toko_id = session.get('cart_toko_id')
    if not cart:
        return render_template('cart.html', cart_items=[], total=0, toko=None)
    toko = Toko.query.get(cart_toko_id)
    cart_items = []
    total = 0
    for item in cart:
        menu = Menu.query.get(item['menu_id'])
        if menu:
            subtotal = menu.price * item['quantity']
            total += subtotal
            cart_items.append({'menu': menu, 'quantity': item['quantity'], 'subtotal': subtotal})
    return render_template('cart.html', cart_items=cart_items, total=total, toko=toko)

@app.route('/remove_from_cart/<int:menu_id>', methods=['POST'])
def remove_from_cart(menu_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['menu_id'] != menu_id]
    session['cart'] = cart
    if not cart:
        session.pop('cart_toko_id', None)
    flash('Item dihapus dari keranjang.')
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', [])
    for item in cart:
        new_quantity = int(request.form.get(f'quantity_{item["menu_id"]}', item['quantity']))
        if new_quantity <= 0:
            cart.remove(item)
        else:
            menu = Menu.query.get(item['menu_id'])
            if menu and new_quantity <= menu.stock and new_quantity <= menu.max_order:
                item['quantity'] = new_quantity
            else:
                flash(f'Jumlah untuk {menu.name} tidak valid.')
    session['cart'] = cart
    if not cart:
        session.pop('cart_toko_id', None)
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash('Keranjang kosong.')
        return redirect(url_for('toko_list'))
    cart_toko_id = session.get('cart_toko_id')
    toko = Toko.query.get(cart_toko_id)
    cart_items = []
    total = 0
    for item in cart:
        menu = Menu.query.get(item['menu_id'])
        if menu:
            subtotal = menu.price * item['quantity']
            total += subtotal
            cart_items.append({'menu': menu, 'quantity': item['quantity'], 'subtotal': subtotal})
    if request.method == 'POST':
        nama_pembeli = request.form['nama_pembeli'].strip()
        telepon = request.form['telepon'].strip()
        if not nama_pembeli or not telepon:
            flash('Nama pembeli dan nomor telepon harus diisi.')
            return redirect(url_for('checkout'))
        # Validate stock
        for item in cart:
            menu = Menu.query.get(item['menu_id'])
            if not menu or item['quantity'] > menu.stock:
                flash(f'Stok untuk {menu.name} tidak mencukupi.')
                return redirect(url_for('cart'))
        # Hitung nomor antrean menggunakan queue_counter
        toko.queue_counter += 1
        nomor_antrean = toko.queue_counter
        # Create Pesanan for each cart item
        orders = []
        for item in cart:
            menu = Menu.query.get(item['menu_id'])
            new_order = Pesanan(toko_id=cart_toko_id, menu_id=item['menu_id'], quantity=item['quantity'], nama_pembeli=nama_pembeli, telepon=telepon, nomor_antrean=nomor_antrean)
            db.session.add(new_order)
            orders.append(new_order)
            # Stok dikurangi saat pembayaran dikonfirmasi
        db.session.commit()
        first_order_id = orders[0].id if orders else None
        # Clear cart
        session.pop('cart', None)
        session.pop('cart_toko_id', None)
        flash(f'Pesanan berhasil dibuat! Nomor antrean: {nomor_antrean}')
        return redirect(url_for('payment', order_id=first_order_id))
    return render_template('checkout.html', cart_items=cart_items, total=total, toko=toko)

@app.route('/order/<int:menu_id>', methods=['GET', 'POST'])
def order(menu_id):
    # Redirect to cart system, or keep for backward compatibility
    return redirect(url_for('toko_detail', toko_id=Menu.query.get(menu_id).toko_id))



@app.route('/payment/<int:order_id>')
def payment(order_id):
    order = Pesanan.query.get_or_404(order_id)
    # Get all orders with the same nomor_antrean
    orders = Pesanan.query.filter_by(nomor_antrean=order.nomor_antrean, toko_id=order.toko_id).all()
    toko = Toko.query.get(order.toko_id)
    total_amount = sum(Menu.query.get(o.menu_id).price * o.quantity for o in orders)
    # Check if original QRIS image is uploaded
    if toko.qris_image:
        # Use the uploaded image directly
        qr_image_url = url_for('static', filename=toko.qris_image)
        return render_template('payment.html', orders=orders, toko=toko, qr_image_url=qr_image_url, total_amount=total_amount)
    else:
        # Fallback to generated QR code
        if toko.qris_string:
            qr_data = toko.qris_string
        elif toko.nmid:
            # Proper QRIS format with NMID
            amount = int(total_amount)
            qr_data = f"00020101021126660014ID.CO.QRIS.WWW0215ID1021{toko.nmid}0303UMI0519100000000000520400005303360540{amount:012d}5802ID5909{toko.nama[:25]}6009Jakarta610512345626303000"
        else:
            import random
            qr_data = f"QRIS-{random.randint(100000, 999999)}-{order.id}"
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return render_template('payment.html', orders=orders, toko=toko, qr_data=qr_data, qr_base64=qr_base64, total_amount=total_amount)

@app.route('/confirm_payment/<int:order_id>')
def confirm_payment(order_id):
    order = Pesanan.query.get_or_404(order_id)
    # Get all orders with the same nomor_antrean
    orders = Pesanan.query.filter_by(nomor_antrean=order.nomor_antrean, toko_id=order.toko_id).all()
    for o in orders:
        o.status_pembayaran = 'paid'
        o.waktu_bayar = datetime.utcnow()
        # Kurangi stok saat pembayaran dikonfirmasi
        menu = Menu.query.get(o.menu_id)
        if menu:
            menu.stock -= o.quantity
            # Record sale
            new_penjualan = Penjualan(menu_id=o.menu_id, quantity=o.quantity)
            db.session.add(new_penjualan)
    db.session.commit()
    flash('Pembayaran berhasil dikonfirmasi!')
    return redirect(url_for('admin'))

@app.route('/expire_payment/<int:order_id>')
def expire_payment(order_id):
    order = Pesanan.query.get_or_404(order_id)
    # Get all orders with the same nomor_antrean
    orders = Pesanan.query.filter_by(nomor_antrean=order.nomor_antrean, toko_id=order.toko_id).all()
    toko = Toko.query.get(order.toko_id)
    for o in orders:
        o.status_pembayaran = 'expired'
        # Restore stock
        menu = Menu.query.get(o.menu_id)
        if menu:
            menu.stock += o.quantity
    # Decrement queue counter since payment not completed
    toko.queue_counter -= 1
    db.session.commit()
    return '', 200

@app.route('/notify_buyer/<int:order_id>')
def notify_buyer(order_id):
    order = Pesanan.query.get_or_404(order_id)
    menu = Menu.query.get(order.menu_id)
    toko = Toko.query.get(order.toko_id)
    message = f"Hai {order.nama_pembeli}, pesanan Anda untuk {order.quantity} porsi {menu.name} dari {toko.nama} sudah siap! Nomor antrean: {order.nomor_antrean}"
    # Mark the order as completed so it disappears from pending orders
    order.status = 'completed'
    db.session.commit()
    # Format nomor telepon untuk WhatsApp (ganti 0 dengan +62 jika dimulai dengan 0)
    telepon = order.telepon
    if telepon.startswith('0'):
        telepon = '+62' + telepon[1:]
    whatsapp_url = f"https://wa.me/{telepon}?text={message.replace(' ', '%20')}"
    return redirect(whatsapp_url)

@app.route('/get_categories/<int:toko_id>')
def get_categories(toko_id):
    categories = Category.query.filter_by(toko_id=toko_id).all()
    return {'categories': [{'id': c.id, 'name': c.name} for c in categories]}

@app.route('/set_best_seller/<int:toko_id>/<int:menu_id>')
@login_required
def set_best_seller(toko_id, menu_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengatur best seller.')
        return redirect(url_for('admin'))
    toko = Toko.query.get_or_404(toko_id)
    menu = Menu.query.get_or_404(menu_id)
    if menu.toko_id != toko_id:
        flash('Menu tidak termasuk dalam toko ini.')
        return redirect(url_for('admin'))
    # Cek akses: hanya central admin atau admin toko sendiri
    if current_user.toko_id is not None and current_user.toko_id != toko_id:
        flash('Akses ditolak. Anda hanya dapat mengatur best seller untuk toko Anda sendiri.')
        return redirect(url_for('admin'))
    toko.best_seller_menu_id = menu_id
    db.session.commit()
    flash(f'Best seller untuk toko {toko.nama} telah diatur ke {menu.name}.')
    return redirect(url_for('admin'))



@app.route('/edit_category/<int:category_id>', methods=['POST'])
@login_required
def edit_category(category_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengedit kategori.')
        return redirect(url_for('admin'))
    category = Category.query.get_or_404(category_id)
    # Cek akses: hanya central admin atau admin toko sendiri
    if current_user.toko_id is not None and current_user.toko_id != category.toko_id:
        flash('Akses ditolak. Anda hanya dapat mengedit kategori untuk toko Anda sendiri.')
        return redirect(url_for('admin'))
    name = request.form['name']
    if name:
        category.name = name
        db.session.commit()
        flash('Kategori berhasil diperbarui.')
    else:
        flash('Nama kategori tidak boleh kosong.')
    return redirect(url_for('edit_toko', toko_id=category.toko_id))

@app.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat menghapus kategori.')
        return redirect(url_for('admin'))
    category = Category.query.get_or_404(category_id)
    # Cek akses: hanya central admin atau admin toko sendiri
    if current_user.toko_id is not None and current_user.toko_id != category.toko_id:
        flash('Akses ditolak. Anda hanya dapat menghapus kategori untuk toko Anda sendiri.')
        return redirect(url_for('admin'))
    # Cek apakah kategori masih digunakan oleh menu
    if Menu.query.filter_by(category_id=category_id).count() > 0:
        flash('Kategori tidak dapat dihapus karena masih digunakan oleh menu.')
        return redirect(url_for('edit_toko', toko_id=category.toko_id))
    db.session.delete(category)
    db.session.commit()
    flash('Kategori berhasil dihapus.')
    return redirect(url_for('edit_toko', toko_id=category.toko_id))

@app.route('/record_sale', methods=['GET', 'POST'])
@login_required
def record_sale():
    if current_user.role != 'admin' or current_user.toko_id is not None:
        flash('Akses ditolak. Hanya admin pusat yang dapat mencatat penjualan.')
        return redirect(url_for('admin'))
    menus = Menu.query.all()
    if request.method == 'POST':
        menu_id = int(request.form['menu_id'])
        quantity = int(request.form['quantity'])
        menu = Menu.query.get(menu_id)
        if not menu:
            flash('Menu tidak valid.')
            return redirect(url_for('record_sale'))
        if quantity <= 0:
            flash('Jumlah terjual harus lebih dari 0.')
            return redirect(url_for('record_sale'))
        new_penjualan = Penjualan(menu_id=menu_id, quantity=quantity)
        db.session.add(new_penjualan)
        db.session.commit()
        flash('Penjualan berhasil dicatat.')
        return redirect(url_for('admin'))
    return render_template('record_sale.html', menus=menus)

@app.route('/reset_sales', methods=['POST'])
@login_required
def reset_sales():
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat reset penjualan.')
        return redirect(url_for('admin'))
    toko_id = request.form.get('toko_id')
    if toko_id:
        # Reset untuk toko tertentu
        toko_id = int(toko_id)
        if current_user.toko_id is not None and current_user.toko_id != toko_id:
            flash('Akses ditolak. Anda hanya dapat reset penjualan untuk toko Anda sendiri.')
            return redirect(url_for('admin'))
        # Hapus penjualan
        Penjualan.query.filter(Penjualan.menu_id.in_([m.id for m in Menu.query.filter_by(toko_id=toko_id).all()])).delete(synchronize_session=False)
        # Hapus semua pesanan untuk toko ini
        Pesanan.query.filter_by(toko_id=toko_id).delete()
        db.session.commit()
        toko = Toko.query.get(toko_id)
        flash(f'Semua penjualan dan pesanan untuk toko {toko.nama} telah direset.')
    else:
        # Reset semua penjualan (hanya admin pusat)
        if current_user.toko_id is not None:
            flash('Akses ditolak. Hanya admin pusat yang dapat reset semua penjualan.')
            return redirect(url_for('admin'))
        Penjualan.query.delete()
        # Hapus semua pesanan
        Pesanan.query.delete()
        db.session.commit()
        flash('Semua penjualan dan pesanan untuk semua toko telah direset.')
    return redirect(url_for('admin'))



@app.route('/upload_peta', methods=['GET', 'POST'])
@login_required
def upload_peta():
    if current_user.role != 'admin' or current_user.toko_id is not None:
        flash('Akses ditolak. Hanya admin pusat yang dapat upload peta.')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        image1 = request.files.get('image1')
        image2 = request.files.get('image2')
        image3 = request.files.get('image3')
        if not image1 or not image2 or not image3:
            flash('Semua tiga gambar harus diupload.')
            return redirect(url_for('upload_peta'))
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        # Save images
        image1_filename = image1.filename
        image1.save(os.path.join(app.config['UPLOAD_FOLDER'], image1_filename))
        image2_filename = image2.filename
        image2.save(os.path.join(app.config['UPLOAD_FOLDER'], image2_filename))
        image3_filename = image3.filename
        image3.save(os.path.join(app.config['UPLOAD_FOLDER'], image3_filename))
        # Get or create peta entry
        peta = Peta.query.first()
        if not peta:
            peta = Peta()
            db.session.add(peta)
        peta.image1 = f"images/{image1_filename}"
        peta.image2 = f"images/{image2_filename}"
        peta.image3 = f"images/{image3_filename}"
        db.session.commit()
        flash('Gambar peta berhasil diupload.')
        return redirect(url_for('admin'))
    return render_template('upload_peta.html')

@app.route('/admin')
@login_required
def admin():
    # Filter toko berdasarkan akses user
    if current_user.toko_id is None:
        toko_list = Toko.query.all()
    else:
        toko_list = Toko.query.filter_by(id=current_user.toko_id).all()
    total_toko = len(toko_list)
    # Filter menus berdasarkan toko yang dapat diakses
    if current_user.toko_id is None:
        total_menus = Menu.query.count()
        total_penjualan = Penjualan.query.count()
    else:
        total_menus = Menu.query.filter_by(toko_id=current_user.toko_id).count()
        total_penjualan = Penjualan.query.join(Menu).filter(Menu.toko_id == current_user.toko_id).count()
    menus = {}
    for toko in toko_list:
        menus[toko.id] = []
        for menu in toko.menus:
            menu.pesanan = Pesanan.query.filter_by(menu_id=menu.id).all()
            menus[toko.id].append(menu)
    # Get pending orders
    if current_user.toko_id is None:
        pending_orders = Pesanan.query.filter_by(status_pembayaran='paid', status='pending').all()
    else:
        pending_orders = Pesanan.query.filter_by(toko_id=current_user.toko_id, status_pembayaran='paid', status='pending').all()
    return render_template('admin.html', toko_list=toko_list, total_toko=total_toko, total_menus=total_menus, total_penjualan=total_penjualan, menus=menus, pending_orders=pending_orders)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
     