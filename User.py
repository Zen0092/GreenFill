import shelve
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin):
    count_id_file = 'user_count.db'
    user_db_file = 'user.db'

    @staticmethod
    def load_count_id():
        with shelve.open(User.count_id_file) as db:
            return db.get('count_id', 0)

    @staticmethod
    def save_count_id(count_id):
        with shelve.open(User.count_id_file) as db:
            db['count_id'] = count_id

    def __init__(self, username, email, password):

        self.__id = User.load_count_id() + 1
        User.save_count_id(self.__id)

        self.__username = username
        self.__email = email
        self.__password_hash = generate_password_hash(password)

        self.save_to_db()

    def save_to_db(self):
        with shelve.open(User.user_db_file, writeback=True) as db:
            users = db.get('Users', {})  # so users is a dictionary
            users[self.__id] = {
                'username': self.__username,
                'email': self.__email,
                'password': self.__password_hash
            }
            # so the dictionary 'users' will look like :
            # {1:{'username': 'Alice', 'email': 'aaaa@gmail.com', 'password':'11111111'}

            db['Users'] = users

    def set_id(self, id):
        self.__id = id

    def set_username(self, username):
        self.__username = username

    def set_email(self, email):
        self.__email = email

    def set_password(self, password):
        self.__password_hash = generate_password_hash(password)

    def get_user_id(self):
        return self.__id

    def get_id(self):
        return str(self.__id)  # Flask-Login requires this to return a string

    def get_username(self):
        return self.__username

    def get_email(self):
        return self.__email

    def get_password(self):
        return self.__password_hash

    def verify_password(self, password):
        return check_password_hash(self.__password_hash, password)



