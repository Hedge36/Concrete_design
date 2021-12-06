from MainLogic import Calculator


def testunit(i):
    """测试逻辑，测试数据基于课本例题5-4至5-10，更多数据请手动输入，无校验。
    i int(0-4)，测试题号，基于课本例题5-4至5-10，不包括8，9。
    """
    paras, ans = dataset[i].rstrip().split("|")
    data = eval("{"+paras+"}")
    calculator.update(**data)
    if ans != "True":
        ans = float(ans)
        cal = round(calculator._Calculator__As, 3)
        if 0.95 < ans / cal < 1.05:
            print("参考答案为%d，计算结果为%.3f,误差为%.1f%%。" %
                  (ans, cal, abs(ans/cal-1)*100))
            print("测试通过")
    else:
        print("无答案")


with open("testdata.csv", encoding="utf-8") as f:
    dataset = f.readlines()[1::2]
calculator = Calculator()

testunit(1)
# print(calculator.__dict__)
