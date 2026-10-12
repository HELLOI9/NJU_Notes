所谓**FOLLOW 集合**，就是**一个非终结符 $A$ 在句型中出现时，它后面“有可能紧跟哪些终结符”？**

我们把这个集合记作：

$$ FOLLOW(A) $$

其中只会包含**终结符**和输入结束符 $\$$。

### FOLLOW 集合的三条计算规则

假设开始符号是 $S$。

#### 规则 1：开始符号的 FOLLOW 中一定有 $\$$

$$ \boxed{\$ \in FOLLOW(S)} $$

因为整个输入串分析完以后，开始符号 $S$ 的后面就是输入结束符。

#### 规则 2：如果有

$$ A\to \alpha B\beta $$

那么：

$$ \boxed{FIRST(\beta)-\{\varepsilon\}\subseteq FOLLOW(B)} $$

> 这里减去$\varepsilon$的原因是定义：后面紧跟的终结符不可能是$\varepsilon$. 

#### 规则 3：如果 $B$ 已经在产生式末尾，或者 $B$ 后面的东西能推出空串，那么把左边非终结符的 FOLLOW 传给 $B$

如果：

$$ A\to \alpha B $$

那么：

$$ \boxed{FOLLOW(A)\subseteq FOLLOW(B)} $$
还有一种等价情况：

$$ A\to\alpha B\beta $$

但是：

$$ \beta\Rightarrow^*\varepsilon $$

也就是：

$$ \varepsilon\in FIRST(\beta) $$

那么：

$$ \boxed{FOLLOW(A)\subseteq FOLLOW(B)} $$
### 手算例子

经典文法：
$$ \begin{aligned} S &\to ABC\\ A &\to a\mid\varepsilon\\ B &\to b\mid\varepsilon\\ C &\to c \end{aligned} $$
假设：
$$ FIRST(A)=\{a,\varepsilon\} $$$$ FIRST(B)=\{b,\varepsilon\} $$$$ FIRST(C)=\{c\} $$
#### Step1：开始符号
因为 $S$ 是开始符号：

$$ FOLLOW(S)=\{\$\} $$
#### Step2：计算FOLLOW(A)
$$ S\to ABC $$

$A$ 后面是：

$$ BC $$

所以：

$$ FIRST(BC)-\{\varepsilon\} $$

加入 $FOLLOW(A)$。

计算：

$$ FIRST(BC) $$

由于：

$$ FIRST(B)=\{b,\varepsilon\} $$

所以首先可以出现 $b$。

但 $B$ 可以为空，所以继续看 $C$：

$$ FIRST(C)=\{c\} $$

因此：

$$ FIRST(BC)=\{b,c\} $$

所以：

$$ \boxed{FOLLOW(A)=\{b,c\}} $$
#### Step3：计算FOLLOW(B)
$$ S\to ABC $$

$B$ 后面是：

$$ C $$

因此：

$$ FIRST(C)-\{\varepsilon\}=\{c\} $$

所以：

$$ FOLLOW(B)\supseteq\{c\} $$

由于 $C$ 不能推出空：

$$ \varepsilon\notin FIRST(C) $$

所以不用加 $FOLLOW(S)$。

最终：

$$ \boxed{FOLLOW(B)=\{c\}} $$
#### Step4：计算FOLLOW(C)
$$ S\to ABC $$

$C$ 在产生式最末尾。

所以：

$$ FOLLOW(S)\subseteq FOLLOW(C) $$

因此：

$$ \boxed{FOLLOW(C)=\{\$\}} $$

==🟡不断扫描所有产生式，不断向 FOLLOW 集合中加入元素，直到所有集合都不再发生变化。==

> FOLLOW集合的求解会经常出现“求不动点”的过程！

考试的时候，可以先给所有非终结符先画表：

| 非终结符 |  FOLLOW  |
| :--: | :------: |
| $S$  | $\{\$\}$ |
| $A$  |          |
| $B$  |          |
| $C$  |          |

然后逐条产生式扫描。