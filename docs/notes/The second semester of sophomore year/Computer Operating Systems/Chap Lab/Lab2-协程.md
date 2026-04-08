# M2：协程库 (libco) 

> **课程：** 操作系统  
> **目标：** 在单一 OS 线程内实现用户态协程库，支持主动切换的多执行流

---

## 1. 项目概述

### 1.1 背景

程序是状态机。单线程程序的状态机在遇到死循环时会"卡死"。本实验的核心问题是：**能否在一个操作系统线程（状态机）内，模拟多个状态机并发执行的效果？**

类比于 Python 的 generator：

```python
def positive_integers():
    i = 0
    while i := i + 1:
        yield i   # 暂停，返回控制权；下次调用从这里继续
```

generator function 调用后返回一个闭包对象（不会立即执行），闭包内部保存了所有局部变量和 PC（程序计数器）。这正是协程的本质：**可以暂停和恢复执行的函数**。

### 1.2 协程的本质（状态机视角）

每个协程的状态 = **寄存器** + **独立堆栈** + **共享内存（进程地址空间）**

| 操作 | 含义 |
|------|------|
| `co_start` | 在共享内存中创建新的状态机（分配独立堆栈，设置 `%rsp` 和 `%rip`） |
| `co_yield` | 保存当前协程的寄存器到 `struct co`，加载另一个协程的寄存器，完成"状态机切换" |
| `co_wait` | 等待目标状态机进入终止状态（`func()` 返回） |

### 1.3 交付物

- 只需提交 `co.c` 一个文件
- 不得修改 `co.h`
- 编译为共享库 `libco-64.so` 和 `libco-32.so`，需在 x86-64 和 x86-32 两个平台均正确运行

---

## 2. 核心概念：协程 vs 线程

| 维度 | 线程 | 协程 |
|------|------|------|
| 调度方式 | 操作系统强制抢占 | 主动调用 `co_yield()` 让出 |
| 运行级别 | 内核态参与调度 | 完全用户态，无需 syscall |
| 开销 | 较大（进程切换代价） | 极小（仅寄存器保存/恢复） |
| 并行 | 可多核并行 | 单线程，不可并行 |
| 中断 | 可被中断打断 | 运行至 `co_yield` 前不被打断 |

线程可视为"每条语句后都插入了 `co_yield()` 的协程"。如果能保证 `co_yield()` 的定时执行（如通过信号机制），协程就可模拟用户态线程。

---

## 3. API 规范

```c
// co.h（禁止修改）
struct co *co_start(const char *name, void (*func)(void *), void *arg);
void       co_yield(void);
void       co_wait(struct co *co);
```

### 3.1 `co_start(name, func, arg)`

- 创建新协程，分配 `struct co`（推荐 `malloc`）
- 新协程从 `func(arg)` 开始执行
- **新协程不立即运行**，调用者继续执行
- 返回 `struct co *` 指针（对调用者不透明，定义在 `.c` 中）

### 3.2 `co_yield()`

- 当前协程主动放弃 CPU
- 从系统中所有**可运行**协程中**随机**选择一个（含自身）
- 协程返回 `func` 后不再可运行

### 3.3 `co_wait(co)`

- 等待指定协程执行完毕（类似 `pthread_join`）
- 协程结束后、`co_wait` 返回前，**必须释放** `co_start` 分配的内存
- 每个协程**只能被 `co_wait` 一次**（否则内存泄漏或 UB）
- `main` 函数本身也是一个协程，可调用 `co_yield` 和 `co_wait`
- `main` 返回后，无论协程状态，进程直接终止

---

## 4. 实现架构设计

### 4.1 `struct co` 定义

```c
#include <stdint.h>
#include <setjmp.h>

#define STACK_SIZE (64 * 1024)  // 64 KiB，题目保证不超过此值

enum co_status {
    CO_NEW     = 1,  // 已创建，从未执行
    CO_RUNNING,      // 执行中（或曾执行过，被 yield 出来）
    CO_WAITING,      // 在 co_wait 上等待另一个协程
    CO_DEAD,         // func() 已返回，等待资源回收
};

struct co {
    char          *name;
    void         (*func)(void *);
    void          *arg;
    enum co_status status;
    struct co     *waiter;    // 谁在 co_wait 等我？
    jmp_buf        context;   // setjmp/longjmp 寄存器现场
    uint8_t        stack[STACK_SIZE];  // 独立堆栈
};
```

### 4.2 全局状态

```c
// 当前正在执行的协程
static struct co *current;

// 协程列表（最多 128 个）
static struct co *co_list[128];
static int co_count = 0;
```

### 4.3 协程状态机

```
co_start()
    │
    ▼
  CO_NEW ──── co_yield() 选中 ────► 执行 stack_switch_call ──► CO_RUNNING
                                                                    │
                                              ◄── co_yield() 选中 ───┘
                                              │
                                         longjmp 恢复
                                              │
                                         func() 返回
                                              │
                                           CO_DEAD ──► 唤醒 waiter ──► 释放内存
```

---

## 5. 关键实现步骤

### 5.1 初始化：注册 main 协程

使用 `__attribute__((constructor))` 在 `main` 执行前初始化：

```c
static struct co MAIN;  // main 对应的协程（静态分配，无需 malloc）

__attribute__((constructor)) static void init(){
    MAIN.name = "main";
    MAIN.arg = NULL;
    MAIN.func = NULL;
    MAIN.status = CO_RUNNING;
    MAIN.waiter = NULL;
    current = &MAIN;
    add(current);
    srand(time(NULL));
}
```

### 5.2 `co_start` 实现

```c
struct co* co_start(const char *name, void (*func)(void *), void *arg) {
    struct co* newCo = (struct co*)malloc(sizeof(struct co));
    assert(newCo != NULL);
    newCo->name = name;
    newCo->func = func;
    newCo->arg = arg;
    newCo->status = CO_NEW;
    newCo->waiter = NULL;
    add(newCo);
    return newCo;
}
```

### 5.3 `stack_switch_call`：切换堆栈并调用函数

这是整个实验的核心内联汇编，来自 AbstractMachine 的 `x86.h`：

```c
static inline void stack_switch_call(void *sp, void *entry, uintptr_t arg) {
    asm volatile (
#if __x86_64__
        "movq %0, %%rsp; movq %2, %%rdi; jmp *%1"
        : : "b"((uintptr_t)sp), "d"(entry), "a"(arg) : "memory"
#else
        "movl %0, %%esp; movl %2, 4(%0); jmp *%1"
        : : "b"((uintptr_t)sp - 8), "d"(entry), "a"(arg) : "memory"
#endif
    );
}
```

**逐行解析（x86-64）：**

| 汇编指令 | 含义 |
|---------|------|
| `movq %0, %%rsp` | 将 `sp`（新堆栈顶指针）载入 `%rsp`，完成堆栈切换 |
| `movq %2, %%rdi` | 将 `arg` 放入第一个参数寄存器（x86-64 调用约定） |
| `jmp *%1` | 跳转到 `entry` 函数，注意是 `jmp` 不是 `call` |

**约束说明：**

- `"b"` → `%rbx`（callee-saved，不会被协程入口函数破坏）
- `"d"` → `%rdx`
- `"a"` → `%rax`

**为什么用 `jmp` 而非 `call`？** `call` 会将返回地址压栈，而我们希望 `entry` 函数返回后能被我们的 wrapper 捕获处理，因此用 `jmp` 跳入 wrapper。

### 5.4 协程入口 wrapper

```c
static void co_wrapper(uintptr_t ptr){
    struct co* nowCo = (struct co*)ptr;
    nowCo->func(nowCo->arg);
    nowCo->status = CO_DEAD;
    if(nowCo->waiter) nowCo->waiter->status = CO_RUNNING;
    co_yield();
    assert(0);
} 
```

### 5.5 `co_yield` 实现

`co_yield` 是实现的核心，必须处理两类场景：

```c
void co_yield() {
    int val = setjmp(current->context);
    if(val == 0){
        struct co* nxt = getNextCo();
        assert(nxt != NULL);
        current = nxt;
        if(nxt->status == CO_NEW){
            nxt->status = CO_RUNNING;
            uintptr_t sp = (uintptr_t)(nxt->STACK + STACK_SIZE);
#if __x86_64__
            sp &= ~0xFULL;
            sp -= 8;
#endif
            stack_switch_call((void*)sp, co_wrapper, (uintptr_t)nxt);
        }
        else longjmp(nxt->context, 1);
    }else{
        return;
    }
}
```

**`setjmp` 的两次返回：**

1. **首次调用** → 返回 `0`：保存寄存器现场，进入调度逻辑
2. **被 `longjmp` 唤醒** → 返回非零值：从这里"原路返回"，协程继续执行

### 5.6 `co_wait` 实现

```c
void co_wait(struct co *co) {
    if(co->status == CO_DEAD){
        remove(co);
        free(co);
        return;
    }
    current->status = CO_WAITING;
    co->waiter = current;
    co_yield();//Once the program returns there, current->status surely has been switchs CO_RUNNING.
    assert(co->status == CO_DEAD);
    remove(co);
    free(co);
}
```

### 5.7 随机调度器

```c
static struct co* getNextCo(){
    struct co* avaliable[MAX_CO];
    int num = 0;
    for(int i = 0; i < cnt; i++)
        if(allCo[i]->status == CO_RUNNING || allCo[i]->status == CO_NEW) avaliable[num++] = allCo[i];
    return avaliable[rand() % num];
}//getNextCo must be random ortherwise cause hunger!
```

---

## 6. 完整坑点分析

### ⚠️ 坑点 1：堆栈对齐（最常见的神秘 Segfault）

**问题：** x86-64 ABI 要求在 `call` 指令执行前，`%rsp` 必须满足 **16 字节对齐**。具体而言，`call` 会将 8 字节返回地址压栈，所以 `call` 前 `%rsp % 16 == 0`，进入被调函数时 `%rsp % 16 == 8`。

**现象：** 在 `libc` 函数内发生 Segfault，gdb 显示崩溃在 SSE 指令处，例如：
```asm
movaps %xmm0, 0x50(%rsp)   ← 崩溃点，要求 16 字节对齐
```

**原因：** `stack_switch_call` 使用的是 `jmp` 而非 `call`，不会压返回地址。进入 `co_entry` 时，`%rsp` 已经对齐到 16 字节，但随后的函数调用会压入 8 字节返回地址，使 `%rsp % 16 == 8`，符合 ABI 预期。

**解决：** `sp` 参数传入时需要确保对齐：
```c
// 堆栈顶端减去 8，让 jmp 进入函数时 %rsp % 16 == 8（模拟 call 的效果）
void *sp = (void *)((uintptr_t)(co->stack + STACK_SIZE) & ~15) - 8;
stack_switch_call(sp, co_entry, (uintptr_t)co);
```

**x86-32 的差异：** 参数通过堆栈传递（不是 `%rdi`），`stack_switch_call` 中 `movl %2, 4(%0)` 将 `arg` 写到 `sp+4` 位置，同样需要注意对齐。

---

### ⚠️ 坑点 2：`setjmp`/`longjmp` 的堆栈检查（`_FORTIFY_SOURCE`）

**问题：** glibc 在开启 `_FORTIFY_SOURCE` 时，`longjmp` 会检查目标堆栈是否合法，防止栈溢出攻击（`__longjmp_chk`）。切换堆栈后调用 `longjmp` 会被判定为"stack smashing"并 abort。

**现象：** 程序输出 `*** stack smashing detected ***` 或 `longjmp causes uninitialized stack frame` 后终止。

**解决：** Makefile 中已添加 `-U_FORTIFY_SOURCE`，确认 `CFLAGS` 中有此选项：
```makefile
CFLAGS += -U_FORTIFY_SOURCE
```

---

### ⚠️ 坑点 3：`CO_NEW` 协程的特殊处理

**问题：** `CO_NEW` 状态的协程没有调用过 `setjmp`，其 `context` 字段是未初始化的垃圾值，**不能对其调用 `longjmp`**。

**必须区分两种情况：**

```c
if (next->status == CO_NEW) {
    // 必须用 stack_switch_call 切换堆栈并跳转
    next->status = CO_RUNNING;
    stack_switch_call(sp, co_entry, (uintptr_t)next);
} else {
    // CO_RUNNING，直接恢复现场
    longjmp(next->context, 1);
}
```

---

### ⚠️ 坑点 4：`co_yield` 中 `current` 的更新时机

**问题：** `setjmp` 保存的是当时的 `%rsp`，如果在 `setjmp` 之后修改了 `current` 再调用 `longjmp` 到另一个协程，必须确保 `current` 在 `longjmp` 之前已经正确指向新协程，否则新协程执行时 `current` 指向错误。

**正确顺序：**
```c
int val = setjmp(current->context);  // 1. 保存当前协程现场
if (val == 0) {
    struct co *next = choose_next();  // 2. 选择下一个
    current = next;                   // 3. 更新 current（必须在切换前）
    // 4. 切换到 next
}
```

---

### ⚠️ 坑点 5：`co_yield` 的"自我切换"

**问题：** `choose_next()` 随机选择时**可以选到当前协程自身**（题目要求）。若选到自身：

- `CO_NEW`：当前协程不可能是 `CO_NEW`（它正在运行），不会有问题
- `CO_RUNNING`：调用 `longjmp(current->context, 1)` 恢复刚刚 `setjmp` 保存的现场，等价于 `co_yield` 直接返回

这是合法的，代码不需要特殊处理。

---

### ⚠️ 坑点 6：协程资源回收的时机

**问题：** 协程 `func()` 返回后，执行流仍在协程自己的堆栈上。此时**不能立即 `free(co)`**，因为当前 `%rsp` 还指向这块内存！

**正确做法：**
1. `func()` 返回后，将状态设为 `CO_DEAD`，唤醒 waiter
2. 调用 `co_yield()` 切换到其他协程（此时执行流离开了该堆栈）
3. 在 `co_wait` 中，等到协程死亡后再 `free`

```c
// co_entry wrapper 中
co->func(co->arg);
co->status = CO_DEAD;
if (co->waiter) co->waiter->status = CO_RUNNING;
co_yield();   // 切走，永不回来（因为 CO_DEAD 不会被调度）
assert(0);    // 不可达
```

```c
// co_wait 中
if (co->status != CO_DEAD)
    co_yield();
free(co);  // 此时执行流不在 co 的堆栈上，安全释放
```

---

### ⚠️ 坑点 7：`co_wait` 的两种情况

`co_wait` 被调用时，目标协程可能处于以下两种状态：

| 情况 | 目标协程状态 | 处理方式 |
|------|------------|---------|
| 协程已结束 | `CO_DEAD` | 直接回收，`co_wait` 立即返回 |
| 协程未结束 | `CO_NEW` 或 `CO_RUNNING` | 设置 waiter，进入 `CO_WAITING`，循环 `co_yield` |

**坑：** 不要假设协程一定还在运行——它可能在 `co_wait` 被调用前就已经结束了。

---

### ⚠️ 坑点 8：`CO_WAITING` 状态的协程不可被调度

**问题：** 调用 `co_wait` 的协程进入 `CO_WAITING` 状态，必须从调度器的可运行集合中排除，否则会被误调度，导致 `co_wait` 提前返回。

```c
// choose_next 中：只选 CO_NEW 或 CO_RUNNING
if (co_list[i]->status == CO_NEW || co_list[i]->status == CO_RUNNING) {
    runnable[n++] = co_list[i];
}
// CO_WAITING 和 CO_DEAD 均被排除
```

---

### ⚠️ 坑点 9：x86-32 的函数调用约定差异

x86-32 中参数通过堆栈传递（不是寄存器），`stack_switch_call` 的 32 位版本：

```c
"movl %0, %%esp; movl %2, 4(%0); jmp *%1"
: : "b"((uintptr_t)sp - 8), "d"(entry), "a"(arg) : "memory"
```

- `sp - 8`：留出 4 字节给返回地址（伪造），4 字节给参数 `arg`
- `movl %2, 4(%0)`：将 `arg` 写入 `sp - 8 + 4 = sp - 4` 处，作为函数第一个参数

对齐要求：x86-32 的 ABI 要求进入函数时 `%esp % 16 == 12`（即减去 4 字节返回地址后对齐）。

---

### ⚠️ 坑点 10：`main` 协程的初始化

**问题：** `main` 函数的执行天然是一个协程，需要在调度器中登记，且其 `context` 会在第一次 `co_yield` 时被 `setjmp` 初始化。

**注意：** `main_co` 不能使用 `malloc` 分配（否则在构造函数之前可能未初始化），推荐静态分配：

```c
static struct co main_co;  // BSS 段，自动初始化为 0
```

---

### ⚠️ 坑点 11：禁止多余输出

**问题：** Online Judge 会精确匹配输出，任何调试 `printf` 都会导致 Wrong Answer。

**推荐做法：** 使用宏控制调试输出：

```c
#ifdef LOCAL_MACHINE
  #define debug(...) fprintf(stderr, __VA_ARGS__)
#else
  #define debug(...)
#endif
```

编译时加 `-DLOCAL_MACHINE` 开启，提交时不加（调试输出消失）。

---

### ⚠️ 坑点 12：协程数量上限与内存泄漏

题目保证最多 128 个协程同时存在，但可能创建大量"执行-等待-销毁"循环。**必须在 `co_wait` 返回前 `free` 协程资源**，否则长期运行会触发 Memory Limit Exceeded。

```c
void co_wait(struct co *co) {
    if(co->status == CO_DEAD){
        remove(co);
        free(co);
        return;
    }
    current->status = CO_WAITING;
    co->waiter = current;
    co_yield();
    assert(co->status == CO_DEAD);
    remove(co);
    free(co);
}
```

---

## 7. 调试指南

### 7.1 环境配置

```bash
# 设置动态库搜索路径（一次设置，当前 shell 永久生效）
export LD_LIBRARY_PATH=$(pwd)/..   # 或实际 .so 文件所在目录

# 直接运行
./libco-test-64

# GDB 调试
gdb ./libco-test-64
(gdb) run
(gdb) bt       # 查看调用栈
(gdb) info reg # 查看所有寄存器
```

### 7.2 观察 `setjmp`/`longjmp` 的行为

```c
// 简单测试程序
#include <stdio.h>
#include <setjmp.h>

int main() {
    jmp_buf buf;
    int n = 0;
    int val = setjmp(buf);
    printf("setjmp returned %d, n = %d\n", val, n);
    if (n < 3) {
        n++;
        longjmp(buf, n);  // 第二个参数作为 setjmp 的返回值（不能为 0）
    }
}
```

在 gdb 中观察 `setjmp` 保存了哪些寄存器（`jmp_buf` 的内容）。

### 7.3 常见错误与排查

| 错误现象 | 可能原因 | 排查方法 |
|---------|---------|---------|
| Segfault 在 `movaps` 指令 | 堆栈未 16 字节对齐 | `gdb` 查看崩溃时 `%rsp` 的值 |
| `stack smashing detected` | `_FORTIFY_SOURCE` 未禁用 | 检查 `CFLAGS` 含 `-U_FORTIFY_SOURCE` |
| 协程从不切换 | `CO_WAITING` 未排除在调度外 | 打印每次调度时的可运行列表 |
| 输出乱序或数字错误 | `current` 更新时机错误 | 在 `co_yield` 各关键点打印 `current->name` |
| 程序卡死（死循环） | 只剩 `CO_WAITING` 协程，无可运行者 | 检查调度器断言 |
| Memory Limit Exceeded | `co_wait` 未 `free` | Valgrind 检测内存泄漏 |

### 7.4 Valgrind 内存检测

```bash
LD_LIBRARY_PATH=.. valgrind --leak-check=full ./libco-test-64
```

---

## 8. 正确性验证

### 8.1 本地测试

```bash
make test
# 期望输出：
# Easy 测试：打印 X/Y-0 到 X/Y-199（字母随机，数字递增）
# Hard 测试：打印 libco-200 到 libco-399
```

### 8.2 Easy 测试逻辑

- 创建 2 个协程，各循环 100 次
- 每次循环打印 `协程名[全局计数器]`，然后 `g_count++`
- 期望：字母（`a`/`b`）随机，数字 0~199 严格递增（无并发冲突）

### 8.3 Hard 测试逻辑（生产者-消费者）

- 2 个生产者：插入数据后 `co_yield()`
- 2 个消费者：检查队列非空则取出，无论如何都 `co_yield()`
- 期望：正确的生产者-消费者语义，编号 200~399 有序

---

## 9. 参考实现框架

以下是整合所有要点的代码框架：

```c
#include "co.h"
#include <stdlib.h>
#include <setjmp.h>
#include <stdint.h>
#include <assert.h>
#include <time.h>

#define STACK_SIZE 65536
#define MAX_CO 128

enum co_status{
    CO_NEW = 1,
    CO_RUNNING,
    CO_WAITING,
    CO_DEAD,
};

struct co {
    const char *name;
    void (*func)(void *);
    void *arg;

    enum co_status status;
    struct co* waiter;
    jmp_buf context;
    uint8_t STACK[STACK_SIZE];
};

struct co* current = NULL;
struct co* allCo[MAX_CO];
struct co MAIN;
int cnt = 0;

static void add(struct co* newCo){
    assert(cnt < MAX_CO);
    allCo[cnt++] = newCo;
}

static void remove(struct co* nowCo){
    for(int i = 0; i < cnt; i++){
        if(allCo[i] == nowCo){
            allCo[i] = allCo[cnt - 1];
            cnt--;
            return;
        }
    }
}

__attribute__((constructor)) static void init(){
    MAIN.name = "main";
    MAIN.arg = NULL;
    MAIN.func = NULL;
    MAIN.status = CO_RUNNING;
    MAIN.waiter = NULL;
    current = &MAIN;
    add(current);
    srand(time(NULL));
}

static inline void stack_switch_call(void *sp, void *entry, uintptr_t arg) {
    asm volatile (
#if __x86_64__
        "movq %0, %%rsp; movq %2, %%rdi; jmp *%1"
        :
        : "b"((uintptr_t)sp), "d"(entry), "a"(arg)
        : "memory"
#else
        "movl %0, %%esp; movl %2, 4(%0); jmp *%1"
        :
        : "b"((uintptr_t)sp - 8), "d"(entry), "a"(arg)
        : "memory"
#endif
    );
}

static void co_wrapper(uintptr_t ptr){
    struct co* nowCo = (struct co*)ptr;
    nowCo->func(nowCo->arg);
    nowCo->status = CO_DEAD;
    if(nowCo->waiter) nowCo->waiter->status = CO_RUNNING;
    co_yield();
    assert(0);
} 

static struct co* getNextCo(){
    struct co* avaliable[MAX_CO];
    int num = 0;
    for(int i = 0; i < cnt; i++)
        if(allCo[i]->status == CO_RUNNING || allCo[i]->status == CO_NEW) avaliable[num++] = allCo[i];
    return avaliable[rand() % num];
}//getNextCo must be random ortherwise cause hunger!

struct co* co_start(const char *name, void (*func)(void *), void *arg) {
    struct co* newCo = (struct co*)malloc(sizeof(struct co));
    assert(newCo != NULL);
    newCo->name = name;
    newCo->func = func;
    newCo->arg = arg;
    newCo->status = CO_NEW;
    newCo->waiter = NULL;
    add(newCo);
    return newCo;
}

void co_wait(struct co* co) {
    if(co->status == CO_DEAD){
        remove(co);
        free(co);
        return;
    }
    current->status = CO_WAITING;
    co->waiter = current;
    co_yield();
    assert(co->status == CO_DEAD);
    remove(co);
    free(co);
}

void co_yield() {
    int val = setjmp(current->context);
    if(val == 0){
        struct co* nxt = getNextCo();
        assert(nxt != NULL);
        current = nxt;
        if(nxt->status == CO_NEW){
            nxt->status = CO_RUNNING;
            uintptr_t sp = (uintptr_t)(nxt->STACK + STACK_SIZE);
#if __x86_64__
            sp &= ~0xFULL;
            sp -= 8;
#endif
            stack_switch_call((void*)sp, co_wrapper, (uintptr_t)nxt);
        }
        else longjmp(nxt->context, 1);
    }else{
        return;
    }
}
```

---

## 附录：关键知识点速查

### x86-64 调用约定（System V ABI）

| 寄存器 | 类型 | 说明 |
|--------|------|------|
| `%rdi, %rsi, %rdx, %rcx, %r8, %r9` | caller-saved | 前 6 个整型参数 |
| `%rax` | caller-saved | 返回值 |
| `%r10, %r11` | caller-saved | 临时寄存器 |
| `%rbx, %rbp, %r12–%r15` | **callee-saved** | 被调函数必须保存/恢复 |
| `%rsp` | 特殊 | 栈指针，callee-saved |

`setjmp` 保存的正是 callee-saved 寄存器（`%rbx, %rbp, %r12–%r15, %rsp, %rip`）。

### `setjmp`/`longjmp` 语义

```c
int setjmp(jmp_buf env);
// 首次调用：保存寄存器现场到 env，返回 0
// 被 longjmp 触发：返回 longjmp 的第二个参数（非零）

void longjmp(jmp_buf env, int val);
// 恢复 env 中保存的寄存器现场
// val 不能为 0（若传 0，setjmp 接收到的是 1）
```

### 堆栈生长方向

x86 堆栈**从高地址向低地址生长**：

```
高地址  ┌──────────────┐  ← stack + STACK_SIZE（堆栈顶，%rsp 初始值）
       │   局部变量    │
       │   返回地址    │
       │     ...      │
低地址  └──────────────┘  ← stack（堆栈底）
```

因此 `stack_switch_call` 传入的 `sp` 应指向 `stack + STACK_SIZE`（高地址端）。
