import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, send_from_directory
from app.config import Config
from app.forms import LoginForm, RegistrationForm, NewNamesForm, NewEmailForm, NewLoginForm, NewPasswordForm,\
    NewAvatarForm, ArtForm, ArtUpdateForm, AdminLoginForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from app.data_base import db, User, Art, Genre, Basket, Gallery
from werkzeug.security import generate_password_hash, check_password_hash
from app.admin import admin
from werkzeug.utils import secure_filename
import hashlib


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db.init_app(app)
admin.init_app(app)
with app.app_context():
    db.create_all()
    # db.session.add(User(login='zxc_ded2001', password='228_ghoul_1337', roles='ADMIN'))
    # db.session.commit()


def create_hash_img_title(title):
    hash_first_lvl = generate_password_hash(title)
    hsh_final_lvl = hashlib.md5(hash_first_lvl.encode('utf-8'))
    return hsh_final_lvl.hexdigest()


def add_in_basket(art_id, url):
    art = Art.get_arts(art_id=art_id)
    basket = Basket(art_id=art.id, prise=art.prise, user_id=current_user.id)
    basket.new_basket()
    flash('Товар добавлен в корзину', 'message')
    return redirect(url)


def finish_buy(basket_info):
    new_arts = []
    for basket_art in basket_info:
        art = Art.get_arts(art_id=basket_art.art_id)
        new_arts.append(art)
        basket_art.delete_basket()
    for art_info in new_arts:
        shutil.copy(
            os.path.join('static/img/shop_art', f'{art_info.hash_name}.png'),
            os.path.join(f'static/img/user_art/User{current_user.id}_{current_user.login}',
                         f'{current_user.id}{art_info.hash_name}.png')
        )
        query = Gallery(user_id=current_user.id, art_id=art_info.id, art=art_info.art,
                        genre=art_info.genre, author=art_info.author, hash_name=str(current_user.id)+art_info.hash_name)
        query.append_gallery()
    return True


@login_manager.user_loader
def load_user(user_id):
    return User.get_user(user_id=user_id)


@app.route('/AsAp/', methods=['POST', 'GET'])
def admin_panel():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.login.data == 'zxc_ded2001' and form.password.data == '228_ghoul_1337':
            return redirect('/adwdawuais24s32a3f40/')
    return render_template('admin/admin_login.html', form=form)


@app.route('/')
@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html', user=current_user)


@app.route('/login', methods=['POST', 'GET'])
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


@app.route('/registration', methods=['POST', 'GET'])
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
            return redirect(url_for('login'))
        except Exception as e:
            return f"Registration action failed with error: {e}"
    return render_template('authorization/registration.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    user = current_user
    if user.roles == 'Автор':
        arts = db.session.query(Art).filter(Art.author == user.login).all()
    else:
        arts = db.session.query(Gallery).filter(Gallery.user_id == user.id).all()
    return render_template('profile/profile.html', user=user, arts=arts, role=user.roles)


@app.route('/user_avatar')
@app.route('/user_avatar/<int:user_id>')
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


@app.route('/profile/config', methods=['POST', 'GET'])
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
        return redirect(url_for('profile', id=current_user.id))

    if email_form.validate_on_submit():
        User.update_user(user_id=current_user.id, params={'email': email_form.email.data})
        return redirect(url_for('profile', id=current_user.id))

    if login_form.validate_on_submit():
        User.update_user(user_id=current_user.id, params={'login': login_form.login.data})
        return redirect(url_for('profile', id=current_user.id))

    if password_form.validate_on_submit():
        if check_password_hash(current_user.password, password_form.password.data):
            password = generate_password_hash(password_form.new_password.data)
            User.update_user(user_id=current_user.id, params={'password': password})
            return redirect(url_for('profile', id=current_user.id))

    if avatar_form.validate_on_submit():
        filename = secure_filename(avatar_form.avatar.data.filename)
        avatar_form.avatar.data.save(f'static/img/{filename}')
        with app.open_resource(app.root_path + url_for('static', filename=f'img/{filename}'), "rb") as file:
            img = file.read()
        User.update_user(user_id=current_user.id, params={'avatar': img})
        os.remove(os.path.join('static/img/', filename))
        return redirect(url_for('profile', id=current_user.id))
    return render_template('profile/profile_conf.html', user=user, name_form=name_form, email_form=email_form,
                           login_form=login_form, password_form=password_form, avatar_form=avatar_form)


@app.route('/add_art', methods=["POST", "GET"])
@login_required
def add_art():
    user = current_user
    genres = Genre.get_genres()
    genres_list = [(genre.name, genre.name) for genre in genres]
    form = ArtForm()
    form.genre.choices = genres_list
    if form.validate_on_submit():
        try:
            hash_name = create_hash_img_title(form.name.data)
            filename = secure_filename(f'{hash_name}.png')
            form.art.data.save(f'static/img/shop_art/{filename}')
            with app.open_resource(app.root_path + url_for('static', filename=f'img/shop_art/{filename}'), "rb") as f:
                art = f.read()
            new_art = Art(name=form.name.data, hash_name=hash_name, art=art,
                          author=current_user.login, genre=form.genre.data, prise=form.prise.data)
            new_art.append_art()
            return redirect(url_for('gallery'))
        except Exception as e:
            return f"Append new art action is failed with error: {e}"
    return render_template('author/add_art.html', user=user, form=form)


@app.route('/gallery')
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


@app.route('/show_art/<string:hash>')
@app.route('/show_gallery/<string:hash_g>')
@login_required
def show_art(hash=None, hash_g=None):
    if hash:
        art = Art.get_arts(hash_name=hash)
        art_obj = make_response(art.art)
        art_obj.headers['Content-Type'] = 'image'
        return art_obj
    elif hash_g:
        art_g = Gallery.get_gallery(hash_name=hash_g)
        art_obj = make_response(art_g.art)
        art_obj.headers['Content-Type'] = 'image'
        return art_obj


@app.route('/delete_art/<string:hash>')
@app.route('/delete_art_gallery/<string:hash_g>')
@login_required
def delete_art(hash=None, hash_g=None):
    try:
        if hash:
            art = Art.get_arts(hash_name=hash)
            os.remove(os.path.join('static/img/shop_art', f'{art.hash_name}.png'))
            art_in_basket = Basket.get_baskets(art.id)
            for art_fd in art_in_basket:
                art_fd.delete_basket()
            art.delete_art()
            return redirect(url_for('gallery'))
        elif hash_g:
            art_g = Gallery.get_gallery(hash_name=hash_g)
            os.remove(os.path.join(f'static/img/user_art/User{current_user.id}_{current_user.login}',
                                f'{art_g.hash_name}.png'))
            art_g.delete_gallery()
            return redirect(url_for('gallery'))
    except Exception as e:
        return f"Delete art action is failed with error: {e}"


@app.route('/download/<string:hash>')
@app.route('/download_gallery/<string:hash_g>')
@login_required
def download(hash=None, hash_g=None):
    try:
        if hash:
            art = Art.get_arts(hash_name=hash)
            return send_from_directory('static/img/shop_art', f'{art.hash_name}.png', as_attachment=True)
        elif hash_g:
            art_g = Gallery.get_gallery(hash_name=hash_g)
            return send_from_directory(f'static/img/user_art/User{current_user.id}_{current_user.login}',
                                       f'{art_g.hash_name}.png', as_attachment=True)
    except Exception as e:
        return f"Download art action is failed with error: {e}"


@app.route('/gallery/update/<string:hash>', methods=['POST', 'GET'])
@login_required
def art_update(hash):
    art = Art.get_arts(hash_name=hash)
    form = ArtUpdateForm(new_name=art.name, genre=art.genre, prise=art.prise)
    form.genre.choices = [(genre.name, genre.name) for genre in Genre.get_genres()]
    if form.is_submitted():
        Art.update_art(hash_name=hash, params={'name': form.new_name.data,
                                               'genre': form.genre.data,
                                               'prise': form.prise.data})
        return redirect(url_for('gallery'))
    return render_template('author/art_settings.html', form=form, user=current_user)


@app.route('/shop', methods=['POST', 'GET'])
@app.route('/shop/<int:page>', methods=['POST', 'GET'])
@app.route('/shop/categories/<string:genre>', methods=['POST', 'GET'])
@app.route('/shop/categories/<string:genre>/<int:page>', methods=['POST', 'GET'])
@app.route('/shop/authors/<string:author>', methods=['POST', 'GET'])
@app.route('/shop/authors/<string:author>/<int:page>', methods=['POST', 'GET'])
@app.route('/shop/authors/<string:author>/<string:genre>', methods=['POST', 'GET'])
@app.route('/shop/authors/<string:author>/<string:genre>/<int:page>', methods=['POST', 'GET'])
@login_required
def shop(page=1, genre=None, author=None):
    if request.method == 'POST':
        try:
            if request.form['submit_name'] == 'add_in_basket':
                add_in_basket(request.form['add_in_basket'], request.path)
        except:
            search_word = request.form['search_word']
            return redirect(url_for('search', search_word=search_word, genre_name=genre, author_name=author))
    if genre and author:
        art = db.session.query(Art).filter(Art.genre == genre, Art.author == author).order_by(Art.create_on).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    elif genre:
        art = db.session.query(Art).filter(Art.genre == genre).order_by(Art.create_on).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    elif author:
        art = db.session.query(Art).filter(Art.author == author).order_by(Art.create_on).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    else:
        art = db.session.query(Art).order_by(Art.create_on).paginate(page, app.config['POSTS_PER_PAGE'], False)
    genres = Genre.get_genres()
    basket_info = Basket.get_baskets(user_id=current_user.id)
    arts_in_basket_id = [item.art_id for item in basket_info]
    return render_template('shop/shop.html', user=current_user, art=art, genres=genres, author_section=author,
                           genre_section=genre, basket_info=basket_info, basket_arts=arts_in_basket_id)


@app.route("/shop/search/", methods=['POST', 'GET'])
@app.route('/shop/search/<string:search_word>', methods=['POST', 'GET'])
@app.route('/shop/search/<string:search_word>/<int:page>', methods=['POST', 'GET'])
@app.route('/shop/search/category/<string:genre_name>/<string:search_word>', methods=['POST', 'GET'])
@app.route('/shop/search/category/<string:genre_name>/<string:search_word>/<int:page>', methods=['POST', 'GET'])
@app.route('/shop/search/author/<string:author_name>/<string:search_word>', methods=['POST', 'GET'])
@app.route('/shop/search/author/<string:author_name>/<string:search_word>/<int:page>', methods=['POST', 'GET'])
@app.route('/shop/search/<string:author_name>/<string:genre_name>/<string:search_word>', methods=['POST', 'GET'])
@app.route('/shop/search/<string:author_name>/<string:genre_name>/<string:search_word>/<int:page>', methods=['POST',
                                                                                                             'GET'])
@login_required
def search(search_word=None, page=1, genre_name=None, author_name=None, search_active=True):
    if request.method == 'POST':
        try:
            if request.form['submit_name'] == 'add_in_basket':
                add_in_basket(request.form['add_in_basket'], request.path)
        except:
            search_word = request.form['search_word']
    if not search_word:
        result_search = db.session.query(Art).order_by(Art.create_on)\
            .paginate(page, app.config['POSTS_PER_PAGE'], False)
    elif genre_name and author_name:
        result_search = db.session.query(Art).filter(Art.name == search_word,
                                                     Art.genre == genre_name,
                                                     Art.author == author_name).order_by(Art.create_on)\
                                            .paginate(page, app.config['POSTS_PER_PAGE'], False)
    elif genre_name:
        result_search = db.session.query(Art).filter(Art.name == search_word,
                                                     Art.genre == genre_name).order_by(Art.create_on)\
            .paginate(page, app.config['POSTS_PER_PAGE'], False)
    elif author_name:
        result_search = db.session.query(Art).filter(Art.name == search_word,
                                                     Art.author == author_name).order_by(Art.create_on)\
            .paginate(page, app.config['POSTS_PER_PAGE'], False)
    else:
        result_search = db.session.query(Art).filter(Art.name == search_word).order_by(Art.create_on)\
            .paginate(page, app.config['POSTS_PER_PAGE'], False)
    genres = Genre.get_genres()
    basket_info = Basket.get_baskets(user_id=current_user.id)
    arts_in_basket_id = [item.art_id for item in basket_info]
    return render_template('shop/shop.html', user=current_user, art=result_search, genres=genres,
                           genre_section=genre_name, author_section=author_name,
                           search_active=search_active, search_word=search_word,
                           basket_info=basket_info, basket_arts=arts_in_basket_id)


@app.route('/shop/all_categories')
@app.route('/shop/all_categories/<string:author>')
@login_required
def categories(author=None):
    genres = Genre.get_genres()
    return render_template('shop/genre_section.html', user=current_user, genres=genres, author_section=author)


@app.route('/shop/authors', methods=['POST', 'GET'])
@login_required
def authors():
    if request.method == 'POST':
        author_name = request.form['author_name']
        author = db.session.query(User).filter(User.login == author_name, User.roles == 'Автор').all()
        return render_template('shop/author_section.html', user=current_user, authors=author)
    author = db.session.query(User).filter(User.roles == 'Автор').order_by(User.created_on).all()
    return render_template('shop/author_section.html', user=current_user, authors=author)


@app.route('/basket', methods=['POST', 'GET'])
@app.route('/basket/delete/<int:art_id>')
@login_required
def basket(art_id=None):
    if request.method == 'POST':
        basket_items = db.session.query(Basket).filter(Basket.user_id == current_user.id).order_by(Basket.prise).all()
        finish_buy(basket_items)
        return redirect('/gallery')
    if art_id:
        item_for_delete = db.session.query(Basket).filter(Basket.art_id == art_id).first()
        item_for_delete.delete_basket()
        return redirect(url_for('basket'))
    basket_items = db.session.query(Basket).filter(Basket.user_id == current_user.id).order_by(Basket.prise).all()
    arts_in_basket = []
    final_prise = 0
    for basket_item in basket_items:
        art = db.session.query(Art).get(basket_item.art_id)
        arts_in_basket.append(art)
        final_prise += art.prise
    return render_template('shop/basket.html', user=current_user, arts=arts_in_basket, final_prise=final_prise)


if __name__ == '__main__':
    app.run()


# Добавить артам хэш который формируется по бинарному значению арта, чтобыы нельзя было загружать один и тот же арт
