from models import db, User, Pengeluaran, Pemasukan, Kategori, Admin
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import date, timedelta
import calendar
from datetime import date, datetime, timedelta

def get_total_pengeluaran_pemasukan_hari_ini(user_id, date):
    total_pengeluaran_hari_ini = Pengeluaran.query.filter(
        Pengeluaran.userID == user_id,
        Pengeluaran.tanggalPengeluaran == date
    ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar() or 0

    total_pemasukan_hari_ini = Pemasukan.query.filter(
        Pemasukan.userID == user_id,
        Pemasukan.tanggalPemasukan == date
    ).with_entities(func.sum(Pemasukan.jumlahPemasukan)).scalar() or 0

    return total_pengeluaran_hari_ini, total_pemasukan_hari_ini


def get_total_pengeluaran_pemasukan_mingguan(user_id, start_date, end_date):
    total_pengeluaran_mingguan = Pengeluaran.query.filter(
        Pengeluaran.userID == user_id,
        Pengeluaran.tanggalPengeluaran.between(start_date, end_date)
    ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar() or 0

    total_pemasukan_mingguan = Pemasukan.query.filter(
        Pemasukan.userID == user_id,
        Pemasukan.tanggalPemasukan.between(start_date, end_date)
    ).with_entities(func.sum(Pemasukan.jumlahPemasukan)).scalar() or 0

    return total_pengeluaran_mingguan, total_pemasukan_mingguan


def get_last_day_of_month(year, month):
    # Mendapatkan hari terakhir dari bulan
    end_of_month = calendar.monthrange(year, month)[1]
    end_of_month_date = date(year, month, end_of_month)

    return end_of_month_date

def get_total_pengeluaran_pemasukan_bulanan(user_id, month):
    start_of_month = month.replace(day=1)
    end_of_month = get_last_day_of_month(month.year, month.month)

    # Mendapatkan awal dan akhir bulan untuk bulan lalu
    start_of_last_month = start_of_month - timedelta(days=1)
    end_of_last_month = get_last_day_of_month(start_of_last_month.year, start_of_last_month.month)

    # Mendapatkan total pengeluaran bulan ini
    total_pengeluaran_bulan_ini = Pengeluaran.query.filter(
        Pengeluaran.userID == user_id,
        Pengeluaran.tanggalPengeluaran >= start_of_month,
        Pengeluaran.tanggalPengeluaran <= end_of_month
    ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar() or 0

    # Mendapatkan total pemasukan bulan ini
    total_pemasukan_bulan_ini = Pemasukan.query.filter(
        Pemasukan.userID == user_id,
        Pemasukan.tanggalPemasukan >= start_of_month,
        Pemasukan.tanggalPemasukan <= end_of_month
    ).with_entities(func.sum(Pemasukan.jumlahPemasukan)).scalar() or 0

    # Mendapatkan total pengeluaran bulan lalu
    total_pengeluaran_bulan_lalu = Pengeluaran.query.filter(
        Pengeluaran.userID == user_id,
        Pengeluaran.tanggalPengeluaran >= start_of_last_month,
        Pengeluaran.tanggalPengeluaran <= end_of_last_month
    ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar() or 0

    # Mendapatkan total pemasukan bulan lalu
    total_pemasukan_bulan_lalu = Pemasukan.query.filter(
        Pemasukan.userID == user_id,
        Pemasukan.tanggalPemasukan >= start_of_last_month,
        Pemasukan.tanggalPemasukan <= end_of_last_month
    ).with_entities(func.sum(Pemasukan.jumlahPemasukan)).scalar() or 0

    return total_pengeluaran_bulan_ini, total_pemasukan_bulan_ini, total_pengeluaran_bulan_lalu, total_pemasukan_bulan_lalu

# Function to get yearly totals
def get_total_pengeluaran_pemasukan_tahunan(user_id, year):
    start_of_year = date(year, 1, 1)
    end_of_year = date(year, 12, 31)

    total_pengeluaran_tahunan = Pengeluaran.query.filter(
        Pengeluaran.userID == user_id,
        Pengeluaran.tanggalPengeluaran >= start_of_year,
        Pengeluaran.tanggalPengeluaran <= end_of_year
    ).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar()

    total_pemasukan_tahunan = Pemasukan.query.filter(
        Pemasukan.userID == user_id,
        Pemasukan.tanggalPemasukan >= start_of_year,
        Pemasukan.tanggalPemasukan <= end_of_year
    ).with_entities(func.sum(Pemasukan.jumlahPemasukan)).scalar()

    return total_pengeluaran_tahunan or 0, total_pemasukan_tahunan or 0

def get_total_transaksi(user_id):
    total_pemasukan = Pemasukan.query.filter_by(userID=user_id).with_entities(func.sum(Pemasukan.jumlahPemasukan)).scalar()
    total_pengeluaran = Pengeluaran.query.filter_by(userID=user_id).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar()

    return total_pemasukan or 0, total_pengeluaran or 0


def get_total_transaksi_by_admin(user_id, admin_name):
    admin = Admin.query.filter_by(adminName=admin_name).first()

    if admin:
        admin_id = admin.adminID

        total_pengeluaran = Pengeluaran.query.filter_by(adminName=admin_id, userID=user_id).with_entities(func.sum(Pengeluaran.jumlahPengeluaran)).scalar() or 0
        total_pemasukan = Pemasukan.query.filter_by(adminName=admin_id, userID=user_id).with_entities(func.sum(Pemasukan.jumlahPemasukan)).scalar() or 0

        return total_pengeluaran, total_pemasukan
    else:
        return 0, 0

from sqlalchemy.sql import func

def get_monthly_data(user_id, year):
    monthly_data = []

    for month in range(1, 13):
        start_date = f"{year}-{month:02d}-01"
        end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')

        total_pengeluaran = (
            db.session.query(func.coalesce(func.sum(Pengeluaran.jumlahPengeluaran), 0))
            .filter(
                Pengeluaran.userID == user_id,
                Pengeluaran.tanggalPengeluaran.between(start_date, end_date)
            )
            .scalar()
        )

        total_pemasukan = (
            db.session.query(func.coalesce(func.sum(Pemasukan.jumlahPemasukan), 0))
            .filter(
                Pemasukan.userID == user_id,
                Pemasukan.tanggalPemasukan.between(start_date, end_date)
            )
            .scalar()
        )

        monthly_data.append({
            "month": month,
            "total_pengeluaran": total_pengeluaran,
            "total_pemasukan": total_pemasukan
        })

    return monthly_data
