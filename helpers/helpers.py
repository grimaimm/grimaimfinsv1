from models import User

# def get_user_fullname(username):
#     user = User.query.filter_by(username=username).first()
#     return user.fullname if user else "Guest"  # Default to "Guest" if user not found

def get_userInfo(username):
    user = User.query.filter_by(username=username).first()
    if user:
        user_info = {
            "userID": user.userID,
            "username": user.username,
            "fullname": user.fullname,
            "password": user.password,  # Note: Handle password carefully and consider not exposing it in the frontend
            "userPicture": user.userPicture
        }
    else:
        user_info = {
            "userID": None,
            "username": None,
            "fullname": None,
            "password": None,
            "userPicture": None
        }

    return user_info
