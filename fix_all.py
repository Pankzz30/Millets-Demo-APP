
import os
import glob

replacements = {
    'var(--cream)': 'var(--bg-primary)',
    'var(--cream-mid)': 'var(--bg-secondary)',
    'var(--blue-dark)': 'var(--brand-color)',
    'var(--blue-light)': 'var(--brand-light)',
    'var(--red)': 'var(--status-danger)',
    'var(--gold)': 'var(--accent-color)',
    'var(--orange)': 'var(--status-warning)'
}

for file in glob.glob('templates/*.html'):
    with open(file, 'r', encoding='utf8') as f:
        text = f.read()
    orig = text
    for old, new in replacements.items():
        text = text.replace(old, new)
    if text != orig:
        with open(file, 'w', encoding='utf8') as f:
            f.write(text)
        print('Updated', file)

