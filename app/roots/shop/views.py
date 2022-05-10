from flask import redirect, render_template, Blueprint, url_for, request, flash
from flask_login import login_required, current_user
from app.data_base import Art, Genre, Basket, db, User, Gallery
import shutil
import os
from app import app

main = Blueprint('main', __name__)


def add_in_basket(art_id, url):
    art = Art.get_arts(art_id=art_id)
    basket_item = Basket(art_id=art.id, prise=art.prise, user_id=current_user.id)
    basket_item.new_basket()
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
            os.path.join('app/static/img/shop_art', f'{art_info.hash_name}.png'),
            os.path.join(f'app/static/img/user_art/User{current_user.id}_{current_user.login}',
                         f'{current_user.id}{art_info.hash_name}.png')
        )
        query = Gallery(user_id=current_user.id, art_id=art_info.id, art=art_info.art,
                        genre=art_info.genre, author=art_info.author, hash_name=str(current_user.id)+art_info.hash_name)
        query.append_gallery()
    return True


@main.route('/shop', methods=['POST', 'GET'])
@main.route('/shop/<int:page>', methods=['POST', 'GET'])
@main.route('/shop/categories/<string:genre>', methods=['POST', 'GET'])
@main.route('/shop/categories/<string:genre>/<int:page>', methods=['POST', 'GET'])
@main.route('/shop/authors/<string:author>', methods=['POST', 'GET'])
@main.route('/shop/authors/<string:author>/<int:page>', methods=['POST', 'GET'])
@main.route('/shop/authors/<string:author>/<string:genre>', methods=['POST', 'GET'])
@main.route('/shop/authors/<string:author>/<string:genre>/<int:page>', methods=['POST', 'GET'])
@login_required
def shop(page=1, genre=None, author=None):
    if request.method == 'POST':
        try:
            if request.form['submit_name'] == 'add_in_basket':
                add_in_basket(request.form['add_in_basket'], request.path)
        except:
            search_word = request.form['search_word']
            return redirect(url_for('main.search', search_word=search_word, genre_name=genre, author_name=author))
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


@main.route("/shop/search/", methods=['POST', 'GET'])
@main.route('/shop/search/<string:search_word>', methods=['POST', 'GET'])
@main.route('/shop/search/<string:search_word>/<int:page>', methods=['POST', 'GET'])
@main.route('/shop/search/category/<string:genre_name>/<string:search_word>', methods=['POST', 'GET'])
@main.route('/shop/search/category/<string:genre_name>/<string:search_word>/<int:page>', methods=['POST', 'GET'])
@main.route('/shop/search/author/<string:author_name>/<string:search_word>', methods=['POST', 'GET'])
@main.route('/shop/search/author/<string:author_name>/<string:search_word>/<int:page>', methods=['POST', 'GET'])
@main.route('/shop/search/<string:author_name>/<string:genre_name>/<string:search_word>', methods=['POST', 'GET'])
@main.route('/shop/search/<string:author_name>/<string:genre_name>/<string:search_word>/<int:page>', methods=['POST',
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


@main.route('/shop/all_categories')
@main.route('/shop/all_categories/<string:author>')
@login_required
def categories(author=None):
    genres = Genre.get_genres()
    return render_template('shop/genre_section.html', user=current_user, genres=genres, author_section=author)


@main.route('/shop/authors', methods=['POST', 'GET'])
@login_required
def authors():
    if request.method == 'POST':
        author_name = request.form['author_name']
        author = db.session.query(User).filter(User.login == author_name, User.roles == 'Автор').all()
        return render_template('shop/author_section.html', user=current_user, authors=author)
    author = db.session.query(User).filter(User.roles == 'Автор').order_by(User.created_on).all()
    return render_template('shop/author_section.html', user=current_user, authors=author)


@main.route('/basket', methods=['POST', 'GET'])
@main.route('/basket/delete/<int:art_id>')
@login_required
def basket(art_id=None):
    if request.method == 'POST':
        basket_items = db.session.query(Basket).filter(Basket.user_id == current_user.id).order_by(Basket.prise).all()
        finish_buy(basket_items)
        return redirect('/gallery')
    if art_id:
        item_for_delete = db.session.query(Basket).filter(Basket.art_id == art_id).first()
        item_for_delete.delete_basket()
        return redirect(url_for('main.basket'))
    basket_items = db.session.query(Basket).filter(Basket.user_id == current_user.id).order_by(Basket.prise).all()
    arts_in_basket = []
    final_prise = 0
    for basket_item in basket_items:
        art = db.session.query(Art).get(basket_item.art_id)
        arts_in_basket.append(art)
        final_prise += art.prise
    return render_template('shop/basket.html', user=current_user, arts=arts_in_basket, final_prise=final_prise)
