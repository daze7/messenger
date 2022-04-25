import datetime
import sys
import datetime as dt
import sqlite3
import webbrowser

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QDialog, QMessageBox


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
        if login and password:
            con = sqlite3.connect('data/datebase/application.db')
            cur = con.cursor()
            com = 'SELECT password FROM user WHERE login = "' + login + '"'
            res = cur.execute(com).fetchone()[0]
            con.close()
            if res == password:
                self.w = Main_Window()
                self.w.show()
                self.close()
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Неправильный пароль")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Некорректный ввод данных")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def sign_up(self):
        self.q = Sign_up_form()
        self.q.show()

class Sign_up_form(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('sign_up_interface.ui', self)
        self.confirm.clicked.connect(self.enter)
        self.up_password.setEchoMode(QLineEdit.Password)

    def enter(self):
        login = self.up_login.text()
        name = self.up_name.text()
        surname = self.up_surname.text()
        password = self.up_password.text()
        date = datetime.datetime.today().isoformat(sep='T')
        if login and name and surname and password:
            con = sqlite3.connect('data/datebase/application.db')
            cur = con.cursor()
            com = 'SELECT name FROM user WHERE login = "' + login + '"'
            res = cur.execute(com).fetchone()
            con.close()
            if res:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Этот логин уже занят")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
            else:
                status = True
                symbols = '''qwertyuiopasdfghjklzxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM0123456789! " # $ % & ' ( ) * + ,
                 - . / : ; < = > ? @ [ \ ] ^ _` { | } ~ '''
                for i in password:
                    if i not in symbols:
                        status = False
                        break
                if not status:
                    msg = QMessageBox()
                    msg.setWindowTitle("Ошибка")
                    msg.setText("Недопустимый пароль")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                else:
                    con = sqlite3.connect('data/datebase/application.db')
                    cur = con.cursor()
                    com = 'INSERT INTO user(id_user, login, name, surname, password, date_regist) VALUES(?, ?, ?, ?, ?, ?)'
                    user_id = '111'
                    dat = [user_id, login, name, surname, password, date]
                    cur.execute(com, dat)
                    con.commit()
                    con.close()
                    self.close()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Регистрация")
                    msg.setText("Вы успешно зарегистрировались!")
                    msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Некорректный ввод данных")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()








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