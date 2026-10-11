# SQL 数据查询

---

## 一、SQL 数据查询概述

### 1.1 数据查询的数学基础

SQL 语言的数据查询功能以**关系代数**为数学基础，常见的关系数据查询包括：

| 关系代数操作 | 说明 |
|---|---|
| 元组**选择**与属性**投影** | 在单个关系上进行 |
| **笛卡儿积**（Cartesian Product） | 两个关系的无条件合并 |
| **θ-连接**（Theta Join） | 带条件的两表连接 |
| **自然连接**（Natural Join） | 基于同名属性的等值连接，消除重复列 |
| **并、交、差** | 两个关系的集合运算 |
| **除**（Division） | 用于"至少……全部……"类查询 |

在交互式 SQL 中还扩展了以下查询功能：**计算**（广义投影）、**统计查询**与**分组统计查询**、**结果排序**。

---

### 1.2 映像语句（SELECT 语句）的完整语法

```sql
SELECT [ALL | DISTINCT] <目标列表达式> [, <目标列表达式>] …
FROM <表名或视图名> [, <表名或视图名>] … | (SELECT 语句) [AS] <别名>
    [ WHERE <条件表达式> ]
    [ GROUP BY <列名1> [ HAVING <条件表达式> ] ]
    [ ORDER BY <列名2> [ ASC | DESC ] ];
```

各子句功能说明：

| 子句 | 作用 |
|---|---|
| `SELECT` | **目标子句**：定义结果表的投影列（目标属性） |
| `FROM` | **范围子句**：指定查询对象（基本表、视图或子查询） |
| `WHERE` | **条件子句**：指定元组选择条件与表间连接条件 |
| `GROUP BY` | **分组子句**：按指定列对结果元组分组 |
| `HAVING` | **分组选择子句**：对分组结果进行条件过滤 |
| `ORDER BY` | **排序子句**：对最终结果按指定列升序/降序排序 |

---

### 1.3 SELECT 语句的执行顺序

执行顺序**与书写顺序不同**，实际处理步骤如下：

1. **FROM**：合并 FROM 子句中的所有表（笛卡儿积）；
2. **WHERE**：按条件对合并后的元组进行选择，过滤不满足条件的元组；
3. **GROUP BY**：对保留下来的元组按指定列分组；
4. **HAVING**：对分组后的每个"组"进行条件过滤，丢弃不满足条件的组；
5. **SELECT**：对每个组进行统计计算，生成结果元组（一个组产生一条结果）；
6. **ORDER BY**：对查询结果进行排序输出。

---

## 二、SELECT 子句与 FROM 子句详解

### 2.1 SELECT 子句（目标子句）

```sql
SELECT [DISTINCT] column-name-list | expressions | *
```

**目标子句的构造方式：**

1. **简单属性投影**：直接写列名，或通过 `表名.列名` 的方式指定来自哪张表的列；
2. **表达式计算（广义投影）**：对常量、表达式或内置函数的计算结果进行投影；
3. **通配符 `*`**：代替 FROM 子句中表的所有列（按建表时的列定义顺序显示）；
4. **结果列重命名**：通过 `<列表达式> AS <列别名>` 的方式为结果列指定别名（`AS` 可省略）；
5. **去重谓词 `DISTINCT`**：消除结果表中的重复元组（缺省为 `ALL`，保留所有行）。

??? warning 注意
    `DISTINCT`是去重行，不能单独对某一列操作！

**示例：**

```sql
-- 查询指定列
SELECT Sname, Sno, Sdept FROM Student;

-- 查询全部列
SELECT * FROM Student;

-- 表达式计算 + 内置函数 + 常量投影
SELECT Sname, 'Year of Birth:', 2014 - Sage, LOWER(Sdept)
FROM Student;

-- 结果列重命名
SELECT Sname NAME, 'Year of Birth:' BIRTH, 2014-Sage BIRTHDAY, LOWER(Sdept) DEPARTMENT
FROM Student;

-- 日期函数示例
SELECT ordno, year(orddate), month(orddate), day(orddate) FROM orders;
SELECT ordno, orddate, datediff(curdate(), orddate) FROM orders;
```

---

### 2.2 FROM 子句（范围子句）

```sql
FROM tablename { , tablename ... }
```

**要点：**

- 指定本次查询可访问的表（基本表、视图或派生子查询）；
- 可在 FROM 子句中为表定义**别名（alias）**：`<表名> <别名>`；
  - 若定义了别名，则后续语句**必须通过别名**访问该表；
- FROM 子句中的表（或别名）**不能重名**；SELECT 子句中的结果列**不能重名**；
- 若 FROM 子句中的多张表存在**同名列**，必须通过 `表名.列名` 明确指定访问哪张表的列。

**别名的三大作用：**

1. 实现表的**自身连接**（一个表与其自身进行连接）；
2. **简化** SQL 命令的书写；
3. 提高 SQL 命令的**可读性**。

---

### 2.3 WHERE 子句（条件子句）

WHERE 子句是映像语句中的**可选成分**，用于定义：

- **单表内的元组选择条件**（σ 运算）；
- **表与表之间的连接条件**（θ-连接）。

> **注意**：FROM 子句中列出多表时，系统默认对它们进行**笛卡儿积**合并；如需执行 θ-连接或自然连接，必须在 WHERE 子句中**显式给出连接条件**。

---

## 三、单表查询

### 3.1 选择表中的若干元组

#### ① 比较运算

谓词：`=`、`>`、`<`、`>=`、`<=`、`!=`（`<>`、`!>`、`!<`）

```sql
-- 查询计算机系学生
SELECT Sname FROM Student WHERE Sdept = 'CS';

-- 查询年龄小于20岁的学生
SELECT Sname, Sage FROM Student WHERE Sage < 20;

-- 查询有不及格记录的学生（去重）
SELECT DISTINCT Sno FROM SC WHERE Grade < 60;
```

#### ② 范围查询：BETWEEN … AND …

谓词：`BETWEEN … AND …` 或 `NOT BETWEEN … AND …`（两端闭区间，即包含边界值）

```sql
-- 年龄在20~23岁之间（含）
SELECT Sname, Sdept, Sage FROM Student WHERE Sage BETWEEN 20 AND 23;

-- 年龄不在20~23岁之间
SELECT Sname, Sdept, Sage FROM Student WHERE Sage NOT BETWEEN 20 AND 23;
```

#### ③ 集合成员查询：IN

谓词：`IN <值表>` 或 `NOT IN <值表>`

```sql
-- 查询CS、MA、IS系的学生
SELECT Sname, Ssex FROM Student WHERE Sdept IN ('CS', 'MA', 'IS');

-- 查询不属于上述三系的学生
SELECT Sname, Ssex FROM Student WHERE Sdept NOT IN ('IS', 'MA', 'CS');
```

#### ④ 字符匹配（模糊查询）：LIKE

谓词：`[ NOT ] LIKE '<匹配串>' [ ESCAPE '<换码字符>' ]`

**通配符说明：**

| 通配符 | 含义 |
|---|---|
| `%` | 任意长度（含0）的字符串 |
| `_` | 任意**单个**字符 |

> **注意**：在 MySQL 中，系统内置的默认转义指示符为 `\`，用 `ESCAPE '\'` 声明转义字符后，`\_` 和 `\%` 就代表普通字符 `_` 和 `%`。

**示例：**

```sql
-- 固定字符串（等价于 =）
SELECT * FROM Student WHERE Sno LIKE '201215121';

-- 姓刘的学生
SELECT Sname, Sno, Ssex FROM Student WHERE Sname LIKE '刘%';

-- 姓"欧阳"且全名三个汉字（一个汉字占两字节，用两个 _ 匹配）
SELECT Sname FROM Student WHERE Sname LIKE '欧阳__';

-- 第2个字为"阳"的学生
SELECT Sname, Sno FROM Student WHERE Sname LIKE '__阳%';

-- 不姓刘的学生
SELECT Sname, Sno, Ssex FROM Student WHERE Sname NOT LIKE '刘%';

-- 转义：查 DB_Design 课程（_ 为普通字符）
SELECT Cno, Ccredit FROM Course WHERE Cname LIKE 'DB\_Design' ESCAPE '\';

-- 转义：以"DB_"开头，倒数第3个字符为 i
SELECT * FROM Course WHERE Cname LIKE 'DB\_%i_ _' ESCAPE '\';
```

#### ⑤ 空值查询：IS NULL / IS NOT NULL

谓词：`IS NULL` 或 `IS NOT NULL`

> **注意**：SQL 标准中，`IS` **不能用 `=` 代替**。商用系统中可用 `= NULL` 代替 `IS NULL`，但 **不能用 `!= NULL` 代替 `IS NOT NULL`**。

```sql
-- 查询缺少成绩的选课记录
SELECT Sno, Cno FROM SC WHERE Grade IS NULL;

-- 查询有成绩的选课记录
SELECT Sno, Cno FROM SC WHERE Grade IS NOT NULL;
```

#### ⑥ 多重条件查询：AND / OR / NOT

- `AND` 优先级**高于** `OR`；
- 可用括号改变运算顺序。

```sql
-- CS系且年龄小于20
SELECT Sname FROM Student WHERE Sdept = 'CS' AND Sage < 20;

-- IN 谓词等价于 OR 连接
SELECT Sname, Ssex FROM Student WHERE Sdept = 'CS' OR Sdept = 'MA' OR Sdept = 'IS';
```

---

### 3.2 消除结果中的重复元组：DISTINCT

```sql
-- 查询选修了课程的学生学号（去重）
SELECT DISTINCT Sno FROM SC;

-- 不加 DISTINCT 则默认 ALL，保留重复行
SELECT Sno FROM SC;
```

---

### 3.3 查询结果排序：ORDER BY

```sql
ORDER BY <列名> [ASC | DESC] { , <列名> [ASC | DESC] ... }
```

- `ASC`：升序（**默认**）；`DESC`：降序；
- 可按**一个或多个列**排序；
- 对于**空值（NULL）**，排序次序由具体 DBMS 实现决定。

```sql
-- 按成绩降序
SELECT Sno, Grade FROM SC WHERE Cno = '3' ORDER BY Grade DESC;

-- 先按系升序，同系内按年龄降序
SELECT * FROM Student ORDER BY Sdept, Sage DESC;
```

---

### 3.4 聚集函数（统计函数）

| 函数 | 功能 |
|---|---|
| `COUNT(*)` | 统计**元组总数**（不忽略 NULL） |
| `COUNT([DISTINCT|ALL] <列名>)` | 统计某列中**非空值**的个数 |
| `SUM([DISTINCT|ALL] <列名>)` | 计算一列值的**总和**（数值型） |
| `AVG([DISTINCT|ALL] <列名>)` | 计算一列值的**平均值**（数值型） |
| `MAX([DISTINCT|ALL] <列名>)` | 求一列中的**最大值** |
| `MIN([DISTINCT|ALL] <列名>)` | 求一列中的**最小值** |

**关于 NULL 的处理规则：**

- 除 `COUNT(*)` 外，所有聚集函数在统计时均**忽略 NULL 值**；
- 在**空集**上进行统计时： `COUNT()` 返回 **0**；其他聚集函数均返回 **NULL**。

**三种统计查询类型：**

| 类型 | 说明 |
|---|---|
| **统计查询** | 无 GROUP BY，对整个查询结果统计，返回单条统计结果 |
| **分组统计查询** | 有 GROUP BY，每"组"返回一条统计结果 |
| **分组-选择统计查询** | 有 GROUP BY + HAVING，对满足条件的组进行统计 |

> **限制**：在统计查询中，SELECT 子句**只允许出现聚集函数**，**不允许对普通属性投影**（除非该属性是分组属性）。

```sql
-- 查询学生总人数
SELECT COUNT(*) FROM Student;

-- 查询选修了课程的学生人数（去重）
SELECT COUNT(DISTINCT Sno) FROM SC;

-- 查询1号课程的平均成绩
SELECT AVG(Grade) FROM SC WHERE Cno = '1';

-- 同时执行多种统计计算
SELECT SUM(Ccredit), COUNT(*), AVG(grade), MAX(grade), MIN(grade)
FROM SC, Course C
WHERE SC.Sno = '201215012' AND SC.Cno = C.Cno AND SC.grade >= 60;
```

---

### 3.5 分组统计查询：GROUP BY 与 HAVING

#### GROUP BY 子句

```sql
GROUP BY colname { , colname ... }
```

- 按指定列的值对元组分组，取值相等的元组归为同一"组"；
- 聚集函数将分别作用于**每个组**；
- **SELECT 子句中的目标属性**必须满足：

    1. **必须包含所有分组属性**；
    2. 可以有聚集函数；
    3. **除分组属性和聚集函数外，不能出现其他属性**。

??? warning 注意
    为什么"除分组属性和聚集函数外，不能出现其他属性"？因为`GRUOP BY`输出的结果是每组一行，如果出现了其他属性则同一组内该属性可能有多个不同取值，数据库无法确定该返回哪一个。

#### HAVING 子句

```sql
HAVING group_condition
```

- 作用于**分组后的组**（元组集合），而非单个元组；
- 只有满足 `group_condition` 的组才会保留用于生成最终结果；
- HAVING 子句中**可以使用聚集函数**。

#### WHERE 与 HAVING 的核心区别

| | WHERE 子句 | HAVING 子句 |
|---|---|---|
| **作用对象** | 基本表或视图中的**单个元组** | 分组后的**元组集合（组）** |
| **能否使用聚集函数** | ❌ 不能 | ✅ 可以 |
| **执行时机** | 分组**之前**过滤 | 分组**之后**过滤 |

```sql
-- 查询各课程及选课人数
SELECT Cno, COUNT(Sno) FROM SC GROUP BY Cno;

-- 查询选修了3门以上课程的学生学号
SELECT Sno FROM SC GROUP BY Sno HAVING COUNT(*) > 3;

-- 查询平均成绩≥90分的学生学号和平均成绩（HAVING 正确用法）
SELECT Sno, AVG(Grade)
FROM SC
GROUP BY Sno
HAVING AVG(Grade) >= 90;
-- 错误写法（WHERE 中不能用聚集函数）：WHERE AVG(Grade) >= 90
```

---

## 四、连接查询

### 4.1 连接查询概述

**连接查询**：同时涉及两个或两个以上的表的查询。

**连接条件（连接谓词）的一般格式：**
```sql
[<表名1>.]<列名1> <比较运算符> [<表名2>.]<列名2>
[<表名1>.]<列名1> BETWEEN [<表名2>.]<列名2> AND [<表名2>.]<列名3>
```

> **连接字段**（连接谓词中的列）：各连接字段类型必须**可比**，但**名字不必相同**。

---

### 4.2 等值连接与自然连接

- **等值连接**：连接运算符为 `=`，结果中保留两表的所有列（包含重复的连接列）；
- **自然连接**：在等值连接基础上消除重复列，使用`JOIN <列表> ON <condition>`。

```sql
-- 等值连接：查询每个学生及其选修课程的情况
SELECT Student.*, SC.*
FROM Student, SC
WHERE Student.Sno = SC.Sno;

-- 选择+连接（复合 WHERE 条件）
SELECT Student.Sno, Sname
FROM Student, SC
WHERE Student.Sno = SC.Sno AND SC.Cno = '2' AND SC.Grade > 90;
```

---

### 4.3 连接操作的三种执行算法

| 算法 | 说明 |
|---|---|
| **嵌套循环法（NESTED-LOOP）** | 对表1的每个元组，逐一扫描表2查找满足连接条件的元组 |
| **索引连接（INDEX-JOIN）** | 在表2的连接字段上建有索引时，利用索引加速连接 |
| **排序合并法（SORT-MERGE）** | 先按连接字段对两表排序，再顺序扫描合并；常用于等值连接 |

---

### 4.4 自身连接（自连接）

一个表与其**自身**进行连接。

- 需要为同一张表分别取**不同的别名**以示区别；
- 所有列名必须通过 `<别名>.<列名>` 的方式访问。

```sql
-- 查询每门课的间接先修课（先修课的先修课）
SELECT FIRST.Cno, SECOND.Cpno
FROM Course FIRST, Course SECOND
WHERE FIRST.Cpno = SECOND.Cno;
```

---

### 4.5 外连接

**外连接**与普通连接的区别：

- 普通连接：只输出**满足连接条件**的元组；
- 外连接：以指定表为连接**主体**，将主体表中**不满足连接条件的元组也一并输出**（对应无匹配的列值填 `NULL`）。

| 类型 | 说明 |
|---|---|
| **左外连接（LEFT OUTER JOIN）** | 列出**左边表**中的所有元组 |
| **右外连接（RIGHT OUTER JOIN）** | 列出**右边表**中的所有元组 |

```sql
-- 左外连接：保留所有学生，即使没有选课记录（Cno、Grade 填 NULL）
SELECT Student.Sno, Sname, Ssex, Sage, Sdept, Cno, Grade
FROM Student LEFT OUTER JOIN SC ON (Student.Sno = SC.Sno);
```

---

### 4.6 多表连接

```sql
-- 三表连接：查询每个学生的学号、姓名、选修课程名及成绩
SELECT Student.Sno, Sname, Cname, Grade
FROM Student, SC, Course
WHERE Student.Sno = SC.Sno AND SC.Cno = Course.Cno;
```

> **注意**：多表连接的嵌套顺序由 **DBMS 自主决定**，与 FROM 子句中的书写顺序及 WHERE 子句中条件的定义顺序**均无关**。

---

## 五、嵌套查询（子查询）

### 5.1 嵌套查询概述

- **查询块**：一个 `SELECT-FROM-WHERE` 语句；
- **嵌套查询**：将一个查询块嵌套在另一个查询块的 `WHERE`、`FROM`、`HAVING`（或 `SELECT`）子句中。有两种类型：

    1. **外层查询**（父查询）：包含子查询的查询块；
    2. **内层查询**（子查询）：被嵌套的查询块；

- SQL 语言允许**多层嵌套**，但也有**限制**：子查询中**不能使用 `ORDER BY` 子句**。

---

### 5.2 不相关子查询 vs. 相关子查询

| | 不相关子查询（独立子查询） | 相关子查询（关联子查询） |
|---|---|---|
| **子查询条件** | 不依赖于父查询 | 依赖于父查询中的当前元组 |
| **执行方向** | 由**里向外**，逐层处理 | 由**外向里**，嵌套循环 |
| **执行次数** | 子查询**执行一次**，结果用于父查询条件 | 父查询每取一个元组，子查询就执行**一次** |

---

### 5.3 带 IN 谓词的子查询

```sql
expr [ NOT ] IN ( subquery )
```

```sql
-- 不相关子查询：查询与"刘晨"在同一系的学生
SELECT Sno, Sname, Sdept
FROM Student
WHERE Sdept IN (
    SELECT Sdept FROM Student WHERE Sname = '刘晨');

-- 多层嵌套不相关子查询：查询选修了"信息系统"课程的学生学号和姓名
SELECT Sno, Sname
FROM Student
WHERE Sno IN (
    SELECT Sno FROM SC
    WHERE Cno IN (
        SELECT Cno FROM Course WHERE Cname = '信息系统'));
```

> **提示**：带 `IN + 子查询` 的嵌套查询，通常可以用**表连接查询**替代，且连接查询的执行效率往往更高。

---

### 5.4 带比较运算符的子查询

当确知子查询**只返回单值**时，可用 `>`、`<`、`=`、`>=`、`<=`、`!=` 等比较运算符代替 `IN`。

```sql
-- 子查询返回单值时可用 = 代替 IN（但需确保子查询唯一返回单值）
SELECT Sno, Sname, Sdept
FROM Student
WHERE Sdept = (SELECT Sdept FROM Student WHERE Sname = '刘晨');

-- 相关子查询：查询超过本人平均成绩的选课记录
SELECT Sno, Cno
FROM SC x
WHERE Grade >= (SELECT AVG(Grade) FROM SC y WHERE y.Sno = x.Sno);
```

> **注意**：子查询返回多值时使用 `=` 会报错；建议优先使用 `IN` 或带量词的比较谓词。

---

### 5.5 带 ANY / ALL 谓词的子查询

`SOME` 与 `ANY` 是同义词。

**语义对照表：**

| 谓词 | 语义 |
|---|---|
| `> ANY` | 大于子查询结果中的**某个**值（即大于最小值） |
| `> ALL` | 大于子查询结果中的**所有**值（即大于最大值） |
| `< ANY` | 小于子查询结果中的**某个**值（即小于最大值） |
| `< ALL` | 小于子查询结果中的**所有**值（即小于最小值） |
| `= ANY` | 等于子查询结果中的**某个**值（等价于 `IN`） |
| `!= ALL` / `<> ALL` | 不等于子查询结果中的**任何**值（等价于 `NOT IN`） |

**ANY/ALL 与聚集函数、IN 的等价转换（表3.7）：**

|  | `=` | `<>` / `!=` | `<` | `<=` | `>` | `>=` |
|---|---|---|---|---|---|---|
| **ANY** | `IN` | — | `< MAX` | `<= MAX` | `> MIN` | `>= MIN` |
| **ALL** | — | `NOT IN` | `< MIN` | `<= MIN` | `> MAX` | `>= MAX` |

```sql
-- 查询非CS系中比CS系任意一个学生年龄小的学生（ANY）
SELECT Sname, Sage
FROM Student
WHERE Sage < ANY (SELECT Sage FROM Student WHERE Sdept = 'CS')
  AND Sdept <> 'CS';
-- 等价写法（用聚集函数）：
WHERE Sage < (SELECT MAX(Sage) FROM Student WHERE Sdept = 'CS')

-- 查询非CS系中比CS系所有学生年龄都小的学生（ALL）
SELECT Sname, Sage
FROM Student
WHERE Sage < ALL (SELECT Sage FROM Student WHERE Sdept = 'CS')
  AND Sdept <> 'CS';
-- 等价写法（用聚集函数）：
WHERE Sage < (SELECT MIN(Sage) FROM Student WHERE Sdept = 'CS')
```

---

### 5.6 带 EXISTS 谓词的子查询

```sql
[ NOT ] EXISTS ( subquery )
```

**语义：**

- `EXISTS`：若子查询结果**非空**，WHERE 返回**真**；否则返回假；
- `NOT EXISTS`：若子查询结果**为空**，WHERE 返回**真**；否则返回假；
- 带 EXISTS 的子查询**不返回任何数据**，只返回逻辑真/假值；
- 目标列表达式通常写为 `*`（列名无实际意义）。

```sql
-- EXISTS：查询所有选修了1号课程的学生姓名
SELECT Sname
FROM Student S
WHERE EXISTS (
    SELECT * FROM SC WHERE SC.Sno = S.Sno AND Cno = '1');

-- NOT EXISTS：查询没有选修1号课程的学生姓名（必须用子查询，无法用连接替代）
SELECT Sname
FROM Student S
WHERE NOT EXISTS (
    SELECT * FROM SC WHERE SC.Sno = S.Sno AND Cno = '1');
```

---

### 5.7 EXISTS 与关系代数的对应关系

| 关系代数运算 | SQL 实现谓词 |
|---|---|
| **自然连接 / 连接** | `IN` 或 `EXISTS` |
| **差运算** | `NOT IN` 或 `NOT EXISTS` |

**替换规则：**

- 所有带 `IN`、比较运算符、`ANY`、`ALL` 谓词的子查询，都能用带 `EXISTS` 的子查询**等价替换**；
- 部分带 `EXISTS` 或 `NOT EXISTS` 的子查询**不能被其他形式等价替换**。

---

### 5.8 用 EXISTS 实现全称量词（除法运算）

SQL 语言**没有全称量词** `∀`，可利用逻辑等价将其转换为存在量词：

$$(\forall x) P \equiv \neg\exists x (\neg P)$$

**经典例题：查询至少选修了学号为201215122的学生所选修的全部课程的学生学号**

查询语义：不存在这样的课程`y`，学生201215122选修了`y`，而学生`x`没有选。

```sql
SELECT DISTINCT Sno
FROM SC SCX
WHERE NOT EXISTS (
    SELECT *
    FROM SC SCY
    WHERE SCY.Sno = '201215122' AND
          NOT EXISTS (
              SELECT *
              FROM SC SCZ
              WHERE SCZ.Sno = SCX.Sno AND SCZ.Cno = SCY.Cno));
```

等价的第二种写法（最内层用 NOT IN）：

```sql
SELECT DISTINCT Sno
FROM SC SCX
WHERE NOT EXISTS (
    SELECT *
    FROM SC SCY
    WHERE SCY.Sno = '201215122' AND
          SCY.Cno NOT IN (
              SELECT SCZ.Cno FROM SC SCZ WHERE SCZ.Sno = SCX.Sno));
```

**查询选修了全部课程的学生姓名：**

```sql
SELECT Sname
FROM Student
WHERE NOT EXISTS (
    SELECT * 
    FROM Course
    WHERE NOT EXISTS (
        SELECT * FROM SC
        WHERE SC.Sno = Student.Sno AND SC.Cno = Course.Cno));
```

---

## 六、集合查询

### 6.1 参与集合操作的要求

- 参与集合操作的各子查询**结果列数必须相同**；
- 对应列的**数据类型也必须相同**。

### 6.2 三种集合操作

| 操作 | 关键字 | 说明 |
|---|---|---|
| **并** | `UNION` | 合并结果，**自动去除**重复元组 |
| **并（保留重复）** | `UNION ALL` | 合并结果，**保留**重复元组 |
| **交** | `INTERSECT` | 返回两个查询结果的**公共元组** |
| **差** | `EXCEPT` | 返回属于第一个结果但**不属于**第二个结果的元组 |

```sql
-- 并：CS系的学生 或 年龄不大于19岁的学生
SELECT * FROM Student WHERE Sdept = 'CS'
UNION
SELECT * FROM Student WHERE Sage <= 19;

-- 交：CS系且年龄不大于19岁的学生
SELECT * FROM Student WHERE Sdept = 'CS'
INTERSECT
SELECT * FROM Student WHERE Sage <= 19;
-- 等价写法：WHERE Sdept = 'CS' AND Sage <= 19

-- 差：CS系中年龄大于19岁的学生
SELECT * FROM Student WHERE Sdept = 'CS'
EXCEPT
SELECT * FROM Student WHERE Sage <= 19;
-- 等价写法：WHERE Sdept = 'CS' AND Sage > 19

-- 并：选修了课程1或课程2的学生
SELECT Sno FROM SC WHERE Cno = '1'
UNION
SELECT Sno FROM SC WHERE Cno = '2';

-- 交：既选修了课程1又选修了课程2的学生（等价写法）
SELECT Sno FROM SC WHERE Cno = '1'
INTERSECT
SELECT Sno FROM SC WHERE Cno = '2';
-- 等价写法：
SELECT Sno FROM SC WHERE Cno = '1' AND Sno IN (SELECT Sno FROM SC WHERE Cno = '2');
```

---

## 七、基于派生表的查询

### 7.1 派生表（Derived Table）

子查询不仅可出现在 WHERE 子句中，还可出现在 **FROM 子句**中。此时子查询生成的**临时结果集**称为**派生表（Derived Table）**，成为主查询的查询对象。

```sql
-- 使用派生表实现"超过本人平均成绩"的查询
SELECT Sno, Cno
FROM SC,
     (SELECT Sno, AVG(Grade) FROM SC GROUP BY Sno) AS Avg_sc(avg_sno, avg_grade)
WHERE SC.Sno = Avg_sc.avg_sno AND SC.Grade >= Avg_sc.avg_grade;
```

```sql
-- 使用派生表查询所有选修了1号课程的学生姓名
SELECT Sname
FROM Student,
     (SELECT Sno FROM SC WHERE Cno = '1') AS SC1
WHERE Student.Sno = SC1.Sno;
```

### 7.2 派生表的列名规则

- 若子查询的所有结果列**均有列名且不重名**，可**不必**为派生表显式指定列名，子查询 SELECT 子句的列名即为派生表的默认列名；
- 否则，需要通过 `AS <别名>(列名1, 列名2, ...)` 的形式**显式指定**派生表的列名。

---

## 八、关系代数与 SQL 语言的对应关系总结

| 关系代数操作 | SQL 实现方式 |
|---|---|
| 选择 σ | `WHERE` 子句 |
| 投影 π | `SELECT` 子句 |
| 笛卡儿积 × | `FROM` 多表（无 WHERE 连接条件） |
| θ-连接 | `FROM` 多表 + `WHERE` 连接条件 |
| 自然连接 ⋈ | `FROM` 多表 + `WHERE` 等值连接条件 + `SELECT` 去除重复列 |
| 并 ∪ | `UNION` / `UNION ALL` |
| 交 ∩ | `INTERSECT` |
| 差 − | `EXCEPT` / `NOT IN` / `NOT EXISTS` |
| 除 ÷ | 双重 `NOT EXISTS` 嵌套子查询 |
| 全称量词 ∀ | `NOT EXISTS(NOT ...)` 转换实现 |

---

## 九、重要知识点辨析与易错总结

1. **WHERE 与 HAVING 的区别**：WHERE 作用于基本表的单个元组（分组前过滤），HAVING 作用于分组后的组（分组后过滤）；WHERE 中不能使用聚集函数，HAVING 中可以。

2. **IN 与 EXISTS 的选择**：IN 适合子查询返回结果集较小的情况；EXISTS 本质上是相关子查询，适合外层表较小、子查询表较大的情况。

3. **NOT IN 与 NOT EXISTS 的陷阱**：当子查询结果集中含有 **NULL 值**时，`NOT IN` 可能无法返回任何结果（因为 `NULL != x` 的结果是 UNKNOWN，而非 FALSE）；`NOT EXISTS` 不受此影响，更为安全。

4. **DISTINCT 谓词的作用域**：`DISTINCT` 作用于整行结果元组，而非单个列；聚集函数中的 `DISTINCT` 用于在统计前去除重复值（如 `COUNT(DISTINCT Sno)`）。

5. **子查询不能含 ORDER BY**：ORDER BY 子句只能出现在最外层的查询中。

6. **FROM 子句中的笛卡儿积**：在 FROM 子句中列出多张表，系统默认对其进行笛卡儿积合并，如果不在 WHERE 子句中给出连接条件，将产生规模极大的中间结果，必须显式添加连接条件。

7. **自连接必须使用别名**：自身连接时同一张表必须分别起不同的别名，且所有列引用必须加别名前缀。

8. **GROUP BY 的目标属性约束**：SELECT 子句中的目标属性，除聚集函数外，只能包含 GROUP BY 子句中指定的**分组属性**，不能出现其他普通属性。

9. **外连接的语法**：外连接不使用 WHERE 子句的连接条件，而使用 `LEFT/RIGHT OUTER JOIN … ON (…)` 语法。

10. **空值（NULL）的特殊性**：NULL 不等于任何值（包括 NULL 本身）；`NULL = NULL` 的结果是 UNKNOWN，而非 TRUE；必须使用 `IS NULL` / `IS NOT NULL` 进行空值判断。