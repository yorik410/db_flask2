from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask
from flask import render_template, redirect
from data import db_session
from data.users import User
from data.news import News
from data.login_form import LoginForm, RegisterForm, AddJobForm, NewsForm, AddDepartmentForm
from data.jobs import Jobs
from data.departments import Department


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()

    def set_team_leader_name(job):
        u = db_sess.query(User).filter(User.id == job.team_leader).first()
        job.team_leader_name = f"{u.surname} {u.name}"
        return job
    # if current_user.is_authenticated:
    #     news = db_sess.query(News).filter(
    #         (News.user == current_user) | (News.is_private != True))
    # else:
    #     news = db_sess.query(News).filter(News.is_private != True)
    jobs = list(map(set_team_leader_name, db_sess.query(Jobs).all()))
    return render_template("index.html", news=jobs)


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            address=form.address.data,
            speciality=form.speciality.data,
            position=form.position.data
        )
        form.set_password(form.password.data)
        user.set_password(form.hashed_password)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if not current_user.is_authenticated:
        return 'Доступ запрещен', 403
    form = AddJobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if len(db_sess.query(User).filter(User.email == form.email.data).all()) == 0:
            return render_template('add_job.html', title='Добавить работу',
                                   form=form,
                                   message="Нельзя добавить незарегистрированного капитана")
        job = Jobs(
            team_leader=db_sess.query(User).filter(User.email == form.email.data).first().id,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_finished=form.is_finished.data
        )
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('add_job.html', title='Добавить работу', form=form)


@app.route("/departments")
def departments():
    db_sess = db_session.create_session()

    def set_team_leader_name(job):
        u = db_sess.query(User).filter(User.id == job.chief).first()
        job.chief_name = f"{u.surname} {u.name}"
        return job
    departments_list = list(map(set_team_leader_name, db_sess.query(Department).all()))
    return render_template('departments.html', title='Отделы', departments=departments_list)


@app.route('/add_department', methods=['GET', 'POST'])
def add_departments():
    if not current_user.is_authenticated:
        return 'Доступ запрещен', 403
    form = AddDepartmentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if len(db_sess.query(User).filter(User.email == form.email.data).all()) == 0:
            return render_template('add_job.html', title='Добавить отдел',
                                   form=form,
                                   message="Нельзя добавить незарегистрированного капитана")
        dep = Department(
            title=form.title.data,
            chief=db_sess.query(User).filter(User.email == form.chief.data).first().id,
            members=form.members.data,
            email=form.email.data,
        )
        db_sess.add(dep)
        db_sess.commit()
        return redirect('/departments')
    return render_template('add_department.html', title='Добавить отдел', form=form)


@app.route('/edit_job/<int:id>', methods=['GET', 'POST'])
def edit_job(id:int):
    db_sess = db_session.create_session()
    if not (current_user.is_authenticated and
            (current_user in (1, db_sess.query(Jobs).filter(Jobs.id == id).team_leader))):
        return 'Доступ запрещен', 403
    form = AddJobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if len(db_sess.query(User).filter(User.email == form.email.data).all()) == 0:
            return render_template('add_job.html', title='Редактировать работу',
                                   form=form,
                                   message="Нельзя добавить незарегистрированного капитана")
        job = db_sess.query(Jobs).filter(Jobs.id == id)
        job.team_leader = db_sess.query(User).filter(User.email == form.email.data).first().id
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.start_date = form.start_date.data
        job.end_date = form.end_date.data
        job.is_finished = form.is_finished.data
        db_sess.commit()
        return redirect('/')
    return render_template('add_job.html', title='Редактировать работу', form=form)


@app.route('/delete_job/<int:id>')
def delete_job(id):
    db_sess = db_session.create_session()
    if not (current_user.is_authenticated and
            (current_user in (1, db_sess.query(Jobs).filter(Jobs.id == id).team_leader))):
        return 'Доступ запрещен', 403
    db_sess.query(Jobs).filter(Jobs.id == id).delete()
    db_sess.commit()
    return redirect("/")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/mars_explorer.db")
    app.run(port=8080, host='127.0.0.1')