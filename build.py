#!/usr/bin/env python3
"""src.html + img/ -> index.html (one self-contained file). Fails if a verified fact, link or anchor is wrong."""
import base64, json, pathlib, re
here = pathlib.Path(__file__).parent
h = (here / 'src.html').read_text(encoding='utf8')
MIME = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg'}
def inline(m):
    f = here / 'img' / m.group(2)
    return f'{m.group(1)}="data:{MIME[f.suffix]};base64,{base64.b64encode(f.read_bytes()).decode()}"'
body = re.sub(r'<!--.*?-->', '', h, flags=re.S)
out = re.sub(r'\b(src|href)="img/([^"]+)"', lambda m: m.group(0) if 'casa-bahia' in m.group(2) else inline(m), h)
assert set(re.findall(r'tel:(\+\d+)', h)) == {'+13058774981'}
assert set(re.findall(r'mailto:([^"]+)', h)) == {'info@crystalboxgroup.com'}
assert 'wa.me' not in h and 'aggregateRating' not in h and 'openingHours' not in h
ids = re.findall(r'\bid="([^"]+)"', body)
assert len(ids) == len(set(ids)), 'duplicate id'
missing = [a for a in re.findall(r'href="#([^"]+)"', body) if a not in ids]
assert not missing, missing
roles = set(re.findall(r'data-role="([^"]+)"', body)); opts = set(re.findall(r'<option>([^<]+)</option>', re.search(r'id="role".*?</select>', body, re.S).group(0)))
assert roles == opts, roles ^ opts
for n in ['123 NoMi Building', '2905 Washington', 'Casa Carrera', 'Casa Bahia', 'La Finestra', 'Villa Camila', 'Casa Estrella', 'Villa Escondida', 'Six Villas']:
    assert f'<h3>{n}</h3>' in body and f'Project photo — {n}, to be supplied' in body, n
for q in ['I love that everything is custom and comes with installation so design is never affected.', 'It’s refreshing to work with a company that pays attention to design and quality.', 'The team is always there to answer questions…']:
    assert q in body, q
assert len(re.findall('<h1', body)) == 1
assert len(re.findall(r'<a data-pdf="[A-Z][^"]+" href="https://crystalboxgroup.com/[^"]+\.pdf"', body)) == 8
json.loads(re.search(r'ld\+json">(.*?)</script>', h, re.S).group(1))
(here / 'index.html').write_text(out, encoding='utf8')
print('index.html', round(len(out) / 1024), 'KB')
