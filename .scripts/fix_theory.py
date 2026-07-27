import re

with open(r'C:\Users\34406\Documents\Obsidian Vault\数学专题\李艳芳线面积分\full_theory.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove duplicate chapter header
content = re.sub(r'\\section\*\{第八章[^}]*\}\s*', '', content)

# 2. Fix amsmath nesting: \[...\] around \begin{align*} is an error
content = re.sub(r'\\\[\s*\\begin\{align\*\}', r'\\begin{align*}', content)
content = re.sub(r'\\end\{align\*\}\s*\\\]', r'\\end{align*}', content)

# 3. Fix example formatting: **例1** → \textbf{例1} on its own line
content = re.sub(r'\*\*例\s*(\d+)\*\*', r'\\textbf{例\1}', content)
content = re.sub(r'\*\*(\d+)\*\*', r'\\textbf{\1}', content)

# 4. Clean excessive blank lines (more than 2 consecutive)
content = re.sub(r'\n{4,}', '\n\n\n', content)

# 5. Fix subscript/superscript issues from markdown
content = content.replace('ᵢ', '_{i}')
content = content.replace('ₙ', '_{n}')
content = content.replace('ₗ', '_{L}')
content = content.replace('₁', '_{1}')
content = content.replace('₂', '_{2}')
content = content.replace('₃', '_{3}')
content = content.replace('₀', '_{0}')
content = content.replace('₋', '_{-}')
content = content.replace('ⁿ', '^{n}')
content = content.replace('∫ₗ', r'\int_{L}')
content = content.replace('∑ⁿᵢ₌₁', r'\sum_{i=1}^{n}')
content = content.replace('∑ⁿᵢ₋₁', r'\sum_{i=1}^{n}')
content = content.replace('Mᵢ₋₁', 'M_{i-1}')
content = content.replace('Δxᵢ', r'\Delta x_{i}')
content = content.replace('Δyᵢ', r'\Delta y_{i}')

# 6. Fix long text that should be in display math
# \tilde{M}_{i-1} \tilde{M}_i → keep as is

with open(r'C:\Users\34406\Documents\Obsidian Vault\数学专题\李艳芳线面积分\full_theory.tex', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Fixed: {len(content):,} chars')
print('Key fixes: chapter header removed, amsmath nesting fixed, subscript/superscript fixed')
