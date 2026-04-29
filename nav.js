(function(){
  // THEME TOGGLE — persists in localStorage, syncs aria-pressed
  var t=document.querySelector('[data-theme-toggle]');
  if(t){
    function setTheme(theme){
      document.documentElement.setAttribute('data-theme',theme);
      try{localStorage.setItem('halvren-theme',theme)}catch(e){}
      t.setAttribute('aria-pressed',theme==='light'?'true':'false');
      t.setAttribute('aria-label',theme==='light'?'Switch to dark theme':'Switch to light theme');
    }
    t.addEventListener('click',function(){
      var current=document.documentElement.getAttribute('data-theme')||'dark';
      setTheme(current==='light'?'dark':'light');
    });
    var mql=window.matchMedia('(prefers-color-scheme: light)');
    mql.addEventListener&&mql.addEventListener('change',function(e){
      try{if(localStorage.getItem('halvren-theme'))return}catch(err){}
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
