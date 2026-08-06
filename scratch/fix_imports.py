import glob
import os

files = glob.glob('backend/**/*.py', recursive=True)
count = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'from modules.' in content:
        content = content.replace('from modules.', 'from backend.modules.')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        count += 1
print(f'Updated {count} files.')
