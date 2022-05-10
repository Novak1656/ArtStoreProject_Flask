class Config(object):
    DEBUG = True
    SECRET_KEY = 'SECRET_KEY'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data_base.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN_SWATCH = 'cerulean'
    # HOST = '192.168.0.17'
    # PORT = 5000
    POSTS_PER_PAGE = 9
