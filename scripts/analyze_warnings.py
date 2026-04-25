import re
from collections import Counter

def analyze_warnings(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"Read {len(lines)} lines from {file_path}")
    print("--- SAMPLE ---")
    for l in lines[:20]:
        print(l.strip())
    print("--- END SAMPLE ---")

    types = ["DeprecationWarning", "RuntimeWarning", "UserWarning", "FutureWarning"]
    summary = Counter()
    
    # regex for "File:Line: Category: Message"
    warning_pattern = re.compile(r"([a-zA-Z0-9_\\\/\.\-]+):(\d+): (\w+): (.*)")

    for line in lines:
        match = warning_pattern.search(line)
        if match:
            category = match.group(3)
            message = match.group(4)[:100]
            summary[(category, message)] += 1
        else:
            for t in types:
                if t in line:
                    summary[(t, "Unknown source/message")] += 1
                
    print(f"\n{'Category':<25} | {'Count':<5} | {'Message'}")
    print("-" * 120)
    for (cat, msg), count in summary.most_common():
        print(f"{cat:<25} | {count:<5} | {msg}")

if __name__ == "__main__":
    analyze_warnings("warnings_report_clean.txt")
