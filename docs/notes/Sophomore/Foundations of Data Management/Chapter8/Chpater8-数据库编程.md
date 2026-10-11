# 第8章 数据库编程

## 1. 概述：SQL的三种使用方式

SQL语言在应用系统中的使用方式有三种，适用于不同的开发场景：

| 使用方式 | 全称 | 应用场景 | 特点 |
|----------|------|----------|------|
| **交互式SQL** | Interactive SQL（ISQL） | 命令行 / 批处理 | 可独立运行，供临时用户即席查询（ad-hoc query） |
| **嵌入式SQL** | Embedded SQL（ESQL） | 主语言 + ESQL，数据库应用开发 | 嵌入宿主语言中，需预编译处理 |
| **过程化SQL** | Procedural Language SQL（PL/SQL） | SQL编程 | 兼有数据访问与流程控制；可在数据库服务器内独立运行；用于存储过程、函数、触发器 |

**引入嵌入式SQL的原因：**
- SQL是非过程性语言，无法实现复杂的业务逻辑（循环、条件判断等）
- 事务处理应用需要高级程序设计语言的能力
- 最终用户不应直接书写SQL，应通过应用程序间接访问数据库，避免误操作（错误的 `UPDATE`、`DELETE` 等）

---

## 2. 8.1 嵌入式SQL（ESQL）

### 2.1.1 处理过程

**定义：** 将SQL语句嵌入程序设计语言（如C、C++、Java）中，被嵌入的程序设计语言称为**宿主语言**，简称**主语言**（Host Language）。

**处理方式——预编译方法：**
```
含嵌入式SQL语句的主语言程序
        ↓
RDBMS预处理程序：将嵌入式SQL语句转换为函数调用
        ↓
转换后的主语言程序
        ↓
主语言编译程序：编译处理
        ↓
目标语言程序（可执行文件）
```

> 💡 **核心要点：** 预编译器识别 `EXEC SQL ... ;` 标记的SQL语句，将其转换为对应的数据库API函数调用，再由主语言编译器统一编译。

### 2.1.2 主语言与ESQL的通信机制

在嵌入式SQL程序中，存在两种不同计算模型的语句并存：
- **SQL语句**：描述性的、面向集合的语句，负责操纵数据库
- **主语言语句**：过程性的、面向记录的语句，负责控制逻辑流程

它们之间的通信通过以下三种机制实现：

#### ① SQL通信区（SQLCA — SQL Communication Area）

**定义：** SQLCA是一个由数据库系统维护的数据结构，用于在SQL语句执行后向应用程序反馈执行状态信息。

**用途：**
- 描述系统当前工作状态
- 描述运行环境信息

**关键变量：**
- `SQLCODE`：每次执行SQL语句后返回的状态码
  - `SQLCODE == SUCCESS（预定义常量）`：SQL语句执行成功
  - `SQLCODE != 0`：出错，应用程序据此进行异常处理

**使用方法：**
```c
EXEC SQL INCLUDE SQLCA;   /* 定义SQL通信区 */
/* 每执行完一条SQL语句后检查 SQLCA.SQLCODE */
if (SQLCA.SQLCODE != 0) {
    /* 处理错误 */
}
```

#### ② 主变量（Host Variable）

**定义：** 在嵌入式SQL语句中可以使用的主语言程序变量，称为**主变量**（Host Variable）。

**作用：**
- **输入主变量**：由应用程序赋值，在SQL语句中被引用（传参给SQL）
- **输出主变量**：由SQL语句赋值，将查询结果返回给应用程序

**使用规则：**
- 必须在 `BEGIN DECLARE SECTION ... END DECLARE SECTION` 中声明
- 在SQL语句中使用时，前面必须加冒号 `:` 前缀，以区别于SQL变量（表名、列名等）
- 在主语言语句中直接使用，**不加**冒号

**声明示例：**
```c
EXEC SQL BEGIN DECLARE SECTION;    /* 主变量声明开始 */
char Deptname[21];
char Hsno[10];
char Hsname[21];
char Hssex[3];
int  HSage;
int  NEWAGE;
EXEC SQL END DECLARE SECTION;     /* 主变量声明结束 */
```

**声明的两个作用：**
1. 在编译时对主语言变量与对应属性进行**类型一致性检查**
2. 为接收数据库返回的结果值而**预先申请足够大的内存空间**

> ⚠️ **注意：** 对于字符类型属性，C语言中的字符数组需要比数据库中对应属性的最大长度多1个字节（存放字符串结束符 `\0`），否则会产生内存溢出错误。

**使用示例：**
```c
EXEC SQL SELECT Sno, Sname, Sage
         INTO :hsno, :hsname, :hsage      /* INTO子句：输出主变量 */
         FROM Student
         WHERE Sno = :givensno;           /* WHERE子句：输入主变量 */
```

#### ③ 指示变量（Indicator Variable）

**定义：** 指示变量是一个**整型变量**，是一种特殊的主变量，用来"指示"相关主变量的值是否为空值（NULL）。一个主变量可以附带一个指示变量。

**用途：**
- 指示输入主变量是否为空值（插入NULL时）
- 检测输出变量是否为空值，或值是否被截断

**取值含义：**

| 指示变量值 | 含义 |
|-----------|------|
| `0` | 数据库返回的是正常值（非NULL），已赋给主变量 |
| `-1` | 数据库中的值是NULL，主变量中无有效值 |
| `> 0` | 数据库字符串被截断后赋给主变量（值为截断前的原始长度） |

**使用示例（输出）——例8.3：**
```c
EXEC SQL SELECT Sno, Cno, Grade
         INTO :Hsno, :Hcno, :Hgrade :Gradeid  /* Gradeid为指示变量 */
         FROM SC
         WHERE Sno = :givensno AND Cno = :givencno;

IF (Gradeid < 0) {
    /* 成绩为空值，不能使用Hgrade */
} ELSE {
    /* 成绩有效，保存在Hgrade中 */
}
```

**使用示例（输入，插入NULL值）——例8.5：**
```c
gra_ind = -1;                  /* 将指示变量设为-1，表示NULL */
EXEC SQL INSERT INTO SC(Sno, Cno, Grade)
         VALUES(:stdno, :couno, :gr :gra_ind);  /* 插入NULL成绩 */
```

> 💡 **补充：** 主变量与指示变量之间用**空格**或保留字 `INDICATOR` 分隔。

#### ④ 游标（Cursor）

（详见 [8.1.4节](#214-使用游标的sql语句)）

#### ⑤ 数据库连接与断开

```c
/* 建立连接 */
EXEC SQL CONNECT TO target [AS connection-name] [USER user-name];
/* target 可以是：<dbname>@<hostname>:<port>、SQL串常量、或 DEFAULT */

/* 切换当前连接 */
EXEC SQL SET CONNECTION connection-name | DEFAULT;

/* 断开连接 */
EXEC SQL DISCONNECT [connection-name];
```

---

### 2.1.3 不用游标的SQL语句

以下类型的SQL语句**不需要使用游标**：
- 说明性语句（如 `INCLUDE SQLCA`、`DECLARE SECTION`）
- 数据定义语句（`CREATE`、`DROP`、`ALTER`）
- 数据控制语句（`GRANT`、`REVOKE`、`COMMIT`、`ROLLBACK`）
- **查询结果为单条记录的 `SELECT` 语句**（用 `INTO` 子句接收结果）
- 非CURRENT形式的 `INSERT`、`DELETE`、`UPDATE` 语句

#### 单记录查询——例8.2：

```c
EXEC SQL SELECT Sno, Sname, Ssex, Sage, Sdept
         INTO :Hsno, :Hname, :Hsex, :Hage, :Hdept
         FROM Student
         WHERE Sno = :givensno;
```

> ⚠️ **注意：** 如果实际查询结果不是单条而是多条记录，则程序出错，RDBMS会在SQLCA中返回错误信息。

#### 非CURRENT形式的UPDATE——例8.4：

```c
EXEC SQL UPDATE SC
         SET Grade = :newgrade
         WHERE Sno = :givensno AND Cno = '1';
```

---

### 2.1.4 使用游标的SQL语句

#### 为什么需要游标？

**核心矛盾：**
- SQL语言是**面向集合**的，一条SQL语句可以产生或处理**多条记录**
- 主语言是**面向记录**的，一组主变量**一次只能存放一条记录**

**游标的本质：** 游标（Cursor）是系统为用户开设的一个**数据缓冲区**，用于存放SQL查询的执行结果。每个游标有一个名字。通过游标，用户可以从结果集中**逐条**获取记录，赋给主变量，由主语言进一步处理。

> 这种处理方式称为 **One-Row-at-a-Time Principle（逐行处理原则）**。

#### 必须使用游标的场景：

- 查询结果为**多条记录**的 `SELECT` 语句
- **CURRENT形式**的 `UPDATE` 语句（更新游标当前指向的元组）
- **CURRENT形式**的 `DELETE` 语句（删除游标当前指向的元组）

#### 游标操作的四个步骤：

##### 步骤1：声明游标（DECLARE）

```c
EXEC SQL DECLARE cursor_name CURSOR FOR
    subquery
    [ORDER BY ......]
    [FOR {READ ONLY | UPDATE [OF columnname, ...]}];
```

- 这是一条**说明性语句**，执行时数据库并不执行对应的 `SELECT` 语句
- 如果声明了 `FOR UPDATE`，则游标为**可更新游标**，可执行CURRENT形式的 `UPDATE`/`DELETE`
- 带有 `UNION` 或 `ORDER BY` 的游标**不可更新**

**示例：**
```c
EXEC SQL DECLARE agent_dollars CURSOR FOR
    SELECT aid, sum(dollars)
    FROM orders
    WHERE cid = :cust_id
    GROUP BY aid;
```

##### 步骤2：打开游标（OPEN）

```c
EXEC SQL OPEN agent_dollars;
```

- 执行对应的 `SELECT` 语句，将结果集放入缓冲区
- 游标指针指向结果集**第一条记录的前面**（尚未指向任何记录）

##### 步骤3：推进游标并取当前记录（FETCH）

```c
EXEC SQL FETCH agent_dollars
         INTO :agent_id, :dollar_sum;
```

- 将游标指针推进到下一条记录
- 将当前记录的值读出，赋给对应的主变量
- 通常放在循环中反复执行，直到 `NOT FOUND` 异常触发循环结束

**完整循环示例：**
```c
EXEC SQL WHENEVER NOT FOUND GOTO finish;

while (TRUE) {
    EXEC SQL FETCH agent_dollars INTO :agent_id, :dollar_sum;
    printf("%s %11.2f\n", agent_id, dollar_sum);
}

finish:
    EXEC SQL CLOSE agent_dollars;
```

##### 步骤4：关闭游标（CLOSE）

```c
EXEC SQL CLOSE agent_dollars;
```

- 关闭游标，释放结果集占用的缓冲区及其他资源
- 游标关闭后**可以重新打开**，每次 `OPEN` 都会重新执行对应的查询语句

> 💡 **补充：** 游标的结果集只能被**顺序遍历一次**（无 `ORDER BY` 时顺序是随机的）。如需重复或逆向遍历，需使用**可滚动游标**（Scrollable Cursor）。

#### 可滚动游标（Scrollable Cursor）：

```c
EXEC SQL DECLARE cursor_name [INSENSITIVE] [SCROLL]
         CURSOR [WITH HOLD] FOR subquery ...;

EXEC SQL FETCH [{NEXT | PRIOR | FIRST | LAST | {ABSOLUTE | RELATIVE} value} FROM]
         cursor_name INTO ...;
```

#### CURRENT形式的UPDATE/DELETE——例8.1：

```c
EXEC SQL UPDATE Student
         SET Sage = :NEWAGE
         WHERE CURRENT OF SX;   /* 更新当前游标SX指向的元组 */
```

---

### 2.1.5 动态SQL

#### 静态SQL vs 动态SQL

| 对比维度 | 静态SQL | 动态SQL |
|---------|---------|---------|
| SQL语句确定时机 | 应用开发阶段（预编译时确定） | 运行时动态生成 |
| 优点 | 预编译时进行分析和执行计划优化，正确性高 | 可根据运行时数据库状态选择最优访问路径 |
| 缺点 | 只能按缺省参数优化，访问路径可能非最优 | 需要动态进行语法分析和访问路径选择，有额外开销 |

#### 何时使用动态SQL？
- 应用程序需要在执行过程中生成SQL语句
- SQL语句用到的数据库对象在预编译时不存在
- 希望SQL语句根据执行时数据库统计信息采用最优访问策略

#### 动态SQL的可变性：
- SQL语句正文动态可变
- 变量个数动态可变
- 语句类型动态可变
- SQL语句引用的数据库对象动态可变

#### 方式1：使用SQL语句主变量

SQL语句主变量：程序主变量包含的内容是**SQL语句的文本**，而不是数据值。

**例8.6：动态创建表**
```c
EXEC SQL BEGIN DECLARE SECTION;
const char *stmt = "CREATE TABLE test(a int);";  /* SQL语句主变量 */
EXEC SQL END DECLARE SECTION;
......
EXEC SQL EXECUTE IMMEDIATE :stmt;   /* 立即执行动态SQL语句 */
```

#### 方式2：动态参数（`?` 占位符）

- SQL语句中使用 `?` 表示该位置的数据在运行时绑定
- 与主变量的区别：动态参数在 `EXECUTE` 时才完成绑定，而不是编译时

**使用步骤：**
1. 声明SQL语句主变量
2. `PREPARE`：准备SQL语句（进行语法分析、生成执行计划）
3. `EXECUTE`：执行准备好的语句，并绑定实际参数

**例8.7：动态插入元组**
```c
EXEC SQL BEGIN DECLARE SECTION;
const char *stmt = "INSERT INTO test VALUES(?);";  /* 含动态参数的SQL */
EXEC SQL END DECLARE SECTION;

EXEC SQL PREPARE mystmt FROM :stmt;   /* 准备语句，进行语法分析 */

EXEC SQL EXECUTE mystmt USING 100;    /* 执行，绑定参数 ? = 100 */
EXEC SQL EXECUTE mystmt USING 200;    /* 再次执行，绑定参数 ? = 200 */
```

> 💡 **补充：** `PREPARE` + `EXECUTE` 分离的好处是同一条语句可以被多次执行，仅需一次语法分析和查询优化，效率更高。

---

### 2.1.6 嵌入式SQL总结

#### 嵌入式SQL程序的基本结构

1. **声明段（Declare Section）**：声明主变量、指示变量、游标
2. **异常处理定义（Condition Handling）**：定义异常捕捉规则
3. **建立数据库连接（SQL Connect）**：`EXEC SQL CONNECT TO ...`
4. **应用程序主体（Main Body）**：主语言逻辑 + ESQL数据访问语句
5. **断开连接（SQL Disconnect）**：`EXEC SQL DISCONNECT ...`

#### 异常处理（WHENEVER语句）

**语法：**
```c
EXEC SQL WHENEVER condition action;
```

预编译器会在每条嵌入式SQL语句之后自动插入 `if (condition) { action }` 检查代码。

**条件类型（condition）：**

| 条件 | 含义 |
|------|------|
| `SQLERROR` | 严重SQL执行错误，通常会终止程序 |
| `NOT FOUND` | SQL语句成功执行，但未访问到任何元组（用于结束游标循环） |
| `SQLWARNING` | 非严重但值得注意的异常，相关信息保存在SQLCA中 |

**动作类型（action）：**

| 动作 | 含义 |
|------|------|
| `CONTINUE` | 忽略异常，不改变程序控制流程 |
| `GOTO label` | 跳转到标号 `label` 处继续执行 |
| `STOP` | 立即终止程序，回滚事务并断开连接 |
| `DO function \| BREAK \| CONTINUE` | 调用C函数，或改变循环控制流 |

**常用示例：**
```c
EXEC SQL WHENEVER SQLERROR  GOTO report_error;
EXEC SQL WHENEVER NOT FOUND GOTO finish;
```

#### SQL数据类型与C语言数据类型对应关系

| SQL类型 | C语言类型 |
|---------|----------|
| `char(n)` / `varchar(n)` | `char arr[n+1]` |
| `smallint` | `short int` |
| `integer` / `int` | `int` |
| `real` | `float` |
| `double precision` | `double` |

---

## 3. 8.2 过程化SQL（PL/SQL & T-SQL）

**定义：** 在交互式SQL的基础上扩充过程式程序设计语言的成分，构成一个可编程的SQL语言，称为**过程化SQL**（也称过程式SQL、可编程SQL）。

**最常用的两种实现：**
- **PL/SQL**（Procedural Language/SQL）：Oracle、PostgreSQL等
- **T-SQL**（Transact-SQL）：Microsoft SQL Server、Sybase

**相比嵌入式SQL的优势：**
- 可独立编程，无需区分主变量与SQL变量
- 无需预编译到编译的转换过程
- 在数据库服务器内部实现数据交换与处理

**用途：** 用于定义**触发器**、**存储过程**、**存储函数**对应的SQL程序块。

### 3.2.1 块结构

过程化SQL的基本结构是**块（Block）**，块之间可以互相嵌套，每个块完成一个逻辑操作。

```sql
DECLARE
    -- 变量、常量、游标、异常等的定义
    -- 定义的变量/常量只在该块内有效，块执行结束后消失
BEGIN
    -- SQL语句、过程化SQL的流程控制语句
EXCEPTION
    -- 异常处理部分（遇到不能继续执行的情况时触发）
END;
```

**三个部分：**
- **定义部分（DECLARE）**：声明局部变量、常量、游标、自定义异常等（可选）
- **执行部分（BEGIN...END）**：必须存在，包含SQL语句和流程控制语句
- **异常处理部分（EXCEPTION）**：捕获并处理运行时异常（可选）

### 3.2.2 变量和常量的定义

#### PL/SQL中的变量和常量定义语法：

```sql
-- 变量定义
变量名  数据类型  [[NOT NULL] {:= | DEFAULT} 初值表达式];

-- 常量定义（必须赋初值，且不可修改）
常量名  数据类型  CONSTANT := 常量表达式;

-- 赋值语句
变量名 := 表达式;
```

#### Oracle常用基本数据类型：

| 数据类型 | 描述 |
|---------|------|
| `NUMBER` | 数字型，范围 10⁻¹³⁰ ~ 10¹²⁵ |
| `CHAR` | 字符型，最大2000个字符 |
| `VARCHAR2` | 变长字符型，最大4000个字符 |
| `DATE` | 日期型，包括日期、小时、分、秒 |
| `LONG` | 大文本 |
| `BOOLEAN` | 逻辑型，取值 TRUE、FALSE、NULL |

#### 变量定义的四种方式：

**方式1：使用基本数据类型**
```sql
sex     BOOLEAN  := TRUE;
today   DATE     NOT NULL := SYSDATE;
age     NUMBER(3) NOT NULL := 25;
```

**方式2：%TYPE（与表中某列类型保持一致）**
```sql
-- 变量类型自动与 Student 表的 Sno 列保持一致
v_sno  Student.Sno%TYPE;
```
优点：当表结构改变时，变量类型自动随之改变，增强代码健壮性。

**方式3：自定义记录类型（RECORD）**
```sql
TYPE student IS RECORD (
    id       NUMBER(4)  NOT NULL DEFAULT 0,
    name     CHAR(10),
    sex      BOOLEAN    NOT NULL DEFAULT TRUE,
    birthdate DATE,
    physics  NUMBER(3),
    chemistry NUMBER(3)
);
student1 student;   -- 声明记录类型变量

-- 属性引用方式
student1.id
student1.name
```

**方式4：%ROWTYPE（与表行结构完全一致）**
```sql
emp_val  emp%ROWTYPE;
-- 引用方式
emp_val.empno
emp_val.ename
```

#### 全局变量与局部变量：

```sql
variable fac number;    /* 全局变量（在过程块之外定义，使用时加 : 前缀） */

DECLARE
    NUM NUMBER(3) := 5;  /* 局部变量（在过程块内定义，只能在块内引用） */
BEGIN
    :fac := 1;           /* 全局变量加 : 前缀 */
    IF NUM > 0 THEN
        FOR i IN 1..NUM LOOP
            :fac := :fac * i;
        END LOOP;
    END IF;
END;
```

#### PL/SQL中的游标属性：

| 属性 | 类型 | 含义 |
|------|------|------|
| `游标名%ISOPEN` | BOOLEAN | 游标是否已打开 |
| `游标名%FOUND` | BOOLEAN | 最近一次FETCH是否返回了结果 |
| `游标名%NOTFOUND` | BOOLEAN | 最近一次FETCH是否未返回结果（用于循环结束判断） |
| `游标名%ROWCOUNT` | NUMBER | 到目前为止已从游标中取出的记录总数 |

### 3.2.3 流程控制

#### 1. 条件控制语句（IF）

```sql
-- 形式1：简单IF
IF condition THEN
    sequence_of_statements;
END IF;

-- 形式2：IF-ELSE
IF condition THEN
    sequence_of_statements1;
ELSE
    sequence_of_statements2;
END IF;

-- 形式3：嵌套IF（IF-ELSIF-ELSE）
IF condition1 THEN
    ...
ELSIF condition2 THEN
    ...
ELSE
    ...
END IF;
```

#### 2. 循环控制语句（LOOP）

```sql
-- 简单LOOP（需用EXIT/BREAK退出）
LOOP
    sequence_of_statements;
    EXIT WHEN condition;   -- 满足条件时退出
END LOOP;

-- WHILE-LOOP
WHILE condition LOOP
    sequence_of_statements;
END LOOP;

-- FOR-LOOP（count自动从bound1递增到bound2）
FOR count IN [REVERSE] bound1..bound2 LOOP
    sequence_of_statements;
END LOOP;
```

#### 3. 错误处理（EXCEPTION）

```sql
EXCEPTION
    WHEN 异常情况1 [OR 异常情况2 ...] THEN
        ...; -- 处理语句
    WHEN 异常情况3 THEN
        ...;
    WHEN OTHERS THEN
        ...; -- 捕获所有未处理的异常
```

常见预定义异常：`NO_DATA_FOUND`（未找到数据）、`TOO_MANY_ROWS`（查询返回多行但期望单行）、`ZERO_DIVIDE`（除以零）等。

---

#### T-SQL（Transact-SQL）要点

T-SQL是微软SQL Server的过程化SQL实现，主要特性如下：

**标识符规则：**
- `@变量名`：局部变量（用户自定义）
- `@@变量名`：全局变量（系统定义，只读）
- `#对象名`：局部临时对象
- `##对象名`：全局临时对象

**局部变量声明与赋值：**
```sql
DECLARE @变量名 数据类型 [, ...]

-- 赋值方式1：SET
SET @variable_name = expression

-- 赋值方式2：SELECT（从查询结果赋值）
SELECT @EmpIDVariable = EmployeeID
FROM Employees
ORDER BY EmployeeID DESC
```

**常用流程控制语句：**
- `BEGIN ... END`：语句块
- `IF ... ELSE ...`：条件判断
- `CASE`：多分支（简单型/搜索型）
- `WHILE, CONTINUE, BREAK`：循环控制
- `GOTO`：无条件跳转
- `WAITFOR`：延时执行（`DELAY` 延迟时长，`TIME` 指定时间）
- `RETURN`：返回

**CASE表达式示例（搜索型）：**
```sql
SELECT 'Price Category' =
    CASE
        WHEN price IS NULL          THEN 'Not yet priced'
        WHEN price < 10             THEN 'Very Reasonable Title'
        WHEN price >= 10 AND price < 20 THEN 'Coffee Table Title'
        ELSE 'Expensive book!'
    END,
    CAST(title AS varchar(20)) AS 'Shortened Title'
FROM titles
ORDER BY price;
```

**WHILE循环示例：**
```sql
WHILE (SELECT AVG(price) FROM titles) < $30
BEGIN
    UPDATE titles SET price = price * 2
    SELECT MAX(price) FROM titles
    IF (SELECT MAX(price) FROM titles) > $50
        BREAK       -- 退出循环
    ELSE
        CONTINUE    -- 继续下一次循环
END
PRINT 'Too much for the market to bear'
```

---

## 4. 8.3 存储过程和函数

### 基本概念

**存储过程（Stored Procedure）：** 用过程化SQL编写的过程，经过**编译和优化**后存储在数据库服务器中，可被应用程序或其他存储过程反复调用。

**存储函数（Stored Function / User Defined Function）：** 与存储过程类似，但**必须定义返回值类型**，通过带参数的 `RETURN` 语句返回执行结果。

### 存储过程与函数的区别

| 对比维度 | 存储过程 | 函数 |
|---------|---------|------|
| 使用场景 | 复杂业务逻辑、数据库运维管理 | 计算和数据查询任务 |
| 返回值 | 无返回类型，通过输出参数返回结果；可以没有 RETURN 语句 | 有返回类型和返回值，必须有带参数的 RETURN 语句 |
| 执行方式 | 只能被直接调用（`CALL/PERFORM`） | 可以出现在SQL语句和表达式中（`SELECT 函数名(...)`） |

### 命名块 vs 匿名块

| 类型 | 特点 |
|------|------|
| **命名块**（过程、函数） | 编译后保存在数据库中，可被反复调用，运行速度快 |
| **匿名块** | 每次执行都重新编译，不能存储到数据库，不能在其他块中调用 |

### 使用存储过程/函数的优点

1. **运行效率高**：已经过编译和优化，调用时无需重新进行语法分析和查询优化
2. **降低网络通信开销**：客户端只需提交过程名和参数值，减少了与数据库服务器之间的数据传输量
3. **便于集中管理和维护**：由数据库管理系统统一管理，易于维护和更新

### 4.1 存储过程的用户接口

#### 创建存储过程

```sql
CREATE [OR REPLACE] PROCEDURE 过程名([参数列表])
AS <过程化SQL块>;
```

**参数类型：**
- `参数名 IN 数据类型`：输入参数（默认）
- `参数名 OUT 数据类型`：输出参数，用于存放执行结果
- `参数名 IN OUT 数据类型`：输入/输出参数

**例8.8：转账存储过程**
```sql
CREATE OR REPLACE PROCEDURE TRANSFER
    (inAccount INT, outAccount INT, amount FLOAT)
AS
DECLARE
    totalDepositOut FLOAT;
    totalDepositIn  FLOAT;
    inAccountnum    INT;
BEGIN
    -- 检查转出账户及余额
    SELECT Total INTO totalDepositOut
    FROM Account WHERE accountnum = outAccount;

    IF totalDepositOut IS NULL THEN   -- 账户不存在
        ROLLBACK; RETURN;
    END IF;

    IF totalDepositOut < amount THEN  -- 余额不足
        ROLLBACK; RETURN;
    END IF;

    -- 检查转入账户
    SELECT Accountnum INTO inAccountnum
    FROM Account WHERE accountnum = inAccount;

    IF inAccount IS NULL THEN         -- 转入账户不存在
        ROLLBACK; RETURN;
    END IF;

    -- 执行转账
    UPDATE Account SET total = total - amount WHERE accountnum = outAccount;
    UPDATE Account SET total = total + amount WHERE accountnum = inAccount;
    COMMIT;
END;
```

#### 执行存储过程

```sql
CALL/PERFORM PROCEDURE 过程名([参数1, 参数2, ...]);
```

**例8.9：**
```sql
CALL PROCEDURE TRANSFER(01003813828, 01003815868, 10000);
```

#### 修改与删除存储过程

```sql
-- 重命名
ALTER PROCEDURE 过程名1 RENAME TO 过程名2;

-- 重新编译
ALTER PROCEDURE 过程名 COMPILE;

-- 删除
DROP PROCEDURE 过程名;
```

### 4.2 存储函数

#### 创建函数（PL/SQL）

```sql
CREATE [OR REPLACE] FUNCTION function_name
    [(parameter1 [{IN|OUT|IN OUT}] datatype [{:=|DEFAULT} expression] ...)]
RETURN returntype
{IS|AS}
    [declarations]
BEGIN
    code
    [EXCEPTION
        exception_handlers]
END;
```

**函数示例：计算员工总收入**
```sql
CREATE OR REPLACE FUNCTION totalsal(v_empno IN emp.empno%TYPE)
RETURN NUMBER
IS
    totalsal1 NUMBER;
BEGIN
    SELECT sal + comm INTO totalsal1
    FROM emp
    WHERE empno = v_empno;
    RETURN totalsal1;
END;

-- 在SQL语句中调用函数
SELECT empno, totalsal(empno) FROM emp WHERE totalsal(empno) > 300;
```

### 4.3 过程化SQL中的游标

过程化SQL中的游标使用方式与嵌入式SQL基本相同，增加了**带参数游标**的支持。

**例8.11：带参数的游标**
```sql
CREATE OR REPLACE PROCEDURE proc_cursor() AS
DECLARE
    cno   CHAR(3);
    cname CHAR(8);
    CURSOR mycursor(leaderno CHAR(3)) FOR   -- 带参数的游标
        SELECT lno, lname FROM leader WHERE lno = leaderno;
BEGIN
    OPEN mycursor('L01');                   -- 用参数L01打开游标
    FETCH mycursor INTO cno, cname;
    INSERT INTO temp(lno, lname) VALUES(cno, cname);
    CLOSE mycursor;

    OPEN mycursor('L02');                   -- 用新参数L02重新打开
    FETCH mycursor INTO cno, cname;
    INSERT INTO temp(lno, lname) VALUES(cno, cname);
    CLOSE mycursor;
END;
```

### 4.4 用过程化SQL创建触发器

触发器（Trigger）是数据库中的一种特殊对象，当指定的数据库事件发生时自动执行，不能被显式调用。

**触发器类型：**
- `BEFORE`：在触发事件执行之前触发
- `AFTER`：在触发事件执行之后触发
- 行级触发器（`FOR EACH ROW`）：对每一行数据变化分别触发
- 语句级触发器：对每条SQL语句触发一次

**例：AFTER行级触发器（例5.21）**
```sql
CREATE TRIGGER SC_T
AFTER UPDATE OF Grade ON SC
REFERENCING
    OLD ROW AS OldTuple,
    NEW ROW AS NewTuple
FOR EACH ROW
WHEN (NewTuple.Grade >= 1.1 * OldTuple.Grade)
    INSERT INTO SC_U(Sno, Cno, OldGrade, NewGrade)
    VALUES(OldTuple.Sno, OldTuple.Cno, OldTuple.Grade, NewTuple.Grade);
```

**例：BEFORE行级触发器（例5.23）**
```sql
CREATE TRIGGER Insert_Or_Update_Sal
BEFORE INSERT OR UPDATE ON Teacher
REFERENCING NEW ROW AS newTuple
FOR EACH ROW
BEGIN
    IF (newTuple.Job = '教授') AND (newTuple.Sal < 4000) THEN
        newTuple.Sal := 4000;
    END IF;
END;
```

---

## 5. 8.4 ODBC编程

### 基本概念

**ODBC（Open Database Connectivity，开放式数据库连接）** 是数据库服务器的一个标准协议，向应用程序提供**通用的应用程序访问接口（API）**。

- 应用程序开发人员无需知道后台数据库平台类型，即可用标准SQL语言访问数据库
- ODBC通过**ODBC驱动程序管理器**将用户调用的SQL语句转换成特定数据库的访问函数
- 不同数据库提供不同的ODBC驱动程序实现
- 客户端需配置**数据源名称（DSN, Data Source Name）**

### ODBC体系架构

```
应用程序
    ↓
ODBC驱动程序管理器
    ↓
┌──────────┬──────────┬──────────┐
ODBC驱动1  ODBC驱动2  ODBC驱动n
    ↓           ↓           ↓
RDBMS1      RDBMS2      RDBMSn
```

### 使用ODBC的程序流程

```
SQLAllocEnv  → 分配SQL环境句柄
    ↓
SQLAllocConnect → 分配数据库连接句柄
    ↓
SQLConnect   → 创建与数据库的连接
    ↓
SQLAllocStmt → 分配SQL语句句柄
    ↓
SQLPrepare / SQLExecDirect → 准备/直接执行SQL语句
    ↓
SQLExecute / SQLFetch / SQLGet → 执行语句，获取结果
    ↓（循环获取多行数据）
SQLFreeStmt  → 释放语句句柄
    ↓
SQLDisConnect → 断开与数据库的连接
    ↓
SQLFreeConnect → 释放连接句柄
    ↓
SQLFreeEnv  → 释放环境句柄
```

### Web数据库访问接口体系

| 接口 | 全称 | 特点 |
|------|------|------|
| **ODBC** | Open Database Connectivity | 基于SQL的标准化数据库访问API，统一了各厂商关系数据库接口 |
| **DAO** | Database Access Object | 第一个面向对象的数据库访问接口，可访问本地和远程数据库 |
| **RDO** | Remote Database Object | 封装ODBC API的对象层，性能高于DAO |
| **OLE DB** | Object Linking and Embedding DataBase | 微软基于COM的统一数据访问技术标准（支持关系及非关系数据源） |
| **ADO** | ActiveX Data Object | 基于OLE DB的高级接口，适用于Web应用 |
| **JDBC** | Java Database Connectivity | Java平台的数据库访问标准 |

---

## 6. 8.6 JDBC编程（简介）

**JDBC（Java Database Connectivity）** 是一种可以执行SQL语句的Java API，提供了Java程序访问数据库的标准接口。

**JDBC驱动实现方式：**
- JDBC-ODBC桥：通过ODBC驱动访问数据库
- Java + 本地驱动：部分用Java实现，部分调用本地库
- 专用协议纯Java驱动：完全用Java实现，性能最好

**Python数据库访问（Python DB-API规范）：**
```
开始
  ↓
创建 Connection（连接对象）
  ↓
获取 Cursor（游标对象）
  ↓
命令执行 → 数据获取 → 数据处理
  ↓
关闭 Cursor
  ↓
关闭 Connection
  ↓
结束
```

---

## 7. 复习思考题要点

1. **嵌入式SQL程序的结构**：声明段 → 异常处理定义 → 连接数据库 → 应用主体 → 断开连接

2. **主变量**：在ESQL中可以使用的主语言程序变量，用于在SQL语句与主语言之间传递数据；在SQL语句中用 `:` 前缀标识。**指示变量**：整型变量，用于指示相关主变量是否为NULL（-1表示NULL，0表示正常值，>0表示被截断）。

3. **ESQL与主语言的通信方式**：① SQLCA（SQL通信区，传递执行状态）；② 主变量（传递参数和结果数据）；③ 游标（交换多条结果元组）

4. **游标（Cursor）**：系统为用户开设的数据缓冲区，用于存放SQL查询结果，解决SQL面向集合与主语言面向记录的矛盾。使用流程：DECLARE（声明）→ OPEN（打开）→ FETCH（逐行取记录）→ CLOSE（关闭）

5. **ESQL执行异常**：`SQLERROR`（严重错误）、`NOT FOUND`（未找到数据）、`SQLWARNING`（警告）

---

> 📝 **本章核心概念速查：**
> - **ESQL** = 宿主语言 + EXEC SQL 前缀的SQL语句 + 预编译处理
> - **主变量** = 主语言变量，在SQL中用 `:` 前缀区分
> - **SQLCA** = SQL执行状态反馈结构体（含SQLCODE）
> - **游标** = 结果集缓冲区，实现"集合→逐条"的数据交换
> - **动态SQL** = 运行时生成的SQL（EXECUTE IMMEDIATE / PREPARE + EXECUTE）
> - **PL/SQL块** = DECLARE + BEGIN + EXCEPTION + END
> - **存储过程** = 命名的、预编译的过程化SQL块，无返回值
> - **存储函数** = 命名的、预编译的过程化SQL块，有返回值，可在SQL表达式中使用
> - **ODBC** = 面向多数据库的通用访问API，通过驱动程序管理器屏蔽数据库差异