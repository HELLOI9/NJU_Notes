## 定义
在LR(0)的基础上，解决SLR(1)的问题，把当前状态下真正允许归约的token直接记录在项中，因此LR(1)项可以写成：
$$ [A\to\alpha\cdot\beta,\ a] $$
其中 $a$ 是一个终结符或者 $\$$，即lookahead。这个项的含义是：==🟡如果最终这条产生式全部识别完成，那么在当前上下文中，只有看到 $a$ 时，这个归约才是合法的。==

特别的，如果是项是$[A\to\alpha\cdot,\ a]$，意思就是只有当前lookhead=$a$时，才能按照$A\to\alpha$归约。

## CLOSURE
LR(1) 的闭包规则是：
$$  [A\to\alpha\cdot B\beta,a] \Rightarrow [B\to\cdot\gamma,b], \quad b\in FIRST(\beta a)  $$
给定项集 $I$，如果：
$$ [A\to\alpha\cdot B\beta,a]\in I $$
那么对 $B$ 的每条产生式$B\to\gamma$以及每一个$ b\in FIRST(\beta a) $加入：
$$ [B\to\cdot\gamma,b] $$
不断重复直到没有新项。

## GOTO
如果：
$$ [A\to\alpha\cdot X\beta,a] $$
识别了 $X$，就变成：
$$ [A\to\alpha X\cdot\beta,a] $$

注意$\text{lookahead }a\text{ 不变}$，然后对得到的项集做 CLOSURE：
$$GOTO(I,X) = CLOSURE( \{[A\to\alpha X\cdot\beta,a]\} ) $$
## ACITON/GOTO表的构造
对于状态 $I_i$：
### Shift
如果$[A\to\alpha\cdot a\beta,b]\in I_i$，其中 $a$ 是终结符，并且$GOTO(I_i,a)=I_j$，那么：$$ACTION[i,a]=s_j$$
### Reduce
如果$[A\to\alpha\cdot,a]\in I_i$且$A\neq S'$，那么：
$$ ACTION[i,a]=r(A\to\alpha) $$
注意这里不是$FOLLOW(A)$
而是这个项自己携带的$a$.
### Accept
如果$[S'\to S\cdot,\$]\in I_i$，那么：
$$ACTION[i,\$]=acc $$
### GOTO
如果$GOTO(I_i,A)=I_j$，其中 $A$ 是非终结符：
$$ GOTO[i,A]=j $$
其余：
$$ error $$
## 手算例子
对于文法：
$$ \begin{aligned} (0)\quad S'&\to S\\ (1)\quad S&\to CC\\ (2)\quad C&\to cC\\ (3)\quad C&\to d \end{aligned} $$
根据规范 LR(1) 项集族：

![[Pasted image 20261012225237.png|360]]

完整的 ACTION / GOTO 表就是：

|状态|ACTION `c`|ACTION `d`|ACTION `$`|GOTO $S$|GOTO $C$|
|--:|:-:|:-:|:-:|:-:|:-:|
|0|s3|s4||1|2|
|1|||acc|||
|2|s6|s7|||5|
|3|s3|s4|||8|
|4|r3|r3||||
|5|||r1|||
|6|s6|s7|||9|
|7|||r3|||
|8|r2|r2||||
|9|||r2|||
## LALR(1)
LALR(1) 可以理解成把规范 LR(1) 自动机里“LR(0) 核心相同”的状态合并，全称是 **Look-Ahead LR(1)**。

它的目的很直接：**LR(1) 很精确，但状态太多；LALR(1) 想在基本保留 LR(1) 精度的同时，把状态数压下来。**

但是LALR(1)会产生一个严重的问题：==🟡归约-归约冲突==.
比如如下的两个项集：
第一个：
$$ I_1: \begin{cases} [A\to\alpha\cdot,\ a]\\ [B\to\beta\cdot,\ b] \end{cases} $$
第二个：
$$ I_2: \begin{cases} [A\to\alpha\cdot,\ b]\\ [B\to\beta\cdot,\ a] \end{cases} $$
注意两个状态分别都没有冲突。
lookahead 取并集以后：
$$ \begin{cases} [A\to\alpha\cdot,\ \{a,b\}]\\ [B\to\beta\cdot,\ \{a,b\}] \end{cases} $$
不难看出发生了冲突。

## 总结

|方法|状态|归约条件|状态数量|能力|
|---|---|---|---|---|
|LR(0)|LR(0) 项集|不看 lookahead|少|弱|
|SLR(1)|LR(0) 项集|FOLLOW 集|少|较弱|
|LALR(1)|合并 LR(1) 同 core 状态|精确 lookahead 合并|少|较强|
|LR(1)|完整 LR(1) 项集|精确 lookahead|多|最强|
