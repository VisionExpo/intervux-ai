import os
import re

def fix_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return
    
    new_content = content
    
    # 1. Ensure 'timezone' is imported if we're going to use it
    if ('lambda: datetime.now(timezone.utc)' in content or 'datetime.utcfromtimestamp' in content) and 'timezone' not in content:
        if 'from datetime import datetime' in content:
            new_content = new_content.replace('from datetime import datetime', 'from datetime import datetime, timezone')
        elif 'import datetime' in content and 'from datetime import' not in content:
            # If it's just 'import datetime', we're fine, we'll use datetime.timezone
            pass
        else:
            # Add it at the top if needed, but usually one of the above is true
            pass

    # 2. Fix datetime.now(timezone.utc) calls
    new_content = new_content.replace('datetime.now(timezone.utc)', 'datetime.now(timezone.utc)')
    
    # 3. Fix SQLAlchemy defaults: default=lambda: datetime.now(timezone.utc) -> default=lambda: datetime.now(timezone.utc)
    new_content = re.sub(r'default=datetime\.utcnow', 'default=lambda: datetime.now(timezone.utc)', new_content)
    new_content = re.sub(r'onupdate=datetime\.utcnow', 'onupdate=lambda: datetime.now(timezone.utc)', new_content)
    
    # 4. Fix remaining lambda: datetime.now(timezone.utc) references (e.g. assignments)
    # Be careful not to double-replace
    new_content = re.sub(r'(?<!lambda: )datetime\.utcnow', 'lambda: datetime.now(timezone.utc)', new_content)
    
    # 5. Fix datetime.fromtimestamp(ts, tz=timezone.utc) -> datetime.fromtimestamp(ts, tz=timezone.utc)
    new_content = re.sub(r'datetime\.utcfromtimestamp\((.*?)\)', r'datetime.fromtimestamp(\1, tz=timezone.utc)', new_content)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {path}")

# Target directories
targets = ['backend', 'tests', 'scripts']

for target in targets:
    for root, dirs, files in os.walk(target):
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
