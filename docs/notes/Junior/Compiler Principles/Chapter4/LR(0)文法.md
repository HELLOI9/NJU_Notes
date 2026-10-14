LR(0)是一种[[自底向上的语法分析技术]]。

## LR(0)项
假设有产生式$A\to XYZ$，给右部加一个点 `·`，就得到四个 LR(0) 项：
$$ A\to \cdot XYZ $$$$ A\to X\cdot YZ $$$$ A\to XY\cdot Z $$$$ A\to XYZ\cdot $$
这个点是在记录这条产生式目前已经识别到了什么位置。
比如对于项 $A\to\alpha\cdot\beta$，表示对产生式 $A\to\alpha\beta$，目前已经识别完了 $\alpha$，接下来还期待识别 $\beta$。

某个时刻，分析器往往不能只认为“我现在可能正在匹配一条产生式”，而是可能同时存在多个可能性。所以一个 LR(0) 状态实际上是LR(0) 项的集合，也就是**项集（item set）**。

构造LR自动机之前，先把原文法 $G$ 增广成 $G'$，即假设原开始符号是 $S$，添加新的开始符号 $S'$，构造增广文法$G'=G+\{S'\to S\}$，通过$S'\to\cdot S$表示分析开始、$S'\to S\cdot$表示分析结束（Accpet）而不是普通的Reduce。

### CLOSURE 项集闭包
如果一个项集I中有：
$$ A\to\alpha\cdot B\beta $$
点后面是一个非终结符 $B$，那么我们需要马上考虑$B$ 可以从哪些产生式开始识别。因此对于每一个$B\to\gamma$，加入：$$ B\to\cdot\gamma $$
如果新加入的项点后面又是非终结符，则继续展开，直到没有新项可以加入，这就是CLOSURE(I)。
比如增广文法：$$ \begin{aligned} E'&\to E\\ E&\to E+T\mid T\\ T&\to T*F\mid F\\ F&\to(E)\mid id \end{aligned} $$
从$I=\{E'\to\cdot E\}$开始，因为点后面是 $E$，加入所有 $E$ 的产生式：$E\to\cdot E+T$、$E\to\cdot T$；点后面有 $T$，所以加入：$T\to\cdot T*F$、$T\to\cdot F$；点后面有$F$，继续加入：$F\to\cdot(E)$、 $F\to\cdot id$。最终得到：
$$ \begin{aligned} CLOSURE(\{E'\to\cdot E\})=\{& E'\to\cdot E,\\ &E\to\cdot E+T,\\ &E\to\cdot T,\\ &T\to\cdot T*F,\\ &T\to\cdot F,\\ &F\to\cdot(E),\\ &F\to\cdot id \} \end{aligned} $$
这整个集合就是一个LR(0)的状态。

除此之外，我们把点在最左边的项叫做**非内核项**，初始项和所有点不在左边的项叫做**内核项**，非内核项可以由内核项通过CLOSURE自动恢复。

### GOTO函数
定义$GOTO(I,X)$，其中：
- $I$：当前项集，也就是当前状态；
- $X$：一个文法符号，可以是终结符或非终结符。
含义是当前状态 $I$ 中，如果识别了一个 $X$，会进入哪个新状态。

对于$GOTO(I,X)$，现在$I$中找到所有$A\to\alpha\cdot X\beta$，然后把点跨过$X$得到$A\to\alpha X\cdot\beta$，再把这些新项收集起来做CLOSURE，最终得到$GOTO(I,X) = CLOSURE( \{A\to\alpha X\cdot\beta \mid A\to\alpha\cdot X\beta\in I \})$ 。

其实可以和DFA对比一下：

| DFA 化                 | LR(0)         |
| --------------------- | ------------- |
| 状态集合                  | 项集            |
| $\varepsilon$-CLOSURE | CLOSURE       |
| MOVE($I,X$)           | GOTO($I,X$)   |
| DFA 状态                | LR(0) 项集      |
| DFA 转移                | LR(0) GOTO 转移 |
### LR(0)自动机
#### 定义
有了规范 LR(0) 项集族，就可以构造自动机：
- 每个 $I_i$ 是一个状态；
- 如果：
$$ GOTO(I_i,X)=I_j $$
就画一条$I_i\xrightarrow{X}I_j$的边。
初始状态为$I_0=CLOSURE(\{S'\to\cdot S\})$。

![[Pasted image 20261012193548.png|382]]

#### 操作
##### Shift
如果当前状态 $I_i$ 在终结符 $a$ 上有：

$$ I_i\xrightarrow{a}I_j $$

那么：
1. 把 $a$ 压入符号栈；
2. 把 $j$ 压入状态栈；
3. 输入向前移动一个 token。

##### Reduce
如果决定按：

$$ A\to\beta $$

归约，假设：

$$ |\beta|=k $$

那么：
1. 弹出 $k$ 个文法符号；
2. 弹出 $k$ 个状态；
3. 设现在栈顶状态是 $I_i$；
4. 沿着：$I_i\xrightarrow{A}I_j$转移；  
5. 压入 $A$ 和状态 $j$。

#### 手算例子
对文法：

$$ \begin{aligned} E'&\to E\\ E&\to E+T\mid T\\ T&\to T*F\mid F\\ F&\to(E)\mid id \end{aligned} $$
输入$id*id\$$，解析如下：

| 步骤  | 状态栈           | 符号栈        | 输入        | 动作            |
| --- | ------------- | ---------- | --------- | ------------- |
| 1   | $0$           | $\$$       | $id*id\$$ | 移入 `id`，到 5   |
| 2   | $0\,5$        | $\$\,id$   | $*id\$$   | $F\to id$ 归约  |
| 3   | $0\,3$        | $\$\,F$    | $*id\$$   | $T\to F$ 归约   |
| 4   | $0\,2$        | $\$\,T$    | $*id\$$   | 移入 `*`，到 7    |
| 5   | $0\,2\,7$     | $\$\,T*$   | $id\$$    | 移入 `id`，到 5   |
| 6   | $0\,2\,7\,5$  | $\$\,T*id$ | $\$$      | $F\to id$ 归约  |
| 7   | $0\,2\,7\,10$ | $\$\,T*F$  | $\$$      | $T\to T*F$ 归约 |
| 8   | $0\,2$        | $\$\,T$    | $\$$      | $E\to T$ 归约   |
| 9   | $0\,1$        | $\$\,E$    | $\$$      | Accept        |
