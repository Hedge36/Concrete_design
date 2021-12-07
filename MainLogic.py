#! usr/bin/env python
# -*- coding:utf-8 -*-
# @Author : Tiantian Li
# @File : Logic.py
# @Description : 矩形截面轴向偏心受压截面设计

# Discussion: 哪些变量作为实例变量，哪些需要封装？
# Problem: 超筋如何调整?承载力不足的如何进行修正？
# 关于多线程计算的思考


class Calculator:
    """矩形截面钢筋混凝土设计类，参数data为预设的公称截面面积数据。"""

    def __init__(self, data):
        # 面向窗体的变量
        self.b = 300    # 宽度(mm)
        self.h = 400    # 高度(mm)
        self.l = 2400   # 长度(mm)
        self.a_s = 40    # 最小混凝土保护层厚度(mm)
        self.M1 = 200   # 上方弯矩(kN*m)
        self.M2 = 250   # 下方弯矩(KN*m)
        self.N = 400    # 轴向力(kN)
        self.ctype = "C25"  # 混凝土类型
        self.rtype = "HRB500"   # 纵筋类型
        self.checksym = True     # 对称配筋
        self.As = 0  # 纵向受拉受拉钢筋配筋面积(mm^2)
        self.test = dict()  # 测试用数据集
        self.data = data    # 公称截面面积数据表(mm^2)
        # 不内置是不想在类内调用库

        # 封装的计算变量
        self.__A = 0   # 横截面积(mm^2)
        self.__M = 0    # 折算弯矩(kN*m)
        self.__Nu = 0  # 轴向承载力(kN)
        self.__As = 0   # 纵向钢筋配筋面积(mm^2)
        self.__As2 = 0  # 纵向受拉受拉钢筋配筋面积(mm^2)
        self.__pho = 0  # 受拉区配筋率
        self.__pho2 = 0  # 受压区配筋率
        self.__second = "无二阶效应"   # 二阶效应参数
        self.__eccent = "大偏心受压"    # 偏心类型
        self.__checkpho = "配筋满足要求"     # 配筋情况
        self.__checkNu = "轴向承载力满足要求"   # 承载情况
        self.__availble = True        # 配筋方案是否可用
        self.__scheme = ""  # 受拉配筋设计
        self.__scheme2 = ""  # 受压配筋设计

# —————————————————————————————————主函数区————————————————————————————————

    def calculate(self):
        self.__As2 = self.As   # 纯方便查参，没用
        if self.checksym:
            self.symmetry()
        else:
            self.asymmetry()

    def symmetry(self):
        """验算对称配筋条件下混凝土压弯参数"""
        # 1. 固定基本参数
        epsilor_cu = 0.0033    # 偏心受压区边缘极限应变值
        pho_min = 0.002         # 最小配筋率

        # 2. 计算参数
        h0, ea, l0 = self.getparas()
        fc, fy = self.getstrength()
        alpha1, beta1 = self.getab()
        self.__A = self.b*self.h
        # 3. 内力信息，略
        # 4. 二阶效应验算
        check = self.checkeffect(l0, fc)
        if check:   # 考虑二阶效应
            self.__M = self.seceff(fc, l0, h0, ea)
        else:       # 不考虑二阶效应
            self.__second = "无二阶效应"
            self.__M = self.M2

        # 5. 配筋计算
        e0 = self.__M / self.N * 1e3
        ei = e0 + ea
        e = ei + self.h / 2 - self.a_s

        x = self.N*1e3/(alpha1*fc*self.b)
        zeta_b = beta1/(1+fy/(2e5*epsilor_cu))
        xb = zeta_b * h0
        checkeccent = x < xb    # 大偏心验证
        if checkeccent and x >= 2*self.a_s:  # 大偏心计算
            self.__eccent = "大偏心受压"
            self.__As2 = self.leccent(e, alpha1, fc, x, h0, fy)
        else:       # 小偏心计算
            self.__eccent = "小偏心受压"
            self.__As2 = self.seccent(alpha1, beta1, fc, h0, zeta_b, e, fy)

        # 6. 配筋验算
        self.__pho2, self__As2 = self.checkpho(self.__As2, pho_min, h0)
        if self.__pho2 > 0.025:
            self.__availble = False
            self.__checkpho = "超筋（自行修正）"
        elif self.__pho2 < 0.00275:
            self.__checkpho = "不满足整体最小配筋率（已修正）"
            self.__pho2 = 0.00275
            self.__As2 = round(self.__pho2*self.b*h0, 3)
        self.__As2, self.__scheme2 = self.indexAs(self.__As2)
        self.__As = self.__As2
        self.__pho = self.__pho2
        self.__scheme = self.__scheme2
        # 未根据需求进行配筋

        # 7. 承载力验算
        self.checkNu(l0, fc, fy)

    def asymmetry(self):
        """钢筋混凝土非对称配筋截面设计"""
        # 1. 固定基本参数
        epsilor_cu = 0.0033    # 偏心受压区边缘极限应变值
        pho_min = 0.002         # 最小配筋率

        # 2. 计算参数
        h0, ea, l0 = self.getparas()
        fc, fy = self.getstrength()
        alpha1, beta1 = self.getab()
        self.__A = self.b*self.h
        # 3. 内力信息，略
        # 4. 二阶效应验算
        check = self.checkeffect(l0, fc)
        if check:   # 考虑二阶效应
            self.__M = self.seceff(fc, l0, h0, ea)
        else:       # 不考虑二阶效应
            self.__second = "无二阶效应"
            self.__M = self.M2

        # 5. 配筋计算
        e0 = self.__M / self.N * 1e3
        ei = e0 + ea
        e = ei + self.h / 2 - self.a_s
        self.test["e"] = e
        zeta_b = beta1/(1+fy/(2e5*epsilor_cu))
        xb = zeta_b * h0

        # 判断破坏条件
        # 假定大偏心
        if ei > 0.3 * h0:
            self.__eccent = "大偏心受压"
            # __As2未知的情况
            if self.__As2 == 0:
                self.__As2 = self.leccent(e, alpha1, fc, xb, h0, fy)
                # leccent只是公式刚好一样，没有直接关联
                if self.__As2 < pho_min*self.b*self.h:
                    self.__As2 = round(pho_min*self.b*self.h, 2)
                self.__As = round((alpha1*fc*self.b*h0*zeta_b -
                                   self.N*1e3)/fy + self.__As2, 2)
            # __As2已知的情况
            else:
                Mu = self.N*1e3*e-fy*self.__As2*(h0 - self.a_s)
                self.test["Mu"] = str(Mu/1e6)+"kN*m"
                alpha_s = Mu/(alpha1*fc*self.b*h0**2)
                zeta = 1 - (1-2*alpha_s)**0.5
                self.test["ζ"] = zeta
                x = zeta*h0
                self.test["x"] = x
                self.__As = round((alpha1*fc*self.b*x +
                                   fy*self.__As2-self.N*1e3)/fy, 2)

        # 假定小偏心
        else:
            self.__eccent = "小偏心受压"
            e2 = self.h/2-self.a_s - (e0 - ea)
            # 反向破坏
            if self.N*1e3 > fc*self.b*self.h:
                self.__As = round((self.N*1e3*e2-alpha1*fc*self.b * self.h
                                   * (h0-0.5*self.h))/fy/(h0 - self.a_s), 2)
            else:
                self.__As = round(pho_min*self.b*self.h, 2)

            u = self.a_s/h0 + fy*self.__As * \
                (1-self.a_s/h0)/((zeta_b-beta1)*alpha1*fc*self.b*h0)
            v = 2*self.N*1e3*e2/(alpha1*fc*self.b*h0**2) - \
                2*beta1*fy*self.__As * (1-self.a_s/h0) / \
                ((zeta_b-beta1)*alpha1*fc*self.b*h0)
            zeta = round(u + (u**2+v)**0.5, 3)
            self.test["ζ"] = zeta
            zeta_cy = 2*beta1 - zeta_b
            zeta_cm = self.h/h0
            if zeta_cy > zeta > zeta_b:
                self.__As2 = (self.N*1e3 - alpha1*fc*zeta*self.b*h0 +
                              fy*self.__As*((zeta-beta1)/(zeta_b-beta1)))/fy
            elif zeta_cm > zeta > zeta_cy:
                zeta = self.a_s/h0 + ((self.a_s/h0)**2 +
                                      2*(self.N*1e3*e2 / (alpha1*fc*self.b*h0**2) -
                                         self.__As2*fy*(1-self.a_s/h0)/(alpha1*fc*self.b*h0)))**0.5
                self.__As2 = (self.N*1e3 - alpha1*fc*zeta*self.b*h0 +
                              fy*self.__As*((zeta-beta1)/(zeta_b-beta1)))/fy
            elif zeta > zeta_cy and zeta > zeta_cm:
                self.__As2 = (self.N*1e3-fc*self.b *
                              self.h*(h0 - 0.5*self.h))/fy/(h0-self.a_s)
            if self.__As2 < pho_min*self.b*self.h:
                self.__As2 = round(pho_min*self.b*self.h, 2)
        # self.checkeccent()

        # 6. 配筋验算
        self.__pho, self__As = self.checkpho(self.__As, pho_min, h0)
        self.__pho2, self__As2 = self.checkpho(self.__As2, pho_min, h0)
        if self.__pho+self.__pho2 > 0.05:
            self.__availble = False
            self.__checkpho = "超筋（自行修正）"
        elif self.__pho+self.__pho2 < 0.055:
            self.__availble = False
            self.__checkpho = "不满足整体最小配筋率（自行修正）"
        self.__As2, self.__scheme2 = self.indexAs(self.__As2)
        self.__As, self.__scheme = self.indexAs(self.__As)
        # 未根据需求进行配筋

        # 7. 承载力验算
        self.checkNu(l0, fc, fy)

# ——————————————————————————————功能函数区——————————————————————————————————

    def getparas(self):
        """获取基本的计算参数。"""
        h0 = self.h - self.a_s     # 有效高度
        ea = max([self.h/30, 20])  # 附加偏心距
        l0 = 1*self.l   # 计算长度,先取着1
        return h0, ea, l0

    def getstrength(self):
        """获取纵筋，箍筋以及混凝土的强度。"""
        cs = int(self.ctype[1:])
        rs = self.rtype
        cslist = list(range(15, 85, 5))
        fclist = [7.20, 9.60, 11.9, 14.3, 16.7, 19.1, 21.1,
                  23.1, 25.3, 27.5, 29.7, 31.8, 33.8, 35.9]
        fcmap = dict(zip(cslist, fclist))  # 混凝土轴心抗压强度
        rslist = ["HPB300", "HRB335", "HRB400", "HRBF400",
                  "RRB400", "HRB500", "HRBF500"]
        fylist = [270, 300, 360, 360, 360, 435, 435]
        fymap = dict(zip(rslist, fylist))
        fc = fcmap[cs]
        fy = fymap[rs]
        return fc, fy

    def getab(self):
        """根据混凝土等级，获取受压区等效矩形应力图系数。"""
        cs = int(self.ctype[1:])
        csmap = {50: (1.00, 0.80), 55: (0.99, 0.79), 60: (0.98, 0.78),
                 65: (0.97, 0.77), 70: (0.96, 0.76), 75: (0.95, 0.75),
                 80: (0.95, 0.74)}     # 根据对应混凝土等级查表
        alpha1, beta1 = csmap.get(cs, csmap[50])
        return alpha1, beta1

    def checkeffect(self, lc, fc) -> bool:
        """验算二阶效应"""
        condition1 = min([self.M1/self.M2, self.M2/self.M1])
        condition2 = self.N*1e3/(fc*self.b*self.h)
        condition3 = lc/(0.289*self.h) - 34 + 12 * condition1
        check = (condition1 > 0.9) | (condition2 > 0.9) | (condition3 > 0)
        return check

    def seceff(self, fc, l0, h0, ea) -> float:
        """计算二阶效应修正系数"""
        C = 0.7 + 0.3*min([self.M1/self.M2, self.M2/self.M1])
        C_m = C if C > 0.7 else 0.7     # 构件断截面偏心距调节系数
        zeta = 0.5*fc*self.__A/self.N/1e3
        zeta_c = zeta if zeta < 1 else 1   # 截面曲率修正系数
        eta_s = 1 + (l0/self.h)**2*zeta_c*h0/1300 / \
            (max(self.M1, self.M2)/self.N*1e3+ea)
        p = C_m*eta_s
        self.__second = round(p, 3) if p > 1 else 1
        M = self.__second * max(self.M1, self.M2)
        return M

    def leccent(self, e, alpha1, fc, x, h0, fy) -> float:
        """大偏心受压配筋率计算"""
        As = (self.N*1e3*e-alpha1*fc*self.b *
              x*(h0-0.5*x))/fy/(h0 - self.a_s)
        return round(As, 3)

    def seccent(self, alpha1, beta1, fc, h0, zeta_b, e, fy) -> float:
        """小偏心受压配筋率计算"""
        Nt = alpha1 * fc * self.b * h0
        zeta = zeta_b + (self.N*1e3 - zeta_b*Nt) / (
            (self.N*e*1e3 - 0.43*Nt*h0) / (beta1-zeta_b) /
            (h0-self.a_s)+Nt)
        self.test["ζ"] = zeta
        As = (self.N * e * 1e3 - Nt * h0 * zeta * (1 - 0.5 * zeta)) / \
            fy / (h0 - self.a_s)
        return round(As, 3)

    def checkeccent(self):
        """不对称配筋下检查偏压情况"""
        x = (self.N*1e3 - fy2*self.__As2 + fy1*self.__As)/(alpha1*fc*self.b)

    def checkpho(self, As, pho_min, h0):
        """检查配筋率,如果配筋率满足要求，返回配筋率与配筋面积，否则修正。"""
        pho = round(As/(self.b * h0), 3)
        checkpho = pho > pho_min  # 配筋率验证
        if not checkpho:
            self.__checkpho = "不满足最小配筋率（已修正）"
            pho = pho_min
            As_temp = pho_min*self.h*self.b
        else:
            self.__checkpho = "满足配筋率要求"
            As_temp = As
        return pho, As_temp

    def indexAs(self, As):
        """根据公称截面面积配筋"""
        diameter, number = abs(self.data - As).stack().idxmin()
        As = self.data.loc[diameter][number]
        scheme = "%sФ%smm" % (number, diameter)
        # return diameter, number, As
        return float(As), scheme

    def getphi(self, p) -> float:
        """根据l0/b查表5-1并插值得到稳定性系数phi"""
        if p < 8:
            return 1
        elif p > 50:
            return 0.19
        plist = list(range(8, 52, 2))
        philist = [1.00, 0.98, 0.95, 0.92, 0.87, 0.81, 0.75, 0.70,
                   0.65, 0.60, 0.56, 0.52, 0.48, 0.44, 0.40, 0.36,
                   0.32, 0.29, 0.26, 0.23, 0.21, 0.19]
        i = int((p-8)/2)    # index of p
        phi = philist[i] + (philist[i+1]-philist[i])/2*(p-plist[i])
        return phi

    def checkNu(self, l0, fc, fy) -> float:
        """验算轴心受压钢筋受压承载力"""
        p = l0 / self.b
        phi = self.getphi(p)
        self.test["Φ"] = phi
        Nu = 0.9*phi*(fc*self.h*self.b+fy*(self.__As+self.__As2))
        self.__Nu = round(Nu/1000, 2)
        checkNu = self.__Nu > self.N    # 轴向承载力验证
        print(checkNu)
        if not checkNu:
            self.__checkNu = "轴向承载力不足（自行修正）"
            self.__availble = False
        else:
            self.__checkNu = "轴向承载力满足要求"
            self.__availble = True

    def pstr(self, t) -> str:
        """update方法用于格式化输出字符串，添加转义符防止exec函数执行"""
        if type(t) == str:
            t = "\"" + t + "\""
        return t


# ———————————————————————————————接口函数区————————————————————————————————


    def queryparam(self, *names):
        """查询参数，固定值，包括A, As, M, Nu, checkNu, checkpho,
        eccent, pho, second，可输入其组合以实现多个参数查询。
        注意，大小写敏感。

        A：横断面面积，mm^2
        As：配筋面积，mm^2
        M：折算弯矩，kN*m
        Nu：轴向承载力大小，kN
        checkNu：轴向承载力承载情况
        checkpho：配筋情况
        eccent：偏心类型
        pho,pho2：受拉（压）钢筋配筋率，%
        second：二阶效应判别及系数
        scheme,scheme：配筋设计
        available：配筋设计是否可用
        """
        find = False
        supports = ['A', 'As', 'M', 'Nu', 'checkNu', 'checkpho',
                    'eccent', 'pho', 'second', 'scheme', 'scheme2',
                    'pho2', 'available']
        for name in names:
            if name in supports:
                if find == False:
                    find = True
                    print("\n查询结果：")
                print("%s:%s" %
                      (name, eval("self._Calculator__%s" % name)))
        if not find:
            print("\n目前暂不支持该参数的查询！")
        else:
            print("其余参数暂不支持查询")

    def update(self, **maps):
        """根据输入更新数据。
        输入格式：b=100,l=300，大小写敏感。
        """
        keys = ["a_s", "b", "l", "ctype", "h", "As",
                "M1", "M2", "N", "rtype", "checksym"]
        for key, value in maps.items():
            if key in keys:
                exec("self.%s=%s" % (key, self.pstr(value)), locals())
        self.calculate()
        # 懒得做数据检查
