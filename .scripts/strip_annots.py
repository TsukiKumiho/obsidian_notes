import fitz, os

src_dir = r'C:\Users\34406\Documents\Obsidian Vault\数学专题\李艳芳线面积分\源文件'
out_dir = r'C:\Users\34406\Documents\Obsidian Vault\数学专题\李艳芳线面积分\无注释版'
os.makedirs(out_dir, exist_ok=True)

for f in os.listdir(src_dir):
    if not f.endswith('.pdf'):
        continue
    src = os.path.join(src_dir, f)
    dst = os.path.join(out_dir, f)
    
    print(f'Processing: {f}')
    doc = fitz.open(src)
    ann_count = 0
    for page in doc:
        annots = page.annots()
        if annots:
            for a in annots:
                page.delete_annot(a)
                ann_count += 1
    
    doc.save(dst, garbage=4, deflate=True)
    doc.close()
    print(f'  Removed {ann_count} annotations')
    print(f'  Saved: {dst}\n')

print('All done.')
