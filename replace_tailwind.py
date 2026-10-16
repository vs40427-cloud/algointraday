with open('E:/Projects/algo intraday/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_line = '<script src="https://cdn.tailwindcss.com"></script>'
new_line = '<link rel="stylesheet" href="style.css">'

if old_line in content:
    content = content.replace(old_line, new_line)
    with open('E:/Projects/algo intraday/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced Tailwind CDN with static style.css')
else:
    print('Pattern not found')