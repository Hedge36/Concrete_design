from MainLogic import Calculator
from UI import MainWindow
import pandas as pd

Window = MainWindow()   # 初始化窗口
data = pd.read_excel("./test.xlsx", index_col=0)

calculator = Calculator()   # 初始化逻辑计算
