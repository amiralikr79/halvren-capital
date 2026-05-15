(function(){
  // THEME TOGGLE — cookie-backed (1y), sun/moon SVG that flips on each click.
  var t=document.querySelector('[data-theme-toggle]');
  if(t){
    var SUN='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
    var MOON='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    function readCookie(){try{var c=document.cookie.split('; ').find(function(r){return r.indexOf('halvren-theme=')===0});return c?c.split('=')[1]:null}catch(e){return null}}
    function persist(mode){try{document.cookie='halvren-theme='+mode+'; Max-Age=31536000; Path=/; SameSite=Lax'}catch(e){}}
    function setTheme(theme){
      document.documentElement.setAttribute('data-theme',theme);
      persist(theme);
      t.setAttribute('aria-pressed',theme==='light'?'true':'false');
      t.setAttribute('aria-label',theme==='light'?'Switch to dark theme':'Switch to light theme');
      t.innerHTML=theme==='dark'?SUN:MOON;
    }
    setTheme(document.documentElement.getAttribute('data-theme')||'dark');
    t.addEventListener('click',function(){
      var current=document.documentElement.getAttribute('data-theme')||'dark';
      setTheme(current==='light'?'dark':'light');
    });
    var mql=window.matchMedia('(prefers-color-scheme: light)');
    mql.addEventListener&&mql.addEventListener('change',function(e){
      if(readCookie())return;
      setTheme(e.matches?'light':'dark');
    });
  }

  // MOBILE MENU — side drawer with backdrop
  var navToggle=document.querySelector('[data-nav-toggle]');
  var navLinks=document.getElementById('nav-links');
  if(navToggle&&navLinks){
    // Inject backdrop once
    var backdrop=document.createElement('div');
    backdrop.className='nav-backdrop';
    backdrop.setAttribute('data-nav-backdrop','');
    backdrop.setAttribute('aria-hidden','true');
    document.body.appendChild(backdrop);

    function setMenu(open){
      navLinks.setAttribute('data-open',open?'true':'false');
      backdrop.setAttribute('data-open',open?'true':'false');
      navToggle.setAttribute('aria-expanded',open?'true':'false');
      navToggle.setAttribute('aria-label',open?'Close menu':'Open menu');
      navToggle.classList.toggle('is-open',open);
      document.body.style.overflow=open?'hidden':'';
    }
    navToggle.addEventListener('click',function(){
      setMenu(navLinks.getAttribute('data-open')!=='true');
    });
    backdrop.addEventListener('click',function(){setMenu(false)});
    navLinks.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click',function(){setMenu(false)});
    });
    document.addEventListener('keydown',function(e){if(e.key==='Escape')setMenu(false)});
  }
})();
