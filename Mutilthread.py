
from MainLogic import Calculator
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QApplication, QMainWindow,QDialog,QLineEdit
import sys

class MoreThreadUse(QtCore.QThread):
    # 多线程，传递参数为一个类的实例，不用信号传递数据，直接把数据写入文件
    def __init__(self,data):
        super().__init__()
        
        self.fuc = data
    def run(self):
        self.fuc = Calculator(self.fuc)
        
