with open('warnings_report.txt', 'rb') as f:
    data = f.read()
content = data.decode('utf-16')
with open('warnings_report_clean.txt', 'w', encoding='utf-8') as f2:
    f2.write(content)
print("Conversion complete.")
