(function () {
  'use strict';

  var WHATSAPP_NUMBER = '50760000000';

  /* Header: transparente en hero, sólido desde Empresa */
  var header = document.getElementById('header');
  var empresaSection = document.getElementById('empresa');

  function updateHeaderStyle() {
    if (!header || !empresaSection) return;
    var solid = empresaSection.getBoundingClientRect().top <= header.offsetHeight;
    header.classList.toggle('header--solid', solid);
  }

  if (header && empresaSection) {
    updateHeaderStyle();
    window.addEventListener('scroll', updateHeaderStyle, { passive: true });
    window.addEventListener('resize', updateHeaderStyle, { passive: true });
  }

  /* Mobile menu */
  var menuToggle = document.getElementById('menu-toggle');
  var mainNav = document.getElementById('main-nav');
  var navBackdrop = document.getElementById('nav-backdrop');

  function isMobileNav() {
    return window.matchMedia('(max-width: 992px)').matches;
  }

  function restoreNavInHeader() {
    if (!header || !mainNav) return;
    var inner = header.querySelector('.header__inner');
    if (!inner || inner.contains(mainNav)) return;
    if (menuToggle && menuToggle.parentNode === inner) {
      menuToggle.insertAdjacentElement('afterend', mainNav);
    } else {
      inner.appendChild(mainNav);
    }
  }

  function moveNavToBody() {
    if (!mainNav || !isMobileNav()) return;
    if (mainNav.parentNode !== document.body) {
      document.body.appendChild(mainNav);
    }
  }

  function syncMobileNavOffset() {
    if (!header) return;
    document.documentElement.style.setProperty(
      '--mobile-header-offset',
      header.getBoundingClientRect().height + 'px'
    );
  }

  function setMenuOpen(open) {
    if (!mainNav || !menuToggle) return;
    if (open && isMobileNav()) {
      syncMobileNavOffset();
      moveNavToBody();
    } else {
      restoreNavInHeader();
    }
    mainNav.classList.toggle('header__nav--open', open);
    menuToggle.setAttribute('aria-expanded', open);
    document.body.classList.toggle('nav-open', open);
    if (navBackdrop) {
      navBackdrop.classList.toggle('nav-backdrop--visible', open);
      navBackdrop.setAttribute('aria-hidden', open ? 'false' : 'true');
    }
  }

  syncMobileNavOffset();
  window.addEventListener('resize', function () {
    syncMobileNavOffset();
    if (!isMobileNav()) {
      restoreNavInHeader();
      if (mainNav && mainNav.classList.contains('header__nav--open')) {
        setMenuOpen(false);
      }
    }
  }, { passive: true });

  if (menuToggle && mainNav) {
    menuToggle.addEventListener('click', function () {
      setMenuOpen(!mainNav.classList.contains('header__nav--open'));
    });

    if (navBackdrop) {
      navBackdrop.addEventListener('click', function () {
        setMenuOpen(false);
      });
    }

    mainNav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        setMenuOpen(false);
      });
    });
  }

  /* Hero slider */
  var slides = document.querySelectorAll('.hero__slide');
  var dotsContainer = document.getElementById('hero-dots');
  var prevBtn = document.getElementById('hero-prev');
  var nextBtn = document.getElementById('hero-next');
  var current = 0;
  var autoplayTimer;

  if (slides.length && dotsContainer) {
    slides.forEach(function (_, i) {
      var dot = document.createElement('button');
      dot.className = 'hero__dot' + (i === 0 ? ' hero__dot--active' : '');
      dot.setAttribute('aria-label', 'Ir a slide ' + (i + 1));
      dot.addEventListener('click', function () { goTo(i); });
      dotsContainer.appendChild(dot);
    });

    var dots = dotsContainer.querySelectorAll('.hero__dot');

    function goTo(index) {
      slides[current].classList.remove('hero__slide--active');
      dots[current].classList.remove('hero__dot--active');
      current = (index + slides.length) % slides.length;
      slides[current].classList.add('hero__slide--active');
      dots[current].classList.add('hero__dot--active');
      resetAutoplay();
    }

    function resetAutoplay() {
      clearInterval(autoplayTimer);
      autoplayTimer = setInterval(function () { goTo(current + 1); }, 6000);
    }

    if (prevBtn) prevBtn.addEventListener('click', function () { goTo(current - 1); });
    if (nextBtn) nextBtn.addEventListener('click', function () { goTo(current + 1); });

    resetAutoplay();
  }

  /* Contact form → WhatsApp */
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      var nombre = document.getElementById('nombre').value.trim();
      var email = document.getElementById('email').value.trim();
      var telefono = document.getElementById('telefono').value.trim();
      var mensaje = document.getElementById('mensaje').value.trim();

      var text = 'Hola ModulArt, me gustaría cotizar un proyecto.%0A%0A'
        + '*Nombre:* ' + encodeURIComponent(nombre) + '%0A'
        + '*Email:* ' + encodeURIComponent(email) + '%0A'
        + '*Teléfono:* ' + encodeURIComponent(telefono) + '%0A'
        + '*Mensaje:* ' + encodeURIComponent(mensaje);

      window.open('https://wa.me/' + WHATSAPP_NUMBER + '?text=' + text, '_blank');
    });
  }
})();
