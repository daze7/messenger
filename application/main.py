import sys


from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit


#class MyLine(QLineEdit):
#    def focusInEvent(self, event):
#        print('here')
#        super(MyLineEdit, self).focusInEvent(event)
#        pass


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_interface.ui', self)
        self.msg_send.clicked.connect(self.send)
        #mes = MyLine(self)
        #mes.move(60, 100)

    def send(self):
        text = self.msg_text.text()
        self.msg_text.clear()
        print(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main_Window()
    ex.show()
    sys.exit(app.exec_())