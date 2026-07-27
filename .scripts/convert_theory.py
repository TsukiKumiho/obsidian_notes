import re, os

with open(r'C:\Users\34406\Documents\Obsidian Vault\李艳芳.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
in_preamble = True
in_solution = False
in_theory = False
prob_counter = 0
tex_env_depth = 0

for line in lines:
    stripped = line.strip()
    
    # Skip AI preamble
    if in_preamble:
        if '2022' in stripped or '第八章' in stripped:
            in_preamble = False
        else:
            continue
    
    # Skip ads
    if '考研交流' in stripped or '课程咨询' in stripped:
        continue
    
    # Skip solution blocks
    if re.match(r'^解[\s\：\:]', stripped) and len(stripped) < 100:
        in_solution = True
        continue
    
    # End solution at next section/header
    if in_solution:
        if stripped.startswith('###') or stripped.startswith('**考点') or re.match(r'^\d+[\.\、]', stripped) or '同步习题' in stripped or '2022' in stripped:
            in_solution = False
        else:
            continue
    
    # Blank lines
    if not stripped:
        output.append('')
        continue
    
    # Headers
    if stripped.startswith('### '):
        hdr = stripped[4:]
        output.append('')
        output.append('\\subsubsection*{' + hdr + '}')
        output.append('')
        continue
    
    if '2022' in stripped and '基础班' in stripped:
        continue  # skip year header
    
    if stripped.startswith('第八章'):
        output.append('\\section*{' + stripped + '}')
        output.append('')
        continue
    
    # 同步习题 separator
    if '同步习题' in stripped:
        output.append('')
        output.append('\\medskip')
        output.append('\\textbf{同步习题}')
        output.append('\\medskip')
        continue
    
    # 考点 headers
    if re.match(r'^\*\*考点|\*\*第[一二三四五六七八九十]', stripped):
        hdr = stripped.replace('*', '')
        output.append('')
        output.append('\\subsubsection*{' + hdr + '}')
        output.append('')
        continue
    
    # Numbered problems
    if re.match(r'^\d+[\.\、\）\)]', stripped):
        output.append('')
        output.append('\\begin{theory}')
        output.append(stripped)
        output.append('\\end{theory}')
        continue
    
    # Regular theory text
    output.append(stripped)

# Write full theory content
tex_content = '\n'.join(output)

# Save
dst = r'C:\Users\34406\Documents\Obsidian Vault\数学专题\李艳芳线面积分\full_theory.tex'
with open(dst, 'w', encoding='utf-8') as f:
    f.write(tex_content)

print(f'Saved: {len(tex_content):,} chars, {tex_content.count(chr(10))+1} lines')
# Show first few lines
for line in tex_content.split('\n')[:15]:
    print(line[:100])
