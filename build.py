#!/usr/bin/env python3
"""src.html -> index.html. Inlines what the first screen needs (logo, icon, hero poster and drawing); lazy photos stay in img/. Fails if a verified fact, file, link or anchor is wrong."""
import base64, json, pathlib, re
here = pathlib.Path(__file__).parent
h = (here / 'src.html').read_text(encoding='utf8')
MIME = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg'}
def inline(m):
    f = here / 'img' / m.group(2)
    return f'{m.group(1)}="data:{MIME[f.suffix]};base64,{base64.b64encode(f.read_bytes()).decode()}"'
body = re.sub(r'<!--.*?-->', '', h, flags=re.S)
out = re.sub(r'<(?:img|link|video)\b[^>]*>', lambda t: t.group(0) if 'loading="lazy"' in t.group(0) else re.sub(r'\b(src|href|poster)="img/([^"]+)"', inline, t.group(0)), h)
for f in re.findall(r'(?:src|href|poster)="((?:img|video)/[^"]+)"', body):
    assert (here / f).exists(), f
assert max(f.stat().st_size for f in (here / 'video').iterdir()) < 4_000_000
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
    assert re.search(rf'<li class="pj" data-c="(res|com|)"><figure><img src="img/project-[^>]+alt="{n}: [^>]+></figure>\s*<div class="t"><h3>{n}</h3>', body), n
for q in ['I love that everything is custom and comes with installation so design is never affected.', 'It’s refreshing to work with a company that pays attention to design and quality.', 'The team is always there to answer questions and help us make decisions during the quoting process so I can offer my clients the best quality and price to the homes they are building.']:
    assert q in body, q
assert len(re.findall('<h1', body)) == 1
assert 'condominium' not in body and 'ending confirmation' not in body and 'noindex' in h and 'canonical" href="https://crystalboxgroup.com/"' in h
assert len(re.findall(r'<a data-pdf="[A-Z][^"]+" href="https://crystalboxgroup.com/[^"]+\.pdf"', body)) == 8
json.loads(re.search(r'ld\+json">(.*?)</script>', h, re.S).group(1))
(here / 'index.html').write_text(out, encoding='utf8')
print('index.html', round(len(out) / 1024), 'KB')
