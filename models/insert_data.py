# from app import db, Kategori, Admin
from models import db
from models import Kategori, Admin

def insert_data_function():
    # Check if data already exists in Kategori table
    if not Kategori.query.first():
        kategori_data = ["Jajan", "Rokok", "Transportasi", "Rumah Tangga", "Bahan Dapur", "Lainnya"]
        for name in kategori_data:
            new_kategori = Kategori(kategoriName=name)
            db.session.add(new_kategori)

    # Check if data already exists in Admin table
    if not Admin.query.first():
        admin_data = ["Aim", "Dhian"]
        for name in admin_data:
            new_admin = Admin(adminName=name)
            db.session.add(new_admin)

    # Commit the changes
    db.session.commit()