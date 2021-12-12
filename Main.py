from MainLogic import Calculator
from UI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import pandas as pd

# —————————————————————————————————函数区————————————————————————————————

# 传参


def convert(ui):
    try:
        a_s = eval(ui.a_s.text())
    except:
        a_s = 0
    try:
        b = eval(ui.b.text())
    except:
        b = 0
    try:
        l = eval(ui.l.text())
    except:
        l = 0
    try:
        h = eval(ui.h.text())
    except:
        h = 0
    try:
        As2 = eval(ui.As2.text())
    except:
        As2 = 0
    try:
        M1 = eval(ui.M1.text())
    except:
        M1 = 0
    try:
        M2 = eval(ui.M2.text())
    except:
        M2 = 0
    try:
        N = eval(ui.N.text())
    except:
        N = 0
    try:
        fc = eval(ui.fc.text())
    except:
        fc = None
    try:
        fy = eval(ui.fy.text())
    except:
        fy = None
    try:
        ctype = ui.ctype.currentText()
    except:
        ctype = "C25"
    try:
        rtype = ui.rtype.currentText()
    except:
        rtype = "HRB500"
    try:
        cs = ui.checksym.currentText()
        if cs == "非对称配筋":
            checksym = False
        else:
            checksym = True
    except:
        checksym = True

    k = ["a_s", "b", "l", "ctype", "h", "As2", "M1",
         "M2", "N", "rtype", "checksym", "fc", "fy"]
    v = [a_s, b, l, ctype, h, As2, M1, M2, N, rtype, checksym, fc, fy]
    datai = dict(zip(k, v))

    return datai
# 输出页面


def display(ui, answer):
    ui.As.setText(str(answer[0]))
    ui.AAs2.setText(str(answer[1]))
    ui.textBrowsercalculate.setText(answer[2])


def success(ui):  # 成功运行
    datai = convert(ui)  # 传递参数
    calculator.update(datai)  # 进行运算
    answer = calculator.text  # 把输出文本赋值给answer
    display(ui, answer)  # 输出显示结果


def error(ui):  # 出错时提示
    ui.textBrowsercalculate.setText("请输入正确数据")
    ui.As.setText("")
    ui.AAs2.setText("")

# 赋默认值


def return0(ui):
    b = 300    # 宽度(mm)
    h = 400    # 高度(mm)
    l = 2400   # 长度(mm)
    a_s = 40    # 最小混凝土保护层厚度(mm)
    M1 = 200   # 上方弯矩(kN*m)
    M2 = 250   # 下方弯矩(KN*m)
    N = 400    # 轴向力(kN)
    ui.ctype.setCurrentIndex(2)
    ui.rtype.setCurrentIndex(4)
    ui.checksym.setCurrentIndex(0)

    k = ["a_s", "b", "l", "h", "M1", "M2", "N"]
    for i in k:
        exec("ui.%s.setText(str(%s))" % (i, i))
    success(ui)

 # 开始计算


def allin(ui):
    try:
        success(ui)
    except:
        error(ui)

# ———————————————————————————————————调用区——————————————————————————————


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    # 公称截面面积数据表
    data = pd.read_excel("./data/test.xlsx", index_col=0)
    # 进行实例化
    calculator = Calculator(data)

    ui.pushButtoncalculate.clicked.connect(partial(allin, ui))
    ui.pushButtonreturn.clicked.connect(partial(return0, ui))

    sys.exit(app.exec_())
