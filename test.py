from MainLogic import Calculator
import pandas as pd


def testunit(i):
    """测试逻辑，测试数据基于课本例题，更多数据请手动输入，无校验。
    i int(0-6)，测试题号。
    0-例题5-4
    1-例题5-5
    2-例题5-6
    3-例题5-7
    4-例题5-10
    5-例题5-12对称
    6-例题5-13对称
    """
    if_pass = 1
    paras, ans = dataset[i].rstrip().split("|")
    data = eval("{"+paras+"}")
    calculator.update(data)
    if ans != "True":
        ans = float(ans)
        cal = round(calculator.As, 3)
        if 0.95 < ans / cal < 1.05:
            pass
            # 测试用
            print("测试通过，参考答案%.3f，计算结果%.3f，偏差率%.2f%%。\n" %
                  (ans, cal, abs(cal-ans)/ans*100))
        else:
            if_pass = 0
    else:
        if_pass = -1
    return if_pass


def test():
    size = len(dataset)
    passtimes = 0
    none = 0
    failed = []
    for i in range(size):
        check = testunit(i)
        if check == 1:
            passtimes += 1
        elif check == 0:
            failed.append(i)
        else:
            none += 1
    print("测试通过率:%.2f%%(%d次测试，%d次通过，%d次无答案)" %
          (passtimes/(size-none)*100, size, passtimes, none))
    if failed:
        for fail in failed:
            print("第%d次测试失败" % (fail+1))


data = pd.read_excel("./data/test.xlsx", index_col=0)

with open("testdata.csv", encoding="utf-8") as f:
    dataset = f.readlines()[1::2]
calculator = Calculator(data)


test()

# 查看类各种属性
# print(calculator.__dict__)
