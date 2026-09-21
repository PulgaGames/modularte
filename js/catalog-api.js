(function (global) {
  'use strict';

  var API_BASE =
    global.location.hostname === 'localhost' || global.location.hostname === '127.0.0.1'
      ? 'http://localhost:3000/api/v1'
      : 'https://modulart-api.onrender.com/api/v1';
  var API_HOST = API_BASE.replace(/\/api\/v1$/, '');

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text == null ? '' : String(text);
    return div.innerHTML;
  }

  function resolveSrc(url) {
    if (!url) return '';
    if (url.indexOf('http') === 0) return url;
    if (url.indexOf('/api/') === 0) return API_HOST + url;
    return url;
  }

  function findStaticCategory(cat, staticMap) {
    if (!staticMap) return null;
    if (staticMap[cat.slug]) return staticMap[cat.slug];
    var keys = Object.keys(staticMap);
    for (var i = 0; i < keys.length; i++) {
      if (staticMap[keys[i]] && staticMap[keys[i]].title === cat.title) {
        return staticMap[keys[i]];
      }
    }
    return null;
  }

  function mergeCatalog(apiItems, staticItems) {
    var seen = {};
    var out = [];
    function add(item) {
      if (!item || !item.src || seen[item.src]) return;
      seen[item.src] = true;
      out.push(item);
    }
    (apiItems || []).forEach(add);
    (staticItems || []).forEach(add);
    return out;
  }

  function mapCatalog(categories, productsPage) {
    var products = (productsPage && productsPage.data) || [];
    var staticMap = global.MODULART_PRODUCTS || {};
    var map = {};
    var order = [];

    var cats = (categories || []).slice().sort(function (a, b) {
      return String(a.title).localeCompare(String(b.title), 'es');
    });

    cats.forEach(function (cat) {
      var apiItems = products
        .filter(function (p) {
          return p.category && p.category.slug === cat.slug;
        })
        .sort(function (a, b) {
          return new Date(b.createdAt) - new Date(a.createdAt);
        })
        .map(function (p) {
          return {
            title: p.title,
            description: p.description,
            material: p.material,
            src: resolveSrc(p.imageUrl),
            alt: p.title
          };
        });

      var staticCat = findStaticCategory(cat, staticMap);
      var catalog = mergeCatalog(apiItems, staticCat && staticCat.catalog);
      var description = cat.description || (staticCat && staticCat.description) || '';

      order.push(cat.slug);
      map[cat.slug] = {
        slug: cat.slug,
        title: cat.title,
        metaDescription: description,
        description: description,
        heroImage: catalog[0] ? catalog[0].src : '/public/images/logo.png',
        heroAlt: catalog[0] ? catalog[0].alt : cat.title,
        catalog: catalog
      };

      if (staticCat && staticCat.slug && staticCat.slug !== cat.slug) {
        map[staticCat.slug] = map[cat.slug];
      }
    });

    global.MODULART_PRODUCTS = map;
    global.MODULART_PRODUCT_ORDER = order;
    global.MODULART_LATEST_PRODUCTS = products.map(function (p) {
      return {
        title: p.title,
        src: resolveSrc(p.imageUrl),
        categorySlug: p.category && p.category.slug,
        categoryTitle: p.category && p.category.title
      };
    });
    return map;
  }

  function loadCatalog() {
    if (global.__modulartCatalogPromise) return global.__modulartCatalogPromise;

    var fetchOpts = { cache: 'no-store' };
    global.__modulartCatalogPromise = Promise.all([
      fetch(API_BASE + '/categories', fetchOpts).then(function (res) {
        if (!res.ok) throw new Error('categories ' + res.status);
        return res.json();
      }),
      fetch(API_BASE + '/products?limit=50', fetchOpts).then(function (res) {
        if (!res.ok) throw new Error('products ' + res.status);
        return res.json();
      })
    ]).then(function (results) {
      return mapCatalog(results[0], results[1]);
    }).catch(function (err) {
      global.__modulartCatalogPromise = null;
      throw err;
    });

    return global.__modulartCatalogPromise;
  }

  function orderedCategories() {
    var map = global.MODULART_PRODUCTS || {};
    var order = global.MODULART_PRODUCT_ORDER || Object.keys(map);
    var withItems = [];
    var empty = [];
    order.forEach(function (slug) {
      var cat = map[slug];
      if (!cat) return;
      if (cat.catalog && cat.catalog.length) withItems.push(cat);
      else empty.push(cat);
    });
    return withItems.concat(empty);
  }

  function fillHome() {
    var grid = document.getElementById('products-grid');
    if (!grid) return;

    var cats = orderedCategories();
    if (!cats.length) return;

    grid.innerHTML = cats.map(function (cat) {
      var cover = cat.catalog[0] ? cat.catalog[0].src : '/public/images/logo.png';
      var n = cat.catalog.length;
      var meta = n === 0 ? 'Próximamente' : n === 1 ? '1 proyecto' : n + ' proyectos';
      var soon = n === 0 ? ' product-card--soon' : '';
      return '<a href="/productos/' + encodeURIComponent(cat.slug) + '/" class="product-card product-card--photo' + soon + '">'
        + '<div class="product-card__media">'
        + '<img src="' + escapeHtml(cover) + '" alt="' + escapeHtml(cat.title) + '" width="640" height="400" loading="lazy" decoding="async">'
        + '</div>'
        + '<h3>' + escapeHtml(cat.title) + '</h3>'
        + '<p class="product-card__count">' + escapeHtml(meta) + '</p>'
        + '<span class="product-card__link">' + (n === 0 ? 'Ver categoría' : 'Ver catálogo') + '</span>'
        + '</a>';
    }).join('');
    grid.removeAttribute('aria-busy');
  }

  function fillRecent() {
    var grid = document.getElementById('recent-projects');
    if (!grid) return;
    var items = (global.MODULART_LATEST_PRODUCTS || []).filter(function (p) {
      return p && p.src && p.categorySlug;
    }).slice(0, 8);
    if (!items.length) return;

    grid.hidden = false;
    var heading = document.getElementById('recent-projects-heading');
    if (heading) heading.hidden = false;

    grid.innerHTML = items.map(function (p) {
      return '<a href="/productos/' + encodeURIComponent(p.categorySlug) + '/" class="product-card product-card--photo">'
        + '<div class="product-card__media">'
        + '<img src="' + escapeHtml(p.src) + '" alt="' + escapeHtml(p.title) + '" width="640" height="400" loading="lazy" decoding="async">'
        + '</div>'
        + '<h3>' + escapeHtml(p.title) + '</h3>'
        + '<p class="product-card__count">' + escapeHtml(p.categoryTitle || '') + '</p>'
        + '<span class="product-card__link">Ver proyecto</span>'
        + '</a>';
    }).join('');
  }

  function fillFooters() {
    var lists = document.querySelectorAll('[data-footer-products]');
    if (!lists.length) return;
    var cats = orderedCategories();
    var html = cats.map(function (cat) {
      return '<li><a href="/productos/' + encodeURIComponent(cat.slug) + '/">' + escapeHtml(cat.title) + '</a></li>';
    }).join('');
    lists.forEach(function (ul) {
      ul.innerHTML = html;
    });
  }

  function hydratePublic(attempt) {
    var grid = document.getElementById('products-grid');
    if (grid) grid.setAttribute('aria-busy', 'true');
    return loadCatalog().then(function () {
      fillHome();
      fillRecent();
      fillFooters();
    }).catch(function () {
      if (grid) grid.removeAttribute('aria-busy');
      if (!attempt) {
        setTimeout(function () {
          hydratePublic(1);
        }, 2800);
      }
    });
  }

  global.ModulArt = {
    API_BASE: API_BASE,
    resolveSrc: resolveSrc,
    loadCatalog: loadCatalog,
    hydratePublic: hydratePublic
  };

  if (document.getElementById('products-grid') || document.querySelector('[data-footer-products]')) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', hydratePublic);
    } else {
      hydratePublic();
    }
  }
})(window);
