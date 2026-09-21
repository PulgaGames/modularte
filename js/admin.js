(function () {
  'use strict';

  var API =
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:3000/api/v1'
      : 'https://modulart-api.onrender.com/api/v1';

  var TOKEN_KEY = 'modulart_token';
  var view = 'products';
  var categories = [];
  var products = [];
  var quotes = [];

  var loginView = document.getElementById('login-view');
  var appView = document.getElementById('app-view');
  var loginForm = document.getElementById('login-form');
  var loginError = document.getElementById('login-error');
  var appError = document.getElementById('app-error');
  var modal = document.getElementById('modal');
  var modalForm = document.getElementById('modal-form');
  var modalTitle = document.getElementById('modal-title');
  var viewTitle = document.getElementById('view-title');
  var viewSub = document.getElementById('view-sub');
  var primaryBtn = document.getElementById('primary-action');

  function token() {
    return sessionStorage.getItem(TOKEN_KEY);
  }

  function showError(el, msg) {
    if (!msg) {
      el.hidden = true;
      el.textContent = '';
      return;
    }
    el.hidden = false;
    el.textContent = msg;
  }

  function api(path, opts) {
    opts = opts || {};
    var headers = Object.assign({}, opts.headers || {});
    if (token()) headers.Authorization = 'Bearer ' + token();
    if (!(opts.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }
    return fetch(API + path, Object.assign({}, opts, { headers: headers })).then(function (res) {
      if (res.status === 401) {
        logout(true);
        return Promise.reject(new Error('Sesión vencida. Entra de nuevo.'));
      }
      if (res.status === 204) return null;
      return res.json().then(function (data) {
        if (!res.ok) {
          var msg = data.message;
          if (Array.isArray(msg)) msg = msg.join(' · ');
          throw new Error(msg || 'Error ' + res.status);
        }
        return data;
      });
    });
  }

  function logout(silent) {
    sessionStorage.removeItem(TOKEN_KEY);
    appView.hidden = true;
    loginView.hidden = false;
    if (!silent) showError(loginError, '');
  }

  function enterApp() {
    loginView.hidden = true;
    appView.hidden = false;
    setView('products');
  }

  function imageSrc(url) {
    if (!url) return '';
    if (url.indexOf('http') === 0) return url;
    if (url.indexOf('/api/') === 0) return API.replace('/api/v1', '') + url;
    return url;
  }

  function copy(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function setView(name) {
    view = name;
    document.querySelectorAll('.admin-nav').forEach(function (btn) {
      btn.classList.toggle('is-active', btn.getAttribute('data-view') === name);
    });
    document.getElementById('view-products').hidden = name !== 'products';
    document.getElementById('view-categories').hidden = name !== 'categories';
    document.getElementById('view-quotes').hidden = name !== 'quotes';
    if (name === 'products') {
      viewTitle.textContent = 'Productos';
      viewSub.textContent = 'Crea, edita y elimina piezas. Sube fotos nuevas.';
      primaryBtn.hidden = false;
      primaryBtn.textContent = 'Nuevo producto';
      loadProducts();
    } else if (name === 'categories') {
      viewTitle.textContent = 'Categorías';
      viewSub.textContent = 'Las categorías agrupan el catálogo (closets, salas, etc.).';
      primaryBtn.hidden = false;
      primaryBtn.textContent = 'Nueva categoría';
      loadCategories();
    } else {
      viewTitle.textContent = 'Cotizaciones';
      viewSub.textContent = 'Solicitudes de clientes. Cambia el estado o elimina.';
      primaryBtn.hidden = true;
      loadQuotes();
    }
  }

  function loadCategories() {
    return api('/categories').then(function (rows) {
      categories = rows;
      renderCategories();
    }).catch(function (err) {
      showError(appError, err.message);
    });
  }

  function loadProducts() {
    return Promise.all([
      api('/categories'),
      api('/products?limit=50')
    ]).then(function (results) {
      categories = results[0];
      products = results[1].data || [];
      renderProducts();
    }).catch(function (err) {
      showError(appError, err.message);
    });
  }

  function loadQuotes() {
    return api('/quotes?limit=50').then(function (page) {
      quotes = page.data || [];
      renderQuotes();
    }).catch(function (err) {
      showError(appError, err.message);
    });
  }

  function renderProducts() {
    var root = document.getElementById('view-products');
    if (!products.length) {
      root.innerHTML = '<p class="admin-empty">No hay productos. Crea el primero.</p>';
      return;
    }
    root.innerHTML = '<div class="admin-grid">' + products.map(function (p) {
      var cat = p.category ? p.category.title : '';
      return '<article class="admin-card">'
        + '<img src="' + copy(imageSrc(p.imageUrl)) + '" alt="' + copy(p.title) + '">'
        + '<div class="admin-card__body">'
        + '<h3>' + copy(p.title) + '</h3>'
        + '<p>' + copy(cat) + (p.location ? ' · ' + copy(p.location) : '') + '</p>'
        + '<p>$' + copy(p.basePrice) + '</p>'
        + '<div class="admin-card__actions">'
        + '<button type="button" class="admin-ghost" data-edit-product="' + p.id + '">Editar</button>'
        + '<button type="button" class="admin-ghost admin-danger" data-del-product="' + p.id + '">Eliminar</button>'
        + '</div></div></article>';
    }).join('') + '</div>';
  }

  function renderCategories() {
    var root = document.getElementById('view-categories');
    if (!categories.length) {
      root.innerHTML = '<p class="admin-empty">No hay categorías.</p>';
      return;
    }
    root.innerHTML = '<table class="admin-table"><thead><tr><th>Nombre</th><th>Slug</th><th></th></tr></thead><tbody>'
      + categories.map(function (c) {
        return '<tr><td>' + copy(c.title) + '</td><td>' + copy(c.slug) + '</td><td>'
          + '<button type="button" class="admin-ghost" data-edit-cat="' + c.id + '">Editar</button> '
          + '<button type="button" class="admin-ghost admin-danger" data-del-cat="' + c.id + '">Eliminar</button>'
          + '</td></tr>';
      }).join('')
      + '</tbody></table>';
  }

  function renderQuotes() {
    var root = document.getElementById('view-quotes');
    if (!quotes.length) {
      root.innerHTML = '<p class="admin-empty">No hay cotizaciones todavía.</p>';
      return;
    }
    root.innerHTML = '<table class="admin-table"><thead><tr><th>Proyecto</th><th>Cliente</th><th>Total</th><th>Estado</th><th></th></tr></thead><tbody>'
      + quotes.map(function (q) {
        return '<tr><td>' + copy(q.projectName) + '</td><td>' + copy(q.clientName) + '<br><small>' + copy(q.clientEmail) + '</small></td>'
          + '<td>$' + copy(q.total) + '</td><td>' + copy(q.status) + '</td><td>'
          + '<button type="button" class="admin-ghost" data-status="' + q.id + ':reviewed">Revisar</button> '
          + '<button type="button" class="admin-ghost" data-status="' + q.id + ':accepted">Aceptar</button> '
          + '<button type="button" class="admin-ghost" data-status="' + q.id + ':rejected">Rechazar</button> '
          + '<button type="button" class="admin-ghost admin-danger" data-del-quote="' + q.id + '">Eliminar</button>'
          + '</td></tr>';
      }).join('')
      + '</tbody></table>';
  }

  function closeModal() {
    modal.hidden = true;
    modalForm.innerHTML = '';
  }

  function openModal(title, html) {
    modalTitle.textContent = title;
    modalForm.innerHTML = html;
    modal.hidden = false;
  }

  function categoryOptions(selected) {
    return categories.map(function (c) {
      return '<option value="' + c.id + '"' + (c.id === selected ? ' selected' : '') + '>' + copy(c.title) + '</option>';
    }).join('');
  }

  function productForm(p) {
    p = p || {};
    return ''
      + '<label>Título<input name="title" required value="' + copy(p.title || '') + '"></label>'
      + '<label>Descripción<textarea name="description" required>' + copy(p.description || '') + '</textarea></label>'
      + '<div class="admin-form__row">'
      + '<label>Material<input name="material" required value="' + copy(p.material || '') + '"></label>'
      + '<label>Ubicación<input name="location" value="' + copy(p.location || '') + '"></label>'
      + '</div>'
      + '<div class="admin-form__row">'
      + '<label>Precio base<input name="basePrice" type="number" min="0" step="0.01" required value="' + copy(p.basePrice || 0) + '"></label>'
      + '<label>Categoría<select name="categoryId" required>' + categoryOptions(p.categoryId) + '</select></label>'
      + '</div>'
      + '<label>Imagen (JPG, PNG, WEBP o GIF, máx 5 MB)<input name="file" type="file" accept="image/*"></label>'
      + '<img id="img-preview" class="admin-preview' + (p.imageUrl ? ' is-on' : '') + '" src="' + copy(imageSrc(p.imageUrl || '')) + '" alt="">'
      + '<input type="hidden" name="imageUrl" value="' + copy(p.imageUrl || '') + '">'
      + '<input type="hidden" name="id" value="' + copy(p.id || '') + '">'
      + '<button type="submit" class="btn btn--primary">Guardar producto</button>';
  }

  function categoryForm(c) {
    c = c || {};
    return ''
      + '<label>Nombre<input name="title" required value="' + copy(c.title || '') + '"></label>'
      + '<label>Slug (url, ej. closets)<input name="slug" required value="' + copy(c.slug || '') + '"></label>'
      + '<label>Descripción<textarea name="description" required>' + copy(c.description || '') + '</textarea></label>'
      + '<input type="hidden" name="id" value="' + copy(c.id || '') + '">'
      + '<button type="submit" class="btn btn--primary">Guardar categoría</button>';
  }

  function maybeUpload(file, fallbackUrl) {
    if (!file || !file.size) return Promise.resolve(fallbackUrl);
    var body = new FormData();
    body.append('file', file);
    return api('/media', { method: 'POST', body: body }).then(function (media) {
      return media.url;
    });
  }

  loginForm.addEventListener('submit', function (e) {
    e.preventDefault();
    showError(loginError, '');
    api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username: document.getElementById('login-user').value.trim(),
        password: document.getElementById('login-pass').value
      })
    }).then(function (data) {
      sessionStorage.setItem(TOKEN_KEY, data.accessToken);
      enterApp();
    }).catch(function (err) {
      showError(loginError, err.message);
    });
  });

  document.getElementById('logout-btn').addEventListener('click', function () {
    logout();
  });

  document.querySelectorAll('.admin-nav').forEach(function (btn) {
    btn.addEventListener('click', function () {
      showError(appError, '');
      setView(btn.getAttribute('data-view'));
    });
  });

  primaryBtn.addEventListener('click', function () {
    if (view === 'products') {
      if (!categories.length) {
        showError(appError, 'Crea una categoría antes de agregar productos.');
        return;
      }
      openModal('Nuevo producto', productForm());
    } else {
      openModal('Nueva categoría', categoryForm());
    }
  });

  modal.addEventListener('click', function (e) {
    if (e.target.hasAttribute('data-close-modal')) closeModal();
  });

  modalForm.addEventListener('change', function (e) {
    if (e.target.name !== 'file' || !e.target.files[0]) return;
    var preview = document.getElementById('img-preview');
    preview.src = URL.createObjectURL(e.target.files[0]);
    preview.classList.add('is-on');
  });

  modalForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var fd = new FormData(modalForm);
    showError(appError, '');

    if (view === 'categories') {
      var catBody = {
        title: fd.get('title'),
        slug: fd.get('slug'),
        description: fd.get('description')
      };
      var catId = fd.get('id');
      var catReq = catId
        ? api('/categories/' + catId, { method: 'PATCH', body: JSON.stringify(catBody) })
        : api('/categories', { method: 'POST', body: JSON.stringify(catBody) });
      catReq.then(function () {
        closeModal();
        loadCategories();
      }).catch(function (err) {
        showError(appError, err.message);
      });
      return;
    }

    var file = modalForm.querySelector('input[name="file"]').files[0];
    maybeUpload(file, fd.get('imageUrl')).then(function (url) {
      if (!url) throw new Error('Sube una imagen o el producto no tiene foto.');
      var body = {
        title: fd.get('title'),
        description: fd.get('description'),
        material: fd.get('material'),
        location: fd.get('location') || undefined,
        basePrice: Number(fd.get('basePrice')),
        categoryId: fd.get('categoryId'),
        imageUrl: url
      };
      var id = fd.get('id');
      return id
        ? api('/products/' + id, { method: 'PATCH', body: JSON.stringify(body) })
        : api('/products', { method: 'POST', body: JSON.stringify(body) });
    }).then(function () {
      closeModal();
      loadProducts();
    }).catch(function (err) {
      showError(appError, err.message);
    });
  });

  document.getElementById('view-products').addEventListener('click', function (e) {
    var edit = e.target.getAttribute('data-edit-product');
    var del = e.target.getAttribute('data-del-product');
    if (edit) {
      var p = products.filter(function (x) { return x.id === edit; })[0];
      openModal('Editar producto', productForm(p));
    }
    if (del && window.confirm('¿Eliminar este producto?')) {
      api('/products/' + del, { method: 'DELETE' }).then(loadProducts).catch(function (err) {
        showError(appError, err.message);
      });
    }
  });

  document.getElementById('view-categories').addEventListener('click', function (e) {
    var edit = e.target.getAttribute('data-edit-cat');
    var del = e.target.getAttribute('data-del-cat');
    if (edit) {
      var c = categories.filter(function (x) { return x.id === edit; })[0];
      openModal('Editar categoría', categoryForm(c));
    }
    if (del && window.confirm('¿Eliminar esta categoría? Solo si no tiene productos.')) {
      api('/categories/' + del, { method: 'DELETE' }).then(loadCategories).catch(function (err) {
        showError(appError, err.message);
      });
    }
  });

  document.getElementById('view-quotes').addEventListener('click', function (e) {
    var status = e.target.getAttribute('data-status');
    var del = e.target.getAttribute('data-del-quote');
    if (status) {
      var parts = status.split(':');
      api('/quotes/' + parts[0] + '/status', {
        method: 'PATCH',
        body: JSON.stringify({ status: parts[1] })
      }).then(loadQuotes).catch(function (err) {
        showError(appError, err.message);
      });
    }
    if (del && window.confirm('¿Eliminar esta cotización?')) {
      api('/quotes/' + del, { method: 'DELETE' }).then(loadQuotes).catch(function (err) {
        showError(appError, err.message);
      });
    }
  });

  if (token()) enterApp();
})();
