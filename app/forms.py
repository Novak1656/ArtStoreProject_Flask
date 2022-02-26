from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, SelectField, DateField, IntegerField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed


class LoginForm(FlaskForm):
    login = StringField('Логин: ', validators=[InputRequired(), Length(min=3, max=25, message="Неверный логин")],
                        render_kw={"placeholder": "Введите логин...", "class": "form-control"})
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=8, max=16, message="Неверный пароль")],
                             render_kw={"placeholder": "Введите пароль...", "class": "form-control"})
    remember = BooleanField("Запомнить меня", default=False)
    submit = SubmitField("Войти", render_kw={"class": "btn btn-success  w-50"})


class RegistrationForm(FlaskForm):
    login = StringField('Логин: ', validators=[InputRequired(), Length(min=3, max=25, message="Логин должен быть от 3 до 25 символов")],
                        render_kw={"placeholder": "Придумайте логин...", "class": "form-control"})
    email = EmailField('Электронная почта: ', validators=[InputRequired(), Email("Некорректный адрес электронной почты")],
                       render_kw={"placeholder": "Введите адрес электронной почты...", "class": "form-control"})
    password = PasswordField('Пароль: ', validators=[InputRequired(), Length(min=8, max=16, message="Пароль должен быть от 8 до 16 символов")],
                             render_kw={"placeholder": "Придумайте пароль...", "class": "form-control"})
    chek_password = PasswordField('Подтвердите пароль: ', validators=[InputRequired(), EqualTo('password', message="Пароли не совпадают")],
                                  render_kw={"placeholder": "Введите пароль ещё раз...", "class": "form-control"})
    role = SelectField('Я: ', choices=[('Пользователь', 'Пользователь'), ('Автор', 'Автор')], validators=[InputRequired()],
                       render_kw={"placeholder": "Автор/Пользователь", "class": "form-control"})
    submit = SubmitField('Зарегестрироваться', render_kw={"class": "btn btn-success"})


class NewNamesForm(FlaskForm):
    name = StringField('Имя:', validators=[InputRequired()],
                       render_kw={"placeholder": "Введите ваше имя...", "class": "form-control"})
    surname = StringField('Фамилия:', validators=[InputRequired()],
                          render_kw={"placeholder": "Введите вашу фамилию...", "class": "form-control"})
    date_of_birth = DateField('Дата рождения:', validators=[InputRequired()],
                              render_kw={"placeholder": "Введите вашу дату рождения...", "class": "form-control"})
    submit = SubmitField('Сохранить изменения', render_kw={"class": "btn btn-success"})


class NewAvatarForm(FlaskForm):
    avatar = FileField('Загрузить изображение:', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')],
                       render_kw={"class": "form-control"})
    submit = SubmitField('Сохранить изменения', render_kw={"class": "btn btn-success"})


class NewEmailForm(FlaskForm):
    email = EmailField('Электронная почта:', validators=[InputRequired()],
                       render_kw={"placeholder": "Введите адрес электронной почты...", "class": "form-control"})
    submit = SubmitField('Сохранить изменения', render_kw={"class": "btn btn-success"})


class NewLoginForm(FlaskForm):
    login = StringField('Логин:', validators=[InputRequired(), Length(min=3, max=25)],
                        render_kw={"placeholder": "Введите новый логин...", "class": "form-control"})
    submit = SubmitField('Сохранить изменения', render_kw={"class": "btn btn-success"})


class NewPasswordForm(FlaskForm):
    password = PasswordField('Текущий пароль:', validators=[InputRequired(), Length(min=8, max=16)],
                             render_kw={"placeholder": "Введите пароль...", "class": "form-control"})
    new_password = PasswordField('Новый пароль:', validators=[InputRequired(), Length(min=8, max=16)],
                                 render_kw={"placeholder": "Введите новый пароль...", "class": "form-control"})
    chek_new_password = PasswordField('Подтверждение пароля:', validators=[InputRequired(), EqualTo('new_password', message="Пароли не совпадают")],
                                      render_kw={"placeholder": "Введите новый пароль ещё раз...",
                                                 "class": "form-control"})
    submit = SubmitField('Сохранить изменения', render_kw={"class": "btn btn-success"})


class ArtForm(FlaskForm):
    art = FileField('Загрузите арт', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')],
                    render_kw={"class": "form-control"})
    name = StringField('Название: ', validators=[InputRequired()],
                       render_kw={"placeholder": "Введите название для арта...", "class": "form-control"})
    genre = SelectField('Жанр: ', coerce=str, validators=[InputRequired()], render_kw={'class': 'form-control'})
    prise = IntegerField('Цена в руб.: ', validators=[InputRequired()], render_kw={'class': 'form-control'})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-success"})


class ArtUpdateForm(FlaskForm):
    new_name = StringField('Название:', render_kw={'class': 'form-control'})
    genre = SelectField('Жанр: ', coerce=str, render_kw={'class': 'form-control'})
    prise = IntegerField('Цена в руб.: ', render_kw={'class': 'form-control'})
    submit = SubmitField('Сохранить изменения', render_kw={'class': 'btn btn-success'})


class AdminLoginForm(FlaskForm):
    login = StringField('Логин:', validators=[InputRequired()], render_kw={'class': 'form-control'})
    password = PasswordField('Пароль:', validators=[InputRequired()], render_kw={'class': 'form-control'})
    submit = SubmitField('Войти', render_kw={'class': 'form-control btn btn-outline-success rounded'})
