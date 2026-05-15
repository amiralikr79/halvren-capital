/* Halvren Tape — earnings marquee + status bar.
 *
 * Single fetch of /data/earnings.json. Injects two thin rows at the very
 * top of <body>, above <nav>. Both rows are mono, ALL CAPS at text-[10px]
 * scale, --color-text-muted on --color-surface. The earnings tape scrolls
 * left at 30s per cycle and pauses on hover; the status bar is static.
 *
 * No deps. Re-renderable. Skips dates already in the past.
 */
(function(){
  if (document.querySelector('[data-halvren-tape]')) return; // idempotent

  function el(tag, attrs, kids){
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs){
      if (k === 'class') n.className = attrs[k];
      else if (k === 'text') n.textContent = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    if (kids) kids.forEach(function(c){ n.appendChild(c); });
    return n;
  }

  function fmt(iso){
    // 2026-05-21 -> "MAY 21"
    var parts = iso.split('-');
    var months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
    return months[parseInt(parts[1],10)-1] + ' ' + parseInt(parts[2],10);
  }

  function todayISO(){
    var d = new Date();
    var y = d.getFullYear();
    var m = String(d.getMonth()+1).padStart(2,'0');
    var dd = String(d.getDate()).padStart(2,'0');
    return y+'-'+m+'-'+dd;
  }

  function buildShell(){
    var wrap = el('div', { 'data-halvren-tape':'', class:'halvren-tape' });
    var status = el('div', { class:'halvren-status', role:'status', 'aria-label':'Spot prices and macro' });
    var tape   = el('div', { class:'halvren-marquee', 'aria-label':'Earnings calendar' });
    tape.appendChild(el('div', { class:'halvren-marquee-track' }));
    wrap.appendChild(status);
    wrap.appendChild(tape);
    return wrap;
  }

  function renderStatus(node, items, asOf){
    node.innerHTML = '';
    var inner = el('div', { class:'halvren-status-inner' });
    var label = el('span', { class:'halvren-status-label', text:'TAPE · '+ (asOf||'') });
    inner.appendChild(label);
    items.forEach(function(it){
      var item = el('span', { class:'halvren-status-item' });
      item.appendChild(el('span', { class:'halvren-status-k', text: it.label }));
      item.appendChild(el('span', { class:'halvren-status-v', text: it.value }));
      inner.appendChild(item);
    });
    node.appendChild(inner);
  }

  function renderTape(node, events){
    var track = node.querySelector('.halvren-marquee-track');
    track.innerHTML = '';
    var today = todayISO();
    var upcoming = events.filter(function(e){ return e.date >= today; })
                         .sort(function(a,b){ return a.date < b.date ? -1 : 1; });
    if (!upcoming.length){
      var empty = el('span', { class:'halvren-marquee-empty', text:'NEXT EARNINGS WINDOW OPENS WHEN CONSENSUS CALENDAR REFRESHES.' });
      track.appendChild(empty);
      node.classList.add('is-static');
      return;
    }
    // Build a single segment, then duplicate it for seamless loop.
    function seg(){
      var s = el('div', { class:'halvren-marquee-seg', 'aria-hidden':'false' });
      upcoming.forEach(function(ev){
        var item = el('a', { class:'halvren-marquee-item', href:'/research', title: ev.ticker + ' ' + ev.label + ' on ' + ev.date });
        item.appendChild(el('span', { class:'halvren-marquee-date', text: fmt(ev.date) }));
        item.appendChild(el('span', { class:'halvren-marquee-ticker', text: ev.ticker }));
        item.appendChild(el('span', { class:'halvren-marquee-label', text: ev.label }));
        s.appendChild(item);
      });
      return s;
    }
    track.appendChild(seg());
    var dupe = seg();
    dupe.setAttribute('aria-hidden','true');
    track.appendChild(dupe);
  }

  function mount(data){
    if (!data) return;
    var shell = buildShell();
    document.body.insertBefore(shell, document.body.firstChild);
    renderStatus(shell.querySelector('.halvren-status'),
                 (data.status_bar && data.status_bar.items) || [],
                 (data.status_bar && data.status_bar.as_of) || data.version || '');
    renderTape(shell.querySelector('.halvren-marquee'), data.events || []);
    document.documentElement.classList.add('has-halvren-tape');
  }

  function boot(){
    // Don't render inside the embeddable Checklist Live iframe page or 404 shell when minimal.
    if (window.self !== window.top) return;
    fetch('/data/earnings.json', { cache: 'default' })
      .then(function(r){ return r.ok ? r.json() : null; })
      .then(mount)
      .catch(function(){ /* silent — tape is non-critical chrome */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
