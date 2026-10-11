# SQL数据更新

## 一、数据更新

数据更新包括三类操作：**插入（INSERT）**、**修改（UPDATE）**、**删除（DELETE）**。

---

### 1.1 插入数据（INSERT）

#### 1.1.1 插入单个元组

**语句格式：**

```sql
INSERT
INTO <表名> [(<属性列1> [, <属性列2> …])]
VALUES (<常量1> [, <常量2>] …);
```

**INTO 子句说明：**

- 指定要插入数据的表名及属性列
- 属性列的顺序可以与表定义中的顺序不一致
- **若未指定属性列**：表示插入完整元组，属性列顺序须与表定义一致
- **若指定部分属性列**：未指定的属性列由 DBMS 自动赋空值（NULL）

**VALUES 子句说明：**

- 提供的值必须与 INTO 子句**匹配**：值的个数一致、值的类型兼容
- `NULL` 关键字可显式表示空值

**完整语法（标准 SQL）：**

```sql
INSERT
INTO tabname [( colname {, colname …} )]
VALUES ( expr | NULL {, expr | NULL …} ) | subquery;
```

**示例：**

```sql
-- 例3.69：插入完整学生元组（指定属性列）
INSERT INTO Student (Sno, Sname, Ssex, Sdept, Sage)
VALUES ('201215128', '陈冬', '男', 'IS', 18);

-- 例3.70：省略属性列，值顺序须与表定义一致
INSERT INTO Student
VALUES ('201215126', '张成民', '男', 18, 'CS');

-- 例3.71：部分属性列插入（Grade 自动赋 NULL）
INSERT INTO SC(Sno, Cno)
VALUES ('201215128', '1');

-- 等价写法（显式写 NULL）
INSERT INTO SC
VALUES ('201215128', '1', NULL);
```

> **补充说明：** 在执行 INSERT 时，DBMS 会检查实体完整性（主键不为空、不重复）和参照完整性（外键值合法），违约则拒绝插入。

---

#### 1.1.2 插入子查询结果（批量插入）

**语句格式：**

```sql
INSERT
INTO <表名> [(<属性列1> [, <属性列2> …])]
子查询;
```

**说明：**

- SELECT 子句的目标列必须与 INTO 子句中的属性列在**数量和类型**上匹配
- 可一次性将查询结果批量写入目标表
- 常用于构建汇总表、临时表等场景

**示例：**

```sql
-- 例3.72：先建表，再将每系学生平均年龄插入汇总表
CREATE TABLE Dept_age (
    Sdept   CHAR(15),     -- 系名
    Avg_age SMALLINT      -- 学生平均年龄
);

INSERT INTO Dept_age(Sdept, Avg_age)
SELECT Sdept, AVG(Sage)
FROM Student
GROUP BY Sdept;
```

---

### 1.2 修改数据（UPDATE）

**语句格式：**

```sql
UPDATE <表名>
SET <列名> = <表达式> [, <列名> = <表达式>] …
[WHERE <条件>];
```

**功能：**

- 修改指定表中**满足 WHERE 子句条件**的元组
- SET 子句用表达式的值替换对应属性列的旧值
- **若省略 WHERE 子句**：修改表中所有元组

**示例：**

```sql
-- 例3.73：修改单个元组
UPDATE Student
SET Sage = 22
WHERE Sno = '201215121';

-- 例3.74：修改所有元组（无 WHERE 子句）
UPDATE Student
SET Sage = Sage + 1;

-- 例3.75：带子查询的修改（将 CS 系学生成绩置零）
UPDATE SC
SET Grade = 0
WHERE Sno IN (
    SELECT Sno
    FROM Student
    WHERE Sdept = 'CS'
);
```

#### 修改操作与完整性约束

DBMS 在执行 UPDATE 时会自动检查以下完整性规则，违约则拒绝执行：

| 约束类型 | 说明 |
|---|---|
| **实体完整性** | 主码列不能被修改为空值或重复值 |
| **参照完整性** | 外键值须在被参照表中存在 |
| **NOT NULL 约束** | 被约束列不能被修改为 NULL |
| **UNIQUE 约束** | 被约束列的新值在表中须唯一 |
| **值域约束** | 值须在合法范围内 |

---

### 1.3 删除数据（DELETE）

**语句格式：**

```sql
DELETE
FROM <表名>
[WHERE <条件>];
```

**功能：**

- 删除指定表中**满足 WHERE 子句条件**的元组
- **若省略 WHERE 子句**：删除表中所有元组（表的结构定义仍保留在数据字典中）

> **注意：** `DELETE` 只删除数据行，不删除表结构；而 `DROP TABLE` 会连结构一起删除。`TRUNCATE TABLE`（非标准 SQL）也删除所有行但速度更快、不可回滚。

**示例：**

```sql
-- 例3.76：删除单个元组
DELETE FROM Student
WHERE Sno = '201215128';

-- 例3.77：删除所有元组
DELETE FROM SC;

-- 例3.78：带子查询的删除（删除 CS 系所有学生的选课记录）
DELETE FROM SC
WHERE Sno IN (
    SELECT Sno
    FROM Student
    WHERE Sdept = 'CS'
);
```

---

## 二、事务处理的基本概念

---

### 2.1 事务的定义

> **事务（Transaction）** 是用户定义的一个数据库操作序列，这些操作**要么全做，要么全不做**，是一个不可分割的工作单位。

- 在关系数据库中，一个事务可以由**一条或一组 SQL 语句**组成
- 事务是**恢复**和**并发控制**的基本单位

---

### 2.2 为什么引入事务

引入事务的目的是**确保数据库的数据完整性（Integrity of the Database）**。

**一致性状态（Consistent State）：** 若数据库中所有数据都满足完整性约束定义，则称数据库处于一致性状态。

**影响数据完整性的三个因素：**

| 因素 | 说明 |
|---|---|
| **Concurrency（并发）** | 多用户的并发访问可能导致数据相互干扰 |
| **Abort（放弃事务）** | 事务中途被放弃可能使数据处于不一致状态 |
| **Crash（系统故障）** | 硬件/软件故障可能导致部分操作结果丢失 |

在 DBMS 中引入事务处理功能，可以确保**在任何情况下，都能保证数据库中数据的正确性**。

---

### 2.3 事务的 ACID 特性

一个事务的运行必须满足以下四个特性：

#### ① 原子性（Atomicity）

- 事务是数据库的**逻辑工作单位**
- 事务中包括的诸操作**要么都做，要么都不做**
- 由 DBMS 的**恢复机制**（Undo/Redo）保证

#### ② 一致性（Consistency）

- 事务执行的结果必须使数据库从**一个一致性状态**变到**另一个一致性状态**
- **一致性状态**：数据库中只包含已成功提交的事务的执行结果
- **不一致状态**：系统故障导致部分修改已写入物理数据库，使数据库处于不正确状态

#### ③ 隔离性（Isolation）

- 一个事务的执行**不能被其他事务干扰**
- 一个事务内部的操作及使用的数据对其他并发事务是**隔离的**
- 并发执行的各个事务之间**不能互相干扰**
- 由 DBMS 的**并发控制机制**（锁机制、MVCC等）保证

#### ④ 持久性（Durability，也称永久性）

- 一个事务一旦**完成提交**，它对数据库中数据的改变就应该是**永久性的**
- 接下来的其他操作或故障不应该对其执行结果有任何影响
- 由 DBMS 的**日志（WAL）机制**保证

---

### 2.4 定义事务

**事务的启动：**

事务以**隐式方式**启动，由 DBMS 决定何时为用户启动新事务。具体有三种情形：

| 启动方式 | 说明 |
|---|---|
| **DDL 命令**（数据定义语言，如`CREATE` `ALTER` `DROP`） | 每条 DDL 命令单独作为一个事务执行，执行前自动提交当前 active 事务 |
| **自动提交模式（AUTOCOMMIT）** | 每条 DML 命令单独作为一个事务，DBMS 自动提交或回滚。在涉及多业务逻辑时，往往要关闭自动提交，手动管理多业务逻辑。 |
| **DML 命令** （数据操纵语言，如`UPDATE` `DELETE` `INSERT`）| DBMS 检查是否已有 active 事务：有则加入当前事务；无则自动启动新事务 |

**事务的结束：**

- 用户调用 `COMMIT` 或 `ROLLBACK` 命令**显式结束**当前事务
- DBMS 也可**强行终止**用户当前事务（如检测到死锁）

---

### 2.5 事务结束方式

#### COMMIT（提交）

- 事务**正常结束**，提交事务中所有操作（读 + 写）
- 被提交事务对数据库的所有更新结果被**写回磁盘**，确保持久化
- 提交可能失败（系统故障、完整性检查不满足），失败后可执行 ROLLBACK

#### ROLLBACK（回滚）

- 事务**异常终止**，撤销事务执行过程中对数据库所做的**全部修改**
- 将数据库回退到事务**开始时的状态**
- 支持**保存点（Savepoint）**：可回滚到事务中的某个中间点，而不必放弃整个事务

**保存点机制：**

```sql
SAVEPOINT sp1;                  -- 设置保存点
-- ... 若干操作 ...
ROLLBACK TO SAVEPOINT sp1;      -- 回滚到保存点（不结束事务）
ROLLBACK;                       -- 放弃整个事务
```

---

### 2.6 有关事务的 SQL 命令

#### 事务结束命令

```sql
COMMIT;     -- 提交事务
ROLLBACK;   -- 回滚事务（也可理解为事务放弃命令）
```

#### 事务设置命令

**① 设置自动提交**

```sql
SET AUTOCOMMIT ON;       -- 打开自动提交
SET AUTOCOMMIT OFF;      -- 关闭自动提交

-- MySQL 语法
SET AUTOCOMMIT = 1;      -- 打开
SET AUTOCOMMIT = 0;      -- 关闭
```

**② 设置事务类型**

```sql
SET TRANSACTION READONLY;    -- 只读型事务（只能执行读操作）
SET TRANSACTION READWRITE;   -- 读写型事务（默认）
```

**③ 设置隔离级别**

```sql
SET TRANSACTION ISOLATION LEVEL
    READUNCOMMITTED |   -- 未提交读
    READCOMMITTED   |   -- 提交读
    READREPEATABLE  |   -- 可重复读
    SERIALIZABLE;       -- 可序列化（最高级别）
```

#### 四种隔离级别详解

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 说明 |
|---|---|---|---|---|
| **READUNCOMMITTED**（未提交读） | 可能 | 可能 | 可能 | 不申请任何锁，可读到其他事务未提交的修改（脏读）；在未提交读隔离级别下，事务可以读未提交数据，但写操作仍需受到正常并发控制 |
| **READCOMMITTED** （提交读） | 不可能 | 可能 | 可能 | 读前申请共享锁，读完立即释放；只读已提交数据。可能会出现同一事务同一数据前后读两次值不同的现象（不可重复读） |
| **READREPEATABLE** （可重复读） | 不可能 | 不可能 | 可能 | 读前申请共享锁，**持锁到事务结束**；避免其他事务修改当前事务正在使用的数据。可能出现同一事务同样条件前后两次查询结果集里多/少了几行的现象（幻读）|
| **SERIALIZABLE** （可串行化） | 不可能 | 不可能 | 不可能 | 以可串行化调度执行并发事务，彻底避免相互干扰；性能最低 |

> **基于封锁的并发控制基本思想：**

> 1. 事务 T 持有数据对象 O 上的**读锁**时，只允许 T 以"读"方式访问 O
> 2. 事务 T 持有数据对象 O 上的**写锁**时，允许 T 以"读"或"写"方式访问 O
> 3. 一个事务在一个数据对象上，最多只能持有一把一种类型的锁（要么读锁，要么写锁）
> 4. 不同事务能不能同时在同一个数据对象上持锁，要看锁是否相容（只有读锁和读锁是相容的）。


总结一下：

| 隔离级别     | 读锁                      | 写锁 | 锁保持时间     | 能防什么         |
| -------- | ----------------------- | -- | --------- | ------------ |
| **未提交读** | 通常不加，或很快释放              | 要加 | 写锁一般持有到提交 | 基本不防，只是写仍受控制 |
| **提交读**  | 读时加，读完就放                | 要加 | 读锁短，写锁到提交 | 防脏读          |
| **可重复读** | 读时加，并保持到事务结束            | 要加 | 读锁长，写锁到提交 | 防脏读、不可重复读    |
| **可串行化** | 读时加，并保持到事务结束；还要加范围锁/谓词锁 | 要加 | 最严格       | 防脏读、不可重复读、幻读 |

---

## 三、SQL 中的空值（NULL）

---

### 3.1 空值的含义

> **空值（NULL）** 就是"不知道"或"不存在"或"无意义"的值。

**空值出现的场景：**

| 情形 | 示例 |
|---|---|
| 属性应有值但目前未知 | 学生成绩尚未录入 |
| 属性不应该有值 | 未婚者的配偶姓名 |
| 出于某种原因不便填写 | 涉密信息 |

空值是非常特殊的值，含有**不确定性**，对关系运算带来特殊问题，需要特殊处理。

---

### 3.2 空值的产生

```sql
-- 例3.79：显式插入 NULL
INSERT INTO SC(Sno, Cno, Grade)
VALUES('201215126', '1', NULL);

-- 或：省略属性列，DBMS 自动赋 NULL
INSERT INTO SC(Sno, Cno)
VALUES('201215126', '1');

-- 例3.80：UPDATE 将属性值修改为 NULL
UPDATE Student
SET Sdept = NULL
WHERE Sno = '201215200';
```

---

### 3.3 空值的判断

判断属性是否为空，使用 `IS NULL` 或 `IS NOT NULL`（**不能**用 `= NULL` 或 `<> NULL`）。

```sql
-- 例3.81：找出有漏填数据的学生
SELECT *
FROM Student
WHERE Sname IS NULL
   OR Ssex  IS NULL
   OR Sage  IS NULL
   OR Sdept IS NULL;
```

---

### 3.4 空值相关的完整性约束

| 约束 | 行为 |
|---|---|
| `NOT NULL` | 该属性不能取空值 |
| `PRIMARY KEY`（主码） | 主码属性不能取空值（隐含 NOT NULL） |
| `UNIQUE` | 当属性值非空时，其值在表中具有唯一性（NULL 值之间不参与唯一性比较） |

> **实践：** 可通过 `UNIQUE + NOT NULL` 联合约束来确保表中元组的唯一性。

---

### 3.5 空值的运算规则

#### 算术运算

$$
\text{NULL} \; \text{op} \; x = \text{NULL}
$$

空值与任何值（包括另一个空值）的算术运算结果均为 **NULL**。

#### 比较运算

$$
\text{NULL} \; \theta \; x = \text{UNKNOWN}
$$

空值与任何值的比较运算结果为 **UNKNOWN**（不是 TRUE，也不是 FALSE）。

#### 三值逻辑（Three-Valued Logic）

引入 UNKNOWN 后，布尔逻辑从二值扩展为三值：

| p | q | p AND q | p OR q | NOT p |
|---|---|---|---|---|
| TRUE | UNKNOWN | UNKNOWN | TRUE | FALSE |
| FALSE | UNKNOWN | FALSE | UNKNOWN | TRUE |
| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

#### DBMS 的实际处理规则

> 在 `WHERE` 子句和 `HAVING` 子句中，**只有条件表达式的判断结果为 TRUE 时**，当前元组（或组）才被作为结果输出。

关系 DBMS 一般规定：**空值参与比较运算的结果为逻辑假 FALSE**。

**典型陷阱示例：**

```sql
-- 例3.82：只找不及格学生（不包括缺考者，因为 NULL < 60 → FALSE）
SELECT Sno
FROM SC
WHERE Grade < 60 AND Cno = '1';

-- 例3.83：找不及格 + 缺考学生（两种写法）

-- 写法一：UNION
SELECT Sno FROM SC WHERE Grade < 60  AND Cno = '1'
UNION
SELECT Sno FROM SC WHERE Grade IS NULL AND Cno = '1';

-- 写法二：OR（推荐）
SELECT Sno
FROM SC
WHERE Cno = '1' AND (Grade < 60 OR Grade IS NULL);

-- ⚠️ 以下写法也是正确的
SELECT Sno FROM SC WHERE Cno = '1' AND NOT (Grade >= 60);
```

---

## 四、视图（VIEW）

---

### 4.1 视图的概念与特点

> **视图（View）** 是从一个或几个基本表（或视图）导出的**虚表**。

**视图的三大特点：**

1. **虚表**：视图在数据库中只存放视图的**定义**（存储在数据字典中），不存放视图对应的数据
2. **动态性**：基本表中的数据发生变化，通过视图查询出的数据也随之改变
3. **派生性**：视图的数据来源于基本表，对视图的操作最终转化为对基本表的操作

---

### 4.2 定义视图（CREATE VIEW）

#### 4.2.1 建立视图

**语句格式：**

```sql
CREATE VIEW <视图名> [(<列名> [, <列名>] …)]
AS <子查询>
[WITH CHECK OPTION];
```

**说明：**

- **子查询**：可以是任意的 SELECT 语句（标准 SQL 中不允许含 ORDER BY，但可使用 DISTINCT）
- **WITH CHECK OPTION**：如果允许在该视图上执行更新操作，则其更新后的结果元组仍然必需满足视图的定义条件。即通过该视图插入或修改后的新元组能够通过该视图上的查询操作查出来。**不影响**对基本表的插入和修改等直接操作
- DBMS 执行 CREATE VIEW 时只将视图定义存入数据字典，**不执行子查询**

#### 视图列名的规则

| 情形 | 处理方式 |
|---|---|
| **全部省略列名** | 沿用子查询 SELECT 目标列的字段名 |
| **全部指定列名** | 可沿用原名，也可使用新名；须保证唯一性 |

**必须明确指定所有列名的情形：**

- 某个目标列是**聚集函数**或**列表达式**（无默认名）
- 多表连接时选出了**同名列**
- 需要为某列启用**更合适的名字**

---

#### 4.2.2 各类视图示例

**① 行列子集视图（最常见）**

> 从单个基本表导出，只去掉了部分行和列，但保留了主码。

```sql
-- 例3.84 / 3.85：信息系学生视图
CREATE VIEW IS_Student
AS
SELECT Sno, Sname, Sage
FROM Student
WHERE Sdept = 'IS'
WITH CHECK OPTION;
```

**② 基于多个基表的视图**

```sql
-- 例3.86：信息系选修了1号课程的学生（含姓名、成绩）
CREATE VIEW IS_S1(Sno, Sname, Grade)
AS
SELECT Student.Sno, Sname, Grade
FROM Student, SC
WHERE Sdept = 'IS'
  AND Student.Sno = SC.Sno
  AND SC.Cno = '1';
```

**③ 基于视图的视图（视图嵌套定义）**

```sql
-- 例3.87：在 IS_S1 视图上进一步筛选（成绩 ≥ 90）
CREATE VIEW IS_S2
AS
SELECT Sno, Sname, Grade
FROM IS_S1
WHERE Grade >= 90;
```

**④ 带表达式的视图（导出属性）**

```sql
-- 例3.88：包含出生年份的视图（列表达式）
CREATE VIEW BT_S(Sno, Sname, Sbirth)
AS
SELECT Sno, Sname, 2014 - Sage
FROM Student;
```

**⑤ 分组视图（含聚集函数）**

```sql
-- 例3.89：学号与平均成绩视图
CREATE VIEW S_G(Sno, Gavg)
AS
SELECT Sno, AVG(Grade)
FROM SC
GROUP BY Sno;
```

**⑥ 使用 SELECT * 的视图（不推荐）**

```sql
-- 例3.90：全女生视图（缺点：基表结构变更后视图映射关系被破坏，建议在SELECT时将所选列全部列举出来）
CREATE VIEW F_Student(F_Sno, name, sex, age, dept)
AS
SELECT *
FROM Student
WHERE Ssex = '女';
```

---

#### 4.2.3 WITH CHECK OPTION 详解

```sql
-- 示例：带 CHECK OPTION 的视图
CREATE VIEW IS_Stud
AS
SELECT Sno, Sname, Sdept
FROM Student
WHERE Sdept = 'IS'
WITH CHECK OPTION;

-- 以下操作被拒绝（违反 Sdept = 'IS' 的条件）
INSERT INTO IS_Stud VALUES(231215101, '王海', 'CS'); -- 拒绝

UPDATE IS_Stud SET Sdept = 'CS' WHERE Sno = '201215121'; -- 拒绝

-- 以下操作可以执行（直接操作基本表，不受 CHECK OPTION 约束）
INSERT INTO Student(Sno, Sname, Sdept) VALUES(231215101, '王海', 'CS'); -- 允许
```

---

### 4.3 删除视图（DROP VIEW）

**语句格式：**

```sql
DROP VIEW <视图名> [CASCADE];
```

**说明：**

- 从数据字典中删除指定视图的定义
- 若该视图上还导出了其他视图，须使用 `CASCADE` 级联删除
- 不使用 CASCADE 而存在依赖视图时，系统**拒绝**删除操作
- 删除基本表时若使用 `CASCADE`，由该表导出的所有视图定义会被连带删除

**示例：**

```sql
DROP VIEW BT_S;         -- 成功（无依赖视图）
DROP VIEW IS_S1;        -- 拒绝（IS_S2 依赖于 IS_S1）
DROP VIEW IS_S1 CASCADE; -- 成功，同时删除 IS_S1 和 IS_S2
```

---

### 4.4 查询视图

用户角度：**查询视图与查询基本表相同**。

#### 视图消解法（View Resolution）

DBMS 实现视图查询的核心方法：

1. 进行有效性检查（视图是否存在，列名是否合法）
2. 将视图查询**转换为等价的对基本表的查询**（视图展开）
3. 执行修正后的查询

??? info 

    其实就是把“对视图的查询”翻译为“对基本表的查询”。我们写视图查询语句时，数据库管理系统会自动把它改写成对基本表的查询，也就是自动做“视图消解”。

**示例：**

```sql
-- 例3.92：在视图上查询（年龄 < 20 的信息系学生）
SELECT Sno, Sage
FROM IS_Student
WHERE Sage < 20;

-- 视图消解后等价于：
SELECT Sno, Sage
FROM Student
WHERE Sdept = 'IS' AND Sage < 20;

-- 例3.94：分组视图上的查询（平均成绩 ≥ 90）
SELECT *
FROM S_G
WHERE Gavg >= 90;

-- 视图消解后等价于：
SELECT Sno, AVG(Grade)
FROM SC
GROUP BY Sno
HAVING AVG(Grade) >= 90;

-- 或以子查询方式：
SELECT *
FROM (SELECT Sno, AVG(Grade) FROM SC GROUP BY Sno) AS S_G(Sno, Gavg)
WHERE Gavg >= 90;
```

---

### 4.5 更新视图

#### 可更新视图的条件

> 一般不允许执行视图上的更新操作，只有满足以下**两个条件**才可以：

> 1. 视图的**每一行**必须对应基表的唯一一行
> 2. 视图的**每一列**必须对应基表的唯一一列

满足上述条件的视图称为**可更新视图（Updatable View）**，视图上的更新操作须转化为基表上的更新操作。

**行列子集视图**一般为可更新视图。

#### 不可更新视图的典型情形

| 类型 | 示例 | 原因 |
|---|---|---|
| **含聚集函数的分组视图** | S_G（AVG(Grade)） | 无法将修改平均值转换为对原始数据的修改 |
| **含复杂子查询的视图** | GOOD_SC（WHERE Grade > AVG） | 谓词依赖于整体统计，更新无法唯一映射 |
| **在不可更新视图上定义的视图** | 继承不可更新性 | — |

**示例：**

```sql
-- 例3.95：更新视图（UPDATE → 转化为对基表的 UPDATE）
UPDATE IS_Student
SET Sname = '刘辰'
WHERE Sno = '201215122';

-- 转化为：
UPDATE Student
SET Sname = '刘辰'
WHERE Sno = '201215122' AND Sdept = 'IS';

-- 例3.96：向视图插入（INSERT → 转化为对基表的 INSERT，自动补填 Sdept）
INSERT INTO IS_Student
VALUES('201215129', '赵新', 20);

-- 转化为：
INSERT INTO Student(Sno, Sname, Sage, Sdept)
VALUES('201215129', '赵新', 20, 'IS');

-- 例3.97：从视图删除（DELETE → 转化为对基表的 DELETE）
DELETE FROM IS_Student
WHERE Sno = '201215129';

-- 转化为：
DELETE FROM Student
WHERE Sno = '201215129' AND Sdept = 'IS';

-- 不可更新示例（S_G 为分组视图）
UPDATE S_G
SET Gavg = 90
WHERE Sno = '201215121'; -- 无法转换，被拒绝
```

---

### 4.6 视图的作用

#### ① 简化用户的操作

将复杂查询（多表连接、嵌套子查询、含导出属性）封装为视图，用户只需查询视图即可。

```sql
-- 先定义视图：求每个学生的最高成绩
CREATE VIEW VMGRADE
AS
SELECT Sno, MAX(Grade) Mgrade
FROM SC
GROUP BY Sno;

-- 再用简单查询完成复杂需求：找每人最高成绩对应的课程号
SELECT SC.Sno, Cno
FROM SC, VMGRADE
WHERE SC.Sno = VMGRADE.Sno AND SC.Grade = VMGRADE.Mgrade;
```

#### ② 使用户能以多种角度看待同一数据

视图机制使不同用户可以以不同方式看待同一数据，适应数据库**共享**的需要。

#### ③ 对重构数据库提供逻辑独立性

当基本表结构改变时，可以通过重新定义视图，使外模式（用户视角）保持不变，从而保证应用程序的相对稳定。

```sql
-- 例：Student 表被垂直分拆为 SX 和 SY 后，通过视图重建逻辑结构
CREATE VIEW Student(Sno, Sname, Ssex, Sage, Sdept)
AS
SELECT SX.Sno, SX.Sname, SY.Ssex, SX.Sage, SY.Sdept
FROM SX, SY
WHERE SX.Sno = SY.Sno;
```

> 注意：由于对视图的更新是有条件的，涉及写操作的应用程序仍可能需要修改。

#### ④ 对机密数据提供安全保护

对不同用户定义不同视图，使每个用户只能看到（查询/修改）其有权访问的数据，实现**数据访问控制**。

#### ⑤ 使查询表达更清晰

将复杂逻辑拆分为多个层次的视图，提升 SQL 语句的可读性和可维护性。

---

## 五、本章知识点总结

### 数据更新三要素对比

| 操作 | 语句 | 省略 WHERE 的效果 | 完整性检查 |
|---|---|---|---|
| 插入 | INSERT INTO … VALUES / 子查询 | 必须提供值 | 实体完整性、参照完整性 |
| 修改 | UPDATE … SET … WHERE | 修改所有元组 | 实体完整性、参照完整性、用户定义完整性 |
| 删除 | DELETE FROM … WHERE | 删除所有元组（表仍存在） | 参照完整性 |

### 事务 ACID 特性速记

| 特性 | 英文 | 由谁保证 |
|---|---|---|
| 原子性 | Atomicity | 恢复机制（Undo） |
| 一致性 | Consistency | 完整性约束 + 原子性 + 隔离性 + 持久性共同保证 |
| 隔离性 | Isolation | 并发控制（锁/MVCC） |
| 持久性 | Durability | 日志机制（WAL/Redo） |

### 视图核心知识速查

| 操作 | 是否允许 | 条件 |
|---|---|---|
| 查询视图 | 总是允许 | 通过视图消解转化为基表查询 |
| INSERT 视图 | 条件允许 | 可更新视图；WITH CHECK OPTION 时须满足谓词 |
| UPDATE 视图 | 条件允许 | 可更新视图 |
| DELETE 视图 | 条件允许 | 可更新视图 |
| 级联删除视图 | 需加 CASCADE | 视图上有依赖视图时必须级联 |

---
