/* Halvren command palette — ⌘K / Ctrl+K.
 *
 * Indexes: 20 operators (from /data/viz-data.json), 10 checklist questions,
 * notes, key pages. Pure JS, no deps. Fuzzy substring + token match.
 * Keyboard: ↑/↓ to move, Enter to open, Esc to close. Hint badge mounts
 * inside .nav-right (desktop only, hidden < 640px).
 */
(function(){
  if (document.querySelector('[data-halvren-cmdk]')) return;
  if (window.self !== window.top) return;

  var PAGES = [
    { title:'Home',              href:'/',             tag:'PG', meta:'' },
    { title:'Research',          href:'/research',     tag:'PG', meta:'' },
    { title:'Coverage',          href:'/coverage',     tag:'PG', meta:'' },
    { title:'Notes',             href:'/notes',        tag:'PG', meta:'' },
    { title:'Checklist',         href:'/checklist',    tag:'PG', meta:'' },
    { title:'Checklist Live',    href:'/checklist/live',tag:'PG',meta:'' },
    { title:'Cycle Map',         href:'/cycle-map',    tag:'PG', meta:'' },
    { title:'Cost Curves',       href:'/cost-curves',  tag:'PG', meta:'' },
    { title:'Letters',           href:'/letters',      tag:'PG', meta:'' },
    { title:'Digest',            href:'/digest',       tag:'PG', meta:'' },
    { title:'Performance',       href:'/performance',  tag:'PG', meta:'' },
    { title:'Process',           href:'/process',      tag:'PG', meta:'' },
    { title:'About',             href:'/about',        tag:'PG', meta:'' },
    { title:'Access',            href:'/access',       tag:'PG', meta:'' },
    { title:'Glossary',          href:'/glossary',     tag:'PG', meta:'' }
  ];

  var NOTES = [
    { title:"The cost curve is a lie if you let them pick the quartile", href:"/notes/cost-curve-is-a-lie-if-you-pick-the-quartile" },
    { title:"What boring looks like on a thirty-year chart", href:"/notes/boring-thirty-year-chart-canadian-infrastructure" },
    { title:"How to read a Canadian oil & gas operator in seven numbers", href:"/notes/how-to-read-canadian-oil-gas-operator-seven-numbers" },
    { title:"Insider buying vs. insider granting", href:"/notes/insider-buying-vs-granting" },
    { title:"ROIC on incremental capital, in plain English", href:"/notes/roic-incremental-capital-plain-english" },
    { title:"Silver's per-share problem", href:"/notes/silver-per-share-problem" },
    { title:"The uranium operator's checklist", href:"/notes/uranium-operator-checklist" },
    { title:"The dividend that survived: 26 raises at CNQ", href:"/notes/dividend-that-survived-cnq" },
    { title:"Pipelines are turnpikes, not commodity bets", href:"/notes/pipelines-are-turnpikes-not-commodity-bets" },
    { title:"What 2015 and 2020 told us about every Canadian energy operator", href:"/notes/what-2015-and-2020-told-us-canadian-energy" }
  ].map(function(n){ n.tag='NOTE'; n.meta=''; return n; });

  var CHECKLIST = [
    { n:1,  q:"Does the business generate free cash flow through the full cycle?" },
    { n:2,  q:"Do the unit economics work at the worst price of the last decade?" },
    { n:3,  q:"What does the balance sheet look like at trough pricing?" },
    { n:4,  q:"What is the return on incremental capital when management reinvests?" },
    { n:5,  q:"How much insider ownership was bought, not granted?" },
    { n:6,  q:"What did management do in 2015 and 2020?" },
    { n:7,  q:"Is compensation tied to per-share value or to size?" },
    { n:8,  q:"Is succession visible?" },
    { n:9,  q:"Where are we on the cost curve that matters?" },
    { n:10, q:"What does a normal decade look like, and does the business still work at that price?" }
  ].map(function(c){ return { title:'Q'+c.n+'. '+c.q, href:'/checklist#q'+c.n, tag:'Q'+c.n, meta:'CHECKLIST' }; });

  var index = PAGES.concat(NOTES).concat(CHECKLIST);

  function loadOperators(){
    return fetch('/data/viz-data.json', { cache:'default' })
      .then(function(r){ return r.ok ? r.json() : null; })
      .then(function(d){
        if (!d || !d.operators) return;
        d.operators.forEach(function(op){
          index.push({
            title: op.short_name,
            href: op.research_url,
            tag: op.ticker,
            meta: (op.sector || '').toUpperCase()
          });
        });
      })
      .catch(function(){});
  }

  function el(tag, attrs, kids){
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs){
      if (k==='class') n.className=attrs[k];
      else if (k==='text') n.textContent=attrs[k];
      else if (k==='html') n.innerHTML=attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    if (kids) kids.forEach(function(c){ n.appendChild(c); });
    return n;
  }

  function search(q){
    q = (q||'').trim().toLowerCase();
    if (!q) return index.slice(0, 40);
    var tokens = q.split(/\s+/);
    return index.filter(function(it){
      var hay = (it.title + ' ' + (it.tag||'') + ' ' + (it.meta||'')).toLowerCase();
      return tokens.every(function(t){ return hay.indexOf(t) !== -1; });
    }).slice(0, 60);
  }

  function group(items){
    var byTag = { 'OPERATOR':[], 'NOTE':[], 'CHECKLIST':[], 'PAGE':[] };
    items.forEach(function(it){
      if (it.tag === 'PG') byTag['PAGE'].push(it);
      else if (it.tag === 'NOTE') byTag['NOTE'].push(it);
      else if (it.meta === 'CHECKLIST') byTag['CHECKLIST'].push(it);
      else byTag['OPERATOR'].push(it);
    });
    return byTag;
  }

  function mount(){
    var hint = el('button', { class:'halvren-cmdk-hint', 'aria-label':'Open command palette', 'data-cmdk-hint':'', type:'button' });
    var sym = el('kbd', { text: (/Mac|iPhone|iPad/.test(navigator.platform) ? '⌘K' : 'Ctrl+K') });
    hint.appendChild(sym);

    var navRight = document.querySelector('.nav-right');
    if (navRight){
      var firstBtn = navRight.querySelector('button, a');
      if (firstBtn) navRight.insertBefore(hint, firstBtn);
      else navRight.appendChild(hint);
    }

    var backdrop = el('div', { class:'halvren-cmdk-backdrop', 'data-halvren-cmdk':'', 'data-open':'false', role:'dialog', 'aria-modal':'true', 'aria-label':'Command palette' });
    var dialog = el('div', { class:'halvren-cmdk' });
    var searchRow = el('div', { class:'halvren-cmdk-search' });
    searchRow.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"></circle><path d="m21 21-4.3-4.3"></path></svg>';
    var input = el('input', { class:'halvren-cmdk-input', type:'text', placeholder:'Search operators, notes, checklist…', autocomplete:'off', spellcheck:'false', 'aria-label':'Search' });
    searchRow.appendChild(input);
    var list = el('div', { class:'halvren-cmdk-list', role:'listbox' });
    var foot = el('div', { class:'halvren-cmdk-foot' });
    foot.innerHTML = '<span><kbd>↑</kbd><kbd>↓</kbd> NAVIGATE · <kbd>↵</kbd> OPEN · <kbd>ESC</kbd> CLOSE</span><span>HALVREN</span>';
    dialog.appendChild(searchRow);
    dialog.appendChild(list);
    dialog.appendChild(foot);
    backdrop.appendChild(dialog);
    document.body.appendChild(backdrop);

    var active = 0;
    var results = [];

    function render(){
      list.innerHTML = '';
      var q = input.value;
      results = search(q);
      if (!results.length){
        list.appendChild(el('div', { class:'halvren-cmdk-empty', text:'Nothing matches "'+q+'". Try a ticker, a year, or a question number.' }));
        return;
      }
      var groups = group(results);
      var flat = [];
      ['OPERATOR','NOTE','CHECKLIST','PAGE'].forEach(function(key){
        var arr = groups[key];
        if (!arr.length) return;
        var grp = el('div', { class:'halvren-cmdk-group' });
        grp.appendChild(el('div', { class:'halvren-cmdk-grouph', text: key === 'PAGE' ? 'PAGES' : key+'S' }));
        arr.forEach(function(it){
          var idx = flat.length;
          var row = el('a', { class:'halvren-cmdk-item', href: it.href, role:'option', 'data-idx': String(idx) });
          row.appendChild(el('span', { class:'ci-tag', text: it.tag }));
          row.appendChild(el('span', { class:'ci-title', text: it.title }));
          if (it.meta) row.appendChild(el('span', { class:'ci-meta', text: it.meta }));
          row.addEventListener('mouseenter', function(){ setActive(idx); });
          grp.appendChild(row);
          flat.push(row);
        });
        list.appendChild(grp);
      });
      results = flat;
      if (active >= results.length) active = 0;
      setActive(active);
    }

    function setActive(i){
      active = i;
      results.forEach(function(r, idx){ r.setAttribute('data-active', idx === active ? 'true' : 'false'); });
      var el2 = results[active];
      if (el2 && el2.scrollIntoView) el2.scrollIntoView({ block:'nearest' });
    }

    function open(){
      backdrop.setAttribute('data-open','true');
      document.body.style.overflow = 'hidden';
      input.value = '';
      render();
      setTimeout(function(){ input.focus(); }, 30);
    }

    function close(){
      backdrop.setAttribute('data-open','false');
      document.body.style.overflow = '';
    }

    hint.addEventListener('click', open);

    document.addEventListener('keydown', function(e){
      var mod = e.metaKey || e.ctrlKey;
      if (mod && (e.key === 'k' || e.key === 'K')){
        e.preventDefault();
        if (backdrop.getAttribute('data-open') === 'true') close();
        else open();
        return;
      }
      if (backdrop.getAttribute('data-open') !== 'true') return;
      if (e.key === 'Escape'){ e.preventDefault(); close(); }
      else if (e.key === 'ArrowDown'){ e.preventDefault(); setActive(Math.min(active+1, results.length-1)); }
      else if (e.key === 'ArrowUp'){   e.preventDefault(); setActive(Math.max(active-1, 0)); }
      else if (e.key === 'Enter'){
        var it = results[active];
        if (it){ e.preventDefault(); window.location.href = it.getAttribute('href'); }
      }
    });

    backdrop.addEventListener('click', function(e){
      if (e.target === backdrop) close();
    });

    input.addEventListener('input', function(){ active = 0; render(); });

    loadOperators().then(render);
  }

  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
