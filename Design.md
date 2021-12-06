# Project11
## 1. Synopsis
> **Project Name:** 	ConcreteCalculator
>
> **Project Description:**
>
> 仅限矩形轴向偏心受压混凝土计算设计。
>
> **Project Repository:**
>
> https://github.com/Hedge36/Concrete_design.git

## 2. Design

> Code Mainly divided into two part, including CoreLogic and UIdesign. Both should be developed in `Class`.  In general, the idea of single-class inheritance is adopted, and the interface and logic are developed separately. The logic part is completely developed by Python, and the interface part is mainly developed by Python's **PyQt5** and **QSS**. 

## 3. Strcture

> 逻辑业务与窗口业务分离，主程序调起业务，线程更新界面，样式表美化界面。

## 4. Discussion

> 1. 是否需要设置线程进行更新，即实际运行中运行速度是否能够满足计算需求不会出现进程阻塞？
> 2. 对于超筋问题，如何修正？配筋过小问题已经修正；
> 3. 实现自动选用钢筋（数组做差返回最小值即可），提高整体计算精度；
> 4. 对于承载力不足的配筋如何自动进行修正；



## 5. Arrangement

程序主体六大模块（准确来说五个，test不算）：

> 1. `Main`:主文件，负责调用各文件，并最终呈现完整界面；
> 2. ~~`MainLogic`：主逻辑接口，采用Python基本语法完成全部的计算；~~
> 3. `Mutilthread`：线程接口，定义PyQt5线程类用于同步更新界面结果；
> 4. `test`：逻辑接口测试文件，没啥用，完工后可删除。
> 5. `UI`：软件主界面及其控件；
> 6. `Uistyle`：QSS样式，软件主界面美化接口；

