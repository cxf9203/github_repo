# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTextBrowser,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(70, 100, 401, 371))
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(520, 130, 81, 51))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(630, 130, 81, 51))
        self.pushButton_2.setFont(font)
        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(510, 240, 256, 192))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(510, 30, 281, 61))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(24)
        font1.setBold(True)
        self.label_2.setFont(font1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 23))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"image", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u542f\u52a8", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u505c\u6b62", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u6e29\u5dde\u804c\u4e1a\u6280\u672f\u5b66\u9662", None))
    # retranslateUi

