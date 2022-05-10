from app.data_base import User
from app import login_manager
from flask_login import login_required, login_user, logout_user, current_user
from flask import Blueprint, redirect, render_template, flash, url_for
from app.forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
import os

authorization = Blueprint('authorization', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.get_user(user_id=user_id)


@authorization.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.get_user(user_login=form.login.data)
            if check_password_hash(user.password, form.password.data):
                rm = form.remember.data
                login_user(user, remember=rm)
                return redirect(url_for('menu'))
        except Exception:
            flash("Неверный логин/пароль", "error")
            raise
    return render_template('authorization/login.html', form=form)


@authorization.route('/registration', methods=['POST', 'GET'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            if form.password.data != form.chek_password.data:
                flash('Пароли не совпадают', 'error')
            password = generate_password_hash(form.password.data)
            with app.open_resource(app.root_path + url_for('static', filename='img/avatar.jpg'), "rb") as file:
                img = file.read()
            user = User(login=form.login.data, email=form.email.data,
                        password=password, roles=form.role.data, avatar=img)
            user.reg_user()
            os.mkdir(app.root_path + url_for('static', filename=f"img/user_art/User{user.id}_{user.login}"))
            return redirect(url_for('authorization.login'))
        except Exception as e:
            return f"Registration action failed with error: {e}"
    return render_template('authorization/registration.html', form=form)


@authorization.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('authorization.login'))
