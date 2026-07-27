import re, os

with open(r'C:\Users\34406\Documents\Obsidian Vault\李艳芳.md', 'r', encoding='utf-8') as f:
    content = f.read()

parts = re.split(r'### 文件[一二三].*', content)

def clean_text(text):
    text = re.sub(r'\d+考研交流[gGqQ][pP].*', '', text)
    text = re.sub(r'\d+课程咨询.*', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def process_section(text):
    text = clean_text(text)
    lines = text.split('\n')
    output = []
    skip_mode = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            output.append('')
            continue
        
        # Skip ad lines
        if '考研交流' in stripped or '课程咨询' in stripped:
            continue
        
        # Skip solution blocks (start with 解)
        if re.match(r'^解[\s\：\:]', stripped) and len(stripped) < 100:
            skip_mode = True
            continue
        
        # End solution mode at next 考点/section header
        if skip_mode:
            if re.match(r'^\*\*考点|^考点\s|^第[一二三四五六七八九十\d]+章|^\d+[\.\、]', stripped):
                skip_mode = False
            else:
                continue
        
        # Format headers
        if re.match(r'^\*\*考点', stripped) or re.match(r'^考点\s', stripped):
            hdr = stripped.replace('*', '')
            output.append('')
            output.append('\\subsection*{' + hdr + '}')
            output.append('')
            continue
        
        if re.match(r'^第[一二三四五六七八九十\d]+章', stripped):
            output.append('')
            output.append('\\section*{' + stripped + '}')
            output.append('')
            continue
        
        # Regular line
        output.append(stripped)
    
    return '\n'.join(output)

jichu = process_section(parts[3])
qianghua = process_section(parts[2])

tex_dir = r'C:\Users\34406\Documents\Obsidian Vault\数学专题\李艳芳线面积分'

with open(os.path.join(tex_dir, 'jichu.tex'), 'w', encoding='utf-8') as f:
    f.write(jichu)
with open(os.path.join(tex_dir, 'qianghua.tex'), 'w', encoding='utf-8') as f:
    f.write(qianghua)

print(f'基础讲义: {len(jichu):,} chars')
print(f'强化讲义: {len(qianghua):,} chars')
# Preview first few lines of each
print('\n--- 基础讲义 preview ---')
print(jichu[:300])
print('\n--- 强化讲义 preview ---')
print(qianghua[:300])
