<script>
(function(){
  var con = document.querySelector('.constellation');
  if (!con) return;
  var tt  = con.querySelector('[data-tooltip]');
  var ttT = con.querySelector('[data-tt-ticker]');
  var ttS = con.querySelector('[data-tt-sector]');
  var ttM = con.querySelector('[data-tt-meta]');

  function show(e){
    var d = e.currentTarget;
    var slug = d.getAttribute('data-slug');
    var ticker = d.getAttribute('data-ticker');
    var sector = d.getAttribute('data-sector');
    var last   = d.getAttribute('data-last');
    ttT.textContent = ticker;
    ttS.textContent = sector;
    ttM.textContent = 'Last reviewed ' + last;
    var rect = d.getBoundingClientRect();
    var hostRect = con.getBoundingClientRect();
    var x = rect.left - hostRect.left + rect.width / 2;
    var y = rect.top  - hostRect.top  - 8;
    tt.style.left = x + 'px';
    tt.style.top  = y + 'px';
    tt.style.transform = 'translate(-50%, -100%)';
    tt.setAttribute('data-visible', 'true');
    tt.setAttribute('aria-hidden', 'false');
    var r = parseFloat(d.getAttribute('r'));
    d.setAttribute('data-rest-r', r);
    d.setAttribute('r', r * 1.7);
  }
  function hide(e){
    tt.removeAttribute('data-visible');
    tt.setAttribute('aria-hidden', 'true');
    var d = e.currentTarget;
    var rest = d.getAttribute('data-rest-r');
    if (rest) d.setAttribute('r', rest);
  }
  function navigate(e){
    var slug = e.currentTarget.getAttribute('data-slug');
    if (slug) window.location.href = '/research/' + slug;
  }
  con.querySelectorAll('.cdot').forEach(function(d){
    d.addEventListener('mouseenter', show);
    d.addEventListener('focus',      show);
    d.addEventListener('mouseleave', hide);
    d.addEventListener('blur',       hide);
    d.addEventListener('click',      navigate);
    d.addEventListener('keydown', function(e){
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); navigate(e); }
    });
  });

  // mobile tabs
  var tabsWrap = document.querySelector('.constellation-mobile-tabs');
  if (!tabsWrap) return;
  var items = document.querySelectorAll('.constellation-mobile-list li');
  tabsWrap.querySelectorAll('button').forEach(function(b){
    b.addEventListener('click', function(){
      var s = b.getAttribute('data-sector');
      tabsWrap.querySelectorAll('button').forEach(function(x){
        x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
      });
      items.forEach(function(li){
        if (li.getAttribute('data-sector') === s) li.removeAttribute('hidden');
        else li.setAttribute('hidden', '');
      });
    });
  });
})();
</script>