## 定义
LL(1) 意思是 **Left-to-right scan, Leftmost derivation**，最后的 1 表示提前看输入中的1个token（lookahead）。

一个文法$G$是LL(1)的，当且仅当$G$的任意两个不同的产生式$A\to \alpha|\beta$满足：
1. 不存在终结符 $a$ 使得$\alpha,\beta$ 能够推出以 $a$ 开头的串。
2. $\alpha,\beta$ 最多一个能推出 $\varepsilon$.
3. 如果一个分支能推出 $\varepsilon$，那么另一个分支的 FIRST 不能和 FOLLOW(A) 有交集。

> 事实上，(1)(2)等价于FIRST($\alpha$)与FIRST($\beta$)的交集是空集，保证了这两个分支能够区分开；(3)保证了 $\varepsilon$分支和另外一个分支能够区分开。后面我们会看到，这保证了分析表的一格不能同时填入两条产生式。

## 预测分析技术
### 预测分析表的构造
对于每一个产生式：

$$ A\to\alpha $$
1. 对于$a\in FIRST(\alpha)-\{\varepsilon\}$填$M[A,a]=A\to\alpha$.
2. 如果$\varepsilon\in FIRST(\alpha)$，对于$b\in FOLLOW(A)$填$M[A,b]=A\to\alpha$.

事实上，可以令：
$$  SELECT(A\to\alpha)= \begin{cases} FIRST(\alpha), & \varepsilon\notin FIRST(\alpha)\\ (FIRST(\alpha)-\{\varepsilon\})\cup FOLLOW(A), & \varepsilon\in FIRST(\alpha) \end{cases}$$
则：
$$  \forall a\in SELECT(A\to\alpha), \quad M[A,a]=A\to\alpha $$
### 手算例子
文法：

$$ E\to TE' $$$$ E'\to +TE'\mid\varepsilon $$$$ T\to FT' $$$$ T'\to *FT'\mid\varepsilon $$$$ F\to (E)\mid id $$
不难得到：

FIRST：

$$ FIRST(E)=FIRST(T)=FIRST(F)=\{(,id\} $$$$ FIRST(E')=\{+,\varepsilon\} $$$$ FIRST(T')=\{*,\varepsilon\} $$

FOLLOW：

$$ FOLLOW(E)=FOLLOW(E')=\{),\$\} $$$$ FOLLOW(T)=FOLLOW(T')=\{+,),\$\} $$$$ FOLLOW(F)=\{+,*,),\$\} $$
我们一条一条产生式填：

比如对于$E\to TE'$，先算右部：
$$ FIRST(TE') $$

因为：
$$ FIRST(T)=\{(,id\} $$

而 $T$ 不能推出空，因此：
$$ FIRST(TE')=\{(,id\} $$

所以：
$$ M[E,(]=E\to TE' $$$$ M[E,id]=E\to TE' $$

> 直观理解：如果现在要解析一个 $E$，看到的是 `id` 或 `(`，就使用 $E\to TE'$。

|非终结符|`id`|`+`|`*`|`(`|`)`|`$`|
|---|---|---|---|---|---|---|
|$E$|$E\to TE'$|Error|Error|$E\to TE'$|Error|Error|
|$E'$|Error|$E'\to+TE'$|Error|Error|$E'\to\varepsilon$|$E'\to\varepsilon$|
|$T$|$T\to FT'$|Error|Error|$T\to FT'$|Error|Error|
|$T'$|Error|$T'\to\varepsilon$|$T'\to*FT'$|Error|$T'\to\varepsilon$|$T'\to\varepsilon$|
|$F$|$F\to id$|Error|Error|$F\to(E)$|Error|Error|
### 表驱动的非递归预测语法分析

```cpp
设置 ip，使它指向 w$ 的第一个符号；
令 X = 栈顶符号；

while (X != $) {

    if (X == ip 所指向的输入符号 a) {
        弹出栈顶 X；
        ip 向前移动一个位置；
    }

    else if (X 是终结符) {
        error();
    }

    else if (M[X, a] 是报错条目) {
        error();
    }

    else if (M[X, a] = X -> Y1 Y2 ... Yk) {
        输出产生式 X -> Y1 Y2 ... Yk；

        弹出栈顶 X；

        将 Yk, Yk-1, ..., Y1 依次压入栈中，
        使得 Y1 最终位于栈顶；
    }

    令 X = 当前新的栈顶符号；
}
```

按照这个算法，以上面的文法，输入$id+id*id$，可以得到这样的分析表：

|已匹配|栈|剩余输入|动作|
|---|---|---|---|
|$\varepsilon$|$E\$$|$id+id*id\$$|输出 $E\to TE'$|
|$\varepsilon$|$TE'\$$|$id+id*id\$$|输出 $T\to FT'$|
|$\varepsilon$|$FT'E'\$$|$id+id*id\$$|输出 $F\to id$|
|$\varepsilon$|$idT'E'\$$|$id+id*id\$$|匹配 $id$|
|$id$|$T'E'\$$|$+id*id\$$|输出 $T'\to\varepsilon$|
|$id$|$E'\$$|$+id*id\$$|输出 $E'\to+TE'$|
|$id$|$+TE'\$$|$+id*id\$$|匹配 $+$|
|$id+$|$TE'\$$|$id*id\$$|输出 $T\to FT'$|
|$id+$|$FT'E'\$$|$id*id\$$|输出 $F\to id$|
|$id+$|$idT'E'\$$|$id*id\$$|匹配 $id$|
|$id+id$|$T'E'\$$|$*id\$$|输出 $T'\to *FT'$|
|$id+id$|$*FT'E'\$$|$*id\$$|匹配 $*$|
|$id+id*$|$FT'E'\$$|$id\$$|输出 $F\to id$|
|$id+id*$|$idT'E'\$$|$id\$$|匹配 $id$|
|$id+id*id$|$T'E'\$$|$\$$|输出 $T'\to\varepsilon$|
|$id+id*id$|$E'\$$|$\$$|输出 $E'\to\varepsilon$|
|$id+id*id$|$\$$|$\$$|接受|
### 通用递归下降分析器
```cpp
void A() {
    选择一个 A 的产生式 A -> X1 X2 ... Xk;

    for (i = 1 to k) {
        if (Xi 是非终结符)
            调用 Xi();

        else if (Xi == 当前输入符号 a)
            读入下一个输入符号;

        else
            error;
    }
}
```

注：可能需要回溯，是一种暴力的笨方法。

### 习题

> 给出文法$S\to aSa\mid aa$，设计一个带回溯的递归下降的分析器。试说明这个分析器能否识别$aaaaaa$.

分析：首先容易发现这个文法并不是LL(1)，因为$FIRST(aSa)=\{a\}$，$FIRST(aa)=\{a\}$.
其次不难发现，这个递归下降的分析器合理的策略是优先使用产生式$S \to aSa$展开.因此若使用递归下降的分析器，正确的推导是：
$$ S \Rightarrow aSa $$

里面的 $S$ 还要产生四个 $a$：

$$ \Rightarrow aaSaa $$

里面这个 $S$ 再使用：

$$ S\to aa $$

得到：

$$ \Rightarrow aaaaaa $$
但是实际的递归表是这样的，我们编号$a_1a_2a_3a_4a_5a_6\$$：

| 调用    | 尝试      | 结果             |
| ----- | ------- | -------------- |
| $S_0$ | $aS_1a$ | 暂时继续           |
| $S_1$ | $aS_2a$ | 暂时继续           |
| $S_2$ | $aS_3a$ | 暂时继续           |
| $S_3$ | $aS_4a$ | 暂时继续           |
| $S_4$ | $aS_5a$ | 失败             |
| $S_4$ | $aa$    | 吃 $a_5a_6$，成功  |
| $S_3$ | $aS_4a$ | 缺最后一个 $a$，失败   |
| $S_3$ | $aa$    | 吃 $a_4a_5$，成功  |
| $S_2$ | $aS_3a$ | 吃到 $a_6$，成功    |
| $S_1$ | $aS_2a$ | 缺最后一个 $a$，失败   |
| $S_1$ | $aa$    | 吃 $a_2a_3$，成功  |
| $S_0$ | $aS_1a$ | 吃到 $a_4$，成功    |
| 主程序   | 检查 `$`  | 还剩 $a_5a_6$，拒绝 |
这个递归的问题在哪？？？在于==🟡$S()$只返回第一个成功的结果==！
如果要解决这个问题，要重新写一个暴力的递归文法，这不科学。最好的解决方法就是改写成LL(1)文法，用预测分析表去写一个确定的、简洁的递归下降函数：
```cpp
void S() {
    match('a');
    match('a');
    A();
}

void A() {
    if (lookahead == 'a') {
        match('a');
        match('a');
        A();
    }
    else if (lookahead == '$') {
        return;   // A -> ε
    }
    else {
        error();
    }
}
```