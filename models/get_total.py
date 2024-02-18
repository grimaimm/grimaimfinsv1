from models import db, User, Pengeluaran, Pemasukan, Kategori, Admin
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import date, timedelta


def get_unique_transaction_dates():
    # Menggabungkan tanggal-tanggal unik dari tabel pemasukan dan pengeluaran
    unique_dates_pemasukan = db.session.query(func.date(Pemasukan.tanggalPemasukan)).distinct().all()
    unique_dates_pengeluaran = db.session.query(func.date(Pengeluaran.tanggalPengeluaran)).distinct().all()

    # Menggabungkan kedua list tanggal
    unique_dates = set(date[0] for date in unique_dates_pemasukan + unique_dates_pengeluaran)

    # Mengurutkan tanggal-tanggal secara ascending
    sorted_dates = sorted(unique_dates)

    return sorted_dates

# def get_total_pemasukan_by_date(tanggal):
#     # Menghitung total pemasukan pada tanggal tertentu
#     total_pemasukan = db.session.query(func.sum(Pemasukan.jumlahPemasukan)).filter(func.date(Pemasukan.tanggalPemasukan) == tanggal).scalar()

#     return total_pemasukan or 0  # Mengembalikan 0 jika total_pemasukan None

# def get_total_pengeluaran_by_date(tanggal):
#     # Menghitung total pengeluaran pada tanggal tertentu
#     total_pengeluaran = db.session.query(func.sum(Pengeluaran.jumlahPengeluaran)).filter(func.date(Pengeluaran.tanggalPengeluaran) == tanggal).scalar()

#     return total_pengeluaran or 0  # Mengembalikan 0 jika total_pengeluaran None


# Fungsi untuk mendapatkan total pemasukan berdasarkan tanggal
def get_total_pemasukan_by_date(tanggal):
    pemasukan_by_date = Pemasukan.query.filter_by(tanggalPemasukan=tanggal, userID=current_user.userID).all()
    return sum(item.jumlahPemasukan for item in pemasukan_by_date)

# Fungsi untuk mendapatkan total pengeluaran berdasarkan tanggal
def get_total_pengeluaran_by_date(tanggal):
    pengeluaran_by_date = Pengeluaran.query.filter_by(tanggalPengeluaran=tanggal, userID=current_user.userID).all()
    return sum(item.jumlahPengeluaran for item in pengeluaran_by_date)



def get_total_pengeluaran_by_kategori_semua(user_id):
    total_pengeluaran_by_kategori_semua = {}

    kategori_data = ["Jajan", "Rokok", "Transportasi", "Rumah Tangga", "Bahan Dapur", "Lainnya"]

    for kategori_name in kategori_data:
        kategori = Kategori.query.filter_by(kategoriName=kategori_name).first()

        if kategori:
            kategori_id = kategori.kategoriID

            total_pengeluaran = Pengeluaran.query.filter(
                Pengeluaran.userID == user_id,
                Pengeluaran.kategoriPengeluaran == kategori_id
            ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar()

            total_pengeluaran_by_kategori_semua[kategori_name] = total_pengeluaran or 0

    return total_pengeluaran_by_kategori_semua


def get_total_pengeluaran_by_kategori_harian(user_id, date=None):
    total_pengeluaran_by_kategori_harian = {}

    kategori_data = ["Jajan", "Rokok", "Transportasi", "Rumah Tangga", "Bahan Dapur", "Lainnya"]

    for kategori_name in kategori_data:
        kategori = Kategori.query.filter_by(kategoriName=kategori_name).first()

        if kategori:
            kategori_id = kategori.kategoriID

            # Modify the query based on whether the date is provided
            if date:
                total_pengeluaran = Pengeluaran.query.filter(
                    Pengeluaran.userID == user_id,
                    Pengeluaran.kategoriPengeluaran == kategori_id,
                    Pengeluaran.tanggalPengeluaran == date
                ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar()
            else:
                total_pengeluaran = Pengeluaran.query.filter(
                    Pengeluaran.userID == user_id,
                    Pengeluaran.kategoriPengeluaran == kategori_id
                ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar()

            total_pengeluaran_by_kategori_harian[kategori_name] = total_pengeluaran or 0

    return total_pengeluaran_by_kategori_harian


def get_total_pengeluaran_by_kategori_mingguan(user_id, start_date, end_date):
    total_pengeluaran_by_kategori_mingguan = {}

    kategori_data = ["Jajan", "Rokok", "Transportasi", "Rumah Tangga", "Bahan Dapur", "Lainnya"]

    for kategori_name in kategori_data:
        kategori = Kategori.query.filter_by(kategoriName=kategori_name).first()

        if kategori:
            kategori_id = kategori.kategoriID

            # Modify the query based on the provided date range
            total_pengeluaran = Pengeluaran.query.filter(
                Pengeluaran.userID == user_id,
                Pengeluaran.kategoriPengeluaran == kategori_id,
                Pengeluaran.tanggalPengeluaran.between(start_date, end_date)
            ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar()

            total_pengeluaran_by_kategori_mingguan[kategori_name] = total_pengeluaran or 0

    return total_pengeluaran_by_kategori_mingguan


def get_total_pengeluaran_by_kategori_bulanan(user_id, start_date, end_date):
    total_pengeluaran_by_kategori_bulanan = {}

    kategori_data = ["Jajan", "Rokok", "Transportasi", "Rumah Tangga", "Bahan Dapur", "Lainnya"]

    for kategori_name in kategori_data:
        kategori = Kategori.query.filter_by(kategoriName=kategori_name).first()

        if kategori:
            kategori_id = kategori.kategoriID

            # Modify the query based on the provided date range
            total_pengeluaran = Pengeluaran.query.filter(
                Pengeluaran.userID == user_id,
                Pengeluaran.kategoriPengeluaran == kategori_id,
                Pengeluaran.tanggalPengeluaran.between(start_date, end_date)
            ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar()

            total_pengeluaran_by_kategori_bulanan[kategori_name] = total_pengeluaran or 0

    return total_pengeluaran_by_kategori_bulanan