import os
size = os.path.getsize('E:/Projects/algo intraday/style.css')
print('style.css size:', size, 'bytes (%.1f KB)' % (size/1024))
with open('E:/Projects/algo intraday/style.css', 'r', encoding='utf-8') as f:
    content = f.read()
    print(content[:300])