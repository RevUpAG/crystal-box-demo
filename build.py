#!/usr/bin/env python3
"""src/ -> English pages at the root and Spanish pages in es/. Fails if a verified fact, file, link, anchor or translation is missing, or if the home page gets crowded again."""
import hashlib, html, json, pathlib, re
here = pathlib.Path(__file__).parent
read = lambda f: (here / f).read_text(encoding='utf8')

PROJECTS = json.loads(read('src/projects.json'))
CATS = ['Residential', 'Commercial', 'Mixed-use']  # a filter shows up once a project has that category
PDF = 'https://crystalboxgroup.com/wp-content/uploads/2026/01/Crystal-Box-Group-ES-%s.pdf'
PRODUCTS = [
    ('Windows and doors', [('Elite', 'elite', 'Elite', 'For single-family homes', '20.6'), ('Multimax', 'multimax', 'Multimax', 'For multi-family projects', '12.8'), ('Prestige', 'prestige', 'Prestige', 'Clean lines and large glass panels', '2.1')]),
    ('Doors', [('Entry Doors', 'entry-doors', 'Entry-Doors', '', '2.4'), ('Designed Doors', 'designed-doors', 'Designed-Doors', '', '7.1'), ('Garage Doors', 'garage-doors', 'Garage-Door', '', '9.9')]),
    ('Details', [('Muntins', 'muntins', 'Muntins', '', '9.4'), ('Railings', 'railings', 'Railings', '', '3.2')]),
]
TEAM = [('Gustavo Parra', 'gustavo-parra', 'CEO & Founder'), ('Rina Byer', 'rina-byer', 'Account Executive'), ('Carlos Lujan', 'carlos-lujan', 'Sales Director'), ('Yeima Armas', 'yeima-armas', 'Estimator Manager'), ('Sindy Ramírez', 'sindy-ramirez', 'Office Assistant'), ('Andres Botero', 'andres-botero', 'Sales Manager'), ('Daniela Soto', 'daniela-soto', 'Project Manager'), ('Edison Rodriguez', 'edison-rodriguez', 'Customer Service'), ('Jose Lugo', 'jose-lugo', 'Logistics Coordinator'), ('Chavela Guay', 'chavela-guay', 'Estimator'), ('Juan Diego Vielma', 'juan-diego-vielma', 'Estimator'), ('Juan José Bermúdez', 'juan-jose-bermudez', 'Sales Executive')]
BRANDS = [('ES Windows and Doors', 'es', 207, 200), ('Euro-Wall', 'euro-wall', 298, 200), ('La Finestra', 'la-finestra', 207, 200)]
NAV = [('projects.html', 'Projects'), ('products.html', 'Products'), ('professionals.html', 'For Professionals'), ('about.html', 'About'), ('contact.html', 'Contact')]
ENGLISH_ONLY = {'privacy.html', 'terms.html'}  # legal texts stay in their original language

def cards(slugs=None, h='h2'):
    ps = [p for s in slugs for p in PROJECTS if p['slug'] == s] if slugs else PROJECTS
    out = []
    for i, p in enumerate(ps):
        w, ht = p.get('size', (1000, 840))
        out.append(f'    <li class="pj{" wide" if i == 0 and len(ps) % 2 else ""}" data-c="{p["cat"]}"><a href="{p["slug"]}.html"><img src="img/project-{p["slug"]}.webp" width="{w}" height="{ht}" loading="lazy" alt="{p["name"]}: {p["alt"][0]}"><div class="t"><{h}>{p["name"]}</{h}><p>{p["city"]}</p></div></a></li>')
    return '\n'.join(out)

def products():
    return '\n'.join(f'  <div class="fam"><h2>{g}</h2><ul>' + ''.join(
        f'<li><a data-pdf="{n}" href="{PDF % pdf}" target="_blank" rel="noopener"><img src="img/product-{f}.webp" width="240" height="240" loading="lazy" alt=""><span><strong>{n}</strong>{d}</span><em>Brochure<small>PDF, {mb} MB</small></em></a></li>'
        for n, f, pdf, d, mb in items) + '</ul></div>' for g, items in PRODUCTS)

def send(label):
    return f'''<div class="send"><button class="btn dark" type="submit">{label}</button><p>By submitting this form, I agree to the <a href="privacy.html">Privacy Policy</a> and <a href="terms.html">Terms &amp; Conditions</a>.</p></div>
      <p class="fail" role="alert" hidden>Your request was not sent. Check your connection and try again, or call +1 (305) 877-4981.</p>
      <p class="cfg">Demo: form and file upload are not connected, nothing is sent. At launch: info@crystalboxgroup.com.</p>'''

LOGOS = '<div class="wrap logos"><p>The brands we use</p>' + ''.join(f'<img src="img/brand-{f}.webp" width="{w}" height="{h}" loading="lazy" alt="{n}">' for n, f, w, h in BRANDS) + '</div>'
TEAM_HTML = '\n'.join(f'    <li><img src="img/team/{f}.webp" width="360" height="360" loading="lazy" alt=""><b>{n}</b><span>{html.escape(r)}</span></li>' for n, f, r in TEAM)

def project(i):
    p, nx = PROJECTS[i], PROJECTS[(i + 1) % len(PROJECTS)]
    facts = [('Location', p['place'])] + ([tuple(p['who'])] if p.get('who') else []) + [('Installation', p['year']), ('Category', p['cat'])]
    v = dict(name=p['name'], slug=p['slug'], place=p['place'], alt=p['alt'][0], photos=str(p['photos']), next=nx['slug'], nextname=nx['name'],
             facts=''.join(f'<div><dt>{k}</dt><dd>{x}</dd></div>' for k, x in facts), text=''.join(f'<p>{x}</p>' for x in p['en']),
             gallery=''.join(f'<img src="img/p/{p["slug"]}-{k}.webp" loading="lazy" alt="{p["name"]}, photo {k}">' for k in range(2, p['photos'] + 1)))
    s = read('src/_project.html')
    for k, x in v.items(): s = s.replace('{{%s}}' % k, x)
    meta = dict(title=f'{p["name"]} | Crystal Box Group', desc=f'{p["name"]}, {p["place"]}. Custom impact windows and doors by Crystal Box Group.', canon=f'portfolio/{p["slug"]}/', nav='projects.html', end=True)
    return meta, s

# ---- English pages
ver = lambda f: f'{f}?v={hashlib.md5(read(f).encode()).hexdigest()[:8]}'
layout = read('src/_layout.html').replace('"style.css"', f'"{ver("style.css")}"').replace('"app.js"', f'"{ver("app.js")}"')
src = {}
for f in sorted((here / 'src').glob('[a-z]*.html')):
    s = f.read_text(encoding='utf8'); src[f.name] = (json.loads(re.match(r'<!--(\{.*?\})-->', s).group(1)), s.split('-->', 1)[1].strip())
for i, p in enumerate(PROJECTS): src[p['slug'] + '.html'] = project(i)
pages = {}
for n, (meta, s) in src.items():
    s = re.sub(r'\{\{projects:([^}]+)\}\}', lambda m: cards(m.group(1).split(','), 'h3'), s)
    for k, v in {'projects': cards(), 'products': products(), 'stage': read('src/_stage.html'), 'logos': LOGOS, 'team': TEAM_HTML}.items(): s = s.replace('{{%s}}' % k, v)
    s = s.replace('{{chips}}', '<button type="button" data-f="" aria-pressed="true">All</button>' + ''.join(f'<button type="button" data-f="{c}" aria-pressed="false">{c}</button>' for c in CATS if any(p['cat'] == c for p in PROJECTS)))
    s = re.sub(r'\{\{send:([^}]+)\}\}', lambda m: send(m.group(1)), s)
    nav = ''.join(f'<a href="{u}"' + (' aria-current="page"' if u == meta.get('nav') else '') + f'>{t}</a>' for u, t in NAV) + '<a class="deal" href="dealer.html">Become a Dealer</a>'
    pg = layout
    for k, v in dict(title=html.escape(meta['title'], quote=False), desc=html.escape(meta['desc']), canon=meta['canon'], cls=meta.get('cls', ''), nav=nav, body=s, end=read('src/_end.html') if meta.get('end') else '').items(): pg = pg.replace('{{%s}}' % k, v)
    pages[n] = pg

# ---- Spanish pages: every visible text and every alt, label, title and description needs an entry
D = json.loads(read('src/es.json'))
for p in PROJECTS:
    D.update(zip(p['en'], p['es'])); D[p['alt'][0]] = p['alt'][1]
NAMES = {p['name'] for p in PROJECTS} | {n for n, *_ in TEAM} | {n for n, *_ in BRANDS} | {'Elite', 'Multimax', 'Prestige', 'Instagram', 'Facebook', 'LinkedIn', 'Crystal Box Group', 'Rev Up Agency Group', 'A', 'B', 'Brochure', 'Blanco Design', 'Project Land', 'Gonzalo Iglesia', 'ES', 'EN', 'North Coconut Grove', '999 Brickell Ave, Suite 560'}
missing = set()
def es(t):
    k = re.sub(r'\s+', ' ', html.unescape(t)).strip()
    if not re.search(r'[A-Za-zÀ-ÿ]', k) or '{{' in k: return t
    out = D.get(k)
    if out is None:
        m = re.fullmatch(r'(.+), photo (\d)', k); c = k.split(': ', 1)
        if k in NAMES or re.fullmatch(r'PDF, [\d.]+ MB|[\w.]+@[\w.]+|Miami, FL 33131|(?:[\w ]+, )?(?:North )?(?:Miami|Fort Lauderdale)(?:, Florida)?|\+1 \(305\).*', k): out = k
        elif m and m.group(1) in NAMES: out = f'{m.group(1)}, foto {m.group(2)}'
        elif len(c) == 2 and c[0] in NAMES and c[1] in D: out = f'{c[0]}: {D[c[1]]}'
        elif k.endswith(' | Crystal Box Group') and k[:-20] in NAMES: out = k
        elif k.endswith('. Custom impact windows and doors by Crystal Box Group.'): out = k.replace('Custom impact windows and doors by', 'Ventanas y puertas de impacto a la medida, por')
        else: missing.add(k); return t
    lead, tail = re.match(r'\s*', t).group(0), re.search(r'\s*$', t).group(0)
    return lead + html.escape(out, quote=False) + tail

def spanish(n, h):
    h = re.sub(r'<(\w+)([^>]*?) data-es="([^"]+)">[^<]*<', r'<\1\2>§\3<', h)
    parts = re.split(r'(<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)', h, flags=re.S); out = []
    for x in parts:
        if x.startswith('<'):
            if not x.startswith(('<!--', '<script', '<style')):
                x = re.sub(r'\b(alt|aria-label|title)="([^"]+)"', lambda m: f'{m.group(1)}="{html.escape(html.unescape(es(m.group(2))))}"', x)
                if re.match(r'<meta (?:name="description"|property="og:(?:title|description|image:alt)")', x): x = re.sub(r'content="([^"]+)"', lambda m: f'content="{html.escape(html.unescape(es(m.group(1))))}"', x)
                x = re.sub(r'\b(src|href|poster)="((?:img|video)/|style\.css|app\.js)', r'\1="../\2', x)
                x = re.sub(r'href="(privacy|terms)\.html"', r'href="../\1.html"', x)
            elif x.startswith('<script src='): x = x.replace('src="app.js', 'src="../app.js')
            out.append(x)
        else: out.append(x[1:] if x.startswith('§') else es(x))
    return ''.join(out)

site = {}
for n, pg in pages.items():
    two = n not in ENGLISH_ONLY
    alt = f'<link rel="alternate" hreflang="en" href="https://revupag.github.io/crystal-box-demo/{n}"><link rel="alternate" hreflang="es" href="https://revupag.github.io/crystal-box-demo/es/{n}">' if two else ''
    sw = lambda u, l, t: f'<a class="lang" href="{u}" lang="{l}" hreflang="{l}" aria-label="{t}">{l.upper()}</a>'
    fill = lambda x, **kw: re.sub(r'\{\{(\w+)\}\}', lambda m: kw[m.group(1)], x)
    site[n] = fill(re.sub(r' data-es="[^"]+"', '', pg), lang='en', locale='en_US', alternate=alt, switch=sw(f'es/{n}' if two else 'es/index.html', 'es', 'Español'))
    if two: site['es/' + n] = fill(spanish(n, pg), lang='es', locale='es_US', alternate=alt, switch=sw(f'../{n}', 'en', 'English'))
assert not missing, 'Translate in src/es.json:\n' + '\n'.join(sorted(missing))

# ---- Checks
text = lambda h: html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)))
body = {n: re.sub(r'<!--.*?-->', '', h, flags=re.S) for n, h in site.items()}
for n, b in body.items():
    d = here / 'es' if n.startswith('es/') else here
    ids = re.findall(r'\bid="([^"]+)"', b)
    assert len(ids) == len(set(ids)), (n, 'duplicate id')
    assert set(re.findall(r'tel:(\+\d+)', b)) == {'+13058774981'} and set(re.findall(r'mailto:([^"]+)', b)) == {'info@crystalboxgroup.com'}, n
    assert not re.search(r'wa\.me|aggregateRating|openingHours|condominium|ending confirmation|Illustrative image|to be supplied|1000 ?\+|\{\{|§', b), n
    assert 'name="robots" content="noindex"' in b and 'rel="canonical" href="https://crystalboxgroup.com/' in b and len(re.findall('<h1', b)) == 1, n
    old = [u for u in re.findall(r'<a\b[^>]*href="(https://crystalboxgroup\.com/[^"]+)"', b) if not u.endswith('.pdf')]
    assert not old, (n, 'link leaves the demo', old)
    files = re.findall(r'(?:src|href|poster)="((?:\.\./)?(?:img|video)/[^"]+)"', b) + re.findall(r'(?:src|href)="([^":]+\.(?:js|css))\?', b)
    assert len([f for f in files if f.endswith(('.js', '.css'))]) == 2, (n, 'script or stylesheet')
    for u in files: assert (d / u).resolve().exists(), (n, u)
    json.loads(re.search(r'ld\+json">(.*?)</script>', site[n], re.S).group(1))
    for u in re.findall(r'<a\b[^>]*href="([^":]+?)"', b):
        page, _, anchor = u.partition('#'); page = page.split('?')[0]
        if n.startswith('es/'): page = page[3:] if page.startswith('../') else 'es/' + page
        page = page or n
        if u.startswith('#'): page = n
        assert page in site, (n, 'dead link', u)
        assert not anchor or f'id="{anchor}"' in body[page], (n, 'dead anchor', u)
opts = set(re.findall(r'<option value="([^"]+)">', re.search(r'id="role".*?</select>', body['quote.html'], re.S).group(0)))
for b in body.values():
    for r in re.findall(r'\?role=([^"&]+)', b): assert r.replace('+', ' ') in opts, r
for d in re.findall(r'\?docs=([^"&]+)', body['professionals.html']): assert f"'{d.replace('+', ' ')}':" in read('app.js'), d
for q in ['As an architect, precision and aesthetics are non-negotiable for me. Crystal Box delivers systems that align with both. I love that everything is custom and comes with installation so design is never affected.', 'I’ve used Crystal Box on a few projects now, and what I really appreciate is how easy they make it to get exactly what I need. It’s refreshing to work with a company that pays attention to design and quality.', 'The team is always there to answer questions and help us make decisions during the quoting process so I can offer my clients the best quality and price to the homes they are building.']: assert any(q in b for b in body.values()), q
assert len(PROJECTS) == 9 and len(re.findall(r'data-pdf="', body['products.html'])) == 8 and len(TEAM) == 12
assert max(here.glob('video/hero*.mp4'), key=lambda f: f.stat().st_size).stat().st_size < 4_000_000
home = body['index.html'].split('<main', 1)[1].split('</main>')[0]; words = len(text(home).split()); secs = len(re.findall('<section', home))
assert words <= 135 and secs <= 6, ('home is crowded', words, secs)

(here / 'es').mkdir(exist_ok=True)
for n, h in site.items(): (here / n).write_text(h, encoding='utf8')
print(len(site), 'pages,', sum(n.startswith('es/') for n in site), 'in Spanish'); print('home:', words, 'words,', secs, 'sections')
