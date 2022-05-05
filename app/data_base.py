from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    update_on = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean())
    roles = db.Column(db.String, default='Пользователь')
    admin = db.Column(db.Boolean())
    name = db.Column(db.String, default='Не указано')
    surname = db.Column(db.String, default='Не указано')
    date_of_birth = db.Column(db.DateTime)
    avatar = db.Column(db.LargeBinary)

    def __init__(self, login, email, password, roles, avatar):
        self.login = login
        self.email = email
        self.password = password
        self.roles = roles
        self.avatar = avatar

    @classmethod
    def get_user(cls, user_id=None, user_login=None):
        try:
            item = None
            if user_id:
                item = db.session.query(cls).filter(cls.id == user_id).first()
            elif user_login:
                item = db.session.query(cls).filter(cls.login == user_login).first()
            if not item:
                raise Exception("User not found")
        except Exception:
            db.session.rollback()
            raise
        return item

    def reg_user(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def update_user(cls, user_id, params):
        try:
            db.session.query(cls).filter(cls.id == user_id).update(params, synchronize_session='fetch')
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def __repr__(self):
        return '< User %r>' % self.id


class Art(db.Model):
    __tablename__ = 'arts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    hash_name = db.Column(db.String)
    art = db.Column(db.LargeBinary)
    author = db.Column(db.String, db.ForeignKey('users.login'))
    genre = db.Column(db.String, db.ForeignKey('genres.name'))
    create_on = db.Column(db.DateTime, default=datetime.now)
    prise = db.Column(db.Integer, nullable=None)
    rel_author = db.relationship("User", backref="arts")
    rel_genre = db.relationship('Genre', backref='arts')

    def append_art(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def get_arts(cls, art_id=None, login=None, hash_name=None):
        try:
            if login:
                arts = db.session.query(cls).filter(cls.author == login).order_by(cls.create_on).all()
            elif art_id:
                arts = db.session.query(cls).filter(cls.id == art_id).first()
            elif hash_name:
                arts = db.session.query(cls).filter(cls.hash_name == hash_name).first()
            else:
                arts = db.session.query(cls).order_by(cls.create_on).all()
        except Exception:
            db.session.rollback()
            raise
        return arts

    def delete_art(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def update_art(cls, hash_name, params):
        try:
            db.session.query(cls).filter(cls.hash_name == hash_name).update(params, synchronize_session='fetch')
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def __repr__(self):
        return '< Art %r>' % self.id


class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    @classmethod
    def get_genres(cls):
        try:
            items = db.session.query(cls).order_by(cls.name).all()
            if not items:
                raise Exception('Genre list is empty')
        except Exception:
            db.session.rollback()
            raise
        return items

    def __repr__(self):
        return '< Genre %r>' % self.id


class Gallery(db.Model):
    __tablename__ = 'gallery'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    art_id = db.Column(db.Integer)
    art = db.Column(db.LargeBinary)
    genre = db.Column(db.String)
    author = db.Column(db.String)
    hash_name = db.Column(db.String)
    rel = db.relationship("User", backref="gallery")

    def append_gallery(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def get_gallery(cls, user_id=None, hash_name=None):
        try:
            if user_id:
                arts = db.session.query(cls).filter(cls.user_id == user_id).order_by(cls.genre).all()
            else:
                arts = db.session.query(cls).filter(cls.hash_name == hash_name).first()
        except Exception:
            db.session.rollback()
            raise
        return arts

    def delete_gallery(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def __repr__(self):
        return '< Gallery %r>' % self.id


class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)


class Basket(db.Model):
    __tablename__ = 'baskets'
    id = db.Column(db.Integer, primary_key=True)
    art_id = db.Column(db.Integer)
    prise = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rel = db.relationship('User', backref='baskets')

    def new_basket(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def get_baskets(cls, art_id=None, user_id=None):
        try:
            if art_id:
                items = db.session.query(cls).filter(cls.art_id == art_id).all()
            elif user_id:
                items = db.session.query(cls).filter(cls.user_id == user_id).all()
        except Exception:
            db.session.rollback()
            raise
        return items

    def delete_basket(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def __repr__(self):
        return '<Basket %r>' % self.id


class Auction(db.Model):
    __tablename__ = 'auctions'
    id = db.Column(db.Integer, primary_key=True)
