from flask import Flask, render_template, url_for, request, redirect, current_app, g, flash, session, abort, \
    make_response
from flask_sqlalchemy import SQLAlchemy
from FDataBase import FDataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from UserLogin import UserLogin
import sqlite3
import os

DATABASE = 'data.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024
USERNAME = 'admin'
PASSWORD = '123'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'data.db')))
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизируйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load user")
    return UserLogin().fromDB(user_id, dbase)
#   !!!!! Print можно убрать


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


# def get_post_user_id(alias):
#     post = dbase.posts.get(alias)  # Получаем пост по его псевдониму (alias)
#     if post:
#         return str(post['user_id_post'])  # Возвращаем идентификатор пользователя, разместившего статью
#         return None  # Возвращаем None, если пост не найден
#
#
# menu = [{"name": "Установка", "url": "install-flask"},
#         {"name": "Первое приложение", "url": "first-app"},
#         {"name": "Обратная связь", "url": "contact"}]


@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce(), logged_in=current_user.is_authenticated)


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['title']) > 1 and len(request.form['text']) > 1 and len(request.form['url']) > 1:
            res = dbase.addPost(request.form['title'], request.form['text'], request.form['url'])
            if not res:
                flash('Ошибка добавления проекта', category='error')
            else:
                flash('Проект добавлен успешно', category='success')
        else:
            flash('Ошибка добавления проекта', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="", user_id_post=current_user.get_id(), text="", url="")


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route("/post/<alias>")
@login_required
def showUserPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    post_user_id = dbase.get_post_user_id(alias)  # Получаем идентификатор пользователя, разместившего пост

    if current_user.get_id() != post_user_id:
        abort(403)  # Возвращаем ошибку 403 (доступ запрещен), если идентификаторы пользователей не совпадают

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


dbase = None
@app.before_request
def before_request():
    """" Установление соединения с БД перед выполнением запроса """
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('contact.html', title="Обратная связь", menu=dbase.getMenu())


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=dbase.getMenu())


# @app.route("/profile/<username>")
# def profile(username):
#     if 'userLogged' not in session or session['userLogged'] != username:
#         abort(401)
#     return f"Пользователь: {username}"

@app.route("/raz")
def raz():
    return render_template("profile.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['login']) > 4 and len(request.form['email']) > 4 \
                and len (request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['login'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегестрировались", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remindme') else False
            login_user(userlogin, remember=rm)
            session['authenticated'] = True
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профиль",
                           blog=dbase.getBlog(current_user.get_id()),
                           first_name=dbase.getFirstName(current_user.get_id()),
                           last_name=dbase.getLastName(current_user.get_id()),
                           city=dbase.getCity(current_user.get_id()),
                           country=dbase.getCountry(current_user.get_id()),
                           email=dbase.getEmail(current_user.get_id()))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    session['authenticated'] = False
    return redirect(url_for('login'))


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


@app.route('/settings')
@login_required
def settings():
    return render_template("settings.html", menu=dbase.getMenu(), title="Настройки")


@app.route('/changeInformation', methods=['GET', 'POST'])
@login_required
def changeInformation():
    if request.method == 'POST':
        # Ваш код обработки POST-запроса
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        country = request.form['country']
        city = request.form['city']
        blog = request.form['blog']

        try:
            res = dbase.updateUserInformation(current_user.get_id(), first_name, last_name, country, city, blog)
            if not res:
                flash("Ошибка обновления информации", "error")
            else:
                flash("Информация обновлена", "success")
        except Exception as e:
            flash("Ошибка обновления информации", "error")

        return redirect(url_for('profile'))

    # Ваш код для GET-запроса
    return render_template('settings.html')  # Замените 'change_information.html' на ваш шаблон


@app.route('/change_password')
@login_required
def change_password():
    return render_template("change_password.html", menu=dbase.getMenu(), title="Изменить пароль")


@app.route('/updatePassword', methods=['GET', 'POST'])
@login_required
def updatePassword():
    if request.method == 'POST':
        # Ваш код обработки POST-запроса
        login = request.form['login']
        oldPsw = generate_password_hash(request.form['oldPassword'])
        newPsw = generate_password_hash(request.form['newPassword'])
        newPsw2 = generate_password_hash(request.form['newPassword2'])

        try:
            res = dbase.updateUserPassword(current_user.get_id(), login, oldPsw, newPsw, newPsw2)
            if not res:
                flash("Ошибка обновления пароля", "error")
            else:
                flash("Пароль обновлён", "success")
        except Exception as e:
            flash("Ошибка обновления пароля2", "error")

        return redirect(url_for('profile'))

    # Ваш код для GET-запроса
    return render_template('change_password.html')  # Замените 'change_information.html' на ваш шаблон


# @app.route('/takeBlog', methods=['GET', 'POST'])
# def takeBlog():
#     db = get_db()
#     dbase = FDataBase(db)
#     blog = dbase.getBlog(current_user.get_id())
#     if not blog:
#         return "Здесь будет информация о себе, которую заполняли ранее или будет возможность нажать сюда и написать всё, что нужно"
#
#     return render_template('profile.html', menu=dbase.getMenu(), blog=blog)


    # Получение данных из базы данных (database_rows должна быть заполнена данными из базы данных)
    # database_rows = takeBlog(current_user.get_id(), current_user.get_blog())
    #
    # return render_template('index.html', database_rows=database_rows)


if __name__ == "__main__":
    app.run(debug=True)
