(function () {
  'use strict';

  var MESES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
  ];

  var NOTA_PAGO =
    'NOTA:\n' +
    'Forma de pago: el 50% para iniciar el proyecto, el 30% en el avance del mismo y el 20% restante al terminar el proyecto.\n' +
    'Los pagos deben de realizarse a nombre de Luis Alexander Pirazan / ACH Banco General/ ahorro # 0429999359718 // Blanca Mónica Ortiz Duque / ACH  BAC  Credomatic / ahorro #110488327';

  var LOGO_PATH = '/public/images/logo.png';

  var container = document.getElementById('items-container');
  var template = document.getElementById('item-template');
  var addBtn = document.getElementById('add-item');
  var downloadBtn = document.getElementById('download-pdf');
  var fechaDisplay = document.getElementById('fecha-display');
  var proyectoInput = document.getElementById('proyecto');
  var subtotalEl = document.getElementById('subtotal');
  var itbmsEl = document.getElementById('itbms');
  var totalEl = document.getElementById('total');

  var logoBase64 = null;

  init();

  function init() {
    setFechaActual();
    addItem();
    addBtn.addEventListener('click', addItem);
    downloadBtn.addEventListener('click', handleDownload);
    initMobileMenu();
    preloadLogo();
  }

  function initMobileMenu() {
    var menuToggle = document.getElementById('menu-toggle');
    var mainNav = document.getElementById('main-nav');
    var navBackdrop = document.getElementById('nav-backdrop');
    var header = document.getElementById('header');
    if (!menuToggle || !mainNav) return;

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
        if (mainNav.classList.contains('header__nav--open')) {
          setMenuOpen(false);
        }
      }
    }, { passive: true });

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

  function prepareLogoForPdf(src) {
    return new Promise(function (resolve) {
      var img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = function () {
        var canvas = document.createElement('canvas');
        var w = img.naturalWidth || 400;
        var h = img.naturalHeight || 400;
        canvas.width = w;
        canvas.height = h;
        var ctx = canvas.getContext('2d');
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, w, h);
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL('image/png'));
      };
      img.onerror = function () { resolve(null); };
      img.src = src;
    });
  }

  function preloadLogo() {
    prepareLogoForPdf(LOGO_PATH).then(function (data) {
      logoBase64 = data;
    });
  }

  function setFechaActual() {
    var now = new Date();
    var texto = 'Panamá, ' + now.getDate() + ' de ' + MESES[now.getMonth()] + ' de ' + now.getFullYear();
    fechaDisplay.textContent = texto;
  }

  function getFechaActual() {
    return fechaDisplay.textContent;
  }

  function parseAmount(str) {
    if (str == null || str === '') return 0;
    var s = String(str).replace(/[^\d,.-]/g, '');
    if (!s) return 0;
    s = s.replace(/\./g, '').replace(',', '.');
    var n = parseFloat(s);
    return isNaN(n) ? 0 : n;
  }

  function formatAmount(num) {
    var rounded = Math.round(num * 100) / 100;
    var parts = rounded.toFixed(2).split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return parts.join(',');
  }

  function formatCurrency(num) {
    return 'B/. ' + formatAmount(num);
  }

  function sanitizeUnitarioInput(value) {
    return value.replace(/[^\d.,]/g, '');
  }

  function addItem() {
    var clone = template.content.cloneNode(true);
    var item = clone.querySelector('[data-item]');
    bindItemEvents(item);
    container.appendChild(clone);
    renumberItems();
    recalculateAll();
  }

  function removeItem(item) {
    if (container.querySelectorAll('[data-item]').length <= 1) return;
    item.remove();
    renumberItems();
    recalculateAll();
  }

  function renumberItems() {
    var items = container.querySelectorAll('[data-item]');
    items.forEach(function (item, index) {
      item.querySelector('[data-num]').textContent = index + 1;
      var removeBtn = item.querySelector('[data-remove]');
      removeBtn.hidden = items.length <= 1;
    });
  }

  function bindItemEvents(item) {
    var cantidad = item.querySelector('[data-cantidad]');
    var unitario = item.querySelector('[data-unitario]');
    var removeBtn = item.querySelector('[data-remove]');

    cantidad.addEventListener('input', function () {
      if (cantidad.value && parseInt(cantidad.value, 10) < 1) cantidad.value = 1;
      updateItemTotal(item);
      recalculateTotals();
    });

    unitario.addEventListener('input', function () {
      var pos = unitario.selectionStart;
      var before = unitario.value.length;
      unitario.value = sanitizeUnitarioInput(unitario.value);
      var diff = unitario.value.length - before;
      unitario.setSelectionRange(pos + diff, pos + diff);
      updateItemTotal(item);
      recalculateTotals();
    });

    unitario.addEventListener('blur', function () {
      var parsed = parseAmount(unitario.value);
      unitario.value = parsed > 0 ? formatAmount(parsed) : '';
      updateItemTotal(item);
      recalculateTotals();
    });

    removeBtn.addEventListener('click', function () { removeItem(item); });
  }

  function updateItemTotal(item) {
    var cantidad = parseInt(item.querySelector('[data-cantidad]').value, 10) || 0;
    var unitario = parseAmount(item.querySelector('[data-unitario]').value);
    var total = cantidad * unitario;
    item.querySelector('[data-total]').value = formatAmount(total);
  }

  function recalculateAll() {
    container.querySelectorAll('[data-item]').forEach(updateItemTotal);
    recalculateTotals();
  }

  function recalculateTotals() {
    var subtotal = 0;
    container.querySelectorAll('[data-item]').forEach(function (item) {
      subtotal += parseAmount(item.querySelector('[data-total]').value);
    });
    var itbms = subtotal * 0.07;
    var total = subtotal + itbms;

    subtotalEl.value = formatCurrency(subtotal);
    itbmsEl.value = formatCurrency(itbms);
    totalEl.value = formatCurrency(total);
  }

  function collectItems() {
    var items = [];
    container.querySelectorAll('[data-item]').forEach(function (item, index) {
      var cantidad = parseInt(item.querySelector('[data-cantidad]').value, 10) || 0;
      var descripcion = item.querySelector('[data-descripcion]').value.trim();
      var unitario = parseAmount(item.querySelector('[data-unitario]').value);
      var total = parseAmount(item.querySelector('[data-total]').value);

      if (descripcion || unitario > 0) {
        items.push({
          num: index + 1,
          cantidad: cantidad,
          descripcion: descripcion,
          unitario: unitario,
          total: total
        });
      }
    });
    return items;
  }

  function validateForm() {
    var items = collectItems();
    if (!items.length) {
      showToast('Agrega al menos un producto con descripción y valor.', true);
      return null;
    }

    var invalid = items.some(function (it) {
      return !it.descripcion || it.cantidad < 1 || it.unitario <= 0;
    });

    if (invalid) {
      showToast('Completa cantidad, descripción y valor unitario de cada producto.', true);
      return null;
    }

    return items;
  }

  function showToast(msg, isError) {
    var existing = document.querySelector('.cot-toast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.className = 'cot-toast' + (isError ? ' cot-toast--error' : '');
    toast.textContent = msg;
    document.body.appendChild(toast);
    requestAnimationFrame(function () { toast.classList.add('cot-toast--visible'); });
    setTimeout(function () {
      toast.classList.remove('cot-toast--visible');
      setTimeout(function () { toast.remove(); }, 300);
    }, 3500);
  }

  function handleDownload() {
    var items = validateForm();
    if (!items) return;

    if (typeof window.jspdf === 'undefined') {
      showToast('Cargando librería PDF, intenta de nuevo en un momento.', true);
      return;
    }

    downloadBtn.disabled = true;

    var logoPromise = logoBase64
      ? Promise.resolve(logoBase64)
      : prepareLogoForPdf(LOGO_PATH);

    logoPromise.then(function (data) {
      if (data) logoBase64 = data;
      try {
        generatePDF(items);
        showToast('Cotización descargada correctamente.');
      } catch (e) {
        showToast('Error al generar el PDF. Intenta de nuevo.', true);
        console.error(e);
      } finally {
        downloadBtn.disabled = false;
      }
    });
  }

  function generatePDF(items) {
    var jsPDF = window.jspdf.jsPDF;
    var doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'letter' });
    var pageW = doc.internal.pageSize.getWidth();
    var margin = 14;
    var y = 10;
    var logoSize = 32;
    var logoX = margin;
    var logoY = y;

    if (logoBase64) {
      doc.setFillColor(0, 0, 0);
      doc.roundedRect(logoX - 1, logoY - 1, logoSize + 2, logoSize + 2, 2, 2, 'F');
      doc.addImage(logoBase64, 'PNG', logoX, logoY, logoSize, logoSize);
    }

    var textStartX = logoBase64 ? logoX + logoSize + 8 : pageW / 2;
    var textAlign = logoBase64 ? 'left' : 'center';

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(15);
    doc.setTextColor(26, 26, 26);
    doc.text('ModulArt Company', textStartX, y + 8, { align: textAlign });

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(60, 60, 60);
    doc.text('Fabricamos todo tipo de muebles', textStartX, y + 14, { align: textAlign });
    doc.text('cel: 6795 3987', textStartX, y + 19, { align: textAlign });
    doc.text('RUC.3NT-2-34623 DV 1', textStartX, y + 24, { align: textAlign });

    doc.setFontSize(9);
    doc.setTextColor(80, 80, 80);
    doc.text(getFechaActual(), pageW - margin, y + 8, { align: 'right' });

    y = Math.max(y + logoSize + 6, 38);
    doc.setDrawColor(184, 115, 51);
    doc.setLineWidth(0.6);
    doc.line(margin, y - 2, pageW - margin, y - 2);

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.setTextColor(184, 115, 51);
    doc.text('COTIZACION', pageW / 2, y + 4, { align: 'center' });
    doc.setLineWidth(0.4);
    doc.setDrawColor(184, 115, 51);
    var cotW = doc.getTextWidth('COTIZACION');
    doc.line(pageW / 2 - cotW / 2, y + 5.5, pageW / 2 + cotW / 2, y + 5.5);

    y += 12;
    var proyecto = proyectoInput.value.trim();
    if (proyecto) {
      doc.setFontSize(11);
      doc.setTextColor(26, 26, 26);
      doc.text(proyecto.toUpperCase(), pageW / 2, y, { align: 'center' });
      y += 7;
    }

    var tableBody = items.map(function (it) {
      return [
        String(it.num),
        String(it.cantidad),
        it.descripcion,
        formatAmount(it.unitario),
        formatAmount(it.total)
      ];
    });

    var subtotal = items.reduce(function (s, it) { return s + it.total; }, 0);
    var itbms = subtotal * 0.07;
    var total = subtotal + itbms;

    doc.autoTable({
      startY: y,
      head: [['NUM', 'CAN', 'DESCRIPCION', 'VALOR UNITARIO', 'VALOR TOTAL']],
      body: tableBody,
      theme: 'grid',
      margin: { left: margin, right: margin },
      headStyles: {
        fillColor: [184, 115, 51],
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        halign: 'center',
        fontSize: 9
      },
      bodyStyles: { fontSize: 9, valign: 'middle', textColor: [40, 40, 40] },
      alternateRowStyles: { fillColor: [248, 246, 243] },
      columnStyles: {
        0: { halign: 'center', cellWidth: 12 },
        1: { halign: 'center', cellWidth: 14 },
        2: { halign: 'left' },
        3: { halign: 'right', cellWidth: 32 },
        4: { halign: 'right', cellWidth: 32 }
      },
      styles: { lineColor: [0, 0, 0], lineWidth: 0.2 }
    });

    var finalY = doc.lastAutoTable.finalY + 4;
    var labelX = pageW - margin - 55;
    var valueX = pageW - margin;

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(40, 40, 40);

    doc.text('SUB TOTAL', labelX, finalY, { align: 'right' });
    doc.text(formatCurrency(subtotal), valueX, finalY, { align: 'right' });

    finalY += 6;
    doc.text('ITBMS', labelX, finalY, { align: 'right' });
    doc.text(formatCurrency(itbms), valueX, finalY, { align: 'right' });

    finalY += 7;
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(184, 115, 51);
    doc.text('TOTAL', labelX, finalY, { align: 'right' });
    doc.text(formatCurrency(total), valueX, finalY, { align: 'right' });

    finalY += 14;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8.5);
    doc.setTextColor(60, 60, 60);

    var notaLines = doc.splitTextToSize(NOTA_PAGO, pageW - margin * 2);
    doc.text(notaLines, margin, finalY);

    finalY += notaLines.length * 3.8 + 6;
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.setTextColor(26, 26, 26);
    doc.text('Responsable: LUIS ALEXANDER PIRAZAN', margin, finalY);

    var filename = 'Cotizacion_ModulArt_' + new Date().toISOString().slice(0, 10) + '.pdf';
    doc.save(filename);
  }
})();
