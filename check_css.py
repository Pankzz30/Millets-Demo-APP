import re

with open('templates/landing.html', 'r', encoding='utf8') as f:
    content = f.read()

css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if css_match:
    css = css_match.group(1)
    classes_in_css = set(re.findall(r'\.([a-zA-Z0-9_-]+)', css))
    html_match = re.search(r'</style>(.*)', content, re.DOTALL)
    if html_match:
        html = html_match.group(1)
        classes_in_html = set()
        for m in re.finditer(r'class=[\"\'\']([^\"\']+)[\"\'\']', html):
            classes_in_html.update(m.group(1).split())
        missing = classes_in_html - classes_in_css
        print('Missing CSS classes:', sorted(list(missing)))
