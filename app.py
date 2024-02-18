# app.py
# -------------------------------------------------------------------------------------------------------------------

# Import modul-modul yang diperlukan
import os, re
from flask import (
    Blueprint,
    Flask,
    flash,
    render_template,
    request,
    url_for,
    redirect,
    session,
    jsonify,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from helpers import get_userInfo
from models import db, User, Pengeluaran, Pemasukan, Kategori, Admin
from models.insert_data import insert_data_function
from models.get_total import (
    get_unique_transaction_dates,
    get_total_pemasukan_by_date,
    get_total_pengeluaran_by_date,
    get_total_pengeluaran_by_kategori_semua,
    get_total_pengeluaran_by_kategori_harian,
    get_total_pengeluaran_by_kategori_mingguan,
    get_total_pengeluaran_by_kategori_bulanan,
)
from models.dashboard import (
    get_total_pengeluaran_pemasukan_hari_ini,
    get_total_pengeluaran_pemasukan_mingguan,
    get_total_pengeluaran_pemasukan_bulanan,
    get_total_pengeluaran_pemasukan_tahunan,
    get_total_transaksi,
    get_total_transaksi_by_admin,
    get_monthly_data,
)
from datetime import date, datetime, timedelta
from calendar import monthrange
from jinja2 import Environment
from babel import Locale
from babel.numbers import format_currency
from sqlalchemy import select, func, text
import locale
import calendar
from math import ceil

# -------------------------------------------------------------------------------------------------------------------

# Membuat instance Flask dengan nama 'app'
app = Flask(__name__)

# -------------------------------------------------------------------------------------------------------------------

# Mengatur locale untuk pengaturan waktu bahasa Indonesia
locale.setlocale(locale.LC_TIME, "id_ID.UTF-8")

# Mengupdate global Jinja untuk memasukkan fungsi enumerate ke dalam lingkup template
app.jinja_env.globals.update(enumerate=enumerate)

# -------------------------------------------------------------------------------------------------------------------

# Membuat instance LoginManager dan menginisialisasikannya dengan aplikasi Flask
login_manager = LoginManager()
login_manager.init_app(app)

# Menentukan rute login yang akan digunakan oleh LoginManager
login_manager.login_view = "login"

# -------------------------------------------------------------------------------------------------------------------

# Menggunakan Flask-Migrate untuk menangani migrasi database
migrate = Migrate(app, db)

# -------------------------------------------------------------------------------------------------------------------

# Mengatur konfigurasi aplikasi, termasuk kunci rahasia, direktori upload gambar, dan ekstensi gambar yang diperbolehkan
app.config["SECRET_KEY"] = "Grimaim_Dashboard_Finance_b_5#y2LF4Q8z\n\xec]/"
app.config["IMAGE_UPLOADS"] = "static/images/profiles"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
DEFAULT_IMAGE = "default-image.jpg"

# -------------------------------------------------------------------------------------------------------------------

# Mendapatkan path direktori utama dari file saat ini
basedir = os.path.abspath(os.path.dirname(__file__))

# Mengatur URI database untuk SQLAlchemy dengan menggunakan SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "grimaimDash.db"
)

# Menonaktifkan fitur "track modifications" pada SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Menginisialisasi koneksi database dengan aplikasi Flask
db.init_app(app)

# Membuat tabel-tabel database dan menyisipkan data awal jika diperlukan
with app.app_context():
    db.create_all()
    insert_data_function()

# -------------------------------------------------------------------------------------------------------------------

# Menggunakan login manager untuk mengambil data pengguna berdasarkan ID
@login_manager.user_loader
def loader_user(userID):
    return User.query.get(userID)


# -------------------------------------------------------------------------------------------------------------------

# Fungsi untuk memeriksa apakah ekstensi gambar diizinkan
def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


# -------------------------------------------------------------------------------------------------------------------

# Routes Login (Index)
@app.route("/", methods=["GET", "POST"])
def login():
    message = None

    if request.method == "POST":
        # Mengambil username dan password dari formulir login
        username = request.form.get("username")
        password = request.form.get("password")

        # Mencari pengguna berdasarkan username
        user = User.query.filter_by(username=username).first()

        # Memeriksa keberhasilan autentikasi
        if user and user.password == password:
            # Jika berhasil, login user
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            # Jika gagal, tampilkan pesan kesalahan
            message = "Gagal masuk. Silakan periksa nama pengguna dan kata sandi Anda."

    return render_template("users/login.html", message=message)


# -------------------------------------------------------------------------------------------------------------------

# Routes Register
@app.route("/register", methods=["GET", "POST"])
def register():
    message = None

    if request.method == "POST":
        # Mengambil informasi dari formulir pendaftaran
        username = request.form.get("username")
        fullname = request.form.get("fullname")
        password = request.form.get("password")

        # Memeriksa apakah pengguna dengan username tersebut sudah ada
        existing_user = User.query.filter_by(username=username).first()

        # Melakukan validasi formulir pendaftaran
        if existing_user:
            message = "Akun Sudah Ada, Silahkan Login!"
        elif not re.match(r"^[A-Za-z0-9]+$", username):
            message = "Nama Pengguna hanya boleh berisi huruf dan angka!"
        elif not fullname or any(char.isdigit() for char in fullname):
            message = "Nama Lengkap hanya boleh berisi huruf dan tidak boleh mengandung angka!"
        elif not (username and fullname and password):
            message = "Silakan isi formulirnya"
        elif len(password) < 8:
            message = "Kata sandi harus memiliki setidaknya 8 karakter"
        else:
            # Jika formulir valid, buat dan simpan pengguna baru
            new_user = User(
                username=username,
                fullname=fullname,
                password=password,
                userPicture="default-image.jpg",
            )
            db.session.add(new_user)
            db.session.commit()
            message = "Akun Berhasil Dibuat, Silahkan Login!"

    return render_template("users/signup.html", message=message)


# -------------------------------------------------------------------------------------------------------------------

# Routes Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# -------------------------------------------------------------------------------------------------------------------

# Routes Chart JS
@app.route("/monthly_data_line/<int:year>", methods=["GET"])
@login_required
def monthly_data_line(year):
    user_id = current_user.userID
    monthly_data = get_monthly_data(user_id, year)
    return jsonify(monthly_data)


# -------------------------------------------------------------------------------------------------------------------

# Routes Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    userInfo = get_userInfo(current_user.username)
    user_id = current_user.userID
    active_tab = request.args.get("tab", "tab1")

    # Hitung total pengeluaran dan pemasukan Hari ini
    today = date.today()
    (
        total_pengeluaran_hari_ini,
        total_pemasukan_hari_ini,
    ) = get_total_pengeluaran_pemasukan_hari_ini(user_id, today)

    # Hitung total pengeluaran dan pemasukan kemarin
    yesterday = today - timedelta(days=1)
    (
        total_pengeluaran_kemarin,
        total_pemasukan_kemarin,
    ) = get_total_pengeluaran_pemasukan_hari_ini(user_id, yesterday)

    # Mengambil data total keseluruhan transaksi
    total_transaksi_pemasukan, total_transaksi_pengeluaran = get_total_transaksi(
        user_id
    )

    # Mengambil data pengeluaran dan pemasukan dari admin input
    admin_data = ["Aim", "Dhian"]
    admin_stats = []
    for admin_name in admin_data:
        total_pengeluaran, total_pemasukan = get_total_transaksi_by_admin(
            user_id, admin_name
        )
        admin_stats.append(
            {
                "admin_name": admin_name,
                "total_pengeluaran": total_pengeluaran,
                "total_pemasukan": total_pemasukan,
            }
        )

    total_harian = True
    total_mingguan = False
    total_bulanan = False
    total_tahunan = False

    return render_template(
        "dashboard/dashboard.html",
        userInfo=userInfo,
        active_tab=active_tab,
        total_harian=total_harian,
        total_mingguan=total_mingguan,
        total_bulanan=total_bulanan,
        total_tahunan=total_tahunan,
        total_pengeluaran_hari_ini=total_pengeluaran_hari_ini,
        total_pemasukan_hari_ini=total_pemasukan_hari_ini,
        total_transaksi_pemasukan=total_transaksi_pemasukan,
        total_transaksi_pengeluaran=total_transaksi_pengeluaran,
        admin_stats=admin_stats,
        total_pengeluaran_kemarin=total_pengeluaran_kemarin,
        total_pemasukan_kemarin=total_pemasukan_kemarin,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Dashboard Mingguan
@app.route("/dashboard/mingguan", methods=["GET", "POST"])
@login_required
def dashboardMingguan():
    userInfo = get_userInfo(current_user.username)
    user_id = current_user.userID
    active_tab = request.args.get("tab", "tab2")

    # Hitung Total Pengeluaran dan Pemasukan Minggu ini
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    (
        total_pengeluaran_minggu_ini,
        total_pemasukan_minggu_ini,
    ) = get_total_pengeluaran_pemasukan_mingguan(user_id, start_of_week, end_of_week)

    # Hitung Total Pengeluaran dan Pemasukan Minggu Lalu
    start_of_previous_week = start_of_week - timedelta(days=7)
    end_of_previous_week = end_of_week - timedelta(days=7)
    (
        total_pengeluaran_minggu_lalu,
        total_pemasukan_minggu_lalu,
    ) = get_total_pengeluaran_pemasukan_mingguan(
        user_id, start_of_previous_week, end_of_previous_week
    )

    # Mengambil data total keseluruhan transaksi
    total_transaksi_pemasukan, total_transaksi_pengeluaran = get_total_transaksi(
        user_id
    )

    # Mengambil data pengeluaran dan pemasukan dari admin input
    admin_data = ["Aim", "Dhian"]
    admin_stats = []
    for admin_name in admin_data:
        total_pengeluaran, total_pemasukan = get_total_transaksi_by_admin(
            user_id, admin_name
        )
        admin_stats.append(
            {
                "admin_name": admin_name,
                "total_pengeluaran": total_pengeluaran,
                "total_pemasukan": total_pemasukan,
            }
        )

    total_harian = False
    total_mingguan = True
    total_bulanan = False
    total_tahunan = False

    return render_template(
        "dashboard/dashboard.html",
        userInfo=userInfo,
        active_tab=active_tab,
        total_harian=total_harian,
        total_mingguan=total_mingguan,
        total_bulanan=total_bulanan,
        total_tahunan=total_tahunan,
        total_pengeluaran_minggu_ini=total_pengeluaran_minggu_ini,
        total_pemasukan_minggu_ini=total_pemasukan_minggu_ini,
        total_pengeluaran_minggu_lalu=total_pengeluaran_minggu_lalu,
        total_pemasukan_minggu_lalu=total_pemasukan_minggu_lalu,
        total_transaksi_pemasukan=total_transaksi_pemasukan,
        total_transaksi_pengeluaran=total_transaksi_pengeluaran,
        admin_stats=admin_stats,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Dashboard Bulanan
@app.route("/dashboard/bulanan", methods=["GET", "POST"])
@login_required
def dashboardBulanan():
    userInfo = get_userInfo(current_user.username)
    user_id = current_user.userID
    active_tab = request.args.get("tab", "tab3")

    # Hitung Total Pengeluaran dan Pemasukan Bulan ini dan Bulan lalu
    today = date.today()
    current_month = today.replace(day=1)
    (
        total_pengeluaran_bulan_ini,
        total_pemasukan_bulan_ini,
        total_pengeluaran_bulan_lalu,
        total_pemasukan_bulan_lalu,
    ) = get_total_pengeluaran_pemasukan_bulanan(user_id, current_month)

    # Mengambil data total keseluruhan transaksi
    total_transaksi_pemasukan, total_transaksi_pengeluaran = get_total_transaksi(
        user_id
    )

    # Mengambil data pengeluaran dan pemasukan dari admin input
    admin_data = ["Aim", "Dhian"]
    admin_stats = []
    for admin_name in admin_data:
        total_pengeluaran, total_pemasukan = get_total_transaksi_by_admin(
            user_id, admin_name
        )
        admin_stats.append(
            {
                "admin_name": admin_name,
                "total_pengeluaran": total_pengeluaran,
                "total_pemasukan": total_pemasukan,
            }
        )

    total_harian = False
    total_mingguan = False
    total_bulanan = True
    total_tahunan = False

    return render_template(
        "dashboard/dashboard.html",
        userInfo=userInfo,
        active_tab=active_tab,
        total_harian=total_harian,
        total_mingguan=total_mingguan,
        total_bulanan=total_bulanan,
        total_tahunan=total_tahunan,
        total_pengeluaran_bulan_ini=total_pengeluaran_bulan_ini,
        total_pemasukan_bulan_ini=total_pemasukan_bulan_ini,
        total_pengeluaran_bulan_lalu=total_pengeluaran_bulan_lalu,
        total_pemasukan_bulan_lalu=total_pemasukan_bulan_lalu,
        total_transaksi_pemasukan=total_transaksi_pemasukan,
        total_transaksi_pengeluaran=total_transaksi_pengeluaran,
        admin_stats=admin_stats,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Dashboard Tahunan
@app.route("/dashboard/tahunan", methods=["GET", "POST"])
@login_required
def dashboardTahunan():
    userInfo = get_userInfo(current_user.username)
    user_id = current_user.userID
    active_tab = request.args.get("tab", "tab4")

    # Hitung Total Pengeluaran dan Pemasukan Tahun ini dan Tahun lalu
    today = date.today()
    current_year = today.year
    last_year = current_year - 1
    (
        total_pengeluaran_tahun_ini,
        total_pemasukan_tahun_ini,
    ) = get_total_pengeluaran_pemasukan_tahunan(user_id, current_year)
    (
        total_pengeluaran_tahun_lalu,
        total_pemasukan_tahun_lalu,
    ) = get_total_pengeluaran_pemasukan_tahunan(user_id, last_year)

    # Mengambil data total keseluruhan transaksi
    total_transaksi_pemasukan, total_transaksi_pengeluaran = get_total_transaksi(
        user_id
    )

    # Mengambil data pengeluaran dan pemasukan dari admin input
    admin_data = ["Aim", "Dhian"]
    admin_stats = []
    for admin_name in admin_data:
        total_pengeluaran, total_pemasukan = get_total_transaksi_by_admin(
            user_id, admin_name
        )
        admin_stats.append(
            {
                "admin_name": admin_name,
                "total_pengeluaran": total_pengeluaran,
                "total_pemasukan": total_pemasukan,
            }
        )

    total_harian = False
    total_mingguan = False
    total_bulanan = False
    total_tahunan = True

    return render_template(
        "dashboard/dashboard.html",
        userInfo=userInfo,
        active_tab=active_tab,
        total_harian=total_harian,
        total_mingguan=total_mingguan,
        total_bulanan=total_bulanan,
        total_tahunan=total_tahunan,
        total_pengeluaran_tahun_ini=total_pengeluaran_tahun_ini,
        total_pemasukan_tahun_ini=total_pemasukan_tahun_ini,
        total_pengeluaran_tahun_lalu=total_pengeluaran_tahun_lalu,
        total_pemasukan_tahun_lalu=total_pemasukan_tahun_lalu,
        total_transaksi_pemasukan=total_transaksi_pemasukan,
        total_transaksi_pengeluaran=total_transaksi_pengeluaran,
        admin_stats=admin_stats,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Pengeluaran
@app.route("/pengeluaran")
@login_required
def pengeluaran():
    userInfo = get_userInfo(current_user.username)
    active_tab = request.args.get("tab", "tab1")
    sort_order = request.args.get("sort", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Jumlah Data yang ditampilkan pada tabel

    # Query untuk menampilkan semua dari tabel Pengeluaran berdasarkan userID
    semuaPengeluaran = Pengeluaran.query.filter_by(userID=current_user.userID).order_by(
        Pengeluaran.tanggalPengeluaran.desc()
        if sort_order == "desc"
        else Pengeluaran.tanggalPengeluaran.asc()
    )

    # Hasil Pagination
    semuaPengeluaran_paginated = semuaPengeluaran.paginate(page=page, per_page=per_page)

    # Menghitung indeks awal untuk halaman saat ini
    start_index = (page - 1) * per_page + 1

    return render_template(
        "pengeluaran/pengeluaran.html",
        semuaPengeluaran_paginated=semuaPengeluaran_paginated,
        userInfo=userInfo,
        active_tab=active_tab,
        sort_order=sort_order,
        start_index=start_index,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Pengeluaran Harian
@app.route("/pengeluaran/harian", methods=["GET", "POST"])
@login_required
def pengeluaranHarian():
    userInfo = get_userInfo(current_user.username)
    active_tab = request.args.get("tab", "tab2")
    sort_order = request.args.get("sort", "desc")

    # Filter pengeluaran untuk hari ini
    today = date.today()
    semuaPengeluaran_Harian = Pengeluaran.query.filter_by(
        userID=current_user.userID, tanggalPengeluaran=today
    ).all()

    # Urutkan berdasarkan urutan yang dipilih = ascending
    reverse_sort = sort_order == "asc"
    semuaPengeluaran_Harian_sorted = sorted(
        semuaPengeluaran_Harian,
        key=lambda x: x.tanggalPengeluaran,
        reverse=reverse_sort,
    )

    return render_template(
        "pengeluaran/pengeluaran.html",
        semuaPengeluaran_Harian_sorted=semuaPengeluaran_Harian_sorted,
        userInfo=userInfo,
        active_tab=active_tab,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Pengeluaran Mingguan
@app.route("/pengeluaran/mingguan", methods=["GET", "POST"])
@login_required
def pengeluaranMingguan():
    userInfo = get_userInfo(current_user.username)
    active_tab = request.args.get("tab", "tab3")
    sort_order = request.args.get("sort", "desc")

    # Menghitung tanggal mulai dan berakhir untuk minggu ini
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Filter pengeluaran untuk minggu ini
    semuaPengeluaran_Mingguan = Pengeluaran.query.filter(
        Pengeluaran.userID == current_user.userID,
        Pengeluaran.tanggalPengeluaran >= start_of_week.date(),
        Pengeluaran.tanggalPengeluaran <= end_of_week.date(),
    ).all()

    # Urutkan berdasarkan urutan yang dipilih = ascending
    reverse_sort = sort_order == "asc"
    semuaPengeluaran_Mingguan_sorted = sorted(
        semuaPengeluaran_Mingguan,
        key=lambda x: x.tanggalPengeluaran,
        reverse=reverse_sort,
    )

    return render_template(
        "pengeluaran/pengeluaran.html",
        semuaPengeluaran_Mingguan_sorted=semuaPengeluaran_Mingguan_sorted,
        userInfo=userInfo,
        active_tab=active_tab,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Pengeluaran Bulanan
@app.route("/pengeluaran/bulanan", methods=["GET", "POST"])
@login_required
def pengeluaranBulanan():
    userInfo = get_userInfo(current_user.username)
    active_tab = request.args.get("tab", "tab4")
    sort_order = request.args.get("sort", "desc")

    # Menghitung tanggal mulai dan berakhir untuk bulan ini
    today = datetime.today()
    start_of_month = today.replace(day=1)
    end_of_month = today.replace(day=monthrange(today.year, today.month)[1])

    # Filter pengeluaran untuk bulan ini
    semuaPengeluaran_Bulanan = Pengeluaran.query.filter(
        Pengeluaran.userID == current_user.userID,
        Pengeluaran.tanggalPengeluaran >= start_of_month.date(),
        Pengeluaran.tanggalPengeluaran <= end_of_month.date(),
    ).all()

    # Urutkan berdasarkan urutan yang dipilih = ascending
    reverse_sort = sort_order == "asc"
    semuaPengeluaran_Bulanan_sorted = sorted(
        semuaPengeluaran_Bulanan,
        key=lambda x: x.tanggalPengeluaran,
        reverse=reverse_sort,
    )

    return render_template(
        "pengeluaran/pengeluaran.html",
        semuaPengeluaran_Bulanan_sorted=semuaPengeluaran_Bulanan_sorted,
        userInfo=userInfo,
        active_tab=active_tab,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Tambah Pengeluaran
@app.route("/pengeluaran/tambah-data", methods=["GET", "POST"])
@login_required
def tambahPengeluaran():
    current_date = datetime.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        # Ekstrak data dari form yang disubmit melalui POST
        tanggalPengeluaran_str = request.form.get("tanggalPengeluaran")
        tanggalPengeluaran = datetime.strptime(
            tanggalPengeluaran_str, "%Y-%m-%d"
        ).date()

        deskripsiPengeluaran = request.form.get("deskripsiPengeluaran")
        kategoriPengeluaran = request.form.get("kategoriPengeluaran")

        # Ekstrak dan proses jumlah pengeluaran, hapus 'Rp.' dan format jumlah
        jumlahPengeluaran = float(
            request.form.get("jumlahPengeluaran").replace("Rp. ", "").replace(".", "")
        )
        adminName = request.form.get("adminName")

        # Buat objek pengeluaran baru dan tambahkan ke database
        pengeluaran_baru = Pengeluaran(
            userID=current_user.userID,
            tanggalPengeluaran=tanggalPengeluaran,
            deskripsiPengeluaran=deskripsiPengeluaran,
            kategoriPengeluaran=kategoriPengeluaran,
            jumlahPengeluaran=jumlahPengeluaran,
            adminName=adminName,
        )

        db.session.add(pengeluaran_baru)
        db.session.commit()
        flash("Data pengeluaran telah berhasil ditambahkan", "success")
        return redirect(url_for("pengeluaran"))

    else:
        # Jika permintaan adalah GET, ambil info pengguna, kategori pengeluaran, dan daftar admin
        userInfo = get_userInfo(current_user.username)
        kategori_list = Kategori.query.all()
        admin_list = Admin.query.all()

        return render_template(
            "pengeluaran/tambahPengeluaran.html",
            userInfo=userInfo,
            kategori_list=kategori_list,
            admin_list=admin_list,
            current_date=current_date,
        )


# -------------------------------------------------------------------------------------------------------------------

# Route Edit Pengeluaran
@app.route("/pengeluaran/ID=<int:pengeluaranID>/edit-data", methods=["GET", "POST"])
@login_required
def editPengeluaran(pengeluaranID):
    # Mengambil data pengeluaran dari database berdasarkan ID yang diberikan
    pengeluaran = Pengeluaran.query.get(pengeluaranID)
    current_date = datetime.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        # Ekstrak data dari form yang disubmit melalui POST
        tanggalPengeluaran_str = request.form.get("tanggalPengeluaran")
        tanggalPengeluaran = datetime.strptime(
            tanggalPengeluaran_str, "%Y-%m-%d"
        ).date()

        deskripsiPengeluaran = request.form.get("deskripsiPengeluaran")
        kategoriPengeluaran = request.form.get("kategoriPengeluaran")

        # Ekstrak dan proses jumlah pengeluaran, hapus 'Rp.' dan format jumlah
        jumlahPengeluaran = float(
            request.form.get("jumlahPengeluaran").replace("Rp. ", "").replace(".", "")
        )
        adminName = request.form.get("adminName")

        # Update data pengeluaran dengan nilai baru dari form
        pengeluaran.tanggalPengeluaran = tanggalPengeluaran
        pengeluaran.deskripsiPengeluaran = deskripsiPengeluaran
        pengeluaran.kategoriPengeluaran = kategoriPengeluaran
        pengeluaran.jumlahPengeluaran = jumlahPengeluaran
        pengeluaran.adminName = adminName

        # Simpan perubahan ke dalam database
        db.session.commit()
        flash(
            f"Data pengeluaran dengan ID: { pengeluaranID } berhasil diupdate",
            "success",
        )
        return redirect(url_for("pengeluaran"))

    else:
        # Jika permintaan adalah GET, ambil info pengguna, kategori pengeluaran, dan daftar admin
        userInfo = get_userInfo(current_user.username)
        kategori_list = Kategori.query.all()
        admin_list = Admin.query.all()

        return render_template(
            "pengeluaran/editPengeluaran.html",
            userInfo=userInfo,
            kategori_list=kategori_list,
            admin_list=admin_list,
            pengeluaran=pengeluaran,
            current_date=current_date,
        )


# -------------------------------------------------------------------------------------------------------------------

# Route Delete Pengeluaran
@app.route("/pengeluaran/delete-data/ID=<int:pengeluaranID>", methods=["GET", "POST"])
@login_required
def deletePengeluaran(pengeluaranID):
    # Ambil data pengeluaran dari database berdasarkan ID yang diberikan
    pengeluaran = Pengeluaran.query.get(pengeluaranID)

    if pengeluaran:
        # Hapus data pengeluaran dari database
        db.session.delete(pengeluaran)
        db.session.commit()
        flash(
            f"Data pengeluaran dengan ID: { pengeluaranID } berhasil dihapus", "success"
        )
    else:
        flash(f"Data pengeluaran dengan ID: { pengeluaranID } tidak ditemukan", "error")

    # Redirect ke halaman pengeluaran setelah menghapus data
    return redirect(url_for("pengeluaran"))


# -------------------------------------------------------------------------------------------------------------------

# Route Pemasukan
@app.route("/pemasukan")
@login_required
def pemasukan():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab1")
    sort_order = request.args.get("sort", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = 50

    # Query semua pemasukan pengguna, diurutkan berdasarkan tanggal dengan urutan menurun atau menaik sesuai parameter
    semuaPemasukan = Pemasukan.query.filter_by(userID=current_user.userID).order_by(
        Pemasukan.tanggalPemasukan.desc()
        if sort_order == "desc"
        else Pemasukan.tanggalPemasukan.asc()
    )

    # Paginasi data pemasukan
    semuaPemasukan_paginated = semuaPemasukan.paginate(page=page, per_page=per_page)

    # Menghitung indeks awal pada setiap halaman
    start_index = (page - 1) * per_page + 1

    return render_template(
        "pemasukan/pemasukan.html",
        semuaPemasukan_paginated=semuaPemasukan_paginated,
        userInfo=userInfo,
        active_tab=active_tab,
        sort_order=sort_order,
        start_index=start_index,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Pemasukan Harian
@app.route("/pemasukan/harian", methods=["GET", "POST"])
@login_required
def pemasukanHarian():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab2")
    sort_order = request.args.get("sort", "desc")

    # Query semua pemasukan harian pengguna untuk hari ini
    today = date.today()
    semuaPemasukan_Harian = Pemasukan.query.filter_by(
        userID=current_user.userID, tanggalPemasukan=today
    ).all()

    # Urutkan data pemasukan harian sesuai parameter sort_order
    reverse_sort = sort_order == "asc"
    semuaPemasukan_Harian_sorted = sorted(
        semuaPemasukan_Harian, key=lambda x: x.tanggalPemasukan, reverse=reverse_sort
    )

    return render_template(
        "pemasukan/pemasukan.html",
        semuaPemasukan_Harian_sorted=semuaPemasukan_Harian_sorted,
        userInfo=userInfo,
        active_tab=active_tab,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Pemasukan Mingguan
@app.route("/pemasukan/mingguan", methods=["GET", "POST"])
@login_required
def pemasukanMingguan():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab3")
    sort_order = request.args.get("sort", "desc")

    # Menghitung awal dan akhir minggu berdasarkan tanggal hari ini
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Query semua pemasukan mingguan pengguna untuk minggu ini
    semuaPemasukan_Mingguan = Pemasukan.query.filter(
        Pemasukan.userID == current_user.userID,
        Pemasukan.tanggalPemasukan >= start_of_week.date(),
        Pemasukan.tanggalPemasukan <= end_of_week.date(),
    ).all()

    # Urutkan data pemasukan mingguan sesuai parameter sort_order
    reverse_sort = sort_order == "asc"
    semuaPemasukan_Mingguan_sorted = sorted(
        semuaPemasukan_Mingguan, key=lambda x: x.tanggalPemasukan, reverse=reverse_sort
    )

    return render_template(
        "pemasukan/pemasukan.html",
        semuaPemasukan_Mingguan_sorted=semuaPemasukan_Mingguan_sorted,
        userInfo=userInfo,
        active_tab=active_tab,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Pemasukan Bulanan
@app.route("/pemasukan/bulanan", methods=["GET", "POST"])
@login_required
def pemasukanBulanan():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab4")
    sort_order = request.args.get("sort", "desc")

    # Menghitung awal dan akhir Bulan berdasarkan tanggal hari ini
    today = datetime.today()
    start_of_month = today.replace(day=1)
    end_of_month = today.replace(day=monthrange(today.year, today.month)[1])

    # Query semua pemasukan bulanan pengguna untuk bulan ini
    semuaPemasukan_Bulanan = Pemasukan.query.filter(
        Pemasukan.userID == current_user.userID,
        Pemasukan.tanggalPemasukan >= start_of_month.date(),
        Pemasukan.tanggalPemasukan <= end_of_month.date(),
    ).all()

    # Urutkan data pemasukan bulanan sesuai parameter sort_order
    reverse_sort = sort_order == "asc"
    semuaPemasukan_Bulanan_sorted = sorted(
        semuaPemasukan_Bulanan, key=lambda x: x.tanggalPemasukan, reverse=reverse_sort
    )

    return render_template(
        "pemasukan/pemasukan.html",
        semuaPemasukan_Bulanan_sorted=semuaPemasukan_Bulanan_sorted,
        userInfo=userInfo,
        active_tab=active_tab,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Tambah Pemasukan
@app.route("/pemasukan/tambah-data", methods=["GET", "POST"])
@login_required
def tambahPemasukan():
    current_date = datetime.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        # Ekstrak data dari form yang disubmit melalui POST
        tanggalPemasukan_str = request.form.get("tanggalPemasukan")
        tanggalPemasukan = datetime.strptime(tanggalPemasukan_str, "%Y-%m-%d").date()

        deskripsiPemasukan = request.form.get("deskripsiPemasukan")

        # Ekstrak dan proses jumlah pemasukan, hapus 'Rp.' dan format jumlah
        jumlahPemasukan = float(
            request.form.get("jumlahPemasukan").replace("Rp. ", "").replace(".", "")
        )
        adminName = request.form.get("adminName")

        # Membuat objek pemasukan baru dan tambahkan ke database
        pemasukan_baru = Pemasukan(
            userID=current_user.userID,
            tanggalPemasukan=tanggalPemasukan,
            deskripsiPemasukan=deskripsiPemasukan,
            jumlahPemasukan=jumlahPemasukan,
            adminName=adminName,
        )

        db.session.add(pemasukan_baru)
        db.session.commit()
        flash("Data pemasukan telah berhasil ditambahkan", "success")
        return redirect(url_for("pemasukan"))

    else:
        # Jika permintaan adalah GET, ambil info pengguna, kategori pemasukan, dan daftar admin
        userInfo = get_userInfo(current_user.username)
        kategori_list = Kategori.query.all()
        admin_list = Admin.query.all()

        return render_template(
            "pemasukan/tambahPemasukan.html",
            userInfo=userInfo,
            kategori_list=kategori_list,
            admin_list=admin_list,
            current_date=current_date,
        )


# -------------------------------------------------------------------------------------------------------------------

# Route Edit Pemasukan
@app.route("/pemasukan/ID=<int:pemasukanID>/edit-data", methods=["GET", "POST"])
@login_required
def editPemasukan(pemasukanID):
    # Mengambil data pemasukan dari database berdasarkan ID yang diberikan
    pemasukan = Pemasukan.query.get(pemasukanID)
    current_date = datetime.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        # Ekstrak data dari form yang disubmit melalui POST
        tanggalPemasukan_str = request.form.get("tanggalPemasukan")
        tanggalPemasukan = datetime.strptime(tanggalPemasukan_str, "%Y-%m-%d").date()
        deskripsiPemasukan = request.form.get("deskripsiPemasukan")

        # Ekstrak dan proses jumlah pemasukan, hapus 'Rp.' dan format jumlah
        jumlahPemasukan = float(
            request.form.get("jumlahPemasukan").replace("Rp. ", "").replace(".", "")
        )
        adminName = request.form.get("adminName")

        # Update data pemasukan dengan nilai baru dari form
        pemasukan.tanggalPemasukan = tanggalPemasukan
        pemasukan.deskripsiPemasukan = deskripsiPemasukan
        pemasukan.jumlahPemasukan = jumlahPemasukan
        pemasukan.adminName = adminName

        # Simpan perubahan ke dalam database
        db.session.commit()
        flash(f"Data pemasukan dengan ID: { pemasukanID } berhasil diupdate", "success")
        return redirect(url_for("pemasukan"))

    else:
        # Jika permintaan adalah GET, ambil info pengguna, kategori pemasukan, dan daftar admin
        userInfo = get_userInfo(current_user.username)
        kategori_list = Kategori.query.all()
        admin_list = Admin.query.all()

        return render_template(
            "pemasukan/editPemasukan.html",
            userInfo=userInfo,
            kategori_list=kategori_list,
            admin_list=admin_list,
            pemasukan=pemasukan,
            current_date=current_date,
        )


# -------------------------------------------------------------------------------------------------------------------

# Route Delete Pemasukan
@app.route("/pemasukan/delete-data/ID=<int:pemasukanID>", methods=["GET", "POST"])
@login_required
def deletePemasukan(pemasukanID):
    # Mengambil data pemasukan dari database berdasarkan ID yang diberikan
    pemasukan = Pemasukan.query.get(pemasukanID)

    if pemasukan:
        # Menghapus data pemasukan dari database
        db.session.delete(pemasukan)
        db.session.commit()
        flash(f"Data pemasukan dengan ID: { pemasukanID } berhasil dihapus", "success")
    else:
        flash(f"Data pemasukan dengan ID: { pemasukanID } tidak ditemukan", "error")

    # Redirect ke halaman pemasukan setelah menghapus data
    return redirect(url_for("pemasukan"))


# -------------------------------------------------------------------------------------------------------------------

# Routes Keuangan
@app.route("/keuangan")
@login_required
def keuangan():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab1")
    sort_order = request.args.get("sort", "desc")

    # Query semua pemasukan dan pengeluaran pengguna, diurutkan berdasarkan tanggal dengan urutan menurun atau menaik sesuai parameter
    semuaPemasukan = (
        Pemasukan.query.filter_by(userID=current_user.userID)
        .order_by(
            Pemasukan.tanggalPemasukan.desc()
            if sort_order == "desc"
            else Pemasukan.tanggalPemasukan.asc()
        )
        .all()
    )

    semuaPengeluaran = (
        Pengeluaran.query.filter_by(userID=current_user.userID)
        .order_by(
            Pengeluaran.tanggalPengeluaran.desc()
            if sort_order == "desc"
            else Pengeluaran.tanggalPengeluaran.asc()
        )
        .all()
    )

    # Menggabungkan tanggal unik dari pemasukan dan pengeluaran
    unique_dates = set(item.tanggalPemasukan for item in semuaPemasukan) | set(
        item.tanggalPengeluaran for item in semuaPengeluaran
    )

    # Urutkan tanggal sesuai parameter sort_order
    sorted_dates = sorted(unique_dates, reverse=(sort_order == "desc"))

    return render_template(
        "keuangan/keuangan.html",
        userInfo=userInfo,
        semuaPemasukan=semuaPemasukan,
        semuaPengeluaran=semuaPengeluaran,
        sorted_dates=sorted_dates,
        active_tab=active_tab,
        sort_order=sort_order,
        get_total_pemasukan_by_date=get_total_pemasukan_by_date,
        get_total_pengeluaran_by_date=get_total_pengeluaran_by_date,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Keuangan Harian
@app.route("/keuangan/harian", methods=["GET", "POST"])
@login_required
def keuanganHarian():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab2")
    sort_order = request.args.get("sort", "desc")

    # Query semua pemasukan harian pengguna untuk hari ini
    today = date.today()
    semuaPemasukan_Harian = (
        Pemasukan.query.filter_by(userID=current_user.userID, tanggalPemasukan=today)
        .order_by(
            Pemasukan.tanggalPemasukan.desc()
            if sort_order == "desc"
            else Pemasukan.tanggalPemasukan.asc()
        )
        .all()
    )

    # Query semua pengeluaran harian pengguna untuk hari ini
    semuaPengeluaran_Harian = (
        Pengeluaran.query.filter_by(
            userID=current_user.userID, tanggalPengeluaran=today
        )
        .order_by(
            Pengeluaran.tanggalPengeluaran.desc()
            if sort_order == "desc"
            else Pengeluaran.tanggalPengeluaran.asc()
        )
        .all()
    )

    # Menggabungkan tanggal unik dari pemasukan dan pengeluaran
    unique_dates = set(item.tanggalPemasukan for item in semuaPemasukan_Harian) | set(
        item.tanggalPengeluaran for item in semuaPengeluaran_Harian
    )

    # Urutkan tanggal sesuai parameter sort_order
    sorted_dates = sorted(unique_dates, reverse=(sort_order == "desc"))

    return render_template(
        "keuangan/keuangan.html",
        semuaPemasukan_Harian=semuaPemasukan_Harian,
        semuaPengeluaran_Harian=semuaPengeluaran_Harian,
        userInfo=userInfo,
        active_tab=active_tab,
        sorted_dates=sorted_dates,
        sort_order=sort_order,
        get_total_pemasukan_by_date=get_total_pemasukan_by_date,
        get_total_pengeluaran_by_date=get_total_pengeluaran_by_date,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Keuangan Mingguan
@app.route("/keuangan/mingguan", methods=["GET", "POST"])
@login_required
def keuanganMingguan():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab3")
    sort_order = request.args.get("sort", "desc")

    # Menghitung awal dan akhir minggu berdasarkan tanggal hari ini
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Query semua pemasukan mingguan pengguna untuk minggu ini
    semuaPemasukan_Mingguan = Pemasukan.query.filter(
        Pemasukan.userID == current_user.userID,
        Pemasukan.tanggalPemasukan >= start_of_week,
        Pemasukan.tanggalPemasukan <= end_of_week,
    ).all()

    # Query semua pengeluaran mingguan pengguna untuk minggu ini
    semuaPengeluaran_Mingguan = Pengeluaran.query.filter(
        Pengeluaran.userID == current_user.userID,
        Pengeluaran.tanggalPengeluaran >= start_of_week,
        Pengeluaran.tanggalPengeluaran <= end_of_week,
    ).all()

    # Menggabungkan tanggal unik dari pemasukan dan pengeluaran
    unique_dates = set(item.tanggalPemasukan for item in semuaPemasukan_Mingguan) | set(
        item.tanggalPengeluaran for item in semuaPengeluaran_Mingguan
    )

    # Urutkan tanggal sesuai parameter sort_order
    sorted_dates = sorted(unique_dates, reverse=(sort_order == "desc"))

    return render_template(
        "keuangan/keuangan.html",
        semuaPemasukan_Mingguan=semuaPemasukan_Mingguan,
        semuaPengeluaran_Mingguan=semuaPengeluaran_Mingguan,
        userInfo=userInfo,
        active_tab=active_tab,
        sorted_dates=sorted_dates,
        sort_order=sort_order,
        get_total_pemasukan_by_date=get_total_pemasukan_by_date,
        get_total_pengeluaran_by_date=get_total_pengeluaran_by_date,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Keuangan Bulanan
@app.route("/keuangan/bulanan", methods=["GET", "POST"])
@login_required
def keuanganBulanan():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab4")
    sort_order = request.args.get("sort", "desc")

    # Menghitung awal dan akhir bulan berdasarkan tanggal hari ini
    today = datetime.today()
    start_of_month = today.replace(day=1)
    end_of_month = (today.replace(day=1) + timedelta(days=32)).replace(
        day=1
    ) - timedelta(days=1)

    # Query semua pemasukan bulanan pengguna untuk bulan ini
    semuaPemasukan_Bulanan = Pemasukan.query.filter(
        Pemasukan.userID == current_user.userID,
        Pemasukan.tanggalPemasukan >= start_of_month,
        Pemasukan.tanggalPemasukan <= end_of_month,
    ).all()

    # Query semua pengeluaran bulanan pengguna untuk bulan ini
    semuaPengeluaran_Bulanan = Pengeluaran.query.filter(
        Pengeluaran.userID == current_user.userID,
        Pengeluaran.tanggalPengeluaran >= start_of_month,
        Pengeluaran.tanggalPengeluaran <= end_of_month,
    ).all()

    # Menggabungkan tanggal unik dari pemasukan dan pengeluaran
    unique_dates = set(item.tanggalPemasukan for item in semuaPemasukan_Bulanan) | set(
        item.tanggalPengeluaran for item in semuaPengeluaran_Bulanan
    )

    # Urutkan tanggal sesuai parameter sort_order
    sorted_dates = sorted(unique_dates, reverse=(sort_order == "desc"))

    return render_template(
        "keuangan/keuangan.html",
        semuaPemasukan_Bulanan=semuaPemasukan_Bulanan,
        semuaPengeluaran_Bulanan=semuaPengeluaran_Bulanan,
        userInfo=userInfo,
        active_tab=active_tab,
        sorted_dates=sorted_dates,
        sort_order=sort_order,
        get_total_pemasukan_by_date=get_total_pemasukan_by_date,
        get_total_pengeluaran_by_date=get_total_pengeluaran_by_date,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Kategori
@app.route("/kategori")
@login_required
def kategori():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)
    user_id = current_user.userID

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab1")

    # Mendapatkan total pengeluaran berdasarkan kategori untuk semua waktu
    total_pengeluaran_by_kategori_semua = get_total_pengeluaran_by_kategori_semua(
        user_id
    )

    # Menentukan jenis kategori yang ditampilkan (semua, harian, mingguan, bulanan)
    kategori_semua = True
    kategori_harian = False
    kategori_mingguan = False
    kategori_bulanan = False

    return render_template(
        "keuangan/kategori.html",
        userInfo=userInfo,
        active_tab=active_tab,
        total_pengeluaran_by_kategori_semua=total_pengeluaran_by_kategori_semua,
        kategori_semua=kategori_semua,
        kategori_harian=kategori_harian,
        kategori_mingguan=kategori_mingguan,
        kategori_bulanan=kategori_bulanan,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Kategori Harian
@app.route("/kategori/harian", methods=["GET", "POST"])
@login_required
def kategori_harian():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)
    user_id = current_user.userID

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab2")

    # Mendapatkan tanggal hari ini dan kemarin
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Mendapatkan total pengeluaran berdasarkan kategori untuk hari ini dan kemarin
    total_pengeluaran_by_kategori_harian = get_total_pengeluaran_by_kategori_harian(
        user_id, date=today
    )
    total_pengeluaran_yesterday = get_total_pengeluaran_by_kategori_harian(
        user_id, date=yesterday
    )

    # Menentukan jenis kategori yang ditampilkan (semua, harian, mingguan, bulanan)
    kategori_semua = False
    kategori_harian = True
    kategori_mingguan = False
    kategori_bulanan = False

    return render_template(
        "keuangan/kategori.html",
        userInfo=userInfo,
        active_tab=active_tab,
        total_pengeluaran_by_kategori_harian=total_pengeluaran_by_kategori_harian,
        total_pengeluaran_yesterday=total_pengeluaran_yesterday,
        kategori_semua=kategori_semua,
        kategori_harian=kategori_harian,
        kategori_mingguan=kategori_mingguan,
        kategori_bulanan=kategori_bulanan,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Kategori Mingguan
@app.route("/kategori/mingguan", methods=["GET", "POST"])
@login_required
def kategori_mingguan():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)
    user_id = current_user.userID

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab3")

    # Menghitung awal dan akhir minggu berdasarkan tanggal hari ini
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Mendapatkan total pengeluaran berdasarkan kategori untuk minggu ini
    total_pengeluaran_by_kategori_mingguan = get_total_pengeluaran_by_kategori_mingguan(
        user_id, start_of_week, end_of_week
    )

    # Menghitung awal dan akhir minggu sebelumnya berdasarkan minggu ini
    start_of_previous_week = start_of_week - timedelta(days=7)
    end_of_previous_week = end_of_week - timedelta(days=7)

    # Mendapatkan total pengeluaran berdasarkan kategori untuk minggu sebelumnya
    total_pengeluaran_previous_week = get_total_pengeluaran_by_kategori_mingguan(
        user_id, start_of_previous_week, end_of_previous_week
    )

    # Menentukan jenis kategori yang ditampilkan (semua, harian, mingguan, bulanan)
    kategori_semua = False
    kategori_harian = False
    kategori_mingguan = True
    kategori_bulanan = False

    return render_template(
        "keuangan/kategori.html",
        userInfo=userInfo,
        active_tab=active_tab,
        total_pengeluaran_by_kategori_mingguan=total_pengeluaran_by_kategori_mingguan,
        total_pengeluaran_previous_week=total_pengeluaran_previous_week,
        kategori_semua=kategori_semua,
        kategori_harian=kategori_harian,
        kategori_mingguan=kategori_mingguan,
        kategori_bulanan=kategori_bulanan,
    )


# -------------------------------------------------------------------------------------------------------------------

# Routes Kategori Bulanan
@app.route("/kategori/bulanan", methods=["GET", "POST"])
@login_required
def kategori_bulanan():
    # Mengambil informasi pengguna berdasarkan username
    userInfo = get_userInfo(current_user.username)
    user_id = current_user.userID

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab4")

    # Menghitung awal dan akhir bulan berdasarkan tanggal hari ini
    today = date.today()
    start_of_month = today.replace(day=1)
    end_of_month = start_of_month.replace(month=start_of_month.month + 1) - timedelta(
        days=1
    )

    # Mendapatkan total pengeluaran berdasarkan kategori untuk bulan ini
    total_pengeluaran_by_kategori_bulanan = get_total_pengeluaran_by_kategori_bulanan(
        user_id, start_of_month, end_of_month
    )

    # Menghitung awal dan akhir bulan sebelumnya berdasarkan bulan ini
    end_of_previous_month = start_of_month - timedelta(days=1)
    start_of_previous_month = end_of_previous_month.replace(day=1)

    # Mendapatkan total pengeluaran berdasarkan kategori untuk bulan sebelumnya
    total_pengeluaran_previous_month = get_total_pengeluaran_by_kategori_bulanan(
        user_id, start_of_previous_month, end_of_previous_month
    )

    # Menentukan jenis kategori yang ditampilkan (semua, harian, mingguan, bulanan)
    kategori_semua = False
    kategori_harian = False
    kategori_mingguan = False
    kategori_bulanan = True

    return render_template(
        "keuangan/kategori.html",
        userInfo=userInfo,
        active_tab=active_tab,
        total_pengeluaran_by_kategori_bulanan=total_pengeluaran_by_kategori_bulanan,
        total_pengeluaran_previous_month=total_pengeluaran_previous_month,
        kategori_semua=kategori_semua,
        kategori_harian=kategori_harian,
        kategori_mingguan=kategori_mingguan,
        kategori_bulanan=kategori_bulanan,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Account
@app.route("/account/<username>", methods=["GET", "POST"])
@login_required
def account(username):
    # Mendapatkan informasi pengguna berdasarkan username
    userInfo = get_userInfo(username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab1")

    if request.method == "POST":
        # Mendapatkan objek pengguna berdasarkan username
        user = User.query.filter_by(username=username).first()

        if user:
            # Mengambil data username dan fullname saat ini
            current_username = user.username
            current_fullname = user.fullname

            # Mendapatkan nilai yang diinputkan untuk username baru
            new_username = request.form.get("username")

            # Memeriksa apakah username yang baru sudah ada
            existing_user = User.query.filter_by(username=new_username).first()

            # Memeriksa apakah username yang baru valid dan tidak sama dengan yang lama
            if existing_user and new_username != username:
                flash(
                    "Akun dengan username tersebut sudah ada. Gunakan username lain.",
                    "error",
                )
            elif new_username and new_username != user.username:
                # Mengupdate username pengguna
                user.username = new_username
                flash("Username berhasil diperbarui", "success")

            # Mendapatkan nilai yang diinputkan untuk fullname baru
            new_fullname = request.form.get("fullname")

            # Memeriksa apakah fullname yang baru valid dan tidak sama dengan yang lama
            if new_fullname and new_fullname != user.fullname:
                # Mengupdate fullname pengguna
                user.fullname = new_fullname
                flash("Nama Lengkap berhasil diperbarui", "success")

            # Mendapatkan gambar profil yang diunggah oleh pengguna
            user_picture = request.files.get("userPicture")

            # Memeriksa apakah gambar yang diunggah adalah gambar yang diizinkan
            if user_picture and allowed_image(user_picture.filename):
                filename = secure_filename(user_picture.filename)

                # Mengupdate nama file gambar profil dan menyimpannya di direktori yang ditentukan
                user.userPicture = filename
                upload_dir = os.path.join(app.root_path, app.config["IMAGE_UPLOADS"])
                os.makedirs(upload_dir, exist_ok=True)
                user_picture.save(os.path.join(upload_dir, filename))

                flash("Foto profil berhasil diperbarui", "success")

            # Menyimpan perubahan ke database
            db.session.commit()

            # Jika terdapat perubahan pada username atau fullname, redirect ke halaman akun yang baru
            if current_username != user.username or current_fullname != user.fullname:
                return redirect(url_for("account", username=user.username))

    # Mengambil timestamp saat ini untuk digunakan pada tampilan gambar profil
    timestamp = int(datetime.timestamp(datetime.now()))

    return render_template(
        "users/account.html",
        userInfo=userInfo,
        timestamp=timestamp,
        active_tab=active_tab,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Password Account
@app.route("/account/<username>/password", methods=["GET", "POST"])
@login_required
def password(username):
    # Mendapatkan informasi pengguna berdasarkan username
    userInfo = get_userInfo(username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab2")

    if request.method == "POST":
        # Mendapatkan objek pengguna berdasarkan username
        user = User.query.filter_by(username=username).first()

        if user:
            # Mendapatkan kata sandi baru yang diinputkan oleh pengguna
            new_password = request.form.get("password")

            # Memeriksa apakah kata sandi baru valid dan tidak sama dengan yang lama
            if new_password and new_password != user.password:
                # Mengupdate kata sandi pengguna
                user.password = new_password
                flash("Kata sandi berhasil diperbarui", "success")
            elif new_password == user.password:
                flash(
                    "Kata sandi baru harus berbeda dengan kata sandi saat ini", "error"
                )

            # Menyimpan perubahan ke database
            db.session.commit()

            # Redirect kembali ke halaman pengaturan kata sandi
            return redirect(url_for("password", username=username))

    # Mengambil timestamp saat ini untuk digunakan pada tampilan gambar profil
    timestamp = int(datetime.timestamp(datetime.now()))

    return render_template(
        "users/account.html",
        userInfo=userInfo,
        timestamp=timestamp,
        active_tab=active_tab,
    )


# -------------------------------------------------------------------------------------------------------------------

# Route Delete Account
@app.route("/account/<username>/delete-account", methods=["GET", "POST"])
@login_required
def delete_account(username):
    # Mendapatkan informasi pengguna berdasarkan username
    userInfo = get_userInfo(username)

    # Mengambil parameter dari query string untuk pengaturan tampilan halaman
    active_tab = request.args.get("tab", "tab3")

    return render_template(
        "users/account.html", userInfo=userInfo, active_tab=active_tab
    )


# Route Confirmation Delete Account
@app.route("/account/<username>/delete", methods=["GET", "POST"])
@login_required
def deletedAccount(username):
    # Mendapatkan objek pengguna yang sedang login
    user = current_user

    # Menghapus pengguna dari database
    db.session.delete(user)
    db.session.commit()

    # Logout pengguna setelah menghapus akun
    logout_user()

    # Redirect ke halaman login setelah penghapusan akun
    return redirect(url_for("login"))


# -------------------------------------------------------------------------------------------------------------------

# Running 'app' Flask dalam mode debug
if __name__ == "__main__":
    app.run()

# -------------------------------------------------------------------------------------------------------------------
