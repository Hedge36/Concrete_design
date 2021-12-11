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
        self.test = dict()  # 测试用数据集
        self.data = data    # 公称截面面积数据表(mm^2)
        self.fc = None
        self.fy = None

        self.A = 0   # 横截面积(mm^2)
        self.M = 0    # 弯矩设计值(kN*m)
        self.Nu = 0  # 轴向承载力(kN)
        self.As = 0   # 纵向钢筋配筋面积(mm^2)
        self.As2 = 0  # 纵向受拉受拉钢筋配筋面积(mm^2)
        self.rAs = 0    # 实际纵向钢筋配筋面积(mm^2)
        self.rAs2 = 0    # 实际纵向受压钢筋配筋面积(mm^2)
        self.pho = 0  # 受拉区配筋率
        self.pho2 = 0  # 受压区配筋率
        self.second = "由于式①②③都小于0,所以无须考虑二阶效应；"   # 二阶效应参数
        self.eccent = "大偏心受压"    # 偏心类型
        self.checkpho = "配筋满足要求"     # 配筋情况
        self.checkNu = "轴向承载力满足要求"   # 承载情况
        self.availble = True        # 配筋方案是否可用
        self.scheme = ""  # 受拉配筋设计
        self.scheme2 = ""  # 受压配筋设计


# —————————————————————————————————主函数区————————————————————————————————

    def calculate(self):
        if self.checksym:
            self.symmetry()
        else:
            self.asymmetry()
        self.textedit()  # 输出

    def symmetry(self):
        """验算对称配筋条件下混凝土压弯参数"""
        # 1. 固定基本参数
        epsilor_cu = 0.0033    # 偏心受压区边缘极限应变值
        pho_min = 0.002         # 最小配筋率

        # 2. 计算参数
        h0, ea, l0 = self.getparas()
        '''自定义强度'''
        if self.fc == None and self.fy == None:
            fc, fy = self.getstrength()
        else:
            fc = self.fc
            fy = self.fy

        alpha1, beta1 = self.getab()
        self.A = self.b*self.h
        # 3. 内力信息，略
        # 4. 二阶效应验算
        check = self.checkeffect(l0, fc)
        if check:   # 考虑二阶效应
            self.M = self.seceff(fc, l0, h0, ea)
        else:       # 不考虑二阶效应
            self.second = "无二阶效应"
            self.M = self.M2

        # 5. 配筋计算
        e0 = self.M / self.N * 1e3
        ei = e0 + ea
        e = ei + self.h / 2 - self.a_s

        x = self.N*1e3/(alpha1*fc*self.b)
        zeta_b = beta1/(1+fy/(2e5*epsilor_cu))
        xb = zeta_b * h0
        checkeccent = x < xb    # 大偏心验证
        if checkeccent and x >= 2*self.a_s:  # 大偏心计算
            self.eccent = "大偏心受压"
            self.As2 = self.leccent(e, alpha1, fc, x, h0, fy)
        else:       # 小偏心计算
            self.eccent = "小偏心受压"
            self.As2 = self.seccent(alpha1, beta1, fc, h0, zeta_b, e, fy)

        # 6. 配筋验算
        self.pho2, self.As2 = self.check_pho(self.As2, pho_min, h0)
        if self.pho2 > 0.025:
            self.availble = False
            self.checkpho = "超筋（自行修正）"
        elif self.pho2 < 0.00275:
            self.checkpho = "不满足整体最小配筋率（已修正）"
            self.pho2 = 0.00275
            self.As2 = round(self.pho2*self.b*h0, 3)
        self.As = self.As2
        self.rAs2, self.scheme2 = self.indexAs(self.As2)
        self.rAs = self.rAs2
        self.pho = self.pho2
        self.scheme = self.scheme2
        # 未根据需求进行配筋

        # 7. 承载力验算
        self.check_Nu(l0, fc, fy)

    def asymmetry(self):
        """钢筋混凝土非对称配筋截面设计"""
        # 1. 固定基本参数
        epsilor_cu = 0.0033    # 偏心受压区边缘极限应变值
        pho_min = 0.002         # 最小配筋率

        # 2. 计算参数
        h0, ea, l0 = self.getparas()
        '''自定义强度'''
        if self.fc == None and self.fy == None:
            fc, fy = self.getstrength()
        else:
            fc = self.fc
            fy = self.fy
        alpha1, beta1 = self.getab()
        self.A = self.b*self.h
        # 3. 内力信息，略
        # 4. 二阶效应验算
        check = self.checkeffect(l0, fc)
        if check:   # 考虑二阶效应
            self.M = self.seceff(fc, l0, h0, ea)
        else:       # 不考虑二阶效应
            self.second = "无二阶效应"
            self.M = self.M2

        # 5. 配筋计算
        e0 = self.M / self.N * 1e3
        ei = e0 + ea
        e = ei + self.h / 2 - self.a_s
        self.test["e"] = e
        zeta_b = beta1/(1+fy/(2e5*epsilor_cu))
        xb = zeta_b * h0

        # 判断破坏条件
        # 假定大偏心
        if ei > 0.3 * h0:
            self.eccent = "大偏心受压"
            # As2未知的情况
            if self.As2 == 0:
                ka = 1
                self.As2 = self.leccent(e, alpha1, fc, xb, h0, fy)
                # leccent只是公式刚好一样，没有直接关联
                if self.As2 < pho_min*self.b*self.h:
                    self.As2 = round(pho_min*self.b*self.h, 2)
                self.As = round((alpha1*fc*self.b*h0*zeta_b -
                                 self.N*1e3)/fy + self.As2, 2)
            # As2已知的情况
            else:
                ka = 0
                Mu = self.N*1e3*e-fy*self.As2*(h0 - self.a_s)
                self.test["Mu"] = str(Mu/1e6)+"kN*m"
                alpha_s = Mu/(alpha1*fc*self.b*h0**2)
                zeta = 1 - (1-2*alpha_s)**0.5
                self.test["ζ"] = zeta
                x = zeta*h0
                self.test["x"] = x
                self.As = round((alpha1*fc*self.b*x +
                                 fy*self.As2-self.N*1e3)/fy, 2)

        # 假定小偏心
        else:
            ka = 1
            self.eccent = "小偏心受压"
            e2 = self.h/2-self.a_s - (e0 - ea)
            # 反向破坏
            if self.N*1e3 > fc*self.b*self.h:
                self.As = round((self.N*1e3*e2-alpha1*fc*self.b * self.h
                                 * (h0-0.5*self.h))/fy/(h0 - self.a_s), 2)
            else:
                self.As = round(pho_min*self.b*self.h, 2)

            u = self.a_s/h0 + fy*self.As * \
                (1-self.a_s/h0)/((zeta_b-beta1)*alpha1*fc*self.b*h0)
            v = 2*self.N*1e3*e2/(alpha1*fc*self.b*h0**2) - \
                2*beta1*fy*self.As * (1-self.a_s/h0) / \
                ((zeta_b-beta1)*alpha1*fc*self.b*h0)
            zeta = round(u + (u**2+v)**0.5, 3)
            self.test["ζ"] = zeta
            zeta_cy = 2*beta1 - zeta_b
            zeta_cm = self.h/h0
            if zeta_cy > zeta > zeta_b:
                self.As2 = (self.N*1e3 - alpha1*fc*zeta*self.b*h0 +
                            fy*self.As*((zeta-beta1)/(zeta_b-beta1)))/fy
            elif zeta_cm > zeta > zeta_cy:
                zeta = self.a_s/h0 + ((self.a_s/h0)**2 +
                                      2*(self.N*1e3*e2 / (alpha1*fc*self.b*h0**2) -
                                         self.As2*fy*(1-self.a_s/h0)/(alpha1*fc*self.b*h0)))**0.5
                self.As2 = (self.N*1e3 - alpha1*fc*zeta*self.b*h0 +
                            fy*self.As*((zeta-beta1)/(zeta_b-beta1)))/fy
            elif zeta > zeta_cy and zeta > zeta_cm:
                self.As2 = (self.N*1e3-fc*self.b *
                            self.h*(h0 - 0.5*self.h))/fy/(h0-self.a_s)
            if self.As2 < pho_min*self.b*self.h:
                self.As2 = round(pho_min*self.b*self.h, 2)
        # self.checkeccent()

        # 6. 配筋验算
        self.pho, self.As = self.check_pho(self.As, pho_min, h0)
        self.pho2, self.As2 = self.check_pho(self.As2, pho_min, h0)
        if self.pho+self.pho2 > 0.05:
            self.availble = False
            self.checkpho = "超筋（自行修正）"
        elif self.pho+self.pho2 < 0.055:
            self.availble = False
            self.checkpho = "不满足整体最小配筋率（自行修正）"

        if ka == 1:
            self.rAs2, self.scheme2 = self.indexAs(self.As2)
        else:
            self.scheme2 = "已知配筋方案"
        self.rAs, self.scheme = self.indexAs(self.As)
        # 未根据需求进行配筋

        # 7. 承载力验算
        self.check_Nu(l0, fc, fy)

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
        zeta = 0.5*fc*self.A/self.N/1e3
        zeta_c = zeta if zeta < 1 else 1   # 截面曲率修正系数
        eta_s = 1 + (l0/self.h)**2*zeta_c*h0/1300 / \
            (max(self.M1, self.M2)/self.N*1e3+ea)
        p = C_m*eta_s
        self.second = round(p, 3) if p > 1 else 1
        M = self.second * max(self.M1, self.M2)
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
        x = (self.N*1e3 - fy2*self.As2 + fy1*self.As)/(alpha1*fc*self.b)

    def check_pho(self, As, pho_min, h0):
        """检查配筋率,如果配筋率满足要求，返回配筋率与配筋面积，否则修正。"""
        pho = round(As/(self.b * h0), 3)
        checkpho = pho > pho_min  # 配筋率验证
        if not checkpho:
            self.checkpho = "不满足最小配筋率（已修正）"
            pho = pho_min
            As_temp = pho_min*self.h*self.b
        else:
            self.checkpho = "满足配筋率要求"
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

    def check_Nu(self, l0, fc, fy) -> float:
        """验算轴心受压钢筋受压承载力"""
        p = l0 / self.b
        phi = self.getphi(p)
        self.test["Φ"] = phi
        Nu = 0.9*phi*(fc*self.h*self.b+fy*(self.rAs+self.rAs2))
        self.Nu = round(Nu/1000, 2)
        checkNu = self.Nu > self.N    # 轴向承载力验证
        if not checkNu:
            self.checkNu = "轴向承载力不足（自行修正）"
            self.availble = False
        else:
            self.checkNu = "轴向承载力满足要求"
            self.availble = True

    def pstr(self, t) -> str:
        """update方法用于格式化输出字符串，添加转义符防止exec函数执行"""
        if type(t) == str:
            t = "\"" + t + "\""
        return t


# ———————————————————————————————输出区————————————————————————————————


    def textedit(self):
        """打印详细计算过程"""
        h0, ea, l0 = self.getparas()
        if self.fc == None and self.fy == None:
            fc, fy = self.getstrength()
        else:
            fc = self.fc
            fy = self.fy

        h0 = self.h-self.a_s
        e0 = self.M*1e3/self.N
        ei = e0+ea
        t1 = """[解]:1)截面几何信息:
        h_0=h-as=%d mm;
        ea=max(h/30,20)=%.2f mm;
        横截面积A=bh=%d mm^2
        """ % (h0, ea, self.A)

        t2 = """\n2)材料强度信息:
        fc=%.1f MPa;
        fy=%d MPa;
        """ % (fc, fy)

        if type(self.second) == str:
            second = self.second
        else:
            second = "由于①②③中存在式子>0,所以必须考虑二阶效应，此时，二阶效应系数为%.2f" % self.second
        t3 = """\n3)二阶效应计算信息:
        ①M1/M2-0.9;
        ②N/(fcA)-0.9;
        ③lc/i-34+12(M1/M2);
        %s，弯矩设计值为 %.2fkN*m
        """ % (second, self.M)

        t4 = """\n4)计算配筋:
        e0=M\\N=%.3f mm;
        ei=e0+ea= %.3fmm;
        判断破坏类型: %s
        纵向受拉钢筋配筋面积:%.2f mm^2
        纵向受压钢筋配筋面积:%.2f mm^2
        """ % (e0, ei, self.eccent, self.As, self.As2)

        t5 = """\n5)验算适用条件:
        受拉区配筋率:%.3f%%
        受压区配筋率:%.3f%%
        验算最小配筋率情况：%s
        """ % (self.pho, self.pho2, self.checkpho)

        t6 = """\n6)根据公称截面面积配筋:
        由计算得到配筋面积查附表3-1，
        受拉钢筋采用%s(As=%smm^2)
        受压钢筋采用%s(As'=%smm^2)
        """ % (self.scheme, self.rAs, self.scheme2, self.rAs2)

        t7 = """\n7)验算垂直于弯矩作用平面的轴心受压承载力:
        根据实际配筋面积计算Nu可得：
        Nu=0.9φ[fcbh+fy'(As'+As)]= %.2f kN,%s
        """ % (self.Nu, self.checkNu)

        self.text3 = t1+t2+t3+t4+t5+t6+t7
        self.text = [self.As, self.As2, self.text3]


# ———————————————————————————————接口函数区————————————————————————————————

    def update(self, maps):
        """根据输入更新数据。
        输入格式:b=100,l=300，大小写敏感。
        """
        keys = ["a_s", "b", "l", "ctype", "h", "As2",
                "M1", "M2", "N", "rtype", "checksym", "fc", "fy"]
        for key, value in maps.items():
            if key in keys:
                exec("self.%s=%s" % (key, self.pstr(value)), locals())
        self.calculate()
        # 懒得做数据检查
