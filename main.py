from flask import Flask, render_template, url_for, request, redirect, make_response, session, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from data import db_session
from data.users import User
from data.forms import Forms
from data.answer import Answer
from data.questions import Question
from forms.user import RegisterForm
from forms.loginform import LoginForm
from forms.apply import Application
from forms.news import NewsForm
from forms.answer import NewAnswer
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/blogs.db")
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@app.route('/home')
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(Forms).filter(Forms.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(Forms).filter(
            (Forms.user == current_user) | (Forms.is_private != True))
    else:
        news = db_sess.query(Forms).filter(Forms.is_private != True)
    return render_template("index.html", title='Главная', news=news)


@app.route('/about')
def about():
    return render_template('about.html', title='О нас')


@app.route('/create-form', methods=['POST', 'GET'])
def create_from():
    return render_template('create-form.html', title='Создать форму')


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


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    db_sess = db_session.create_session()
    news = db_sess.query(Forms).filter(Forms.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(Forms).filter(
            (Forms.user == current_user) | (Forms.is_private != True))
    else:
        news = db_sess.query(Forms).filter(Forms.is_private != True)
    return render_template('account.html', title='Личный кабинет', news=news)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = Forms()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()

        return redirect(url_for('apply', n=news.content, title=news.title))
    return render_template('news.html', title='Добавление формы',
                           form=form)


@app.route('/apply/<title>/<int:n>', methods=['GET', 'POST'])
def apply(title, n):
    a = []
    for i in range(n):
        a.append(Application())
    db_sess = db_session.create_session()
    form = db_sess.query(Forms).filter(Forms.title == title,
                                       Forms.user == current_user
                                       ).first()
    if a[-1].questions.data:
        for i in a:
            print(i, i.questions, i.questions.data)
            questions1 = Question()
            questions1.question = i.questions.data
            form.questions.append(questions1)
            db_sess.merge(form)
            db_sess.commit()
        return redirect('/account')

    return render_template('applicationForm.html', title='Заполнение формы',
                           form=a, n=n)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Forms).filter(Forms.id == id,
                                       Forms.user == current_user
                                       ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/account')


@app.route('/news_open/<int:id>', methods=['GET', 'POST'])
def news_open(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Forms).filter(Forms.id == id,
                                       Forms.user == current_user
                                       ).first()

    questions = db_sess.query(Question).filter(Question.id == id).first()
    q = questions.question
    author = news.user.name
    date = news.created_date
    title = news.title
    form = NewAnswer()
    if form.answer.data:
        print(000)
        answer = Answer()
        answer.answer = form.answer.data
        questions.answer.append(answer)
        db_sess.merge(questions)
        db_sess.commit()
        return redirect('/home')
    return render_template('open.html', title='Заполнение формы',
                           form=form, name=title, author=author, date=date, que=q)


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')
