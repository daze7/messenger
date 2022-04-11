import sys
import datetime as dt
import sqlite3

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QDialog, QMessageBox


class Autorize_Form(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('autorize.ui', self)
        self.signin.clicked.connect(self.sign_in)
        self.signup.clicked.connect(self.sign_up)

    def sign_in(self):
        login = self.login.text()
        password = self.password.text()
        if login and password:
            con = sqlite3.connect('data/datebase/application.db')
            cur = con.cursor()
            com = 'SELECT password FROM user WHERE login = ' + login
            res = cur.execute(com).fetchone()
            con.close()
            if res == password:
                self.w = Main_Window()
                self.w.show()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Некорректный ввод данных")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def sign_up(self):
        pass




class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_interface.ui', self)
        self.msg_send.clicked.connect(self.send)

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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = Autorize_Form()
    ex.show()
    sys.exit(app.exec_())