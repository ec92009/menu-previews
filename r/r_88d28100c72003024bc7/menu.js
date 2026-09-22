const data=JSON.parse(document.getElementById('data').textContent);
const ui={
 es:{back:'← Cambiar idioma',category:'Ensaladas',sample:'Selección de la carta',note:'Un comienzo fresco',notice:'Muestra de la carta · Precios de la carta original, pendientes de confirmación.',photo:'Fotografías de la carta original del restaurante.',top:'Volver arriba ↑'},
 en:{back:'← Change language',category:'Salads',sample:'A taste of our menu',note:'A fresh beginning',notice:'Menu sample · Prices from the original menu, awaiting confirmation.',photo:'Photographs from the restaurant’s original menu.',top:'Back to top ↑'},
 fr:{back:'← Changer de langue',category:'Salades',sample:'Un aperçu de notre carte',note:'Pour commencer en fraîcheur',notice:'Extrait de la carte · Prix de la carte originale, à confirmer.',photo:'Photographies de la carte originale du restaurant.',top:'Retour en haut ↑'},
 de:{back:'← Sprache ändern',category:'Salate',sample:'Eine Auswahl unserer Speisen',note:'Ein frischer Anfang',notice:'Menüvorschau · Preise aus der Originalkarte, noch zu bestätigen.',photo:'Fotos aus der Originalkarte des Restaurants.',top:'Nach oben ↑'},
 it:{back:'← Cambia lingua',category:'Insalate',sample:'Una selezione del nostro menù',note:'Un inizio fresco',notice:'Anteprima del menù · Prezzi del menù originale, da confermare.',photo:'Fotografie del menù originale del ristorante.',top:'Torna su ↑'},
 nl:{back:'← Andere taal',category:'Salades',sample:'Een selectie van onze kaart',note:'Een fris begin',notice:'Voorbeeldmenu · Prijzen uit de oorspronkelijke menukaart, nog te bevestigen.',photo:'Foto’s uit de oorspronkelijke menukaart van het restaurant.',top:'Naar boven ↑'}
};
const policyLabels={es:['Privacidad','Condiciones','Eliminación de datos'],en:['Privacy','Terms','Data deletion'],fr:['Confidentialité','Conditions','Suppression des données'],de:['Datenschutz','Nutzungsbedingungen','Datenlöschung'],it:['Privacy','Condizioni','Cancellazione dei dati'],nl:['Privacy','Voorwaarden','Gegevens verwijderen']};
let current='es';const welcome=document.getElementById('welcome'),menu=document.getElementById('menu');
function show(lang,navigate=true){if(!ui[lang])return;current=lang;const t=ui[lang];document.querySelectorAll('[data-policy]').forEach((el,i)=>el.textContent=policyLabels[lang][i]);document.documentElement.lang=lang;document.title='La Paella · '+t.sample;
for(const [id,value] of Object.entries({'language-back':t.back,notice:t.notice,'photo-note':t.photo,'footer-up':t.top}))document.getElementById(id).textContent=value;
document.querySelectorAll('[data-category]').forEach(el=>{el.textContent=data.categories.find(c=>c.category_id===el.dataset.category).names[lang];});
document.getElementById('up').setAttribute('aria-label',t.top);
document.querySelectorAll('.dish').forEach(el=>{const item=data.items.find(x=>x.item_id===el.dataset.item);el.querySelector('h3').textContent=item.names[lang];el.querySelector('.price').textContent=new Intl.NumberFormat(lang,{style:'currency',currency:'EUR'}).format(item.price_minor/100);el.querySelector('img').alt=item.names[lang];const original=el.querySelector('.original');original.textContent=item.names[data.original_language];original.hidden=lang===data.original_language;});
document.querySelectorAll('[data-language]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.language===lang)));
if(navigate){const url=new URL(location.href);url.searchParams.set('lang',lang);url.hash='menu';history.replaceState(null,'',url);menu.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});document.getElementById('language-back').focus({preventScroll:true});}updateCategory();}
document.querySelectorAll('[data-language]').forEach(b=>b.addEventListener('click',()=>show(b.dataset.language)));
document.getElementById('language-back').addEventListener('click',()=>{const url=new URL(location.href);url.hash='welcome';history.replaceState(null,'',url);welcome.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});document.querySelector('[data-language="'+current+'"]').focus({preventScroll:true});});
const selected=new URLSearchParams(location.search).get('lang');show(ui[selected]?selected:'es',false);
if(ui[selected]&&!location.hash)requestAnimationFrame(()=>menu.scrollIntoView({behavior:'instant'}));

// Keep the active category aligned with the visible section and anchor jumps.
function updateCategory(){if(menu.hidden)return;let active=data.categories[0].category_id;for(const section of document.querySelectorAll('.menu-category')){if(section.getBoundingClientRect().top<=130)active=section.id;}document.querySelectorAll('nav [data-category]').forEach(link=>{if(link.dataset.category===active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});}
addEventListener('scroll',updateCategory,{passive:true});updateCategory();
