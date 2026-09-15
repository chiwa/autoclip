import sys

with open('app/web/static/history.html', 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

with open('minified_render.txt', 'r', encoding='utf-8') as f:
    render = f.read().strip()

lines[31] = render

with open('app/web/static/history.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
