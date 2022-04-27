import datetime
import sys
import datetime as dt
import sqlite3
import webbrowser

import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QDialog, QMessageBox, QPushButton, QScrollArea, QWidget, QVBoxLayout
from werkzeug.security import check_password_hash
from PyQt5.QtWidgets import QFormLayout, QGroupBox, QLabel


server_addres = 'http://127.0.0.1:5000/'


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
                    f = open('data/user.txt', 'w')
                    f.write(login)
                    f.close()
                    self.w = Main_Window(res)
                    self.w.show()
                    self.close()
                else:
                    msg = QMessageBox()
                    msg.setWindowTitle("Ошибка")
                    msg.setText("Неправильный пароль")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                cur.close()
                con.close()
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
    def __init__(self, val):
        super().__init__()
        self.title = "Messenger"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        formLayout = QFormLayout()
        groupBox = QGroupBox("Ваши чаты")
        comboList = []
        self.add_user = QPushButton("Добавить пользователя")
        self.add_user.setStyleSheet("background-color: red")
        formLayout.addRow(self.add_user)
        con = sqlite3.connect('data/datebase/application.db')
        cur = con.cursor()
        com = 'SELECT name, surname, login FROM chat'
        res = cur.execute(com).fetchall()
        cur.close()
        con.close()
        print(res)
        for i in range(len(res)):
            usern = res[i][0] + ' ' + res[i][1] + '(' + res[i][2] + ')'
            self.button = QPushButton(usern)
            formLayout.addRow(self.button)
            self.button.clicked.connect(self.open_chat)
        groupBox.setLayout(formLayout)
        scroll = QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        self.add_user.clicked.connect(self.create_chat)


    def create_chat(self):
        self.w = Search_User()
        self.w.show()
        print('yes')
        pass


    def open_chat(self):
        username = self.button.text()
        print(username)
        self.w = Main_Window(username)
        self.w.show()
        print('shiki')
        pass


class Main_Window(QMainWindow):
    def __init__(self, username):
        super().__init__()
        uic.loadUi('main_interface.ui', self)
        self.msg_send.clicked.connect(self.send)
        self.label.setText(username.split('(')[0])


    def keyPressEvent(self, event):
        if event.key() == 16777220:
            Main_Window.send(self)

    def send(self):
        text = self.msg_text.text()
        if text:
            try:
                requests.post(server_addres + 'cheak_server')

                now = dt.datetime.now().strftime("%H:%M")
                con = sqlite3.connect('data/datebase/application.db')
                cur = con.cursor()


                self.msg_text.clear()
                self.msg_field.append('[' + now + '] ' + text)
                cur.close()
                con.close()
            except requests.exceptions.RequestException:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Извините, cервер недоступен")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return None


class Search_User(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('search_user.ui', self)
        self.add_to_list.clicked.connect(self.search)

    def search(self):
        print('here')
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = Autorize_Form()
    ex.show()
    sys.exit(app.exec_())