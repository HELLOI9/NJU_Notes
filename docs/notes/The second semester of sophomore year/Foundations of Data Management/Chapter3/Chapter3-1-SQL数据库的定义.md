# 第3章 关系数据库标准语言 SQL

---

## 3.1 SQL 概述

### 定义

**SQL**（Structured Query Language，结构化查询语言）是关系数据库的**标准语言**，是一种通用的、功能极强的关系数据库语言。

---

### SQL 的五大特点

#### 1. 综合统一

SQL 将 **DDL**（数据定义语言）、**DML**（数据操纵语言）、**DCL**（数据控制语言）的功能集于一体，可独立完成数据库生命周期中的全部活动：

- 定义、修改、删除关系模式；定义和删除视图；插入数据；建立数据库
- 对数据库中的数据进行查询和更新
- 数据库重构与维护
- 数据库安全性、完整性控制及事务控制
- 嵌入式 SQL 与动态 SQL 定义

> **优势**：用户数据库投入运行后，可根据需要随时逐步修改模式，**不影响数据库的正常运行**。

#### 2. 高度非过程化

- 非关系数据模型的 DML 是"面向过程"的，必须显式指定存取路径
- SQL 只需提出**"做什么"**，无须了解"怎么做"（存取路径的选择由系统自动完成）

#### 3. 面向集合的操作方式

| 对比维度 | 非关系数据模型 | SQL |
|----------|---------------|-----|
| 操作方式 | 面向记录 | 面向集合 |
| 操作对象 | 一条记录 | 元组的集合 |
| 操作结果 | 单条记录 | 元组的集合 |

#### 4. 多种使用方式

- **独立语言**：可通过命令行交互、批处理方式直接访问数据库
- **嵌入式语言**：可嵌入 C、C++、Java 等高级语言程序中供程序员使用

#### 5. 语言简洁，易学易用

SQL 完成核心功能仅使用 **9 个动词**：

| 功能类别 | 动词 |
|----------|------|
| 数据定义（DDL） | `CREATE`、`DROP`、`ALTER` |
| 数据查询（DQL） | `SELECT` |
| 数据操作（DML） | `INSERT`、`UPDATE`、`DELETE` |
| 数据控制（DCL） | `GRANT`、`REVOKE` |

---

### SQL 中的基本概念

#### 关系模型 → SQL 术语对照

| 关系模型术语 | SQL 术语 | 备注 |
|-------------|---------|------|
| 关系（Relation） | 基本表（Base Table） | 两者统称为"表"（Table） |
| 子模式（Sub-schema） | 视图（View） | 视图又称"虚表" |
| 属性（Attribute） | 列（Column） | — |
| 元组（Tuple） | 行（Row） | — |

#### SQL 语言的基本语言成分

- **符号**：26 个英文字母、阿拉伯数字、括号、四则运算符等
- **保留字**：在 SQL 中具有特定含义的语言成分（如 `CREATE`、`TABLE`、`PRIMARY KEY` 等）
- **标识符**：用于命名用户创建的数据库对象（表、视图、属性、存储过程等）
- **常量**：数值常量、字符（串）常量（需单引号定界）、日期/时间常量

#### SQL 基本表示规范（交互式 SQL）

- 完整 SQL 语句通常以**命令动词**开始，以**分号 `;`** 作为结束符
- SQL 语言（除常量外）仅支持**西文字符**，字母**不区分大小写**
- 数值常量不需要定界符；字符串或日期/时间常量需使用**单引号**定界

---

### SQL 与关系数据库三级模式的对应关系

```
SQL
├── 视图（View）          ← 外模式（External Schema）
├── 基本表（Base Table）  ← 模式（Schema / Conceptual Schema）
└── 存储文件             ← 内模式（Internal Schema）
```

| 层次 | SQL 对象 | 特点 |
|------|---------|------|
| **外模式** | 视图 | 从一个或多个基本表导出；数据库中只存放视图的定义，不存放对应数据；是虚表；可在视图上再定义视图 |
| **模式** | 基本表 | 本身独立存在；一个关系对应一个基本表；一个或多个基本表对应一个存储文件；一个表可带若干索引 |
| **内模式** | 存储文件 | 存储文件的逻辑结构组成关系数据库的内模式；物理结构对用户隐蔽 |

---

## 3.2 学生-课程数据库

> 贯穿全章的示例数据库，包含三个关系：**Student（学生）**、**Course（课程）**、**SC（选修）**

### Student 表

| Sno（学号） | Sname（姓名） | Ssex（性别） | Sage（年龄） | Sdept（所在系） |
|------------|-------------|------------|------------|--------------|
| 201215121 | 李勇 | 男 | 20 | CS |
| 201215122 | 刘晨 | 女 | 19 | CS |
| 201215123 | 王敏 | 女 | 18 | MA |
| 201215125 | 张立 | 男 | 19 | IS |

### Course 表

| Cno（课程号） | Cname（课程名） | Cpno（先行课） | Ccredit（学分） |
|-------------|--------------|-------------|--------------|
| 1 | 数据库 | 5 | 4 |
| 2 | 数学 | — | 2 |
| 3 | 信息系统 | 1 | 4 |
| 4 | 操作系统 | 6 | 3 |
| 5 | 数据结构 | 7 | 4 |
| 6 | 数据处理 | — | 2 |
| 7 | PASCAL语言 | 6 | 4 |

### SC 表（选修关系）

| Sno（学号） | Cno（课程号） | Grade（成绩） |
|------------|-------------|------------|
| 201215121 | 1 | 92 |
| 201215121 | 2 | 85 |
| 201215121 | 3 | 88 |
| 201215122 | 2 | 90 |
| 201215122 | 3 | 80 |

---

## 3.3 SQL 数据定义

### 层次化的数据库对象命名机制

```
DBMS 实例（Instance）
└── 数据库（Database）/ 目录（Catalog）
    └── 模式（Schema）
        └── 表、视图、索引等数据库对象
```

### SQL 数据定义语句总览

| 操作对象 | 创建 | 删除 | 修改 |
|---------|------|------|------|
| 模式 | `CREATE SCHEMA` | `DROP SCHEMA` | — |
| 表 | `CREATE TABLE` | `DROP TABLE` | `ALTER TABLE` |
| 视图 | `CREATE VIEW` | `DROP VIEW` | — |
| 索引 | `CREATE INDEX` | `DROP INDEX` | `ALTER INDEX` |

---

### 3.3.1 模式（Schema）的定义与删除

#### 定义模式

模式定义了一个**命名空间**，在其中可以定义基本表、视图、索引等数据库对象。

**语法格式：**

```sql
CREATE SCHEMA <模式名> AUTHORIZATION <用户名>
    [<表定义子句> | <视图定义子句> | <授权定义子句>];
```

**示例：**

```sql
-- 例3.1：为用户 WANG 定义学生-课程模式
CREATE SCHEMA "S_T" AUTHORIZATION WANG;

-- 例3.2：省略模式名，模式名隐含为用户名
CREATE SCHEMA AUTHORIZATION WANG;

-- 例3.3：创建模式 TEST 并在其中定义表 TAB1
CREATE SCHEMA TEST AUTHORIZATION ZHANG
    CREATE TABLE TAB1 (
        COL1 SMALLINT,
        COL2 INT,
        COL3 CHAR(20),
        COL4 NUMERIC(10,3),
        COL5 DECIMAL(5,2)
    );
```

#### 删除模式

```sql
DROP SCHEMA <模式名> <CASCADE | RESTRICT>;
```

| 选项 | 含义 |
|------|------|
| `CASCADE`（级联） | 删除模式的同时，将该模式中所有数据库对象全部删除 |
| `RESTRICT`（限制） | 若该模式中存在任何下属对象，则拒绝执行删除操作 |

```sql
-- 例3.4：级联删除模式 ZHANG 及其下的表 TAB1
DROP SCHEMA ZHANG CASCADE;
```

---

### 3.3.2 基本表的定义、修改与删除

#### 定义基本表

**语法格式：**

```sql
CREATE TABLE <表名> (
    <列名> <数据类型> [<列级完整性约束条件>],
    [<列名> <数据类型> [<列级完整性约束条件>],] ...
    [<表级完整性约束条件>]
);
```

> **重要原则**：若完整性约束条件涉及**多个属性列**，则必须定义在**表级**；若只涉及单一属性列，列级和表级均可。

**示例一：学生表 Student**

```sql
-- 例3.5：Sno 为主码，Sname 取值唯一
CREATE TABLE Student (
    Sno   CHAR(9)  PRIMARY KEY,   -- 列级完整性约束，Sno 是主码
    Sname CHAR(20) UNIQUE,        -- Sname 取值唯一
    Ssex  CHAR(2),
    Sage  SMALLINT,
    Sdept CHAR(20)
);
```

> **注意**：在实际应用中，姓名不具备唯一性，不能作为学生表的码。

**示例二：课程表 Course（含自参照外码）**

```sql
-- 例3.6：Cpno 是外码，参照本表的 Cno（先修课）
CREATE TABLE Course (
    Cno     CHAR(4)  PRIMARY KEY,
    Cname   CHAR(40) NOT NULL,
    Cpno    CHAR(4),
    Ccredit SMALLINT,
    FOREIGN KEY (Cpno) REFERENCES Course(Cno)  -- 自参照
);
```

**示例三：选修表 SC（复合主码 + 双外码）**

```sql
-- 例3.7：主码由 Sno 和 Cno 共同构成，必须定义在表级
CREATE TABLE SC (
    Sno   CHAR(9),
    Cno   CHAR(4),
    Grade SMALLINT,
    PRIMARY KEY (Sno, Cno),                          -- 表级：复合主码
    FOREIGN KEY (Sno) REFERENCES Student(Sno),       -- 外码，参照 Student
    FOREIGN KEY (Cno) REFERENCES Course(Cno)         -- 外码，参照 Course
);
```

---

#### 数据类型

选用数据类型时需考虑两个因素：**取值范围** 和 **需要进行的运算**。

**常用 SQL 数据类型（ISO SQL99）：**

| 数据类型 | 说明 |
|---------|------|
| `CHAR(n)` / `CHARACTER(n)` | 长度为 n 的**定长**字符串 |
| `VARCHAR(n)` / `CHARACTER VARYING(n)` | 最大长度为 n 的**变长**字符串 |
| `CLOB` | 字符串大对象 |
| `BLOB` | 二进制大对象 |
| `INT` / `INTEGER` | 长整数（4 字节） |
| `SMALLINT` | 短整数（2 字节） |
| `BIGINT` | 大整数（8 字节） |
| `NUMERIC(p, d)` | 定点数，共 p 位，小数点后 d 位 |
| `DECIMAL(p, d)` / `DEC(p, d)` | 同 `NUMERIC` |
| `REAL` | 单精度浮点数 |
| `DOUBLE PRECISION` | 双精度浮点数 |
| `FLOAT(n)` | 精度至少为 n 位的浮点数 |
| `BOOLEAN` | 逻辑布尔量 |
| `DATE` | 日期，格式 `YYYY-MM-DD`，列长 10 字节 |
| `TIME` | 时间，格式 `HH:MM:SS`，列长 8 字节 |
| `TIMESTAMP` | 时间戳（年月日时分秒微秒），列长 26 字节 |
| `INTERVAL` | 时间间隔类型 |

**SQL 数据类型体系（ISO SQL99）：**

```
Data Types
├── Predefined (Built-in)
│   ├── Character strings: CHARACTER, CHARACTER VARYING, CLOB
│   ├── Binary strings:    BINARY LARGE OBJECT
│   ├── Bit strings:       BIT, BIT VARYING
│   ├── Numbers:           INTEGER, SMALLINT, NUMERIC, DECIMAL, FLOAT, REAL, DOUBLE PRECISION
│   └── Datetimes:         DATE, TIME, TIMESTAMP, INTERVAL
├── Constructed Types
│   └── Boolean:           BOOLEAN
└── User-defined Types
```

**常用内置函数（数值 & 字符）：**

| 函数 | 说明 |
|------|------|
| `abs(n)` | 绝对值 |
| `mod(n, b)` | n 除以 b 的余数 |
| `sqrt(n)` | 平方根 |
| `CHAR_LENGTH(str)` | 字符串长度 |
| `SUBSTRING(str FROM m FOR n)` | 截取子串 |
| `TRIM(str)` / `LTRIM` / `RTRIM` | 去除空格 |
| `POSITION(str1 IN str2)` | 子串位置 |
| `LOWER(str)` / `UPPER(str)` | 大小写转换 |

**常用日期函数：**

| 函数 | 说明 |
|------|------|
| `GETDATE()` | 返回当前系统日期时间 |
| `DAY(...)` | 返回日期的"日"部分 |
| `MONTH(...)` | 返回日期的"月"部分 |
| `YEAR(...)` | 返回日期的"年"部分 |

---

#### 修改基本表

```sql
ALTER TABLE <表名>
    [ADD [COLUMN] <新列名> <数据类型> [完整性约束]]   -- 增加新列
    [ADD <表级完整性约束>]                            -- 增加表级约束
    [DROP [COLUMN] <列名> [CASCADE | RESTRICT]]       -- 删除列
    [DROP CONSTRAINT <约束名> [RESTRICT | CASCADE]]   -- 删除约束
    [ALTER COLUMN <列名> <数据类型>];                 -- 修改列定义
```

| 子句 | 功能 |
|------|------|
| `ADD [COLUMN]` | 增加新列（新列一律为 `NULL`，不论原表是否有数据） |
| `ADD <约束>` | 增加新的表级完整性约束 |
| `DROP [COLUMN] ... CASCADE` | 删除列，并自动删除引用该列的其他对象 |
| `DROP [COLUMN] ... RESTRICT` | 若该列被其他对象引用，则拒绝删除 |
| `DROP CONSTRAINT` | 删除指定完整性约束 |
| `ALTER COLUMN` | 修改列名或数据类型 |

```sql
-- 例3.8：增加"入学时间"列（新列值为 NULL）
ALTER TABLE Student ADD S_entrance DATE;

-- 例3.9：将年龄列的数据类型改为整型
ALTER TABLE Student ALTER COLUMN Sage INT;

-- 例3.10：增加课程名称唯一性约束
ALTER TABLE Course ADD UNIQUE(Cname);
```

---

#### 删除基本表

```sql
DROP TABLE <表名> [RESTRICT | CASCADE];
```

| 选项 | 含义 |
|------|------|
| `RESTRICT` | 若存在依赖该表的对象（视图、约束等），则拒绝删除 |
| `CASCADE` | 删除基本表的同时，相关索引、视图、触发器等**一并删除** |

```sql
-- 例3.11：级联删除 Student 表
DROP TABLE Student CASCADE;

-- 例3.12：有视图时的对比
DROP TABLE Student RESTRICT;
-- ERROR: cannot drop table Student because other objects depend on it

DROP TABLE Student CASCADE;
-- NOTICE: drop cascades to view IS_Student
```

---

### 3.3.3 索引的建立与删除

#### 索引概述

**建立索引的目的**：加快查询速度

- 索引由**数据库管理员**或**表的拥有者**建立
- 由 RDBMS 自动维护，用户**不必也不能**显式选择索引
- RDBMS 自动使用合适的索引作为存取路径

**常见索引类型：**

- 顺序文件上的索引
- B+ 树索引
- 散列（Hash）索引
- 位图（Bitmap）索引

#### 建立索引

```sql
CREATE [UNIQUE] [CLUSTER] INDEX <索引名>
ON <表名>(<列名> [<次序>] [, <列名> [<次序>]] ...);
```

| 关键字 | 含义 |
|--------|------|
| `UNIQUE` | 索引的每个索引值唯一对应一条数据记录 |
| `CLUSTER` | 建立聚簇索引（物理顺序与索引顺序一致） |
| `ASC` | 升序（默认） |
| `DESC` | 降序 |

```sql
-- 例3.13：为三张表建立索引
CREATE UNIQUE INDEX Stusno ON Student(Sno);
CREATE UNIQUE INDEX Coucno ON Course(Cno);
CREATE UNIQUE INDEX SCno   ON SC(Sno ASC, Cno DESC);
```

#### 修改索引

```sql
-- 例3.14：将 SC 表的 SCno 索引重命名为 SCSno
ALTER INDEX SCno RENAME TO SCSno;
```

#### 删除索引

```sql
-- 例3.15：删除索引（系统同时从数据字典中删除该索引的描述）
DROP INDEX Stusname;
```

---

### 3.3.4 数据字典

**数据字典**是 RDBMS 内部的一组**系统表**，记录了数据库中所有定义信息：

- 关系模式定义
- 视图定义
- 索引定义
- 完整性约束定义
- 各类用户对数据库的操作权限
- 统计信息等

> RDBMS 在执行 SQL 数据定义语句时，实际上是在**更新数据字典表中的相应信息**。

#### 国产数据库数据字典示例

**华为 GaussDB 核心系统表：**

| 系统表名 | 描述 |
|---------|------|
| `PG_class` | 最核心的系统表，记录表、视图、索引、属性、序列等对象的定义信息 |
| `PG_attribute` | 存储所有表中的字段定义信息 |
| `PG_index` | 存储索引的部分信息 |
| `PG_attrdef` | 存储字段的缺省值 |
| `PG_constraint` | 存储表上的数据完整性约束定义 |
| `PG_tablespace` | 存储表空间信息 |
| `PG_namespace` | 存储名字空间（模式）信息 |
| `PG_database` | 存储集群中所有数据库的信息 |

**蚂蚁集团 OceanBase：**

OceanBase 是**分布式数据库**，采用**多租户架构**，提供三种类型的字典视图：

| 视图类型 | 访问对象 |
|---------|---------|
| `information_schema` 视图 | 面向普通用户租户 |
| `oceanbase.CDB` 视图 | 面向系统租户 |
| `oceanbase.DBA` 视图 | 面向拥有管理员权限的用户 |

---

## 核心知识点总结

```
SQL 数据定义核心体系
│
├── 模式（Schema）
│   ├── CREATE SCHEMA ... AUTHORIZATION ...
│   └── DROP SCHEMA ... [CASCADE | RESTRICT]
│
├── 基本表（Table）
│   ├── CREATE TABLE（含列级/表级完整性约束）
│   ├── ALTER TABLE（ADD / DROP / ALTER COLUMN）
│   └── DROP TABLE [CASCADE | RESTRICT]
│
├── 索引（Index）
│   ├── CREATE [UNIQUE][CLUSTER] INDEX
│   ├── ALTER INDEX ... RENAME TO ...
│   └── DROP INDEX
│
└── 数据字典（Data Dictionary）
    └── RDBMS 内部系统表，随 DDL 语句自动更新
```
