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

> 使用语言Python，代码架构主要分为CoreLogic和UIdesign两部分。 两者都通过类进行模块化开发。 采用单类继承的思想，接口和逻辑分别开发。 逻辑部分由Python基础语法开发，接口部分主要由Python的**PyQt5**开发，暂未添加样式表与线程缓冲并发。

## 3. Strcture

> 逻辑业务与窗口业务分离，主程序调起业务。

## 4. Discussion

> ~~1. 是否需要设置线程进行更新，即实际运行中运行速度是否能够满足计算需求不会出现进程阻塞？暂不考虑~~
> 2. 对于超筋问题，如何修正？配筋过小问题已经修正；
> ~~3. 实现自动选用钢筋（数组做差返回最小值即可），提高整体计算精度，目前仅限于单直径配筋，同时具有一定的误差性。已实现~~
> 4. 对于承载力不足的配筋如何自动进行修正；



## 5. Arrangement

程序主体四大模块（准确来说三个，test不算，后期根据实际情况删除了几个）：

> 1. `Main`:主文件，负责调用各文件，并最终呈现完整界面；
> 2. ~~`MainLogic`：主逻辑接口，采用Python基本语法完成全部的计算；~~
> 3. `test`：逻辑接口测试文件，没啥用，完工后可删除。
> 4. `UI`：软件主界面及其控件；

