## 定义
SLR(1)的状态还是[[LR(0)文法|LR(0)]]项集，自动机也是原来的LR(0)自动机，只是Reduce的规则变了。

如果状态 $I_i$ 中存在完成项：
$$ A\to\beta\cdot $$
那么不是对所有终结符都填 Reduce，而是：
$$ \boxed{ \forall a\in FOLLOW(A),\quad ACTION[i,a]=Reduce(A\to\beta) } $$

SLR(1)仍然属于Simple LR，因为在**当前这个具体状态和上下文**下，可能只有 FOLLOW(A) 中的一部分真正合法，SLR并不能区分哪些状态合法，哪些不合法。

## 手算例子
对文法：
$$ \begin{aligned} (1)\quad E&\to E+T\\ (2)\quad E&\to T\\ (3)\quad T&\to T*F\\ (4)\quad T&\to F\\ (5)\quad F&\to(E)\\ (6)\quad F&\to id \end{aligned} $$
输入为$id*id\$$.

分析：还是先画出自动机：
![[Pasted image 20261012214853.png|431]]

SLR的ACTION/GOTO表的构造方法:
假设状态 $I_i$。
如果自动机有终结符转移：
$$ I_i\xrightarrow{a}I_j $$
则：
$$ \boxed{ACTION[i,a]=s_j} $$
如果自动机有非终结符转移：
$$ I_i\xrightarrow{A}I_j $$
则：
$$ \boxed{GOTO[i,A]=j} $$
如果 $I_i$ 中有完成项：
$$ A\to\beta\cdot $$
则对于：
$$ a\in FOLLOW(A) $$
填：
$$ \boxed{ACTION[i,a]=r_k} $$
其中 $k$ 是产生式 $A\to\beta$ 的编号。
如果：
$$ E'\to E\cdot $$
则：
$$ \boxed{ACTION[i,\$]=acc} $$

剩下没填的格子就是：
$$ \boxed{error} $$

按照上面的规则，比如状态 2 这一行：

|状态|`id`|`+`|`*`|`(`|`)`|`$`|
|---|---|---|---|---|---|---|
|2||r2|s7||r2|r2|

意思就是：
- 当前状态 2，lookahead 是 `*`：继续 **shift 到状态 7**
- lookahead 是 `+`、`)` 或 `$`：按$E\to T$归约
- 如果是 `id` 或 `(`：报错
最终可以得到完整的ACTION/GOTO表：

|状态|`id`|`+`|`*`|`(`|`)`|`$`|$E$|$T$|$F$|
|--:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|0|s5|||s4|||1|2|3|
|1||s6||||acc||||
|2||r2|s7||r2|r2||||
|3||r4|r4||r4|r4||||
|4|s5|||s4|||8|2|3|
|5||r6|r6||r6|r6||||
|6|s5|||s4||||9|3|
|7|s5|||s4|||||10|
|8||s6|||s11|||||
|9||r1|s7||r1|r1||||
|10||r3|r3||r3|r3||||
|11||r5|r5||r5|r5||||

完整的运行表：

| 状态栈           | 符号意义   | 输入           | 动作            |
| ------------- | ------ | ------------ | ------------- |
| $0$           |        | $id*id+id\$$ | s5            |
| $0\,5$        | $id$   | $*id+id\$$   | r6: $F\to id$ |
| $0\,3$        | $F$    | $*id+id\$$   | r4: $T\to F$  |
| $0\,2$        | $T$    | $*id+id\$$   | s7            |
| $0\,2\,7$     | $T*$   | $id+id\$$    | s5            |
| $0\,2\,7\,5$  | $T*id$ | $+id\$$      | r6            |
| $0\,2\,7\,10$ | $T*F$  | $+id\$$      | r3            |
| $0\,2$        | $T$    | $+id\$$      | r2            |
| $0\,1$        | $E$    | $+id\$$      | s6            |
| $0\,1\,6$     | $E+$   | $id\$$       | s5            |
| $0\,1\,6\,5$  | $E+id$ | $\$$         | r6            |
| $0\,1\,6\,3$  | $E+F$  | $\$$         | r4            |
| $0\,1\,6\,9$  | $E+T$  | $\$$         | r1            |
| $0\,1$        | $E$    | $\$$         | acc           |
## 缺陷
对于文法：
$$ \begin{aligned} S&\to L=R\mid R\\ L&\to *R\mid id\\ R&\to L \end{aligned} $$

某个 LR(0) 状态：
$$ \begin{aligned} S&\to L\cdot =R\\ R&\to L\cdot \end{aligned} $$
若当前输入是$ = $，则会产生Shift-Reduce Confict.
因此要加强为[[LR(1)].

## 二义性

### 运算符优先级
比如如下文法：
$$ \begin{aligned} E&\to E+E\\ E&\to E*E\\ E&\to id \end{aligned} $$
可以规定：

|当前已完成运算符|lookahead 运算符|动作|
|---|---|---|
|lookahead 优先级更高|如 `+` 后看到 `*`|Shift|
|当前产生式优先级更高|如 `*` 后看到 `+`|Reduce|
|优先级相同且左结合|`+` 后看到 `+`|Reduce|
|优先级相同且右结合|如赋值 `=`|Shift|
或者改写文法：
$$ \begin{aligned} E&\to E+T\mid T\\ T&\to T*F\mid F\\ F&\to(E)\mid id \end{aligned} $$
天然保证优先级，同时左递归保证了左结合。

### IF-ELSE冲突
比如如下文法：
$$ \begin{aligned} S&\to \text{if }E\text{ then }S\\ S&\to \text{if }E\text{ then }S\text{ else }S\\ S&\to other \end{aligned} $$
可以规定遇到 dangling else 的 Shift-Reduce 冲突时选择 Shift。
也可以改写文法，如：
$$ \begin{aligned} S&\to M\mid U\\ M&\to other\\ M&\to \text{if }E\text{ then }M\text{ else }M\\ U&\to \text{if }E\text{ then }S\\ U&\to \text{if }E\text{ then }M\text{ else }U \end{aligned} $$
这里的$M$表示已匹配（matched）语句，$U$表示未匹配（unmatched）语句。

> 这个新文法最核心的限制是$M\to \text{if }E\text{ then }M\text{ else }M$、$U\to \text{if }E\text{ then }M\text{ else }U$，这确保了如果一个`else`要和当前的`if`匹配，那么它的`then`分支内部不能还残留一个未匹配的`if`.