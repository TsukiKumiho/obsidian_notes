import re

path = r'C:\Users\34406\Documents\Obsidian Vault\数学错题本\2026_06_880_02.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the block starting from the x^2 counterexample
start_marker = 'f(x)=\\begin{cases}x^2, & -1\\le x<0'
end_marker = '### $\\lambda$ 那步的几何直觉'

start = content.find(start_marker)
end = content.find(end_marker)

if start < 0:
    print('Start marker not found')
else:
    print(f'Found start at {start}')
    if end < 0:
        print('End marker not found, using rest of file after start')
        old_part = content[start:]
    else:
        old_part = content[start:end-2]  # -2 for the \n\n before next section
    
    new_part = r"""f(x)=\begin{cases}\sqrt{-x}, & -1\le x<0 \\ x^2, & 0\le x\le1\end{cases}
$$

两段在 $0$ 处连续（均为 $0$）。$x<0$ 时 $\sqrt{-x}$ 是**凸**的（$f''<0$），$x>0$ 时 $x^2$ 是凹的——凹凸翻转 → 整体**不是凹函数**。

验证 $g$ 递增：$x<0$ 时 $g(x)=\frac{\sqrt{-x}-1}{x-1}$。令 $t=\sqrt{-x}\in[0,1]$，$g'(x)=\frac{1-t^2}{2t(x-1)^2}\ge0$；$x>0$ 时 $g(x)=x+1$，$g'=1>0$。且 $\lim_{0^-}g=g(0)=1$ 连续。$g$ 在 $[-1,1)$ **严格递增**。

**充分性不成立**。选 **C**。连续函数也可构成反例，无需跳跃间断。

### 核心要点

| 要点 | 内容 |
|:---|:---|
| 错因 | 默认 $f$ 可导 → 用 $f''$ 分析。题干只说"有定义" |
| 凹的原始定义 | $f(\lambda a+(1-\lambda)b)\le\lambda f(a)+(1-\lambda)f(b)$，不依赖可导性 |
| 反例核心 | 凹凸翻转：左边凸($\sqrt{-x}$)右边凹($x^2$)，连续拼接，$g$ 递增但整体非凹 |

""" + ('\n' if end >= 0 else '')
    
    content = content.replace(old_part, new_part)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
