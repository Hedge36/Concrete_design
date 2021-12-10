from MainLogic import Calculator
from UI import Ui_MainWindow
from Mutilthread import*
import pandas as pd
from functools import partial

# —————————————————————————————————class————————————————————————————————

# —————————————————————————————————fuc————————————————————————————————
      
def allin(ui):
    data=convert(ui)
    morethreaduse=MoreThreadUse(data)
    #display(self,ui)
    calculator = Calculator(data)
    
    ui.As2.setText(str(calculator.b))
def convert(ui):

    try:        
        a_s = eval(ui.a_s.text())        
    except : 
        a_s = 0        
    try:
        b =eval( ui.b.text())         
    except :
        b = 0        	                
    try:
        l = eval(ui.l.text())
    except :        
	    l = 0            
    try:
        h = eval(ui.h.text()) 
    except :
        h = 0            
    try:
        As = eval(ui.As.text() )
    except :
        As = 0            
    try:
        M1 = eval(ui.M1.text()) 
    except :
        M1 = 0            
    try:
        M2 = eval(ui.M2.text()) 
    except :
        M2 = 0            
    try:
	    N = eval(ui.N.text()) 
    except :
        N = 0            
    try:
        ctype  = eval(ui.ctype.text()) 
    except :
        ctype = "C25"            
    try:rtype= eval(ui.rtype.text()) 
    except :rtype = "HRB500"            
    try:checksym = eval(ui.checksym.text()) 
    except :checksym = True
    print(h)
        
    k = ["a_s", "b", "l", "ctype", "h","As", "M1", "M2", "N", "rtype", "checksym"]

    v=[a_s,b,l,ctype,h,As,M1,M2,N,rtype,checksym]
    data=dict(zip(k,v)) 
    print(data)
    return data
   
# ———————————————————————————————————调用区——————————————————————————————

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()

    ui.setupUi(MainWindow)
    MainWindow.show()

    ui.pushButtoncalculate.clicked.connect(partial(allin, ui))
 
    sys.exit(app.exec_())
    
  
        



