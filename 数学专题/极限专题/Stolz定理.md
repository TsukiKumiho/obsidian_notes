# Stolz 定理 | 极限专题

> **Stolz 定理**：数列极限版的"洛必达法则"。适用于 $n \to \infty$ 且分子或分母为和式的 $\frac{\infty}{\infty}$ 型（或 $\frac{0}{0}$ 型）未定式。
>
> **与定积分定义的区分**：定积分定义处理 $\frac{1}{n}\sum f(k/n)$ 型；Stolz 处理 $\frac{\sum a_k}{n^\alpha}$ 型——即分子为"不定和式"时的极限。

---

## 一、定理陈述

### $\frac{\infty}{\infty}$ 型（最常用）

若 $\{b_n\}$ 严格单调且 $b_n \to \infty$，且

$$
\lim_{n\to\infty} \frac{a_{n+1} - a_n}{b_{n+1} - b_n} = L \quad (L \text{ 可为有限或} \pm\infty)
$$

则

$$
\lim_{n\to\infty} \frac{a_n}{b_n} = L
$$

### $\frac{0}{0}$ 型

若 $a_n \to 0, b_n \to 0$，$\{b_n\}$ 严格单调，且 $\lim \frac{a_{n+1}-a_n}{b_{n+1}-b_n} = L$，则 $\lim \frac{a_n}{b_n} = L$。

---

## 二、核心推论：幂和极限

> ⚡ **必背结论**：$\displaystyle\lim_{n\to\infty} \frac{1^p + 2^p + \cdots + n^p}{n^{p+1}} = \frac{1}{p+1}$（$p > -1$）

此结论由 Stolz 定理一次性推出，避免了记忆所有幂和公式：

**推演**：$a_n = \sum_{k=1}^n k^p$，$b_n = n^{p+1}$。

$$
\lim\frac{a_n}{b_n} = \lim\frac{(n+1)^p}{(n+1)^{p+1} - n^{p+1}} = \lim\frac{n^p}{(p+1)n^p} = \frac{1}{p+1}
$$

（分母用二项式定理展开：$(n+1)^{p+1} - n^{p+1} = (p+1)n^p + \cdots$）

---

## 三、题型分类

### 题型一：直接 Stolz 型

#### 题 1 【基础】

$$
\lim_{n \to \infty} \frac{1 + \frac{1}{2} + \cdots + \frac{1}{n}}{\ln n}
$$

**解法**：

$a_n = \sum_{k=1}^n \frac{1}{k}$，$b_n = \ln n$（单调 $\to \infty$）。

$$
\lim\frac{a_{n+1}-a_n}{b_{n+1}-b_n}
= \lim\frac{\frac{1}{n+1}}{\ln(1+\frac{1}{n})}
= \lim\frac{\frac{1}{n}}{\frac{1}{n}} = 1
$$

（$\ln(1+1/n) \sim 1/n$）

**答案**：$1$

---

#### 题 2 【基础】

$$
\lim_{n \to \infty} \frac{1^2 + 2^2 + \cdots + n^2}{n^3}
$$

**解法**：

令 $a_n = \sum_{k=1}^n k^2$，$b_n = n^3$。

$$
\lim\frac{a_n}{b_n} = \lim\frac{(n+1)^2}{(n+1)^3 - n^3}
= \lim\frac{n^2}{3n^2 + 3n + 1} = \frac{1}{3}
$$

（分母 $(n+1)^3 - n^3 = 3n^2 + 3n + 1$）

> 💡 验证：$\sum k^2 = \frac{n(n+1)(2n+1)}{6}$，除以 $n^3$ 得 $\frac{1}{3}$。Stolz 无需记公式。

**答案**：$\dfrac{1}{3}$

---

#### 题 3 【进阶】

$$
\lim_{n \to \infty} \frac{1}{\sqrt{n}}\left(1 + \frac{1}{\sqrt{2}} + \cdots + \frac{1}{\sqrt{n}}\right)
$$

**解法**：

$a_n = \sum_{k=1}^n \frac{1}{\sqrt{k}}$，$b_n = \sqrt{n}$。

$$
\lim\frac{a_n}{b_n} = \lim\frac{\frac{1}{\sqrt{n+1}}}{\sqrt{n+1} - \sqrt{n}}
= \lim\frac{\frac{1}{\sqrt{n+1}}}{\frac{1}{\sqrt{n+1}+\sqrt{n}}}
= \lim(\sqrt{1+\frac{1}{n}} + 1) = 2
$$

**答案**：$2$

---

### 题型二：Stolz 的多次使用

#### 题 4 【进阶】

$$
\lim_{n \to \infty} \frac{\ln(n!)}{n\ln n}
$$

**解法**：

$a_n = \ln(n!) = \sum_{k=1}^n \ln k$，$b_n = n\ln n$。

$$
\lim\frac{a_{n+1}-a_n}{b_{n+1}-b_n}
= \lim\frac{\ln(n+1)}{(n+1)\ln(n+1) - n\ln n}
$$

分母的处理：（用微分近似）$(n+1)\ln(n+1) - n\ln n \approx \ln n + 1$。

更精确：$(n+1)\ln(n+1) = (n+1)(\ln n + \ln(1+1/n)) = (n+1)(\ln n + \frac{1}{n} + o(\frac{1}{n}))$
$= n\ln n + \ln n + 1 + o(1)$。

故分母 $\approx \ln n + 1$。分子 $\sim \ln n$。极限 $= 1$。

**答案**：$1$

---

### 题型三：Stolz 的 $\frac{0}{0}$ 型

#### 题 5 【基础】

$$
\lim_{n \to \infty} n\sin\frac{1}{n}
$$

**解法**：

$\frac{0}{0}$ 型 Stolz：$a_n = \sin(1/n)$，$b_n = 1/n$。

$$
\lim\frac{a_n}{b_n} = \lim\frac{\sin(1/(n+1)) - \sin(1/n)}{1/(n+1) - 1/n}
$$

此法过于繁琐。更好的做法：直接用重要极限 $\frac{\sin(1/n)}{1/n} \to 1$。

> 💡 Stolz 的 $\frac{0}{0}$ 型在日常使用较少，$\frac{\infty}{\infty}$ 型才是主力。

**答案**：$1$

---

## 四、Stolz vs 定积分定义

| 特征 | Stolz | 定积分定义 |
| :--- | :--- | :--- |
| 分子形式 | $\sum_{k=1}^n a_k$（$a_k = k^p$ 等） | $\frac{1}{n}\sum_{k=1}^n f(k/n)$ |
| 分母形式 | $n^\alpha$（$\alpha > 0$） | $\frac{1}{n}$ 因子已在前面 |
| 典型题 | $\frac{\sum k^p}{n^{p+1}}$ | $\frac{1}{n}\sum\sqrt{k/n}$ |

> ⚠️ 两者处理的是**不同类型的求和**。Stolz 不要求被加数可写为 $f(k/n)$ 形式，适用范围更广。

---

## 五、自测练习

### 练习 1
$$
\lim_{n \to \infty} \frac{1^3 + 2^3 + \cdots + n^3}{n^4}
$$

### 练习 2
$$
\lim_{n \to \infty} \frac{\sqrt{1} + \sqrt{2} + \cdots + \sqrt{n}}{n^{3/2}}
$$

### 练习 3
$$
\lim_{n \to \infty} n\left(\frac{1}{n^2+1} + \frac{1}{n^2+2} + \cdots + \frac{1}{n^2+n}\right)
$$

（提示：先夹逼或用 Stolz？）

---

## 六、答案

**练习 1**：$\frac{1}{4}$（$p=3$，公式 $\frac{1}{p+1} = \frac{1}{4}$）

**练习 2**：$p = 1/2$，$\frac{1}{p+1} = \frac{1}{3/2} = \frac{2}{3}$

**练习 3**：$= \lim \frac{1}{n}\sum_{k=1}^n \frac{1}{1+(k/n)^2} = \int_0^1 \frac{dx}{1+x^2} = \frac{\pi}{4}$。这里更适合**定积分定义**而非 Stolz。

>  *配套专题：定积分定义求极限 · 夹逼准则 · 单调有界准则*
