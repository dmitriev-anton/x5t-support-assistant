# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
import pyqtgui

class SubUI(QtWidgets.QMainWindow, pyqtgui.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле newUI.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = SubUI()  # Создаём объект класса SubUI
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()