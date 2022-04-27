import datetime
import sys
import datetime as dt
import sqlite3
import webbrowser

import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QDialog, QMessageBox
from werkzeug.security import check_password_hash


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
                re = requests.post('http://127.0.0.1:5000/user_info').json()
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
                com = f'SELECT password FROM users WHERE login = "{login}"'
                res = cur.execute(com).fetchone()[0]
                if check_password_hash(res, password):
                    self.w = Main_Window()
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
            requests.post('http://127.0.0.1:5000/cheak_server')
            webbrowser.open('http://127.0.0.1:5000/registration_users')
        except requests.exceptions.RequestException:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Сервер недоступен")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return None


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_interface.ui', self)
        self.msg_send.clicked.connect(self.send)
        self.add_user.clicked.connect(self.search)

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            Main_Window.send(self)

    def send(self):
        text = self.msg_text.text()
        if text:
            now = dt.datetime.now().strftime("%H:%M")
            con = sqlite3.connect('data/datebase/application.db')
            cur = con.cursor()
            con.close()
            self.msg_text.clear()
            self.msg_field.append('[' + now + '] ' + text)

    def search(self):
        self.f = Search_user()
        self.f.show()

class Search_user(QMainWindow):
    def __int__(self):
        super().__init__()
        uic.loadUi('search_user2.ui', self)
        #self.add_user.clicked.connect(self.add_to_list)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = Autorize_Form()
    ex.show()
    sys.exit(app.exec_())