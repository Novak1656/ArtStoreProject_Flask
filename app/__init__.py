from flask import Flask, render_template, redirect
from app.config import Config
from app.forms import LoginForm, RegistrationForm, NewNamesForm, NewEmailForm, NewLoginForm, NewPasswordForm,\
    NewAvatarForm, ArtForm, ArtUpdateForm, AdminLoginForm
from flask_login import LoginManager, login_required, current_user
from app.data_base import db, User, Art, Genre, Basket, Gallery
from app.admin import admin


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db.init_app(app)
admin.init_app(app)

with app.app_context():
    db.create_all()
    # db.session.add(User(login='acclrtrrr', password='1656_SS3_1656', roles='ADMIN'))
    # db.session.commit()

from app.roots.arts.views import arts
from app.roots.shop.views import main
from app.roots.authorization.views import authorization
from app.roots.users.views import users

app.register_blueprint(arts)
app.register_blueprint(main)
app.register_blueprint(authorization)
app.register_blueprint(users)


@app.route('/AsAp/', methods=['POST', 'GET'])
def admin_panel():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.login.data == 'acclrtrrr' and form.password.data == '1656_SS3_1656':
            return redirect('/adwdawuais24s32a3f40/')
    return render_template('admin/admin_login.html', form=form)


@app.route('/')
@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html', user=current_user)
