import sqlite3
import time
import math
import re
from flask import url_for
from flask_login import current_user


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_post_user_id(self, alias):
        try:
            self.__cur.execute(f"SELECT user_id_post FROM posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return str(res[0])  # Возвращаем идентификатор пользователя, разместившего статью
        except sqlite3.Error as e:
            print("Ошибка получения идентификатора пользователя из БД " + str(e))

        return None

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addPost(self, title, text, url):
        try:
            self.__cur.execute(f"SELECT COUNT() as count FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Статья с таким url уже существует")
                return False

            base = url_for('static', filename='img')

            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)

            tm = math.floor(time.time())
            user_id = current_user.get_id()
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?, ?)", (user_id, title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД " + str(e))
            return False

        return True

    def getPost(self, alias):
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id_post, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    def addUser(self, login, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as count FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            standartBlog = "Здесь будет информация о себе, которую заполняли ранее или будет возможность написать всё, что нужно"
            standartFirstName = "Имя"
            standartLastName = "Фамилия"
            standartCity = "Город"
            standartCountry = "Страна"
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?)",
                               (login, email, hpsw, standartFirstName, standartLastName, standartCountry,
                                standartCity, standartBlog, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД" + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошиибка получения данных из БД " + str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE user_id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: " + str(e))
            return False
        return True

    def updateUserInformation(self, user_id, first_name, last_name, country, city, blog):
        if not (first_name or last_name or country or city or blog):
            return True

        try:
            query = "UPDATE users SET "
            params = []

            if first_name:
                query += "first_name = ?, "
                params.append(first_name)
            if last_name:
                query += "last_name = ?, "
                params.append(last_name)
            if country:
                query += "country = ?, "
                params.append(country)
            if city:
                query += "city = ?, "
                params.append(city)
            if blog:
                query += "blog = ?, "
                params.append(blog)

            query = query.rstrip(", ")  # Удаляем лишнюю запятую и пробел в конце строки
            query += " WHERE user_id = ?"
            params.append(user_id)

            self.__cur.execute(query, tuple(params))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления информации о пользователе в БД: " + str(e))
            return False
        return True
        #     В этой версии кода мы создаем строку запроса query, которая будет динамически формироваться в зависимости от
        # того, какие переменные имеют новые значения.Переменные, которым присваивается новое значение, добавляются в
        # строку запроса и соответствующее значение добавляется в список params. \
        #     После построения запроса мы удаляем лишнюю запятую и пробел в конце строки запроса с помощью rstrip(", ").
        #     Затем мы добавляем значение user_id в список params и выполняем запрос с использованием execute(),
        # передавая кортеж params в качестве параметров.
        #     Теперь, если какие - то переменные(first_name, last_name, country, city) остаются пустыми или не имеют новых
        # значений, они не будут включены в запрос обновления, и соответствующие столбцы в базе данных сохранят свои
        # предыдущие значения.

    def updateUserPassword(self, user_id, login, old_psw, new_psw, confirm_psw):
        # Проверка правильности введенного старого пароля и логина
        try:
            #query = f"SELECT psw FROM users WHERE user_id = ? AND login = ?"
            self.__cur.execute(f"SELECT psw FROM posts WHERE user_id = '{user_id}' AND login = '{login}' LIMIT 1")
            #self.__cur.execute(query, (user_id, login))
            result = self.__cur.fetchone()
            if not result:
                print("Неправильный логин или старый пароль1")
                return False
            stored_password = result[0]
            if stored_password != old_psw:
                print("Неправильный логин или старый пароль2")
                return False
        except sqlite3.Error as e:
            print("Ошибка при проверке старого пароля и логина: " + str(e))
            return False

        # Проверка правильности введенного нового пароля и его подтверждения
        if new_psw != confirm_psw:
            print("Новый пароль и его подтверждение не совпадают")
            return False

        try:
            #query = "UPDATE users SET psw = ? WHERE user_id = ?"
            #self.__cur.execute(query, (new_psw, user_id))
            self.__cur.execute(f"UPDATE users SET psw = '{new_psw}' WHERE user_id = '{user_id}'")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка при обновлении пароля в БД: " + str(e))
            return False

        return True

    def getBlog(self, user_id):
        try:
            self.__cur.execute(f"SELECT blog FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД: " + str(e))
        return False

    def getFirstName(self, user_id):
        try:
            self.__cur.execute(f"SELECT first_name FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения имени из БД: " + str(e))
        return False

    def getLastName(self, user_id):
        try:
            self.__cur.execute(f"SELECT last_name FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения почты из БД: " + str(e))
        return False

    def getCountry(self, user_id):
        try:
            self.__cur.execute(f"SELECT country FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения города из БД: " + str(e))
        return False

    def getCity(self, user_id):
        try:
            self.__cur.execute(f"SELECT city FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения города из БД: " + str(e))
        return False

    def getEmail(self, user_id):
        try:
            self.__cur.execute(f"SELECT email FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения почты из БД: " + str(e))
        return False
