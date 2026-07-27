import re, os

with open(r'C:\Users\34406\Documents\Obsidian Vault\李艳芳.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find file boundaries
boundaries = []
for i, line in enumerate(lines):
    if '文件一' in line or '文件二' in line or '文件三' in line:
        boundaries.append(i)
        # Get clean section name
        name = line.strip().replace('#', '').replace('*', '').strip()
        print(f'Line {i}: {name[:60]}')

if len(boundaries) >= 3:
    # Part 1 = 强化习题 (skip, already done)
    # Part 2 = 强化讲义 (lines from boundaries[1] to boundaries[2]-1)
    # Part 3 = 基础讲义 (lines from boundaries[2] to end)
    pass
else:
    # Try to find the section breaks differently
    # The 强化习题 ends when the next ### 文件 starts
    # Let me just find lines that have the file names
    for i, line in enumerate(lines):
        if '强化习题' in line and 'pdf' in line.lower():
            boundaries.append(i)
        if '强化讲义' in line and 'pdf' in line.lower():
            boundaries.append(i)
        if '基础讲义' in line and 'pdf' in line.lower():
            boundaries.append(i)

print(f'Found {len(boundaries)} boundaries')
for b in boundaries:
    print(f'  Line {b}: {lines[b].strip()[:60]}')
