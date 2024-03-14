from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField("Возраст", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    position = StringField("Должность")
    speciality = StringField("Специальность")
    address = StringField("Адрес")
    submit = SubmitField('Зарегистрироваться')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class AddJobForm(FlaskForm):
    email = EmailField('Почта капитана команды', validators=[DataRequired()])
    job = StringField('Название работы', validators=[DataRequired()])
    work_size = IntegerField("Количество работы", validators=[DataRequired()])
    collaborators = StringField("Id участников", validators=[DataRequired()])
    start_date = DateField("Дата начала", validators=[DataRequired()])
    end_date = DateField("Дата окончания")
    is_finished = BooleanField('Работа закончена')
    submit = SubmitField('Создать')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')