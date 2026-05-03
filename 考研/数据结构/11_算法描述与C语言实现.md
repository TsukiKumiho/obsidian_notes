## 408 数据结构 | 算法描述与 C 语言关键实现（完整注释版）

> 按章节排序，覆盖全书核心算法的描述和 C 语言实现模板。每段代码均提供逐行注释，说明逻辑、参数含义以及边界条件。

---

### 一、线性表

#### 1.1 顺序表 — 插入

**算法描述**：将第 $i$ 个位置及之后的元素整体后移一位，新元素填入位置 $i$，表长 +1。若插入位置超出范围或表满则失败。

```c
// ==================== 顺序表结构定义 ====================
#define MaxSize 100          // 顺序表最大容量
typedef struct {
    int data[MaxSize];       // 存储元素的数组（静态分配）
    int length;              // 当前表长（已存元素个数）
} SqList;

/*
 * 顺序表插入：在第 i 个位置（位序，1-based）插入元素 e
 * 参数：L -- 顺序表指针；i -- 插入位序；e -- 被插入元素值
 * 返回：1=成功，0=失败（位置非法或表满）
 * 时间复杂度：O(n)
 */
int ListInsert(SqList *L, int i, int e) {
    // 边界检查 1：位序 i 须在 [1, length+1] 内
    if (i < 1 || i > L->length + 1) return 0;
    // 边界检查 2：表满则无法插入
    if (L->length >= MaxSize) return 0;

    // 将 data[i-1] 到 data[length-1] 整体后移一位
    // 后移必须从最后一个元素开始，否则会覆盖未搬走的数据
    for (int j = L->length; j >= i; j--)
        L->data[j] = L->data[j - 1];     // data[j-1] 搬到 data[j]

    // 填入新元素到位序 i（下标 i-1）
    L->data[i - 1] = e;
    L->length++;                          // 表长加 1
    return 1;
}
```

#### 1.2 顺序表 — 删除

**算法描述**：将第 $i$ 个位置之后的元素整体前移一位，表长 -1。被删元素通过指针参数返回。

```c
/*
 * 顺序表删除：删除第 i 个位置（位序，1-based）的元素
 * 参数：L -- 顺序表指针；i -- 删除位序；e -- 输出被删元素值
 * 返回：1=成功，0=失败（位置非法或空表）
 * 时间复杂度：O(n)
 */
int ListDelete(SqList *L, int i, int *e) {
    // 位序 i 必须在 [1, length] 内（不能删不存在的元素）
    if (i < 1 || i > L->length) return 0;

    // 取出被删元素值，通过指针返回
    *e = L->data[i - 1];

    // 将 data[i] 到 data[length-1] 整体前移一位
    // 前移必须从被删位置的下一个开始，从前向后进行
    for (int j = i; j < L->length; j++)
        L->data[j - 1] = L->data[j];     // data[j] 搬到 data[j-1]

    L->length--;                          // 表长减 1
    return 1;
}
```

#### 1.3 顺序表 — 按值查找

**算法描述**：从第一个元素开始依次比较，找到则返回位序（1-based），找不到返回 0。

```c
/*
 * 顺序表按值查找：查找第一个值为 e 的元素
 * 参数：L -- 顺序表（传值即可）；e -- 目标值
 * 返回：位序(1-based)，0 表示未找到
 * 时间复杂度：O(n)
 */
int LocateElem(SqList L, int e) {
    for (int i = 0; i < L.length; i++)
        if (L.data[i] == e)
            return i + 1;                // 下标 i 对应位序 i+1
    return 0;                            // 遍历完未找到
}
```

#### 1.4 单链表 — 定义与头插法建表

```c
// ==================== 单链表结点定义 ====================
typedef struct LNode {
    int data;                  // 数据域
    struct LNode *next;        // 指针域，指向后继结点
} LNode, *LinkList;            // LinkList 等价于 LNode*（指向头结点）

/*
 * 头插法建立单链表：每次新结点插入到头结点之后（头插 = 逆序）
 * 输入以 9999 结束
 * 返回：带哨兵头结点的链表
 * 时间复杂度：O(n)
 */
LinkList List_HeadInsert(LinkList L) {
    // 分配头结点（哨兵结点），不存数据，仅用于统一插入删除逻辑
    L = (LinkList)malloc(sizeof(LNode));
    L->next = NULL;                      // 初始化为空表

    int x;
    // 循环读入数据，直到输入 9999 终止
    while (scanf("%d", &x) && x != 9999) {
        LNode *s = (LNode*)malloc(sizeof(LNode));  // 创建新结点
        s->data = x;
        s->next = L->next;               // ① s 的后继 = 原首元结点
        L->next = s;                     // ② 头结点的后继 = 新结点 s
    }
    return L;
}
```

#### 1.5 单链表 — 尾插法建表

**算法描述**：每次新结点插入链表尾部，需要尾指针 `r` 始终指向最后一个结点。

```c
/*
 * 尾插法建立单链表：每次新结点插入到尾结点之后（尾插 = 原序）
 * 输入以 9999 结束
 * 返回：带哨兵头结点的链表
 * 时间复杂度：O(n)
 */
LinkList List_TailInsert(LinkList L) {
    L = (LinkList)malloc(sizeof(LNode)); // 分配头结点
    LNode *r = L;                        // r 始终指向当前尾结点（初始 = 头结点）

    int x;
    while (scanf("%d", &x) && x != 9999) {
        LNode *s = (LNode*)malloc(sizeof(LNode));  // 创建新结点
        s->data = x;
        r->next = s;                     // ① 原尾结点的 next 指向新结点
        r = s;                           // ② r 更新为新尾结点
    }
    r->next = NULL;                      // ③ 尾结点 next 置空（必须！）
    return L;
}
```

#### 1.6 单链表 — 按位插入

**算法描述**：先找到第 $i-1$ 个结点，在其后插入新结点。

```c
/*
 * 单链表按位插入：在第 i 个位置（位序，1-based）插入元素 e
 * 即插入后新结点成为第 i 个元素（e 在新结点中）
 * 参数：L -- 带头结点的单链表；i -- 位序；e -- 插入元素值
 * 返回：1=成功，0=失败（i 非法）
 * 时间复杂度：O(n)（查找前驱需要遍历）
 */
int ListInsert(LinkList L, int i, int e) {
    LNode *p = L;                        // p 指向头结点，j 记录 p 是第几个结点（头结点算第 0 个）
    int j = 0;

    // 循环找到第 i-1 个结点（插入位置的前驱）
    while (p && j < i - 1) {
        p = p->next;
        j++;
    }

    // 如果 p 为空或 j 越过目标位置，说明 i 不合法
    if (!p || j > i - 1) return 0;

    // 在 p 之后插入新结点
    LNode *s = (LNode*)malloc(sizeof(LNode));
    s->data = e;
    s->next = p->next;                   // ① 新结点的 next = p 的原后继
    p->next = s;                         // ② p 的 next 指向新结点（顺序不能反！）
    return 1;
}
```

#### 1.7 单链表 — 按位删除

**算法描述**：找到第 $i-1$ 个结点，删除其后继。

```c
/*
 * 单链表按位删除：删除第 i 个结点（位序，1-based）
 * 参数：L -- 带头结点的单链表；i -- 位序；e -- 输出被删元素值
 * 返回：1=成功，0=失败（i 非法或空表）
 * 时间复杂度：O(n)
 */
int ListDelete(LinkList L, int i, int *e) {
    LNode *p = L;
    int j = 0;

    // 找第 i-1 个结点（注意检查 p->next 不为 NULL，保证第 i 个存在）
    while (p->next && j < i - 1) {
        p = p->next;
        j++;
    }

    // p->next == NULL 说明不存在第 i 个结点
    if (!(p->next) || j > i - 1) return 0;

    // 执行删除
    LNode *q = p->next;                  // q 指向被删结点
    *e = q->data;                        // 通过指针返回被删元素值
    p->next = q->next;                   // 从链中断开 q
    free(q);                             // 释放被删结点内存（408 考试中常要求）
    return 1;
}
```

#### 1.8 单链表 — 原地逆置

**算法描述**：摘下头结点后的每个结点，用头插法插入到头结点之后。

```c
/*
 * 单链表原地逆置：将链表顺序反转，空间复��度 O(1)
 * 思路：每次摘下原链表当前第一个结点，头插到新链表（仍用原头结点）
 * 时间复杂度：O(n)，空间复杂度：O(1)
 */
void Reverse(LinkList L) {
    // p 指向当前待摘下的结点（从首元结点开始）
    LNode *p = L->next, *q;              // q 用于暂存 p 的后继，防止断链

    L->next = NULL;                      // 头结点 next 置空，L 变为空表（新链表）

    while (p) {
        q = p->next;                     // ① 暂存 p 的后继（因为 p 要被摘走）
        p->next = L->next;               // ② p 头插进新链表：p.next = 头.next
        L->next = p;                     // ③ 头.next = p
        p = q;                           // ④ p 移动到下一个待处理结点
    }
}
```

#### 1.9 单链表 — 合并两个有序链表

**算法描述**：归并思想，两两比较，取较小者链入新表，处理剩余段。

```c
/*
 * 合并两个有序递增单链表为一个有序递增单链表
 * 思路：类似归并排序的合并阶段，两两比较取较小结点链入
 * 参数：A, B -- 两个带头结点的有序链表
 * 返回：合并后的链表 C（复用 A 的头结点，释放 B 的头结点）
 * 时间复杂度：O(n+m)，空间复杂度：O(1)
 */
LinkList Merge(LinkList A, LinkList B) {
    LNode *p = A->next, *q = B->next;    // p, q 分别指向两表的首元结点
    LinkList C = A;                      // 复用 A 的头结点作为结果表 C 的头
    LNode *r = C;                        // r 是 C 的尾指针，用于尾插

    // 两路归并：取两表中较小结点链入 C 的尾部
    while (p && q) {
        if (p->data <= q->data) {        // 使用 <= 保证稳定性（相等时 A 的先入）
            r->next = p;                 // p 链入 C
            p = p->next;                 // p 后移
        } else {
            r->next = q;                 // q 链入 C
            q = q->next;                 // q 后移
        }
        r = r->next;                     // r 始终指向 C 的尾结点
    }

    // 处理剩余部分：至多有一个链表还有剩余
    r->next = p ? p : q;                 // 直接链接剩余段
    free(B);                             // 释放 B 的头结点（B 的结点已被借用）
    return C;
}
```

#### 1.10 单链表 — 查找倒数第 $k$ 个结点

**算法描述**：快慢指针。快指针先走 $k$ 步，然后两指针同步走，快指针到末尾时，慢指针指向倒数第 $k$ 个。

```c
/*
 * 查找单链表中倒数第 k 个结点（快慢指针法）
 * 思路：fast 先走 k 步，然后 fast/slow 同步走，
 *       fast 走到 NULL 时，slow 恰好指向倒数第 k 个
 * 参数：L -- 带头结点的单链表；k -- 倒数的位置
 * 返回：目标结点指针，若 k 非法则返回 NULL
 * 时间复杂度：O(n)，空间复杂度：O(1)
 */
LNode* FindKthToTail(LinkList L, int k) {
    LNode *fast = L->next, *slow = L->next;   // 都从首元结点出发

    // 第一阶段：fast 先走 k 步
    for (int i = 0; i < k; i++) {
        if (!fast) return NULL;               // 链表长度不足 k，返回 NULL
        fast = fast->next;
    }

    // 第二阶段：fast 和 slow 同步走，fast 走到 NULL 时 slow 即目标
    while (fast) {
        slow = slow->next;
        fast = fast->next;
    }
    return slow;
}
```

---

### 二、栈与队列

#### 2.1 顺序栈

**算法描述**：用数组实现，栈顶指针 `top` 指向栈顶元素位置（初值 -1 表示空）。入栈先加 top 再存值，出栈先取值再减 top。

```c
// ==================== 顺序栈定义 ====================
#define MaxSize 50            // 栈的最大容量
typedef struct {
    int data[MaxSize];        // 存放栈元素的数组
    int top;                  // 栈顶指针，指向当前栈顶元素的下标
                              // top = -1 表示空栈
} SqStack;

/*
 * 初始化栈：栈顶指针置 -1（空栈）
 */
void InitStack(SqStack *S) {
    S->top = -1;
}

/*
 * 判空：top == -1 时为真
 */
int StackEmpty(SqStack S) {
    return S.top == -1;
}

/*
 * 入栈（push）：元素 e 入栈
 * 返回：1=成功，0=栈满失败
 * 时间复杂度：O(1)
 */
int Push(SqStack *S, int e) {
    // 栈满判断：top 指向数组最后一个位置时不可再入栈
    if (S->top == MaxSize - 1) return 0;
    // 先移动 top 再存入：++top 后下标为新栈顶位置
    S->data[++(S->top)] = e;
    return 1;
}

/*
 * 出栈（pop）：弹出栈顶元素，值通过指针 e 返回
 * 返回：1=成功，0=栈空失败
 * 时间复杂度：O(1)
 */
int Pop(SqStack *S, int *e) {
    // 栈空判断：不能对空栈执行出栈
    if (StackEmpty(*S)) return 0;
    // 先取栈顶值，再 top 下移：top-- 返回原值
    *e = S->data[(S->top)--];
    return 1;
}
```

#### 2.2 链栈

**算法描述**：用单链表实现，栈顶在链表头（头结点后第一个结点）。入栈 = 头插，出栈 = 头删。

```c
// ==================== 链栈结点定义 ====================
typedef struct StackNode {
    int data;                    // 数据域
    struct StackNode *next;      // 指针域
} StackNode, *LinkStack;         // LinkStack 指向链栈的头结点

/*
 * 入栈（push）：头插法，时间复杂度 O(1)
 * 参数：S -- 带头结点的链栈；e -- 入栈元素
 * 注意：链栈不判满（除非内存耗尽）
 */
void Push(LinkStack S, int e) {
    StackNode *p = (StackNode*)malloc(sizeof(StackNode));
    p->data = e;
    p->next = S->next;           // ① 新结点 next 指向原首元结点（原栈顶）
    S->next = p;                 // ② 头结点 next 指向新结点（新栈顶）
}

/*
 * 出栈（pop）：删除头结点后的第一个结点（栈顶）
 * 参数：S -- 带头结点的链栈；e -- 输出出栈元素值
 * 返回：1=成功，0=栈空失败
 * 时间复杂度：O(1)
 */
int Pop(LinkStack S, int *e) {
    // 空栈判断：头结点 next 为 NULL
    if (!S->next) return 0;

    StackNode *p = S->next;      // p 指向栈顶结点（待删除）
    *e = p->data;                // 取出数据
    S->next = p->next;           // 头结点 next 跳过 p
    free(p);                     // 释放被删结点
    return 1;
}
```

#### 2.3 循环队列

**算法描述**：用数组实现，首尾逻辑相连。牺牲一个存储单元区分队空（`front==rear`）与队满（`(rear+1)%MaxSize==front`）。

```c
// ==================== 循环队列定义 ====================
#define MaxSize 50
typedef struct {
    int data[MaxSize];           // 存放队列元素的数组
    int front;                   // 队头指针：指向队头元素位置
    int rear;                    // 队尾指针：指向队尾元素的下一个空位
} SqQueue;

/*
 * 初始化：front 和 rear 都置 0，表示空
 */
void InitQueue(SqQueue *Q) {
    Q->front = Q->rear = 0;
}

/*
 * 判空：front == rear 表示队列为空
 * 注意：不能以此判断"队满"，因为队满时也是 front == rear
 *       此处采用"牺牲一个单元"的方案，队满时有另外的条件
 */
int QueueEmpty(SqQueue Q) {
    return Q.front == Q.rear;
}

/*
 * 入队：元素 e 加入队尾
 * 返回：1=成功，0=队满失败
 * 时间复杂度：O(1)
 */
int EnQueue(SqQueue *Q, int e) {
    // 队满判断：(rear+1) % MaxSize == front
    // 牺牲一个存储单元，使"队满"与"队空"条件不同
    if ((Q->rear + 1) % MaxSize == Q->front) return 0;

    Q->data[Q->rear] = e;                      // 元素存入当前 rear 位置
    Q->rear = (Q->rear + 1) % MaxSize;          // rear 循环后移
    return 1;
}

/*
 * 出队：队头元素出队，值通过指针 e 返回
 * 返回：1=成功，0=队空失败
 * 时间复杂度：O(1)
 */
int DeQueue(SqQueue *Q, int *e) {
    if (QueueEmpty(*Q)) return 0;
    *e = Q->data[Q->front];                    // 取出队头元素
    Q->front = (Q->front + 1) % MaxSize;       // front 循环后移
    return 1;
}

/*
 * 队列长度：利用取模运算处理循环
 * 加 MaxSize 防止 rear-front 为负
 */
int QueueLength(SqQueue Q) {
    return (Q.rear - Q.front + MaxSize) % MaxSize;
}
```

#### 2.4 链队列

**算法描述**：单链表 + 队头指针 + 队尾指针。入队在尾结点之后，出队从首元结点。

```c
// ==================== 链队列定义 ====================
typedef struct QNode {           // 链队列的结点
    int data;
    struct QNode *next;
} QNode;

typedef struct {                 // 链队列的控制结构（含头尾指针）
    QNode *front;                // 队头指针，指向头结点
    QNode *rear;                 // 队尾指针，指向尾结点
} LinkQueue;

/*
 * 初始化：创建头结点，front 和 rear 都指向它
 * 头结点不存数据，其 next 为 NULL 表示队列空
 */
void InitQueue(LinkQueue *Q) {
    Q->front = Q->rear = (QNode*)malloc(sizeof(QNode));
    Q->front->next = NULL;
}

/*
 * 入队：e 加入队尾，时间复杂度 O(1)
 * 不需要判满（除非内存耗尽）
 */
void EnQueue(LinkQueue *Q, int e) {
    QNode *p = (QNode*)malloc(sizeof(QNode));
    p->data = e;
    p->next = NULL;              // 新结点将成为队尾，next 必须为 NULL
    Q->rear->next = p;           // ① 原尾结点 next 指向新结点
    Q->rear = p;                 // ② rear 更新为新尾结点
}

/*
 * 出队：删除队头元素
 * 返回：1=成功，0=队空失败
 * 时间复杂度：O(1)
 * 注意：删除最后一个元素时需同时更新 rear！
 */
int DeQueue(LinkQueue *Q, int *e) {
    // 队空：front == rear（都指向头结点）
    if (Q->front == Q->rear) return 0;

    QNode *p = Q->front->next;   // p 指向首元结点（待删除）
    *e = p->data;
    Q->front->next = p->next;    // 头结点 next 跳过 p

    // 关键！若删除的是最后一个元素，需让 rear 指回头结点
    if (Q->rear == p)
        Q->rear = Q->front;

    free(p);
    return 1;
}
```

---

### 三、串 — 模式匹配

#### 3.1 朴素模式匹配 (BF)

**算法描述**：从主串每个位置开始，与模式串逐字符比较。失配时主串回退一位重新匹配。

```c
/*
 * 朴素模式匹配（Brute Force）
 * 参数：S -- 主串（下标从 0 开始）；T -- 模式串
 * 返回：匹配成功的起始下标，-1 表示未找到
 * 时间复杂度：最坏 O(nm)，n=|S|, m=|T|
 */
int BF(char *S, char *T) {
    int i = 0, j = 0;            // i 为主串下标，j 为模式串下标

    // 当两个串都未到字符串结尾时循环
    while (S[i] != '\0' && T[j] != '\0') {
        if (S[i] == T[j]) {      // 当前字符匹配成功
            i++;
            j++;
        } else {                 // 失配：主串回到"本轮起始位置+1"，模式串回到开头
            i = i - j + 1;       // 回退：i 从本轮起始的 i-j 移到 i-j+1
            j = 0;               // 模式串重置
        }
    }

    // 若 j 走到了 T 的末尾，说明匹配成功
    // i-j 即匹配开始位置（主串中）
    return (T[j] == '\0') ? i - j : -1;
}
```

#### 3.2 KMP — 求 `next` 数组

**算法描述**：`next[j]` = 模式串前 $j-1$ 个字符中最长相等前后缀的长度 + 1（教材常见定义，下标从 1 起）。

```c
/*
 * 求 KMP 的 next 数组（教材常见定义：下标从 1 开始）
 * next[j] 含义：模式串第 j 位失配时，下一步比较 T[next[j]]
 * 规定：next[1] = 0（表示 j 退到 0 时 i 应后移一位）
 *
 * 递推思想：
 *  设 next[j] = k，表示 T[1..k-1] == T[j-k+1..j-1]，长度为 k-1
 *  若 T[k] == T[j]，则 next[j+1] = k+1
 *  若 T[k] != T[j]，则 k = next[k] 继续回溯
 *
 * 参数：T -- 模式串（下标从 1 开始存放，T[0] 不用）
 *       next[] -- 输出数组
 * 时间复杂度：O(m)
 */
void GetNext(char *T, int next[]) {
    int i = 1, j = 0;            // i：当前模式串下标；j：当前最长相等前后缀长度
    next[1] = 0;                 // 第 1 个字符失配，规定 next[1]=0

    // 遍历模式串的其余位置
    while (i < strlen(T + 1)) {  // T+1 跳过 T[0]
        if (j == 0 || T[i] == T[j]) {
            // j==0 或当前字符匹配，i,j 同步后移
            i++;
            j++;
            next[i] = j;         // next[i] = 当前最长相等前后缀长度
        } else {
            j = next[j];         // 失配：j 回溯到 next[j]
        }
    }
}
```

#### 3.3 KMP — 模式匹配

**算法描述**：主串指针 `i` 不回退，模式串指针 `j` 失配时按 `next[j]` 跳转。

```c
/*
 * KMP 模式匹配（下标从 1 开始，字符串存储在 T[1..m]）
 * 参数：S -- 主串；T -- 模式串；next[] -- 已计算好的 next 数组
 * 返回：匹配位置（1-based），0 表示未找到
 * 时间复杂度：O(n+m)
 */
int KMP(char *S, char *T, int next[]) {
    int i = 1, j = 1;            // 下标从 1 开始

    while (i <= strlen(S + 1) && j <= strlen(T + 1)) {
        if (j == 0 || S[i] == T[j]) {
            // ① j==0：模式串退到头了，主串后移重新开始
            // ② 当前字符匹配：双双后移
            i++;
            j++;
        } else {
            j = next[j];         // 失配时模式串按 next 跳转，主串不回退！
        }
    }

    // 若 j 超出 T 长度，表示匹配成功
    return (j > strlen(T + 1)) ? i - (int)strlen(T + 1) : 0;
}
```

#### 3.4 KMP — 求 `nextval`（改进版）

```c
/*
 * 求 nextval（next 的改进版）
 * 改进逻辑：若 P[next[j]] == P[j]，则失配时跳转后必然再次失配
 *          此时直接跳过，取 nextval[next[j]]
 *
 * 参数：T -- 模式串；next[] -- 原始 next 数组；nextval[] -- 输出改进版
 */
void GetNextval(char *T, int next[], int nextval[]) {
    nextval[1] = 0;

    for (int j = 2; j <= strlen(T + 1); j++) {
        if (T[next[j]] == T[j])
            // 如果跳转到的字符和当前字符相同，必然再次失配
            nextval[j] = nextval[next[j]];   // 继续向前跳转
        else
            nextval[j] = next[j];            // 否则保持 next 原值
    }
}
```

---

### 四、树与二叉树

#### 4.1 二叉链表定义

```c
// ==================== 二叉链表定义（最常用存储方式）====================
typedef struct BiTNode {
    int data;                    // 数据域
    struct BiTNode *lchild;      // 左孩子指针
    struct BiTNode *rchild;      // 右孩子指针
} BiTNode, *BiTree;              // BiTree 是指向根结点的指针
```

#### 4.2 递归遍历（前序 / 中序 / 后序）

**算法描述**：若根非空，按"根-左-右"（前序）、"左-根-右"（中序）、"左-右-根"（后序）依次访问。

```c
/*
 * 递归遍历三个版本的时间复杂度均为 O(n)，空间复杂度 O(h)（递归栈深度）
 * h 为树高，最坏情况（单链树）退化为 O(n)
 */

// ---------- 前序遍历（Preorder: 根 → 左 → 右）----------
void PreOrder(BiTree T) {
    if (T) {                     // 递归边界：结点为空直接返回
        visit(T);                // ① 访问根结点
        PreOrder(T->lchild);     // ② 递归遍历左子树
        PreOrder(T->rchild);     // ③ 递归遍历右子树
    }
}

// ---------- 中序遍历（Inorder: 左 → 根 → 右）----------
void InOrder(BiTree T) {
    if (T) {
        InOrder(T->lchild);      // ① 递归遍历左子树
        visit(T);                // ② 访问根结点
        InOrder(T->rchild);      // ③ 递归遍历右子树
    }
}

// ---------- 后序遍历（Postorder: 左 → 右 → 根）----------
void PostOrder(BiTree T) {
    if (T) {
        PostOrder(T->lchild);    // ① 递归遍历左子树
        PostOrder(T->rchild);    // ② 递归遍历右子树
        visit(T);                // ③ 访问根结点
    }
}
```

#### 4.3 层序遍历

**算法描述**：用队列。根入队 → 循环：出队并访问 → 左孩子入队 → 右孩子入队。本质是图的 BFS。

```c
/*
 * 层序遍历（Level Order / BFS）
 * 时间复杂度：O(n)，空间复杂度：O(w)（w = 树的最大宽度）
 */
void LevelOrder(BiTree T) {
    BiTree Queue[100];           // 辅助队列，存放待访问的结点指针
    int front = 0, rear = 0;     // 队头、队尾下标

    if (T)
        Queue[rear++] = T;       // 根结点入队

    while (front < rear) {       // 队列非空
        BiTree p = Queue[front++];  // ① 队头结点出队
        visit(p);                    // ② 访问出队结点
        if (p->lchild)
            Queue[rear++] = p->lchild;  // ③ 左孩子入队
        if (p->rchild)
            Queue[rear++] = p->rchild;  // ④ 右孩子入队
    }
}
```

#### 4.4 中序非递归遍历（栈）

**算法描述**：① 沿左链入栈到底；② 出栈并访问；③ 转向右子树。用栈模拟递归调用过程。

```c
/*
 * 中序非递归遍历
 * 思路：一路向左走到头，沿途结点全部入栈；
 *       出栈访问一个结点后，转向其右子树重复。
 * 时间复杂度：O(n)（每个结点进栈出栈各一次）
 * 空间复杂度：O(h)，h 为树高
 */
void InOrder_NonRec(BiTree T) {
    BiTree Stack[100];           // 模拟递归栈
    int top = -1;                // 栈顶指针
    BiTree p = T;                // 工作指针

    while (p || top != -1) {     // 只要 p 不空 或 栈不空
        // ① 沿着左链一路到底，中途结点全部入栈
        while (p) {
            Stack[++top] = p;    // 入栈
            p = p->lchild;       // 向左走
        }

        // ② 左链走到底（p == NULL），从栈顶弹出并访问
        if (top != -1) {
            p = Stack[top--];    // 弹栈
            visit(p);            // 访问
            p = p->rchild;       // ③ 转向右子树（进入下一轮循环）
        }
    }
}
```

#### 4.5 前序非递归遍历（栈）

```c
/*
 * 前序非递归遍历
 * 思路：访问根 → 右孩子入栈 → 转向左孩子
 *       这样保证左子树优先于右子树被访问
 * 时间：O(n)，空间：O(h)
 */
void PreOrder_NonRec(BiTree T) {
    BiTree Stack[100];
    int top = -1;
    BiTree p = T;

    while (p || top != -1) {
        // 沿着左链走：每遇到一个结点先访问，再将右孩子入栈
        while (p) {
            visit(p);              // 访问当前结点（根）
            Stack[++top] = p->rchild;  // 右孩子入栈（之后处理）
            p = p->lchild;         // 转向左孩子（优先处理）
        }
        // 左链走到底，弹栈（取出之前保存的右孩子继续处理）
        if (top != -1)
            p = Stack[top--];
    }
}
```

#### 4.6 后序非递归遍历（双栈法）

```c
/*
 * 后序非递归遍历（双栈法）
 * 思路：S1 做"变形的根-右-左"遍历，S2 记录逆序
 *       S2 出栈即得到后序"左-右-根"
 * 时间：O(n)，空间：O(n)
 */
void PostOrder_NonRec(BiTree T) {
    BiTree S1[100], S2[100];     // 双栈
    int top1 = -1, top2 = -1;

    if (T)
        S1[++top1] = T;          // 根入 S1

    // S1 做类似"根-右-左"的遍历，结果按顺序存入 S2
    while (top1 != -1) {
        BiTree p = S1[top1--];   // S1 弹出一个结点
        S2[++top2] = p;          // 该结点入 S2

        // 注意：先左后右入 S1，则 S1 弹出顺序为"先右后左"
        if (p->lchild) S1[++top1] = p->lchild;
        if (p->rchild) S1[++top1] = p->rchild;
    }

    // S2 出栈顺序恰好是"左 → 右 → 根"，即后序遍历
    while (top2 != -1)
        visit(S2[top2--]);
}
```

#### 4.7 求二叉树高度（递归）

```c
/*
 * 求二叉树高度：递归计算左右子树高度，取较大者 +1
 * 递归边界：空树高度为 0
 * 时间复杂度：O(n)，空间复杂度：O(h)
 */
int BiTreeDepth(BiTree T) {
    if (!T) return 0;                            // 空树高度为 0

    int ld = BiTreeDepth(T->lchild);             // 左子树高度
    int rd = BiTreeDepth(T->rchild);             // 右子树高度

    return (ld > rd ? ld : rd) + 1;              // 较大者 +1（根结点自身）
}
```

#### 4.8 求二叉树结点数

```c
/*
 * 求二叉树结点总数：递归 = 左子树结点 + 右子树结点 + 1（根）
 * 时间复杂度：O(n)
 */
int NodeCount(BiTree T) {
    if (!T) return 0;                            // 空树无结点
    return NodeCount(T->lchild) + NodeCount(T->rchild) + 1;
}
```

#### 4.9 哈夫曼树构建

**算法描述**：$n$ 个叶结点 → 每次选两棵权值最小的树合并为新树（新树权 = 两子权和）→ $n-1$ 次后得到一棵哈夫曼树。

```c
// ==================== 哈夫曼树结点定义 ====================
typedef struct {
    int weight;                  // 权值
    int parent;                  // 双亲结点下标（0 表示无双亲）
    int lchild;                  // 左孩子下标（0 表示无左孩子）
    int rchild;                  // 右孩子下标（0 表示无右孩子）
} HTNode, *HuffmanTree;          // 下标从 1 开始，0 号单元弃用

/*
 * 构建哈夫曼树
 * 参数：HT -- 预分配了 2n 个单元的数组（下标 1..2n-1）；n -- 叶结点数
 * 时间复杂度：O(n^2)（朴素选最小），若用小根堆可优化至 O(n log n)
 */
void CreateHuffmanTree(HuffmanTree HT, int n) {
    int m = 2 * n - 1;           // 哈夫曼树总共有 2n-1 个结点（n 叶 + n-1 内）

    // ① 初始化所有结点：parent, lchild, rchild 均置 0
    for (int i = 1; i <= m; i++)
        HT[i].parent = HT[i].lchild = HT[i].rchild = 0;

    // ② 进行 n-1 次合并，构建内部结点
    for (int i = n + 1; i <= m; i++) {
        int s1, s2;              // 当前 parent=0 的结点中权值最小的两个下标
        // Select(HT, i - 1, &s1, &s2);   // 实现略：遍历找最小的两个
        HT[s1].parent = HT[s2].parent = i;   // 两个最小结点双亲指向 i
        HT[i].lchild = s1;                   // i 的左孩子为 s1
        HT[i].rchild = s2;                   // i 的右孩子为 s2
        HT[i].weight = HT[s1].weight + HT[s2].weight;  // 新权 = 两子权和
    }
}
```

#### 4.10 并查集

**算法描述**：`find` 找根 + 路径压缩，`union` 按秩合并。

```c
// ==================== 并查集 ====================
int father[1000];                // father[i] = i 的父结点（i 自身是根时 father[i]=i）
int rank[1000];                  // rank[i] = 以 i 为根的树的秩（近似高度）

/*
 * 初始化：每个元素自成一个集合
 * 时间复杂度：O(n)
 */
void MakeSet(int n) {
    for (int i = 0; i < n; i++) {
        father[i] = i;           // 每个结点的父亲初始为自己
        rank[i] = 0;             // 初值为 0
    }
}

/*
 * Find 操作：查找 x 所在集合的代表元（根），并完成路径压缩
 * 路径压缩：查找过程中将经过的结点直接挂在根下，加速后续查找
 * 时间复杂度：均摊 O(α(n)) ≈ O(1)
 */
int Find(int x) {
    if (father[x] != x)          // x 不是根
        father[x] = Find(father[x]);  // 递归找根并将 father[x] 改为根（路径压缩）
    return father[x];
}

/*
 * Union 操作：合并 x 和 y 所在的两个集合
 * 按秩合并：将秩（树高）较小的集合合并到秩较大的集合，避免树过高
 * 时间复杂度：均摊 O(α(n)) ≈ O(1)
 */
void Union(int x, int y) {
    int fx = Find(x), fy = Find(y);  // 分别找到 x 和 y 的根
    if (fx == fy) return;            // 已在同一集合，无需合并

    // 将秩小的根指向秩大的根
    if (rank[fx] > rank[fy])
        father[fy] = fx;             // fx 树高更大，fy 并入 fx
    else {
        father[fx] = fy;             // 否则 fx 并入 fy
        if (rank[fx] == rank[fy])    // 若两树等高，被并入的那棵树高度要 +1
            rank[fy]++;
    }
}
```

---

### 五、图

#### 5.1 存储结构 — 邻接矩阵

```c
#define MaxVertexNum 100           // 最大顶点数
typedef char VertexType;           // 顶点数据类型（C 语言中常用 char）

/*
 * 邻接矩阵存储：Edge[i][j] = 1 表示顶点 i 到 j 有边
 * 无向图的邻接矩阵是对称的，有向图一般不对称
 * 空间复杂度：O(|V|^2)，适合稠密图
 */
typedef struct {
    VertexType Vex[MaxVertexNum];            // 顶点表，存放各顶点信息
    int Edge[MaxVertexNum][MaxVertexNum];    // 邻接矩阵，存放边信息
    int vexnum;                              // 图的当前顶点数
    int arcnum;                              // 图的当前边（弧）数
} MGraph;
```

#### 5.2 存储结构 — 邻接表

```c
// ==================== 邻接表 ====================
// 边表结点：表示一条边/弧
typedef struct ArcNode {
    int adjvex;                  // 该弧所指向的顶点在顶点表中的下标
    struct ArcNode *next;        // 指向下一条边的指针
    int weight;                  // 边的权值（若为带权图）
} ArcNode;

// 顶点表结点：每个顶点对应一个链表头
typedef struct VNode {
    VertexType data;             // 顶点信息
    ArcNode *firstarc;           // 指向第一条依附于该顶点的边
} VNode, AdjList[MaxVertexNum];  // AdjList 是 VNode 数组的别名

// 图的邻接表表示
typedef struct {
    AdjList vertices;            // 邻接表（顶点数组 + 边链表）
    int vexnum;                  // 图的当前顶点数
    int arcnum;                  // 图的当前边数
} ALGraph;
// 空间复杂度：O(|V|+|E|)，适合稀疏图
```

#### 5.3 DFS（邻接表 + 递归）

**算法描述**：访问当前顶点 → 标记为已访问 → 对每个未访问的邻接点递归执行 DFS。

```c
// 访问标记数组，全局或传参均可
int visited[MaxVertexNum];

/*
 * DFS 核心递归函数（邻接表版）
 * 参数：G -- 图；v -- 当前访问的顶点下标
 * 时间复杂度：邻接表 O(|V|+|E|)
 */
void DFS(ALGraph G, int v) {
    visited[v] = 1;              // ① 标记当前顶点为已访问
    visit(v);                    // ② 访问当前顶点（输出/处理）

    // ③ 遍历 v 的所有邻接点
    for (ArcNode *p = G.vertices[v].firstarc; p; p = p->next) {
        if (!visited[p->adjvex])    // 若该邻接点未访问
            DFS(G, p->adjvex);      // 递归访问
    }
}

/*
 * DFS 遍历入口：对图中所有未访问顶点调用 DFS
 * 作用：处理非连通图（每个连通分量分别 DFS）
 */
void DFSTraverse(ALGraph G) {
    // 初始化访问标记数组
    for (int i = 0; i < G.vexnum; i++)
        visited[i] = 0;

    // 遍历所有顶点，对于未访问的顶点启动一次 DFS
    for (int i = 0; i < G.vexnum; i++)
        if (!visited[i])
            DFS(G, i);
}
```

#### 5.4 DFS（邻接矩阵 + 递归）

```c
/*
 * DFS（邻接矩阵版）
 * 时间复杂度：邻接矩阵 O(|V|^2)
 * 因为每次需扫描该顶点对应的整行来查找邻接点
 */
void DFS_M(MGraph G, int v) {
    visited[v] = 1;
    visit(v);

    // 检查顶点 v 与其他所有顶点是否有边
    for (int w = 0; w < G.vexnum; w++)
        if (G.Edge[v][w] && !visited[w])   // 有边且 w 未访问
            DFS_M(G, w);                   // 递归访问 w
}
```

#### 5.5 BFS（邻接表 + 队列）

**算法描述**：入队起点并标记 → 循环：出队访问 → 将所有未访问的邻接点入队并标记。

```c
/*
 * BFS（广度优先搜索，邻接表版）
 * 参数：G -- 图；v -- 起始顶点下标
 * 时间复杂度：邻接表 O(|V|+|E|)
 * 辅助结构：队列
 */
void BFS(ALGraph G, int v) {
    int Queue[MaxVertexNum];     // 辅助队列
    int front = 0, rear = 0;     // 队头队尾下标

    visited[v] = 1;              // 标记起点为已访问（入队前标记，防止重复入队）
    Queue[rear++] = v;           // 起点入队

    while (front < rear) {       // 队列非空
        int u = Queue[front++];  // ① 队头出队
        visit(u);                // ② 访问

        // ③ 遍历 u 的所有邻接点，未访问的入队
        for (ArcNode *p = G.vertices[u].firstarc; p; p = p->next) {
            if (!visited[p->adjvex]) {
                visited[p->adjvex] = 1;       // 入队前立即标记
                Queue[rear++] = p->adjvex;    // 入队
            }
        }
    }
}
```

#### 5.6 Prim 算法（邻接矩阵、适合稠密图）

**算法描述**：从一个顶点开始，每次选一条连接"已选顶点集合"与"未选顶点集合"的最小权边。

```c
/*
 * Prim 算法求最小生成树（邻接矩阵版）
 * lowcost[i]：顶点 i 到当前生成树的最短距离
 * adjvex[i]：lowcost[i] 对应的生成树内部顶点
 * 初始以顶点 0 为起点
 * 时间复杂度：O(|V|^2)，适合稠密图
 */
void Prim(MGraph G) {
    int lowcost[MaxVertexNum];   // lowcost[i] = i 到当前生成树的最短边权值
    int adjvex[MaxVertexNum];    // 该最短边在生成树中的那个顶点

    // ① 初始化：以顶点 0 为起始点
    for (int i = 1; i < G.vexnum; i++) {
        lowcost[i] = G.Edge[0][i];   // 初始时生成树只有顶点 0
        adjvex[i] = 0;               // 最短边另一端都是顶点 0
    }
    lowcost[0] = 0;                  // 标记顶点 0 已加入生成树（lowcost=0 表示已加入）

    // ② 循环 n-1 次，每次将一个顶点加入生成树
    for (int i = 1; i < G.vexnum; i++) {
        // 找出所有未加入树顶点中 lowcost 最小的
        int min = INT_MAX, k;        // k 记录最小边对应的顶点
        for (int j = 0; j < G.vexnum; j++)
            if (lowcost[j] != 0 && lowcost[j] < min) {  // lowcost!=0 表示未加入
                min = lowcost[j];
                k = j;
            }

        // 输出这条边（adjvex[k] 是已在树中的那端，k 是新加入的顶点）
        printf("(%d,%d)", adjvex[k], k);
        lowcost[k] = 0;              // 标记顶点 k 已加入生成树

        // ③ 更新 lowcost：新加入的顶点 k 可能提供更短路径
        for (int j = 0; j < G.vexnum; j++) {
            if (lowcost[j] != 0 && G.Edge[k][j] < lowcost[j]) {
                lowcost[j] = G.Edge[k][j];  // 更新为更短距离
                adjvex[j] = k;              // 更新生成树端点为 k
            }
        }
    }
}
```

#### 5.7 Kruskal 算法（并查集）

**算法描述**：所有边按权值升序排列，依次取边；若加入后不形成回路（用并查集判定两端是否在同一集合），则加入该边。

```c
// Kruskal 算法使用的边结构
typedef struct {
    int u, v;                    // 边的两个端点
    int w;                       // 边的权值
} Edge;

/*
 * Kruskal 算法求最小生成树（并查集实现）
 * 参数：edges[] -- 所有边数组；e -- 边数；n -- 顶点数
 * 时间复杂度：O(|E| log |E|)（主要在于排序），适合稀疏图
 * 前提：需要事先求出所有边并排序
 */
void Kruskal(Edge edges[], int e, int n) {
    // ① 对所有边按权值升序排序（需自行实现排序函数）
    sort(edges, e);

    // ② 初始化并查集（每个顶点自成一个集合）
    MakeSet(n);

    // ③ 遍历所有边，选出 n-1 条即可构成生成树
    for (int i = 0, cnt = 0; i < e && cnt < n - 1; i++) {
        int u = edges[i].u, v = edges[i].v;
        if (Find(u) != Find(v)) {       // 两端不在同一集合 → 不形成回路
            Union(u, v);                // 合并两个集合
            cnt++;                      // 已选边数 +1
            printf("(%d,%d):%d\n", u, v, edges[i].w);
        }
    }
}
```

#### 5.8 Dijkstra 算法

**算法描述**：维护 `dist[]`（当前最短路径估计）和 `visited[]`（是否已确定）。每次选中 `dist` 最小且未确定的顶点，标记为已确定，并用该顶点松弛其他顶点（`dist[j] = min(dist[j], dist[u]+Edge[u][j])`）。

```c
/*
 * Dijkstra 算法求单源最短路径（只能处理非负边权）
 * 参数：G -- 图的邻接矩阵（无边用 INT_MAX 表示）
 *       v0 -- 源点下标
 * 输出：dist[i] = v0 到 i 的最短距离
 *       path[i] = i 在最短路径上的前驱顶点（用于回溯路径）
 * 时间复杂度：O(|V|^2)，堆优化可达 O(|E| log |V|)
 */
void Dijkstra(MGraph G, int v0) {
    int dist[MaxVertexNum];      // dist[i] = v0 到 i 的最短距离
    int visited[MaxVertexNum];   // visited[i] = 1 表示 i 已确定最短路径
    int path[MaxVertexNum];      // path[i] = i 的最短路前驱（可选，用于回溯路径）

    // ① 初始化
    for (int i = 0; i < G.vexnum; i++) {
        dist[i] = G.Edge[v0][i];         // 初始为直接边的权值（无边则为无穷）
        visited[i] = 0;                  // 所有顶点均未确定
        path[i] = (dist[i] < INT_MAX) ? v0 : -1;  // 有直接边则前驱为 v0
    }
    dist[v0] = 0;                        // 源点到自身距离为 0
    visited[v0] = 1;                     // 源点已确定

    // ② 进行 n-1 次迭代，每次确定一个顶点
    for (int i = 1; i < G.vexnum; i++) {
        // 在所有未确定顶点中找 dist 最小的记为 u
        int min = INT_MAX, u;
        for (int j = 0; j < G.vexnum; j++)
            if (!visited[j] && dist[j] < min) {
                min = dist[j];
                u = j;
            }
        visited[u] = 1;                  // 标记 u 已确定

        // ③ 以 u 为中转点，尝试松弛其他未确定顶点
        for (int j = 0; j < G.vexnum; j++) {
            // 条件：j 未确定 && u->j 有边 && 经过 u 比当前 dist[j] 短
            if (!visited[j] && G.Edge[u][j] < INT_MAX
                && dist[u] + G.Edge[u][j] < dist[j]) {
                dist[j] = dist[u] + G.Edge[u][j];  // 更新更短距离
                path[j] = u;                       // 更新前驱
            }
        }
    }
}
```

#### 5.9 Floyd 算法

**算法描述**：三重循环，以每个顶点 $k$ 为中转点，尝试更新所有 $i \to j$ 的最短距离：`dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])`。

```c
/*
 * Floyd 算法求所有顶点对之间的最短路径（允许负权边，但不允许负权回路）
 * 参数：G -- 图；dist[][] -- 输出最短距离矩阵
 * 核心思想：动态规划，逐步允许更多顶点作为中转
 * 时间复杂度：O(|V|^3)，空间复杂度：O(|V|^2)
 */
void Floyd(MGraph G, int dist[][MaxVertexNum]) {
    // ① 初始化：dist 初始为直接边的权值矩阵
    for (int i = 0; i < G.vexnum; i++)
        for (int j = 0; j < G.vexnum; j++)
            dist[i][j] = G.Edge[i][j];

    // ② 动态规划：依次允许顶点 0,1,...,k-1 作为中转点
    for (int k = 0; k < G.vexnum; k++)              // 当前允许的中转点
        for (int i = 0; i < G.vexnum; i++)          // 起点
            for (int j = 0; j < G.vexnum; j++)      // 终点
                // 需要先检查 i->k 和 k->j 是否都有边（防止加法溢出）
                if (dist[i][k] < INT_MAX && dist[k][j] < INT_MAX
                    && dist[i][k] + dist[k][j] < dist[i][j])
                    dist[i][j] = dist[i][k] + dist[k][j];  // 通过 k 中转更短
}
```

#### 5.10 拓扑排序

**算法描述**：① 统计所有顶点的入度；② 入度为 0 的顶点入栈；③ 循环：出栈输出 → 消除该顶点的所有出边（邻接点入度 -1），若邻接点入度变为 0 则入栈；④ 若输出顶点数 < 总顶点数，则图中有回路。

```c
/*
 * 拓扑排序（基于邻接表 + 栈）
 * 参数：G -- 有向图（需为 DAG，否则排序失败）
 * 返回：1=排序成功，0=存在回路
 * 时间复杂度：O(|V|+|E|)
 */
int TopologicalSort(ALGraph G) {
    int indegree[MaxVertexNum] = {0};   // 各顶点入度，初始全 0
    int Stack[MaxVertexNum], top = -1;  // 辅助栈，存放入度为 0 的顶点

    // ① 统计所有顶点的入度
    for (int i = 0; i < G.vexnum; i++) {
        for (ArcNode *p = G.vertices[i].firstarc; p; p = p->next) {
            indegree[p->adjvex]++;       // 每条边 i->adjvex 使 adjvex 入度 +1
        }
    }

    // ② 将所有入度为 0 的顶点入栈
    for (int i = 0; i < G.vexnum; i++)
        if (indegree[i] == 0)
            Stack[++top] = i;

    int count = 0;                        // 已输出的顶点计数

    // ③ 主循环
    while (top != -1) {
        int v = Stack[top--];             // 弹出栈顶（入度为 0 的顶点）
        printf("%d ", v);                 // 输出（或加入拓扑序列）
        count++;

        // 删除 v 的所有出边：对每个邻接点入度 -1
        for (ArcNode *p = G.vertices[v].firstarc; p; p = p->next) {
            if (--indegree[p->adjvex] == 0)    // 邻接点入度减 1 后变为 0
                Stack[++top] = p->adjvex;      // 入栈
        }
    }

    // ④ 如果输出的顶点数少于总顶点数，说明存在回路（有向环）
    return count < G.vexnum ? 0 : 1;
}
```

---

### 六、查找

#### 6.1 顺序查找

**算法描述**：从一端开始逐个比较，找到则返回下标，否则返回 -1。哨兵版可将比较次数减半（每次不用判断数组越界）。

```c
/*
 * 普通版顺序查找
 * 时间复杂度：O(n)（平均和最坏）
 */
int SeqSearch(int a[], int n, int key) {
    for (int i = 0; i < n; i++)
        if (a[i] == key)
            return i;                // 找到，返回下标
    return -1;                       // 未找到
}

/*
 * 哨兵版顺序查找（下标从 1 开始）
 * 优点：循环中不需要做越界判断（i >= 0），每次循环少一次比较
 * a[0] 存放哨兵值，a[1..n] 存放实际数据
 * 时间复杂度：仍是 O(n)，但常数因子更小
 */
int SeqSearch_Sentinel(int a[], int n, int key) {
    a[0] = key;                      // 将哨兵放到 a[0]
    int i = n;                       // 从最后一个元素开始

    // 因为 a[0]=key，所以循环一定会停在找到 key 的位置（保证不会越界）
    while (a[i] != key)
        i--;
    return i;                        // i=0 表示未找到（停在了哨兵位置）
}
```

#### 6.2 折半查找（二分查找）

**算法描述**：前提是**有序表 + 顺序存储**。每次取区间中间元素比较，相等则返回，不等则缩一半范围继续查找。

```c
/*
 * 折半查找（二分查找）
 * 前提：数组 a 已按升序排列，且支持下标随机访问
 * 参数：a -- 有序数组；n -- 元素个数；key -- 目标值
 * 返回：目标值的下标，-1 表示未找到
 * 时间复杂度：O(log n)
 */
int BinarySearch(int a[], int n, int key) {
    int low = 0, high = n - 1;       // 查找区间 [low, high]

    while (low <= high) {            // 注意：等于号包含！当 low==high 时区间仍有一个元素
        // mid 防溢出写法（不使用 (low+high)/2，因为 low+high 可能溢出 int）
        int mid = low + (high - low) / 2;

        if (a[mid] == key)           // 命中
            return mid;
        else if (a[mid] < key)       // key 在右半区
            low = mid + 1;           // 缩到 [mid+1, high]
        else                         // key 在左半区
            high = mid - 1;          // 缩到 [low, mid-1]
    }
    return -1;                       // 区间为空，未找到
}
```

#### 6.3 分块查找

**算法描述**：先查索引表（折半/顺序）确定目标在哪一块，再在块内顺序查找。

```c
// ==================== 分块查找（索引查找） ====================
// 索引表项：每块记录最大关键字和块起始下标
typedef struct {
    int maxKey;     // 该块中的最大关键字值
    int start;      // 该块在数组中的起始下标
} Index;

/*
 * 分块查找
 * 参数：a -- 待查数组；idx -- 索引表；n -- 索引表项数；key -- 目标值
 * 返回：目标值下标，-1 未找到
 * 时间复杂度：O(√n)（折半查索引 O(log b) + 块内顺序 O(s)，b≈s≈√n 时最优）
 */
int BlockSearch(int a[], Index idx[], int n, int key) {
    int i = 0;

    // ① 在索引表中顺序查找（确定在哪一块）
    while (i < n && key > idx[i].maxKey)
        i++;
    if (i >= n) return -1;                    // 超出所有块的范围

    // ② 在确定的块内顺序查找
    // 块的结束位置取下一块的 start，若为最后一块则假设到数组合适范围
    int j;
    for (j = idx[i].start; j < idx[i + 1].start && j < n; j++)
        if (a[j] == key)
            return j;
    return -1;
}
```

#### 6.4 BST — 查找（递归）

```c
/*
 * 二叉排序树递归查找
 * 参数：T -- 树根指针；key -- 关键字
 * 返回：找到的结点指针，NULL 表示未找到
 * 时间复杂度：平均 O(log n)，最坏 O(n)（退化为链表时）
 */
BiTNode* BST_Search(BiTree T, int key) {
    // 递归边界：空树 或 找到目标
    if (!T || T->data == key)
        return T;
    // 根据 BST 性质：左小右大，决定递归方向
    if (key < T->data)
        return BST_Search(T->lchild, key);   // 小于根，去左子树
    else
        return BST_Search(T->rchild, key);   // 大于根，去右子树
}
```

#### 6.5 BST — 插入（递归）

**算法描述**：若根空则新建结点并插入；否则与根比较，小则递归插入左子树，大则递归插入右子树。若关键字已存在则不插入。

```c
/*
 * 二叉排序树插入（递归版）
 * 参数：T -- 树根指针的地址（二级指针，因为可能修改 T 本身）
 *       key -- 待插入关键字
 * 返回：1=成功插入，0=已存在（插入失败）
 * 时间复杂度：同查找，平均 O(log n)
 */
int BST_Insert(BiTree *T, int key) {
    // 情况①：空树 或 走到叶子结点的空孩子位置 → 创建新结点
    if (*T == NULL) {
        *T = (BiTree)malloc(sizeof(BiTNode));
        (*T)->data = key;
        (*T)->lchild = (*T)->rchild = NULL;
        return 1;
    }
    // 情况②：关键字已存在，不重复插入
    if (key == (*T)->data)
        return 0;
    // 情况③：根据大小决定插入左或右子树
    if (key < (*T)->data)
        return BST_Insert(&((*T)->lchild), key);   // 递归插入左子树
    else
        return BST_Insert(&((*T)->rchild), key);   // 递归插入右子树
}
```

#### 6.6 BST — 删除

**算法描述**：找到目标结点，分三种情况处理：
① 叶结点 → 直接删除；
② 只有一个孩子 → 让孩子替代它；
③ 有两个孩子 → 用中序前驱（左子树中最右结点）或中序后继替换，转化为删除前驱/后继结点。

```c
/*
 * 二叉排序树删除
 * 参数：T -- 树根指针的地址；key -- 待删除关键字
 * 返回：1=成功，0=未找到
 * 时间复杂度：同查找，平均 O(log n)
 */
int BST_Delete(BiTree *T, int key) {
    if (*T == NULL) return 0;            // 递归边界：未找到该关键字

    // ① 向下查找目标结点
    if (key < (*T)->data)
        return BST_Delete(&((*T)->lchild), key);
    else if (key > (*T)->data)
        return BST_Delete(&((*T)->rchild), key);
    else {
        // ========== 找到目标结点 p = *T ==========
        BiTree p = *T, s;                // p 指向被删结点

        // 情况 1：只有右孩子（或左右都无，即叶子）
        if (!p->lchild) {
            *T = p->rchild;              // 用右孩子（可能为 NULL）接替
            free(p);
        }
        // 情况 2：只有左孩子
        else if (!p->rchild) {
            *T = p->lchild;              // 用左孩子接替
            free(p);
        }
        // 情况 3：左右孩子都有（最复杂的情况）
        else {
            // 找中序前驱：左子树中最右下的结点（比 p 小的最大结点）
            BiTree q = p;                // q 记录 s 的双亲
            s = p->lchild;               // s 先到左子树根
            while (s->rchild) {          // 一路向右走到头
                q = s;
                s = s->rchild;
            }
            // 用 s 的数据替换 p 的数据
            p->data = s->data;
            // 删除 s 结点（s 至多有一个孩子，因为 s 是最右结点）
            if (q != p)                  // s 不是 p 的直接左孩子
                q->rchild = s->lchild;   // s 的左孩子接替 s（作为 q 的右孩子）
            else                         // s 就是 p 的直接左孩子
                q->lchild = s->lchild;   // s 的左孩子接替 s（作为 p 的左孩子）
            free(s);
        }
        return 1;
    }
}
```

#### 6.7 AVL — LL 右单旋

**算法描述**：失衡结点 A 的左孩子 B 替代 A，A 成为 B 的右孩子，B 的原右子树成为 A 的左子树。

```
旋转前（LL型）：     旋转后：
      A                 B
     / \               / \
    B   Ar    →       Bl   A
   / \                    / \
  Bl  Br                 Br Ar
```

```c
/*
 * AVL LL 型失衡 → 右单旋转
 * 参数：A -- 最小失衡子树的根
 * 返回：旋转后的新根
 * 时间复杂度：O(1)
 */
BiTree RotateLL(BiTree A) {
    BiTree B = A->lchild;              // B 是 A 的左孩子（插入在 B 的左子树导致失衡）

    A->lchild = B->rchild;             // ① B 的右子树变为 A 的左子树（Br 接替到 A 左）
    B->rchild = A;                     // ② A 变为 B 的右孩子

    return B;                          // ③ B 成为新根（原 B 上升，原 A 下降）
}
```

#### 6.8 AVL — RR 左单旋

```c
/*
 * AVL RR 型失衡 → 左单旋转（LL 的镜像）
 * 插入在右孩子的右子树导致失衡
 */
BiTree RotateRR(BiTree A) {
    BiTree B = A->rchild;              // B 是 A 的右孩子

    A->rchild = B->lchild;             // ① B 的左子树变为 A 的右子树
    B->lchild = A;                     // ② A 变为 B 的左孩子

    return B;                          // ③ B 成为新根
}
```

#### 6.9 AVL — LR 双旋（先左后右）

**算法描述**：插入在左孩子的右子树导致失衡。
先对 A 的左孩子 B 做左旋（RotateRR），将其变为 LL 型；再对 A 做右旋（RotateLL）。

```c
/*
 * AVL LR 型失衡 → 先左旋后右旋
 * 插入在左孩子的右子树，需两次旋转
 */
BiTree RotateLR(BiTree A) {
    A->lchild = RotateRR(A->lchild);   // ① 先对 A 的左孩子 B 做左单旋（RR旋转）
    return RotateLL(A);                // ② 再对 A 做右单旋（LL旋转）
}
```

#### 6.10 AVL — RL 双旋（先右后左）

```c
/*
 * AVL RL 型失衡 → 先右旋后左旋
 * 插入在右孩子的左子树，需两次旋转
 */
BiTree RotateRL(BiTree A) {
    A->rchild = RotateLL(A->rchild);   // ① 先对 A 的右孩子 B 做右单旋（LL旋转）
    return RotateRR(A);                // ② 再对 A 做左单旋（RR旋转）
}
```

#### 6.11 散列表 — 开放定址法（线性探测）

**算法描述**：地址 = `(H(key) + i) % m`，`i = 0, 1, 2, ...`，依次探测。找到空位则插入；找到 `key` 则查找成功；遇到空位（未插入过）则查找失败（因为若插入过会在此处停止）。

```c
// ==================== 散列表：开放定址法（线性探测）====================
#define HashSize 13                  // 散列表长度，通常取质数减少冲突
#define EMPTY -1                     // 表示该位置为空（未存任何元素）
int HashTable[HashSize];

/*
 * 初始化哈希表：全部标记为空
 */
void HashInit() {
    for (int i = 0; i < HashSize; i++)
        HashTable[i] = EMPTY;
}

/*
 * 哈希查找（线性探测）
 * 探测序列：H = key % HashSize, (H+1) % HashSize, (H+2) % HashSize, ...
 * 参数：key -- 查找关键字
 * 返回：找到时返回下标，未找到返回 -1
 * 注意：遇到 EMPTY 位置即可停止，因为同一探测序列不会跳过空位插入
 */
int HashSearch(int key) {
    int addr = key % HashSize;       // 计算哈希地址
    // 沿探测序列查找，遇到 EMPTY（未存过任何元素）则停止
    while (HashTable[addr] != EMPTY) {
        if (HashTable[addr] == key)
            return addr;             // 找到
        addr = (addr + 1) % HashSize; // 线性探测：下一个位置
    }
    return -1;                       // 遇到空位说明不存在
}

/*
 * 哈希插入（线性探测）
 * 参数：key -- 插入关键字
 * 返回：1=成功，0=已存在或表满
 */
int HashInsert(int key) {
    int addr = key % HashSize;
    // 沿线性探测找空位或相同 key
    while (HashTable[addr] != EMPTY) {
        if (HashTable[addr] == key)
            return 0;                // 关键字已存在，不重复插入
        addr = (addr + 1) % HashSize;
    }
    HashTable[addr] = key;           // 找到空位，插入
    return 1;
}
```

#### 6.12 散列表 — 拉链法

**算法描述**：每个槽位是一个链表头指针。冲突时新结点插入对应链表（头插法，效率更高）。

```c
// ==================== 散列表：拉链法 ====================
typedef struct HashNode {
    int key;                         // 关键字
    struct HashNode *next;           // 指向同义词链表的下一个结点
} HashNode;

HashNode *HashTable[HashSize];       // 指针数组，每个槽位存放一个链表头

/*
 * 初始化：所有槽位置空
 */
void HashInit() {
    for (int i = 0; i < HashSize; i++)
        HashTable[i] = NULL;
}

/*
 * 哈希查找（拉链法）
 * 参数：key -- 查找关键字
 * 返回：找到的结点指针，NULL 表示不存在
 * 时间复杂度：平均 O(1)，最坏 O(n)（全部冲突到同一链表）
 */
HashNode* HashSearch(int key) {
    int addr = key % HashSize;       // 计算槽位
    HashNode *p = HashTable[addr];   // 指向该槽位的链表头

    // 在单链表中顺序查找
    while (p && p->key != key)
        p = p->next;
    return p;                        // 找到返回结点指针，否则返回 NULL
}

/*
 * 哈希插入（拉链法，头插）
 * 参数：key -- 插入关键字
 * 返回：1=成功
 * 优点：不需要处理"表满"，只需要分配新结点
 */
int HashInsert(int key) {
    int addr = key % HashSize;
    // 创建新结点，头插到对应链表（O(1)）
    HashNode *p = (HashNode*)malloc(sizeof(HashNode));
    p->key = key;
    p->next = HashTable[addr];       // ① 新结点 next 指向原链表头
    HashTable[addr] = p;             // ② 链表头更新为新结点
    return 1;
}
```

---

### 七、内部排序

#### 7.1 直接插入排序

**算法描述**：将数组视为两部分：前方已排序部分和后方未排序部分。每次取未排序部分的第一个元素，在已排序部分中找到正确位置插入（将比它大的元素后移）。

```c
/*
 * 直接插入排序
 * 稳定排序 | 原地排序 | 最好 O(n) | 最坏 O(n^2)
 *
 * 最好情况：数组已有序（每趟只比较 1 次）
 * 最坏情况：数组逆序（每趟需移动已排序部分全部元素）
 * 适用场景：数据量较小（n ≤ 50）或基本有序时效率很高
 */
void InsertSort(int a[], int n) {
    for (int i = 1; i < n; i++) {        // i 指向未排序部分的第一个元素
        int key = a[i];                  // 暂存当前待插入元素
        int j = i - 1;                   // j 指向已排序部分的最后一个元素

        // 在已排序部分从右向左找插入位置
        // 同时将比 key 大的元素右移一位
        while (j >= 0 && a[j] > key) {   // 注意：是 > 不是 >=，保证稳定性
            a[j + 1] = a[j];             // 后移
            j--;
        }

        // 循环结束时 j 指向第一个 ≤ key 的元素，key 应插入到 j+1 处
        a[j + 1] = key;
    }
}
```

#### 7.2 折半插入排序

**算法描述**：在直接插入的基础上，用折半查找定位插入位置，减少比较次数（但移动次数不变）。

```c
/*
 * 折半插入排序
 * 稳定排序 | 原地排序 | 平均 O(n^2)
 * 改进点：比较次数从 O(n) 降为 O(log n)（每趟）
 *        但移动次数仍是 O(n)，所以总复杂度仍为 O(n^2)
 */
void BinaryInsertSort(int a[], int n) {
    for (int i = 1; i < n; i++) {
        int key = a[i];
        int low = 0, high = i - 1;       // 在 a[0..i-1] 中折半查找插入位置

        // ① 折半查找确定插入位置（找到第一个大于 key 的位置 = low）
        while (low <= high) {
            int mid = low + (high - low) / 2;
            if (a[mid] > key)            // key 应在 mid 左侧
                high = mid - 1;
            else                         // key ≥ a[mid]，应在 mid 右侧
                low = mid + 1;           // 使用 >= 保证稳定性（相等时插在后面）
        }
        // 循环结束后 low 即为插入位置

        // ② 统一后移 a[low..i-1]
        for (int j = i - 1; j >= low; j--)
            a[j + 1] = a[j];

        // ③ 插入
        a[low] = key;
    }
}
```

#### 7.3 希尔排序

**算法描述**：先按较大步长 `gap` 将序列分成若干子序列，每个子序列做直接插入排序；逐步缩小 `gap` 直到 1（最后一次是完整的插入排序）。此前大的 `gap` 使元素快速移动，减少最后的总移动量。

```c
/*
 * 希尔排序（缩小增量排序）
 * 不稳定排序 | 原地排序 | 复杂度取决于增量序列
 *
 * 常用增量序列：n/2, n/4, ..., 1（Shell 原始方案）
 * 思路：让元素先大步移动到大致位置，再逐步细化
 */
void ShellSort(int a[], int n) {
    // ① 外层循环：逐步缩小增量 gap
    //    gap /= 2 是最简单的递减方案，也可用 Hibbard 等更优增量
    for (int gap = n / 2; gap > 0; gap /= 2) {

        // ② 内层：对每个 gap 分组做"插入排序"
        //    从 gap 开始，因为 a[0..gap-1] 分别是各组的第一个元素
        for (int i = gap; i < n; i++) {
            int key = a[i];               // 当前待插入元素
            int j = i;

            // 在 key 所属的那一组（下标间隔为 gap）中进行插入排序
            while (j >= gap && a[j - gap] > key) {
                a[j] = a[j - gap];        // 同组内元素后移 gap 距离
                j -= gap;                 // 跳到同组的上一个位置
            }
            a[j] = key;                   // 插入
        }
    }
}
```

#### 7.4 冒泡排序

**算法描述**：每趟从第一个元素开始，相邻两两比较，逆序则交换。每趟结束后，最大元素像气泡一样"浮"到最后。若某一趟未发生交换，说明已有序，提前结束。

```c
/*
 * 冒泡排序
 * 稳定排序 | 原地排序 | 最好 O(n) | 最坏 O(n^2)
 *
 * 优化：flag 标志检测是否提前有序
 */
void BubbleSort(int a[], int n) {
    for (int i = 0; i < n - 1; i++) {    // i 表示已完成的趟数（也是已归位的元素数）
        int flag = 0;                    // 本趟是否发生交换的标志

        // j 从 0 到 n-1-i-1（末尾 i 个元素已有序，无需再比较）
        for (int j = 0; j < n - 1 - i; j++) {
            if (a[j] > a[j + 1]) {       // 相邻逆序则交换
                // 使用 > 而非 >=，保证稳定性（相等时不交换）
                int t = a[j];
                a[j] = a[j + 1];
                a[j + 1] = t;
                flag = 1;                // 标记本趟发生了交换
            }
        }

        if (!flag) break;                // 若本趟没有交换，说明已全部有序
    }
}
```

#### 7.5 快速排序

**算法描述**（分治）：
① Partition：选一个枢轴 pivot（通常取第一个元素），将数组划分为两部分：左边 ≤ pivot，右边 ≥ pivot，pivot 放在最终位置；
② 递归对左右两部分分别排序。

```c
/*
 * Partition（一趟划分/分区）
 * 目标：将 a[low] 作为 pivot，最终 pivot 左边都 ≤ pivot，右边都 ≥ pivot
 * 返回：pivot 的最终位置下标
 * 时间复杂度：O(n)（一趟）
 */
int Partition(int a[], int low, int high) {
    int pivot = a[low];                  // ① 选定枢纽（通常取当前区间第一个元素）

    // ② 两端交替向中间扫描
    while (low < high) {
        // 从右向左找第一个小于 pivot 的元素
        while (low < high && a[high] >= pivot)
            high--;
        a[low] = a[high];                // 找到后移到左边的 low 位置

        // 从左向右找第一个大于 pivot 的元素
        while (low < high && a[low] <= pivot)
            low++;
        a[high] = a[low];                // 找到后移到右边的 high 位置
    }

    // ③ low == high 时，pivot 归位
    a[low] = pivot;
    return low;                          // 返回 pivot 的最终下标
}

/*
 * 快速排序（递归版）
 * 不稳定排序 | 原地排序 | 平均 O(n log n) | 最坏 O(n^2)
 *
 * 最坏情况：每次划分极度不均（如已有序，且 pivot 选第一个），退化为 O(n^2)
 * 空间复杂度：O(log n) 到 O(n)（递归栈深度）
 */
void QuickSort(int a[], int low, int high) {
    if (low < high) {                       // 区间长度 > 1 才需要排序
        int pivotPos = Partition(a, low, high);  // ① 划分
        QuickSort(a, low, pivotPos - 1);         // ② 递归排序左半部分
        QuickSort(a, pivotPos + 1, high);        // ③ 递归排序右半部分
    }
}
```

#### 7.6 简单选择排序

**算法描述**：第 $i$ 趟（$i = 0, 1, \dots, n-2$）从 $a[i..n-1]$ 中选出最小元素，与 $a[i]$ 交换。

```c
/*
 * 简单选择排序
 * 不稳定排序 | 原地排序 | 时间 O(n^2)（无论好坏都如此）
 *
 * 不稳定原因：跨距离交换（如 [5, 5, 2] 第一趟 2 与第一个 5 交换，两个 5 的相对次序改变）
 */
void SelectSort(int a[], int n) {
    for (int i = 0; i < n - 1; i++) {    // i 是当前待放置的位置，共 n-1 趟
        int minIdx = i;                  // 假设当前位置是最小的

        // 在 a[i+1..n-1] 中找最小元素的下标
        for (int j = i + 1; j < n; j++)
            if (a[j] < a[minIdx])
                minIdx = j;              // 更新最小值下标

        // 若 minIdx != i，交换 a[i] 与 a[minIdx]
        if (minIdx != i) {
            int t = a[i];
            a[i] = a[minIdx];
            a[minIdx] = t;
        }
    }
}
```

#### 7.7 堆排序

**算法描述（大根堆升序排序）**：
① 建堆：从最后一个非叶结点开始向前，对每个子树做向下调整（HeapAdjust）；
② 排序：反复将堆顶（最大值）与末尾元素交换，然后对剩余部分重新调整堆。

```c
/*
 * 大根堆向下调整（HeapAdjust / SiftDown）
 * 功能：将以 k 为根的子树调整为大根堆（前提：k 的左右子树已是大根堆）
 * 参数：a -- 数组；k -- 待调整子树的根下标；len -- 当前堆的有效长度
 * 时间复杂度：O(log n)（每次调整沿树高走）
 */
void HeapAdjust(int a[], int k, int len) {
    int root = a[k];                     // 暂存根结点的值

    // 沿较大的孩子向下筛选
    // i = 2*k+1 是 k 的左孩子（数组下标从 0 开始）
    for (int i = 2 * k + 1; i < len; i = 2 * i + 1) {
        // 若右孩子存在且更大，选右孩子
        if (i + 1 < len && a[i] < a[i + 1])
            i++;

        // 若根值已 ≥ 较大的孩子，则筛选结束
        if (root >= a[i])
            break;

        // 否则，将较大的孩子上移到双亲位置，继续向下筛选
        a[k] = a[i];
        k = i;                           // k 下降到孩子位置
    }
    a[k] = root;                         // 最终位置放入根值
}

/*
 * 建堆：从最后一个非叶结点依次向前做 HeapAdjust
 * 最后一个非叶结点下标 = n/2 - 1（完全二叉树性质）
 * 时间复杂度：O(n)（均摊分析，不是 n log n）
 */
void BuildMaxHeap(int a[], int n) {
    for (int i = n / 2 - 1; i >= 0; i--)
        HeapAdjust(a, i, n);
}

/*
 * 堆排序（大根堆实现升序排序）
 * 不稳定排序 | 原地排序 | 时间 O(n log n)
 *
 * 不稳定原因：堆调整过程中元素跨距跳交换
 */
void HeapSort(int a[], int n) {
    BuildMaxHeap(a, n);                  // ① 建初始大根堆

    // ② 进行 n-1 次交换-调整
    for (int i = n - 1; i > 0; i--) {
        // 交换堆顶 a[0]（当前最大值）与堆尾 a[i]
        int t = a[0];
        a[0] = a[i];
        a[i] = t;

        // 堆长度减 1，重新调整堆顶
        HeapAdjust(a, 0, i);
    }
}
```

#### 7.8 归并排序（二路）

**算法描述**：分治。递归将数组分成两半，各自有序后，合并（Merge）两个有序子序列。

```c
/*
 * Merge（合并）：将两个有序段 a[low..mid] 和 a[mid+1..high] 合并为一个有序段
 * 时间复杂度：O(n)（n = high-low+1）
 * 空间复杂度：O(n)（需临时数组 tmp）
 */
void Merge(int a[], int low, int mid, int high) {
    // 分配临时数组，存放合并结果
    int *tmp = (int*)malloc((high - low + 1) * sizeof(int));
    int i = low, j = mid + 1, k = 0;     // i 遍历左段，j 遍历右段，k 遍历 tmp

    // ① 两路归并：取较小者放入 tmp
    while (i <= mid && j <= high) {
        if (a[i] <= a[j])                // 使用 <= 保证稳定性
            tmp[k++] = a[i++];
        else
            tmp[k++] = a[j++];
    }

    // ② 处理剩余部分（至多一段还有剩余）
    while (i <= mid)  tmp[k++] = a[i++];
    while (j <= high) tmp[k++] = a[j++];

    // ③ 复制回原数组
    for (i = low, k = 0; i <= high; i++, k++)
        a[i] = tmp[k];

    free(tmp);                           // 释放临时数组内存
}

/*
 * 归并排序（递归版）
 * 稳定排序 | 非原地（需 O(n) 辅助空间） | 时间 O(n log n)（最坏也是）
 *
 * 优点：稳定 + 时间复杂度严格 O(n log n)
 * 缺点：需要 O(n) 额外空间
 */
void MergeSort(int a[], int low, int high) {
    if (low < high) {                    // 区间长度 > 1
        int mid = low + (high - low) / 2;  // 防溢出取中点
        MergeSort(a, low, mid);           // ① 递归排序左半
        MergeSort(a, mid + 1, high);      // ② 递归排序右半
        Merge(a, low, mid, high);         // ③ 合并两个有序段
    }
}
```

#### 7.9 计数排序

**算法描述**：核心是"统计 + 累加 + 逆序填入"。先统计每个值出现次数，再累加得到每个值的最终位置，最后从后向前稳定地将元素填入输出数组。

```c
/*
 * 计数排序
 * 稳定排序 | 非原地 | 时间 O(n+k) | 空间 O(n+k)（k = 值域大小）
 *
 * 前提：关键词值域有限（如 0~100 之间的整数）
 * 不适合：关键词取值范围远大于 n（空间浪费严重）
 */
void CountingSort(int a[], int n) {
    // ① 求最大值和最小值（确定值域范围）
    int max = a[0], min = a[0];
    for (int i = 1; i < n; i++) {
        if (a[i] > max) max = a[i];
        if (a[i] < min) min = a[i];
    }

    int range = max - min + 1;           // 值域大小

    // count[i] = 值 i+min 的出现次数（分配数组后统计）
    int *count = (int*)calloc(range, sizeof(int));  // calloc 初始化为 0
    int *output = (int*)malloc(n * sizeof(int));    // 输出数组

    // ② 统计每个值出现的次数
    for (int i = 0; i < n; i++)
        count[a[i] - min]++;             // 偏移 -min 使得最小值为下标 0

    // ③ 累加：count[i] = 值 ≤ (i+min) 的元素个数（即该值在排序后的最后位置+1）
    for (int i = 1; i < range; i++)
        count[i] += count[i - 1];

    // ④ 从后向前遍历原数组（保证稳定性）
    for (int i = n - 1; i >= 0; i--) {
        int idx = a[i] - min;            // 当前值的 count 下标
        output[--count[idx]] = a[i];     // count[idx] 先减 1，再作为输出位置
    }

    // ⑤ 复制回原数组
    for (int i = 0; i < n; i++)
        a[i] = output[i];

    free(count);
    free(output);
}
```

#### 7.10 基数排序（LSD 最低位优先）

**算法描述**：从最低位到最高位，对每一位进行一趟"分配-收集"（使用计数排序作为稳定子排序）。位数最多的决定了总趟数。

```c
/*
 * 基数排序（LSD：最低位优先）
 * 稳定排序 | 非原地 | 时间 O(d(n+r)) | 空间 O(n+r)
 * d = 最大位数，r = 基数（十进制 r=10）
 *
 * 核心思想：按"位"稳定性排序，低位排序保证高位相同时低位有序
 */
void RadixSort(int a[], int n) {
    // ① 找最大值（确定最多有几位）
    int max = a[0];
    for (int i = 1; i < n; i++)
        if (a[i] > max) max = a[i];

    // ② 对每一位（个、十、百...）进行计数排序
    // exp = 1, 10, 100, ... 代表当前处理的位
    for (int exp = 1; max / exp > 0; exp *= 10) {
        int output[n];                   // 本趟输出数组
        int count[10] = {0};             // 每位 0~9，10 个桶

        // ③ 统计当前位上各数字的出现次数
        for (int i = 0; i < n; i++)
            count[(a[i] / exp) % 10]++;

        // ④ 累加 count：确定元素在 output 中的位置
        for (int i = 1; i < 10; i++)
            count[i] += count[i - 1];

        // ⑤ 逆序填入 output（保证稳定性）
        for (int i = n - 1; i >= 0; i--) {
            int digit = (a[i] / exp) % 10;  // 当前位的数字
            output[--count[digit]] = a[i];  // 填入正确位置
        }

        // ⑥ 写回原数组，作为下一趟的输入
        for (int i = 0; i < n; i++)
            a[i] = output[i];
    }
}
```

---

📥 *是否需要将某个算法的代码进一步拆解为更详细的分步注释？*
