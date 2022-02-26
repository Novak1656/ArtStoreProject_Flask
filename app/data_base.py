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

    def __repr__(self):
        return '< Art %r>' % self.id


class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

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

    def __repr__(self):
        return '<Basket %r>' % self.id


class Auction(db.Model):
    __tablename__ = 'auctions'
    id = db.Column(db.Integer, primary_key=True)
