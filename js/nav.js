/* Current page's menu link, kept in view on phones (2026-10-14).
   On narrow screens the header menu scrolls sideways (css/mobile.css, 1), and
   the current page's link (a.active) could start off-screen, e.g. Monitoring,
   AI, Resources or Resume on a 390px phone. This scrolls the MENU, never the
   page, so that link sits near the middle. It does nothing when the menu
   already fits. Runs again after fonts load, since they change link widths. */
(function () {
  function centreActive() {
    var list = document.querySelector('.nav-links');
    var link = list && list.querySelector('a.active');
    if (!link || list.scrollWidth <= list.clientWidth) return;
    var l = list.getBoundingClientRect();
    var a = link.getBoundingClientRect();
    list.scrollLeft += (a.left + a.width / 2) - (l.left + l.width / 2);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', centreActive);
  } else {
    centreActive();
  }
  window.addEventListener('load', centreActive);
})();
