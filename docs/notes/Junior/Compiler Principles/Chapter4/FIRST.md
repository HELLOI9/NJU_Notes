**FIRST**集合的含义是：
$$ \boxed{FIRST(\alpha)=\text{“串 }\alpha\text{ 最开始可能出现什么终结符”}} $$
这里的 $\alpha$ 可以是一个非终结符，也可以是一整串符号。

### FIRST的求解规则

#### 规则 1：单个终结符

如果 $X$ 是终结符，那么：

$$ \boxed{FIRST(X)=\{X\}} $$

例如：

$$ FIRST(a)=\{a\} $$

#### 规则 2：单个空串

$$ \boxed{FIRST(\varepsilon)=\{\varepsilon\}} $$

#### 规则 3：产生式右部以终结符开头

如果：

$$ A\to a\alpha $$

其中 $a$ 是终结符，那么：

$$ \boxed{a\in FIRST(A)} $$

例如：

$$ A\to aB $$

则：

$$ a\in FIRST(A) $$

#### 规则 4：产生式右部以非终结符开头

如果：

$$ A\to X_1X_2\cdots X_n $$

则从左往右处理。

先把：

$$ FIRST(X_1)-\{\varepsilon\} $$

加入 $FIRST(A)$。

如果：

$$ \varepsilon\in FIRST(X_1) $$

再继续看 $X_2$，把：

$$ FIRST(X_2)-\{\varepsilon\} $$

加入。

如果：

$$ \varepsilon\in FIRST(X_1), \varepsilon\in FIRST(X_2) $$

再继续看 $X_3$。

一般地，如果：

$$ X_1,X_2,\dots,X_{i-1} $$

都能推出 $\varepsilon$，那么：

$$ FIRST(X_i)-\{\varepsilon\} $$

也要加入 $FIRST(A)$。

也就是：

$$ \boxed{ FIRST(A)\supseteq FIRST(X_1)-\{\varepsilon\} } $$

如果 $X_1\Rightarrow^*\varepsilon$，再加：

$$ FIRST(X_2)-\{\varepsilon\} $$

如果 $X_1X_2\Rightarrow^*\varepsilon$，再加：

$$ FIRST(X_3)-\{\varepsilon\} $$

以此类推。


#### 规则 5：整个右部都能为空

如果：

$$ A\to X_1X_2\cdots X_n $$

而且：

$$ \varepsilon\in FIRST(X_i),\quad \forall i=1,\dots,n $$

也就是所有 $X_i$ 都能推出空串，那么：

$$ \boxed{\varepsilon\in FIRST(A)} $$

因为：

$$ A\Rightarrow X_1X_2\cdots X_n\Rightarrow^*\varepsilon $$

#### 规则 6：多个产生式取并集

如果：

$$ A\to\alpha_1\mid\alpha_2\mid\cdots\mid\alpha_k $$

那么：

$$ \boxed{ FIRST(A) = FIRST(\alpha_1) \cup FIRST(\alpha_2) \cup\cdots\cup FIRST(\alpha_k) } $$

例如：

$$ A\to aB\mid cD\mid\varepsilon $$

那么：

$$ \boxed{ FIRST(A)=\{a,c,\varepsilon\} } $$
### 手算例子
$$ A\to B $$$$ B\to A\mid b $$

先从：

$$ B\to b $$

得到：

$$ b\in FIRST(B) $$

然后因为：

$$ A\to B $$

得到：

$$ b\in FIRST(A) $$

再继续扫描，集合不再变化，于是停止。

最终：

$$ \boxed{FIRST(A)=FIRST(B)=\{b\}} $$
> ⚠️ FIRST集合的求解会经常出现“求不动点”的过程！


