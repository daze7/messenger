import datetime
import sys
import datetime as dt
import sqlite3
import webbrowser

import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QDialog, QMessageBox, QPushButton, QScrollArea, \
    QWidget, QVBoxLayout
from werkzeug.security import check_password_hash
from PyQt5.QtWidgets import QFormLayout, QGroupBox, QLabel

server_addres = 'http://586f-176-107-249-110.ngrok.io/'


class Autorize_Form(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('autorize.ui', self)
        self.signin.clicked.connect(self.sign_in)
        self.signup.clicked.connect(self.sign_up)
        self.password.setEchoMode(QLineEdit.Password)

    def sign_in(self):
        login = self.login.text()
        password = self.password.text()
        con = sqlite3.connect('data/datebase/application.db')
        cur = con.cursor()
        com = 'SELECT id FROM users'
        res = cur.execute(com).fetchall()
        cur.close()
        con.close()
        if login and password:
            try:
                re = requests.post(server_addres + 'user_info').json()
                con = sqlite3.connect('data/datebase/application.db')
                cur = con.cursor()
                com = 'SELECT login FROM users'
                value = ''.join([i[0] for i in cur.execute(com).fetchall()])
                for i in re:
                    if re[i]['login'] not in value:
                        cur.execute(f"INSERT INTO users(user_id,login,name,surname,password,date_regist,status) "
                                    f"VALUES('{re[i]['user_id']}','{re[i]['login']}','{re[i]['name']}',"
                                    f"'{re[i]['surname']}', '{re[i]['password']}', '{re[i]['date_register']}', "
                                    f"'{re[i]['status']}')")
                        value += re[i]["login"]
                        con.commit()
                        cur.close()
                        con.close()
                con = sqlite3.connect('data/datebase/application.db')
                cur = con.cursor()
                if login not in value:
                    msg = QMessageBox()
                    msg.setWindowTitle("Ошибка")
                    msg.setText("Неправильный пароль")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                    cur.close()
                    con.close()
                    return None
                com = f'SELECT password FROM users WHERE login = "{login}"'
                res = cur.execute(com).fetchone()[0]
                if check_password_hash(res, password):
                    com = f'SELECT name FROM users WHERE login = "{login}"'
                    res = cur.execute(com).fetchone()[0]
                    f = open('data/from_user.txt', 'w')
                    f.write(login)
                    f.close()
                    cur.close()
                    con.close()
                    self.w = Contacts()
                    self.w.show()
                    self.close()
                else:
                    msg = QMessageBox()
                    msg.setWindowTitle("Ошибка")
                    msg.setText("Неправильный пароль")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
            except requests.exceptions.RequestException:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Сервер недоступен")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return None
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Некорректный ввод данных")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def sign_up(self):
        try:
            requests.post(server_addres + 'cheak_server')
            webbrowser.open(server_addres + 'registration_users')
        except requests.exceptions.RequestException:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Сервер недоступен")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return None


class Contacts(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Messenger"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.formLayout = QFormLayout()
        self.groupBox = QGroupBox("Ваши чаты")
        comboList = []
        self.add_user = QPushButton("Добавить пользователя")
        self.add_user.setStyleSheet("background-color: red")
        self.formLayout.addRow(self.add_user)
        con = sqlite3.connect('data/datebase/application.db')
        cur = con.cursor()
        com = 'SELECT name, surname, login FROM chat'
        res = cur.execute(com).fetchall()
        cur.close()
        con.close()
        self.usern = []
        for i in range(len(res)):
            self.usern.append(res[i][0] + ' ' + res[i][1] + '(' + res[i][2] + ')')
            self.button = QPushButton(self.usern[i])
            self.formLayout.addRow(self.button)
            self.button.clicked.connect(lambda ch, i=i: self.open_chat(i))
        self.groupBox.setLayout(self.formLayout)
        scroll = QScrollArea()
        scroll.setWidget(self.groupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        self.add_user.clicked.connect(self.create_chat)

    def create_chat(self):
        self.close()
        self.w = Search_User()
        self.w.show()

    def open_chat(self, i):
        self.w = Main_Window(self.usern[i])
        self.w.show()


class Main_Window(QMainWindow):
    def __init__(self, username):
        super().__init__()
        uic.loadUi('main_interface.ui', self)
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.check_users)
        self.timer1.startTimer(3000)
        # self.timer2 = QTimer()
        # self.timer2.setInterval(100)
        # self.timer2.timeout.connect(self.check_message)

        self.msg_send.clicked.connect(self.send)
        self.label.setText(username.split('(')[0])
        self.show_history()

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            Main_Window.send(self)

    def send(self):
        text = self.msg_text.text()
        if text:
            self.check_users()
            try:
                f1 = open('data/from_user.txt', 'r')
                from_login = f1.readline()
                f1.close()
                f2 = open('data/for_user.txt', 'r')
                for_login = f2.readline()
                f2.close()
                con = sqlite3.connect('data/datebase/application.db')
                cur = con.cursor()
                from_user_id = cur.execute(f"SELECT user_id FROM users WHERE login = '{from_login}'").fetchone()
                for_user_id = cur.execute(f"SELECT user_id FROM users WHERE login = '{for_login}'").fetchone()
                date = dt.datetime.now().strftime("%H:%M")

                data = {'for_user_id': for_user_id, 'from_user_id': from_user_id, 'date': date, 'text': text}
                requests.post(server_addres + 'send_message', json=data)

                self.msg_text.clear()
                self.msg_field.append('')
                self.msg_field.append('Вы' + '[' + date + ']:')
                self.msg_field.append(text)
                cur.close()
                con.close()
            except requests.exceptions.RequestException:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Извините, cервер недоступен")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return None

    def check_message(self):
        try:
            self.check_users()
            con = sqlite3.connect('data/datebase/application.db')
            cur = con.cursor()
            resp = requests.post(server_addres + 'check_message').json()
            for i in resp:
                if i == 'result':
                    return None
                cur.execute(f"INSERT INTO message(for_user_id,from_user_id,date,type,text,photo,status) "
                            f"VALUES('{i[1]}','{i[2]}','{i[3]}','{i[4]}','{i[5]}','','new')")
                con.commit()
            cur.close()
            con.close()
        except BaseException as e:
            return e

    def show_history(self):
        try:
            self.check_users()
            f2 = open('data/for_user.txt', 'r')
            for_login = f2.readline()
            f2.close()
            con = sqlite3.connect('data/datebase/application.db')
            cur = con.cursor()
            for_user_id = cur.execute(f"SELECT user_id FROM users WHERE login = '{for_login}'").fetchone()[0]

            value = cur.execute(
                f"SELECT id,text,date,from_user_id FROM message WHERE for_user_id = '{for_user_id}'").fetchall()

            name = cur.execute(f"SELECT name,surname FROM users WHERE login = '{for_login}'").fetchall()
            self.msg_field.clear()
            for i in value:
                if i[3] != for_user_id:
                    self.msg_field.append('')
                    self.msg_field.append('Вы' + '[' + i[2] + ']:')
                    self.msg_field.append(i[1])
                    cur.execute(f"UPDATE message "
                                 f"SET status='old' "
                                 f"WHERE id = {i[0]}")
                    con.commit()
                else:
                    self.msg_field.append('')
                    self.msg_field.append(name[0][0] + ' ' + name[0][1] + '[' + i[2] + ']:')
                    self.msg_field.append(i[1])
                    cur.execute(f"UPDATE message "
                                 f"SET status='old' "
                                 f"WHERE id = {i[0]}")
            cur.close()
            con.close()
        except BaseException:
            return None

    def check_users(self):
        try:
            re = requests.post(server_addres + 'user_info').json()
            con = sqlite3.connect('data/datebase/application.db')
            cur = con.cursor()
            com = 'SELECT login FROM users'
            value = ''.join([i[0] for i in cur.execute(com).fetchall()])
            for i in re:
                if re[i]['login'] not in value:
                    cur.execute(f"INSERT INTO users(user_id,login,name,surname,password,date_regist,status) "
                                f"VALUES('{re[i]['user_id']}','{re[i]['login']}','{re[i]['name']}',"
                                f"'{re[i]['surname']}', '{re[i]['password']}', '{re[i]['date_register']}', "
                                f"'{re[i]['status']}')")
                    value += re[i]["login"]
                    con.commit()
                    cur.close()
                    con.close()
        except requests.exceptions.RequestException:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Сервер недоступен")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        return None


class Search_User(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('search_user.ui', self)
        self.add_to_list.clicked.connect(self.search)

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            Search_User.search(self)

    def search(self):
        login = self.lineEdit.text()
        con = sqlite3.connect('data/datebase/application.db')
        cur = con.cursor()
        com = 'SELECT name, surname FROM users WHERE login = "' + login + '"'
        res = cur.execute(com).fetchone()
        cur.close()
        con.close()
        if not res:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Пользователя с таким логином не существует")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        else:
            butname = res[0] + ' ' + res[1] + '(' + login + ')'
            con = sqlite3.connect('data/datebase/application.db')
            cur = con.cursor()
            com = 'INSERT INTO chat(login, name, surname) VALUES("' + login + '","' + res[0] + '","' + res[1] + '")'
            cur.execute(com)
            con.commit()
            cur.close()
            con.close()
            ex = Contacts()
            ex.show()
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = Autorize_Form()
    #ex = Contacts()
    ex.show()
    sys.exit(app.exec_())
