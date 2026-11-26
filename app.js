/* ===== CONFIG: FORM DESTINATION =====
   Paste a Formspree endpoint (https://formspree.io/f/XXXXXXXX) or your own URL that delivers to info@crystalboxgroup.com.
   Empty = demo mode: forms validate and show the success state, and nothing leaves the browser. */
const FORM_ENDPOINT = '';

const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const still = matchMedia('(prefers-reduced-motion:reduce)').matches;
const ES = document.documentElement.lang === 'es', t = (en, es) => ES ? es : en;
const track = (event, data) => dataLayer.push({ event, ...data });

/* ---- Tracking ---- */
document.addEventListener('click', e => {
  const a = e.target.closest('a'); if (!a) return;
  if (a.protocol === 'tel:') track('call_click', { placement: a.dataset.place });
  if (a.dataset.pdf) track('brochure_download', { product: a.dataset.pdf });
});

/* ---- Menu ---- */
const nav = $('#nav'), burger = $('.burger');
const menu = on => { nav.classList.toggle('on', on); burger.setAttribute('aria-expanded', on); burger.textContent = on ? t('Close', 'Cerrar') : t('Menu', 'Menú'); };
burger.addEventListener('click', () => menu(!nav.classList.contains('on')));
document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('on')) { menu(false); burger.focus(); } });
addEventListener('pageshow', e => e.persisted && menu(false));

/* ---- Hero video: stays still until the drawing has opened, rests off screen, off with reduced motion or Save-Data ---- */
const hv = $('.hero video'), vp = $('.vp');
if (hv && (still || navigator.connection?.saveData)) { hv.removeAttribute('autoplay'); hv.replaceChildren(); hv.load(); }
else if (hv) {
  let byUser = false, onScreen = true, opened = false;
  const play = () => opened && onScreen && !byUser && hv.play().catch(() => { /* autoplay blocked: the poster stays */ });
  hv.pause();
  Promise.all($('.cad').getAnimations().map(a => a.finished)).finally(() => { opened = true; play(); });
  hv.addEventListener('playing', () => { vp.hidden = false; if (!opened) hv.pause(); });
  new IntersectionObserver(es => { onScreen = es[0].isIntersecting; onScreen ? play() : hv.pause(); }).observe(hv);
  vp.addEventListener('click', () => { byUser = !byUser; vp.classList.toggle('off', byUser); vp.setAttribute('aria-label', byUser ? t('Play video', 'Reproducir video') : t('Pause video', 'Pausar video')); byUser ? hv.pause() : play(); });
}

/* ---- Project filter: an odd count opens with one wide photo, so no card is left alone ---- */
$$('.chips button').forEach(b => b.addEventListener('click', () => {
  $$('.chips button').forEach(x => x.setAttribute('aria-pressed', x === b));
  const all = $$('.pj'), shown = all.filter(c => !b.dataset.f || c.dataset.c === b.dataset.f);
  all.forEach(c => { c.hidden = !shown.includes(c); c.classList.toggle('wide', c === shown[0] && shown.length % 2 === 1); });
  $('#count').textContent = shown.length + t(' projects shown', ' proyectos');
}));

/* ---- Videos on the Projects page: one at a time ---- */
$$('.reels video').forEach((v, i, all) => v.addEventListener('play', () => all.forEach(o => o !== v && o.pause())));

/* ---- Process: plays when it comes into view, stops if you choose a step ---- */
const stage = $('#stage');
if (stage) {
  const steps = $$('.step'); let timer, chosen = still;
  const go = n => { stage.dataset.step = n; steps.forEach((s, i) => i === n - 1 ? s.setAttribute('aria-current', 'step') : s.removeAttribute('aria-current')); };
  if (!still) delete stage.dataset.step;
  steps.forEach((s, i) => s.addEventListener('click', () => { chosen = true; clearTimeout(timer); go(i + 1); }));
  new IntersectionObserver(es => {
    clearTimeout(timer); if (chosen || !es[0].isIntersecting) return;
    go(1); timer = setTimeout(() => { go(2); timer = setTimeout(() => go(3), 3400); }, 2800);
  }, { threshold: .4 }).observe(stage);
}

/* ---- Quote page: role and documents arrive from the link that was clicked ---- */
const DOCS = { 'Spec sheets': 'Fichas técnicas', 'Product approvals': 'Aprobaciones de producto', 'CAD and shop drawings': 'CAD y planos de taller' };
const ask = new URLSearchParams(location.search), role = $('#role');
if (role && [...role.options].some(o => o.value && o.value === ask.get('role'))) role.value = ask.get('role');
const doc = ask.get('docs');
if ($('#more') && Object.hasOwn(DOCS, doc)) { $('#message').value = t('Documents requested: ' + doc, 'Documentos solicitados: ' + DOCS[doc]); $('#more').open = true; }

/* ---- Forms: one validator and one sender for quote, dealer and work ---- */
const MSG = t(
  { name: 'Add your name.', email: 'Add a valid email, like name@studio.com.', phone: 'Add a phone number with area code.', role: 'Select your role.', category: 'Choose a category.', type: 'Choose a type.', city: 'Add the project city.', company: 'Add your company name.', website: 'Add your company website.', place: 'Add your city and state.', country: 'Add your country.', why: 'Tell us why you are interested.', resume: 'Attach your resume.', interest: 'Choose one.', message: 'Write your message.' },
  { name: 'Escriba su nombre.', email: 'Escriba un correo válido, como nombre@estudio.com.', phone: 'Escriba un teléfono con código de área.', role: 'Seleccione su rol.', category: 'Elija una categoría.', type: 'Elija un tipo.', city: 'Escriba la ciudad del proyecto.', company: 'Escriba el nombre de su empresa.', website: 'Escriba el sitio web de su empresa.', place: 'Escriba su ciudad y estado.', country: 'Escriba su país.', why: 'Cuéntenos por qué le interesa.', resume: 'Adjunte su hoja de vida.', interest: 'Elija una opción.', message: 'Escriba su mensaje.' });
const valid = el => el.type === 'radio' ? !!el.form.elements[el.name].value : el.type === 'tel' ? el.value.replace(/\D/g, '').length >= 10 : el.value.trim() !== '' && el.checkValidity();
const mark = (el, bad) => { el.type === 'radio' ? el.closest('fieldset').classList.toggle('bad', bad) : bad ? el.setAttribute('aria-invalid', 'true') : el.removeAttribute('aria-invalid'); $('#e-' + el.name).textContent = bad ? MSG[el.name] : ''; };
$$('.cfg').forEach(p => p.hidden = !!FORM_ENDPOINT);
$$('form').forEach(form => {
  const must = $$('[required]', form), btn = $('button[type=submit]', form), label = btn.textContent, fail = $('.fail', form), box = $('.sent', form.parentNode);
  form.addEventListener('input', e => { const el = must.find(m => m.name === e.target.name); if (el && $('#e-' + el.name).textContent && valid(el)) mark(el, false); });
  form.addEventListener('submit', async e => {
    e.preventDefault();
    must.forEach(el => mark(el, !valid(el)));
    const bad = must.find(el => !valid(el));
    if (bad) { bad.focus(); return; }
    const d = new FormData(form), v = k => String(d.get(k) || '').trim(), kind = form.dataset.event;
    d.append('form', kind);
    fail.hidden = true;
    if (FORM_ENDPOINT) {
      btn.disabled = true; btn.textContent = t('Sending…', 'Enviando…');
      let ok = false;
      try { ok = (await fetch(FORM_ENDPOINT, { method: 'POST', body: d, headers: { Accept: 'application/json' } })).ok; } catch { /* shown below */ }
      btn.disabled = false; btn.textContent = label;
      if (!ok) { fail.hidden = false; return; }
    }
    track(kind, kind === 'quote_submit' ? { role: v('role'), project_category: v('category'), project_type: v('type'), timeline: v('timeline'), openings: v('openings') } : {});
    $('h2', box).textContent = t('Thank you, ', 'Gracias, ') + v('name').split(' ')[0] + '.';
    $('p', box).textContent = !FORM_ENDPOINT ? t('This is the confirmation your clients will see. Demo mode: nothing was sent.', 'Esta es la confirmación que verán sus clientes. Modo demo: no se envió nada.') : kind === 'quote_submit' ? t('Your request was sent. A Crystal Box specialist will contact you to discuss your needs.', 'Recibimos su solicitud. Un especialista de Crystal Box le contactará.') : t('Your request was sent to Crystal Box.', 'Crystal Box recibió su mensaje.');
    const shown = k => { const el = form.elements[k], o = el?.selectedOptions?.[0] || $(`input[name=${k}]:checked + span`, form); return o ? o.textContent : v(k); };
    const dl = $('dl', box);
    if (dl) dl.replaceChildren(...[[t('Project', 'Proyecto'), 'category'], [t('Type', 'Tipo'), 'type'], [t('City', 'Ciudad'), 'city'], [t('Role', 'Rol'), 'role'], [t('Timeline', 'Plazo'), 'timeline'], [t('Openings', 'Vanos'), 'openings'], [t('Message', 'Mensaje'), 'message']].filter(([, k]) => v(k)).map(([label, k]) => { const r = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd'); dt.textContent = label; dd.textContent = shown(k); r.append(dt, dd); return r; }));
    form.hidden = true; box.hidden = false; box.focus({ preventScroll: true }); box.scrollIntoView({ block: 'center' });
  });
});
