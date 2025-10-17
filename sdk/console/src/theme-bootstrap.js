// Set theme early based on OS preference, default to dark when unknown.
(function () {
  try {
    var docEl = document.documentElement;
    var hasMatchMedia = typeof window !== 'undefined' && !!window.matchMedia;
    var prefersDark = hasMatchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    var prefersLight = hasMatchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    var theme = prefersDark ? 'dark' : (prefersLight ? 'light' : 'dark');

    if (theme === 'dark') {
      docEl.classList.add('dark');
      docEl.setAttribute('data-theme', 'dark');
    } else {
      docEl.classList.remove('dark');
      docEl.setAttribute('data-theme', 'light');
    }

    if (hasMatchMedia) {
      var mql = window.matchMedia('(prefers-color-scheme: dark)');
  /** @param {MediaQueryListEvent} e */
  var onChange = function (e) {
        if (e.matches) {
          docEl.classList.add('dark');
          docEl.setAttribute('data-theme', 'dark');
        } else {
          docEl.classList.remove('dark');
          docEl.setAttribute('data-theme', 'light');
        }
      };
      // Modern browsers
      if (typeof mql.addEventListener === 'function') {
        mql.addEventListener('change', onChange);
      } else if (typeof mql.addListener === 'function') {
        // Fallback
        mql.addListener(onChange);
      }
    }
  } catch (_) {
    // On any error, default to dark
    var el = document.documentElement;
    el.classList.add('dark');
    el.setAttribute('data-theme', 'dark');
  }
})();
