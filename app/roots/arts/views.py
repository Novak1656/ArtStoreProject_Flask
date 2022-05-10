from flask import redirect, render_template, Blueprint, make_response, url_for, send_from_directory
from flask_login import login_required, current_user
from app.forms import ArtForm, ArtUpdateForm
from app.data_base import Art, Gallery, Genre, Basket
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import hashlib
from app import app
import os

arts = Blueprint('arts', __name__)


def create_hash_img_title(title):
    hash_first_lvl = generate_password_hash(title)
    hsh_final_lvl = hashlib.md5(hash_first_lvl.encode('utf-8'))
    return hsh_final_lvl.hexdigest()


@arts.route('/add_art', methods=["POST", "GET"])
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
            form.art.data.save(f'app/static/img/shop_art/{filename}')
            with app.open_resource(app.root_path + url_for('static', filename=f'img/shop_art/{filename}'), "rb") as f:
                art = f.read()
            new_art = Art(name=form.name.data, hash_name=hash_name, art=art,
                          author=current_user.login, genre=form.genre.data, prise=form.prise.data)
            new_art.append_art()
            return redirect(url_for('users.gallery'))
        except Exception as e:
            return f"Append new art action is failed with error: {e}"
    return render_template('author/add_art.html', user=user, form=form)


@arts.route('/show_art/<string:hash>')
@arts.route('/show_gallery/<string:hash_g>')
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


@arts.route('/delete_art/<string:hash>')
@arts.route('/delete_art_gallery/<string:hash_g>')
@login_required
def delete_art(hash=None, hash_g=None):
    try:
        if hash:
            art = Art.get_arts(hash_name=hash)
            os.remove(os.path.join('app/static/img/shop_art', f'{art.hash_name}.png'))
            art_in_basket = Basket.get_baskets(art.id)
            for art_fd in art_in_basket:
                art_fd.delete_basket()
            art.delete_art()
            return redirect(url_for('users.gallery'))
        elif hash_g:
            art_g = Gallery.get_gallery(hash_name=hash_g)
            os.remove(os.path.join(f'app/static/img/user_art/User{current_user.id}_{current_user.login}',
                                f'{art_g.hash_name}.png'))
            art_g.delete_gallery()
            return redirect(url_for('users.gallery'))
    except Exception as e:
        return f"Delete art action is failed with error: {e}"


@arts.route('/download/<string:hash>')
@arts.route('/download_gallery/<string:hash_g>')
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


@arts.route('/gallery/update/<string:hash>', methods=['POST', 'GET'])
@login_required
def art_update(hash):
    art = Art.get_arts(hash_name=hash)
    form = ArtUpdateForm(new_name=art.name, genre=art.genre, prise=art.prise)
    form.genre.choices = [(genre.name, genre.name) for genre in Genre.get_genres()]
    if form.is_submitted():
        Art.update_art(hash_name=hash, params={'name': form.new_name.data,
                                               'genre': form.genre.data,
                                               'prise': form.prise.data})
        return redirect(url_for('users.gallery'))
    return render_template('author/art_settings.html', form=form, user=current_user)
