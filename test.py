from MainLogic import Calculator

calculator = Calculator()
calculator.update(**{"b": 800, "h": 1000, "N": 7500,
                     "M2": 1800, "M1": 0.9*1800, "rtype": 'HRB400',
                     "ctype": "C40", "l": 6000})
# calculator.queryparam("checkNu")
# print(calculator.__dict__)
