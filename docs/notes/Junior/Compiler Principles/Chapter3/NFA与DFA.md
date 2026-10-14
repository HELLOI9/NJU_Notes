## 自动机

### 状态转换图（Transition Diagram）

状态转换图是有限自动机的一种**图形表示**。它本质上是一个带标号的有向图：

- 每个结点表示一个**状态**；
- 每条有向边表示一个**状态转移**；
- 边上的标号表示触发该转移所需要读入的输入符号；
- 一个没有来源的箭头指向**初始状态**；
- 双圆圈表示**接受状态**或终止状态。

### DFA

DFA（Deterministic Finite Automaton，确定有限自动机）形式化定义为一个五元组：

$$ \boxed{ M=(Q,\Sigma,\delta,q_0,F) } $$

其中：

- $Q$：有限的状态集合；
- $\Sigma$：有限的输入字母表；
- $\delta$：状态转移函数；
- $q_0\in Q$：初始状态；
- $F\subseteq Q$：接受状态集合。

DFA 状态转移函数：

$$ \boxed{ \delta:Q\times\Sigma\to Q } $$

它的含义是对于任意当前状态 $q\in Q$ 和任意输入符号 $a\in\Sigma$，都有且仅有一个确定的下一状态。

接受条件：有且仅有一条最终到达接受态的路径。

### NFA

NFA（Nondeterministic Finite Automaton，非确定有限自动机）形式化定义为一个五元组：

$$ \boxed{ M=(Q,\Sigma,\delta,q_0,F) } $$

其中：

- $Q$：有限的状态集合；
- $\Sigma$：有限的输入字母表；
- $\delta$：状态转移函数；
- $q_0\in Q$：初始状态；
- $F\subseteq Q$：接受状态集合。

NFA状态转移函数：

$$ \boxed{ \delta: Q\times(\Sigma\cup\{\epsilon\}) \to 2^Q } $$

接受条件：至少存在一条运行到接受态的路径。

## 子集构造法

### 核心思想

核心思想：==DFA的一个状态对应NFA的“一组可能的状态”==。

定义$\epsilon$-closure（epsilon closure，$\epsilon$ 闭包）表示：从某个状态出发，**不读任何输入字符**，只走 $\epsilon$ 边，能够到达的所有状态。注意：还包括它自己！！！

整个算法就两步：

第一步，计算：

$$ \operatorname{move}(T,a) $$

意思是从 $T$ 中的所有 NFA 状态出发，真正读一个字符 $a$能到达的状态。

第二步，求 $\epsilon$-closure：

因为读完 $a$ 以后，还可以继续免费走若干条 $\epsilon$ 边，所以真正的 DFA 下一状态是：

$$\epsilon\text{-closure}(\operatorname{move}(T,a)) $$

这就是整个算法最重要的公式。

### 算法

假设 NFA有状态集合 $Q$、字母表 $\Sigma$、初态 $q_0$、接受状态集合 $F$。

### 第一步：求 DFA 初态

DFA 初态不是简单的 $q_0$，而是：

$$  D_0=\epsilon\text{-closure}(\{q_0\}) $$

### 第二步：对每个 DFA 状态集合 $T$

对于每一个输入字符 $a\in\Sigma$，计算：

$$ U=\epsilon\text{-closure}(\operatorname{move}(T,a)) $$

然后：

- 如果 $U$ 以前没出现过，就把它加入 DFA 状态集合；
- 加一条 DFA 转移：

$$ T\xrightarrow{a}U $$

### 第三步：不断重复

直到再也产生不出新的状态集合。

### 第四步：判断哪些 DFA 状态是接受态

如果 DFA 的某个集合状态 $T$ 中包含至少一个 NFA 接受状态：

$$ T\cap F\neq\varnothing $$

那么$T$是DFA接收状态。

## DFA状态最小化

首先把 DFA 状态分成两组：

$$ P_0= \{ F_D,\; Q_D-F_D \} $$

即：

- 接受态一组；
- 非接受态一组。

然后不断检查同一组中的状态。

如果两个状态 $p,q$ 对某个字符 $a$：

$$ \delta_D(p,a) $$

和

$$ \delta_D(q,a) $$

落入了当前划分中的**不同组**，那么 $p,q$ 一定不能等价，需要拆开。

不断细分，直到划分不再变化。

最后同一个分组中的状态就是可以合并的状态。

假设最终划分为：

$$ P=\{B_1,B_2,\dots,B_k\} $$

那么每一个分组 $B_i$ 压缩成最小 DFA 的一个状态。

如果 $q\in B_i$，定义：

$$ \delta_{\min}(B_i,a) = [\delta_D(q,a)] $$

其中右边表示 $\delta_D(q,a)$ 所在的分组。