from flask import redirect, render_template, Blueprint, make_response, url_for
from flask_login import login_required, current_user
from app.forms import NewLoginForm, NewPasswordForm, NewNamesForm, NewEmailForm, NewAvatarForm
from app.data_base import User, db, Art, Gallery
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app
import os

users = Blueprint('users', __name__)


@users.route('/profile')
@login_required
def profile():
    user = current_user
    if user.roles == 'Автор':
        arts = db.session.query(Art).filter(Art.author == user.login).all()
    else:
        arts = db.session.query(Gallery).filter(Gallery.user_id == user.id).all()
    return render_template('profile/profile.html', user=user, arts=arts, role=user.roles)


@users.route('/user_avatar')
@users.route('/user_avatar/<int:user_id>')
@login_required
def user_avatar(user_id=None):
    if user_id:
        user = User.get_user(user_id=user_id)
        avatar = make_response(user.avatar)
        avatar.headers['Content-Type'] = 'image'
        return avatar
    elif not user_id:
        avatar = make_response(current_user.avatar)
        avatar.headers['Content-Type'] = 'image'
        return avatar


@users.route('/profile/config', methods=['POST', 'GET'])
@login_required
def profile_config():
    user = current_user
    name_form = NewNamesForm()
    email_form = NewEmailForm()
    login_form = NewLoginForm()
    password_form = NewPasswordForm()
    avatar_form = NewAvatarForm()

    if name_form.validate_on_submit():
        params = {'name': name_form.name.data, 'surname': name_form.surname.data,
                  'date_of_birth': name_form.date_of_birth.data}
        User.update_user(user_id=current_user.id, params=params)
        return redirect(url_for('users.profile', id=current_user.id))

    if email_form.validate_on_submit():
        User.update_user(user_id=current_user.id, params={'email': email_form.email.data})
        return redirect(url_for('users.profile', id=current_user.id))

    if login_form.validate_on_submit():
        User.update_user(user_id=current_user.id, params={'login': login_form.login.data})
        return redirect(url_for('users.profile', id=current_user.id))

    if password_form.validate_on_submit():
        if check_password_hash(current_user.password, password_form.password.data):
            password = generate_password_hash(password_form.new_password.data)
            User.update_user(user_id=current_user.id, params={'password': password})
            return redirect(url_for('users.profile', id=current_user.id))

    if avatar_form.validate_on_submit():
        filename = secure_filename(avatar_form.avatar.data.filename)
        avatar_form.avatar.data.save(f'app/static/img/{filename}')
        with app.open_resource(app.root_path + url_for('static', filename=f'img/{filename}'), "rb") as file:
            img = file.read()
        User.update_user(user_id=current_user.id, params={'avatar': img})
        os.remove(os.path.join('app/static/img/', filename))
        return redirect(url_for('users.profile', id=current_user.id))
    return render_template('profile/profile_conf.html', user=user, name_form=name_form, email_form=email_form,
                           login_form=login_form, password_form=password_form, avatar_form=avatar_form)


@users.route('/gallery')
@login_required
def gallery():
    user = current_user
    if user.roles == 'Автор':
        arts = Art.get_arts(login=current_user.login)
        g_arts = Gallery.get_gallery(user_id=current_user.id)
        return render_template('gallery/author/gallery_a.html', user=user, arts=arts, g_arts=g_arts)
    else:
        arts = Gallery.get_gallery(user_id=current_user.id)
        return render_template('gallery/user/gallery_u.html', user=user, arts=arts)
