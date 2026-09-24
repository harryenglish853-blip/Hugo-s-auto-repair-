/* Hugo's Alignment, Tires & Auto Repair: site behaviour.
   No dependencies. Everything degrades gracefully without JavaScript. */
(function () {
  'use strict';

  var CONFIG = window.HUGOS_CONFIG || {};
  var ADDRESS = '6040 N Black Canyon Hwy, Phoenix, AZ 85017';
  var PHONE = '(602) 242-0442';
  var TEL = 'tel:+16022420442';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var LANG = (document.documentElement.lang || 'en').slice(0, 2) === 'es' ? 'es' : 'en';

  /* UI strings (English / Spanish) */
  var T = {
    en: {
      noticing: "What I'm noticing: ",
      stars: ' out of 5 stars',
      via: 'via',
      locale: 'en-US',
      open: 'Open now · until {close} today',
      closed: 'Closed now · opens {open} ',
      today: 'today', tomorrow: 'tomorrow', monday: 'Monday',
      err: {
        name: 'Please enter your name.',
        phone: 'Please enter a phone number we can call back, including area code.',
        email: 'Please enter a valid email address, or leave it blank.',
        vehicle_year: 'Please enter a 4-digit year, like 2014.',
        service: 'Please choose the service you need (or "Not Sure").',
        other: 'Please check this field.'
      },
      sending: 'Sending…',
      subject: 'Service request: ',
      success: "<strong>Thanks. Hugo's received your request.</strong> The shop will follow up soon. Need help sooner? Call ",
      failed: "<strong>Sorry, your request didn't go through.</strong> Please try again, or call Hugo's at "
    },
    es: {
      noticing: 'Lo que estoy notando: ',
      stars: ' de 5 estrellas',
      via: 'en',
      locale: 'es-US',
      open: 'Abierto ahora · hasta las {close}',
      closed: 'Cerrado ahora · abre a las {open} ',
      today: 'hoy', tomorrow: 'mañana', monday: 'el lunes',
      err: {
        name: 'Por favor escribe tu nombre.',
        phone: 'Por favor escribe un número de teléfono con código de área.',
        email: 'Escribe un correo electrónico válido o déjalo en blanco.',
        vehicle_year: 'Escribe el año con 4 dígitos, por ejemplo 2014.',
        service: 'Elige el servicio que necesitas (o "No estoy seguro").',
        other: 'Por favor revisa este campo.'
      },
      sending: 'Enviando…',
      subject: 'Solicitud de servicio: ',
      success: '<strong>Gracias. Hugo\'s recibió tu solicitud.</strong> El taller se comunicará contigo pronto. ¿Lo necesitas antes? Llama al ',
      failed: '<strong>Lo sentimos, tu solicitud no se pudo enviar.</strong> Inténtalo de nuevo o llama a Hugo\'s al '
    }
  }[LANG];

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* ---------- header: scrolled state + mobile menu ---------- */
  var header = $('[data-header]');
  var toggle = $('[data-menu-toggle]');
  var nav = $('#site-nav');

  function onScroll() { header.classList.toggle('is-scrolled', window.scrollY > 8); }
  if (header) {
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  function setMenu(open) {
    header.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    document.documentElement.style.overflow = open ? 'hidden' : '';
    if (open) { var first = $('a', nav); if (first) first.focus(); }
  }
  if (toggle && nav) {
    toggle.addEventListener('click', function () { setMenu(toggle.getAttribute('aria-expanded') !== 'true'); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('is-open')) { setMenu(false); toggle.focus(); }
    });
    window.matchMedia('(min-width: 1240px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });
  }

  /* ---------- directions: open Apple Maps on Apple devices, Google Maps elsewhere ---------- */
  var isApple = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  if (isApple) {
    var appleUrl = 'https://maps.apple.com/?daddr=' + encodeURIComponent(ADDRESS) + '&dirflg=d';
    $$('[data-directions]').forEach(function (a) { a.href = appleUrl; });
  }

  /* ---------- scroll reveal ---------- */
  var revealTargets = $$('.reveal, .trust__item, .tire-reel__frame');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealTargets.forEach(function (el) { io.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- hero video (only when real footage is configured) ---------- */
  (function heroVideo() {
    var v = CONFIG.heroVideo || {};
    var media = $('[data-hero-media]');
    var conn = navigator.connection || {};
    if (!media || !(v.mp4 || v.webm) || reduceMotion.matches || conn.saveData) return;
    var video = document.createElement('video');
    video.className = 'hero__video';
    video.muted = true; video.loop = true; video.playsInline = true; video.autoplay = true;
    video.setAttribute('muted', ''); video.setAttribute('playsinline', ''); video.setAttribute('aria-hidden', 'true');
    video.preload = 'metadata';
    if (v.poster) video.poster = v.poster;
    if (v.webm) { var s1 = document.createElement('source'); s1.src = v.webm; s1.type = 'video/webm'; video.appendChild(s1); }
    if (v.mp4) { var s2 = document.createElement('source'); s2.src = v.mp4; s2.type = 'video/mp4'; video.appendChild(s2); }
    video.addEventListener('playing', function () { video.classList.add('is-ready'); }, { once: true });
    media.appendChild(video);
    var p = video.play(); if (p && p.catch) p.catch(function () { /* autoplay blocked: keep illustration */ });
  })();

  /* ---------- "What is your car doing?" ---------- */
  var problems = $('[data-problems]');
  var answer = $('[data-problem-answer]');
  var chosen = null;
  if (problems && answer) {
    problems.addEventListener('click', function (e) {
      var btn = e.target.closest('.problem');
      if (!btn) return;
      $$('.problem', problems).forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      chosen = btn;
      $('[data-problem-label]', answer).textContent = btn.getAttribute('data-problem');
      var wasHidden = answer.hidden;
      answer.hidden = false;
      if (wasHidden) {
        var rect = answer.getBoundingClientRect();
        if (rect.bottom > window.innerHeight - 80) {
          answer.scrollIntoView({ behavior: reduceMotion.matches ? 'auto' : 'smooth', block: 'center' });
        }
      }
    });
    var reqLink = $('[data-problem-request]', answer);
    if (reqLink) reqLink.addEventListener('click', function () {
      if (!chosen) return;
      var sel = $('#f-service'); var msg = $('#f-message');
      if (sel && !sel.value) sel.value = chosen.getAttribute('data-service') || 'Not Sure';
      if (msg && !msg.value) msg.value = T.noticing + chosen.getAttribute('data-problem') + '\n';
    });
  }

  /* ---------- alignment visual: straightens as it scrolls through view ---------- */
  var viz = $('[data-align-viz]');
  if (viz) {
    var manual = false;
    var ticking = false;
    var setP = function (p) {
      viz.style.setProperty('--p', p.toFixed(3));
      viz.classList.toggle('is-aligned', p > 0.92);
    };
    var update = function () {
      ticking = false;
      if (manual) return;
      var r = viz.getBoundingClientRect();
      var vh = window.innerHeight;
      // 0 when the figure's top enters at the bottom, 1 when its centre reaches ~45% of viewport
      var start = vh;
      var end = vh * 0.45 - r.height / 2;
      var p = (start - r.top) / (start - end);
      setP(Math.max(0, Math.min(1, p)));
    };
    var chips = $$('[data-align-set]', viz);
    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        manual = true;
        viz.classList.add('is-animating');
        chips.forEach(function (o) { o.setAttribute('aria-pressed', String(o === c)); });
        setP(Number(c.getAttribute('data-align-set')));
      });
    });
    if (reduceMotion.matches) {
      // no scroll-linked motion: show the aligned state; the buttons still switch views
      manual = true; viz.classList.add('is-animating'); setP(1);
      chips[1] && chips[1].setAttribute('aria-pressed', 'true');
    } else {
      window.addEventListener('scroll', function () {
        if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
      }, { passive: true });
      window.addEventListener('resize', update);
      update();
    }
  }

  /* ---------- reviews (genuine only; rendered from config) ---------- */
  var reviewsEl = $('[data-reviews]');
  var reviewsLink = $('[data-reviews-link]');
  if (reviewsLink && CONFIG.reviewsUrl) reviewsLink.href = CONFIG.reviewsUrl;
  if (reviewsEl && Array.isArray(CONFIG.reviews) && CONFIG.reviews.length) {
    reviewsEl.innerHTML = CONFIG.reviews.map(function (r) {
      var rating = Math.max(0, Math.min(5, Math.round(Number(r.rating) || 0)));
      var stars = '';
      for (var i = 1; i <= 5; i++) {
        stars += '<svg width="18" height="18" viewBox="0 0 24 24" class="' + (i > rating ? 'is-off' : '') + '"><use href="#i-star"/></svg>';
      }
      var src = r.url
        ? '<a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(r.source || 'Source') + '</a>'
        : esc(r.source || '');
      var date = r.date ? ' · <time datetime="' + esc(r.date) + '">' +
        esc(new Date(r.date + 'T12:00:00').toLocaleDateString(T.locale, { month: 'short', year: 'numeric' })) + '</time>' : '';
      return '<figure class="review">' +
        '<div class="review__stars" role="img" aria-label="' + rating + T.stars + '">' + stars + '</div>' +
        '<blockquote><p>' + esc(r.text) + '</p></blockquote>' +
        '<figcaption><strong>' + esc(r.name) + '</strong> · ' + T.via + ' ' + src + date + '</figcaption>' +
        '</figure>';
    }).join('');
  }

  /* ---------- open / closed status (Phoenix time: MST, no DST) ---------- */
  var statusEl = $('[data-open-status]');
  if (statusEl && window.Intl) {
    try {
      var parts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/Phoenix', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false
      }).formatToParts(new Date());
      var get = function (t) { return (parts.find(function (p) { return p.type === t; }) || {}).value; };
      var day = get('weekday');
      var mins = (Number(get('hour')) % 24) * 60 + Number(get('minute'));
      // hours come from the page (set once in tools/build.py)
      var toMins = function (hhmm) { var p = String(hhmm).split(':'); return Number(p[0]) * 60 + Number(p[1] || 0); };
      var opens = toMins(statusEl.getAttribute('data-open') || '08:00');
      var closes = toMins(statusEl.getAttribute('data-close') || '18:00');
      var fill = function (str) {
        return str.replace('{open}', statusEl.getAttribute('data-open-label') || '')
                  .replace('{close}', statusEl.getAttribute('data-close-label') || '');
      };
      var isWorkday = day !== 'Sun';
      var open = isWorkday && mins >= opens && mins < closes;
      if (open) {
        statusEl.textContent = fill(T.open);
        statusEl.classList.add('is-open');
      } else {
        var next = (isWorkday && mins < opens) ? T.today : (day === 'Sat' || day === 'Sun' ? T.monday : T.tomorrow);
        statusEl.textContent = fill(T.closed) + next;
      }
    } catch (e) { /* leave blank */ }
  }

  /* ---------- service request form ---------- */
  var form = $('[data-request-form]');
  var offline = $('[data-request-offline]');
  if (form && !(CONFIG.formEndpoint || '').trim()) {
    // Form not connected yet: show the call / visit panel instead of a form that can't send.
    form.hidden = true;
    if (offline) offline.hidden = false;
    $$('[data-problem-request]').forEach(function (a) { a.hidden = true; });
    form = null;
  }
  if (form) {
    var statusBox = $('[data-form-status]', form);
    var submit = $('button[type="submit"]', form);
    var messages = T.err;

    var showStatus = function (kind, html) {
      statusBox.hidden = false;
      statusBox.className = 'form-status form-status--' + kind;
      statusBox.innerHTML = html;
    };
    var clearError = function (field) {
      field.removeAttribute('aria-invalid');
      var id = field.id + '-error';
      var err = document.getElementById(id);
      if (err) err.remove();
      var desc = (field.getAttribute('aria-describedby') || '').split(' ').filter(function (x) { return x && x !== id; });
      if (desc.length) field.setAttribute('aria-describedby', desc.join(' ')); else field.removeAttribute('aria-describedby');
    };
    var setError = function (field) {
      clearError(field);
      var id = field.id + '-error';
      var p = document.createElement('p');
      p.className = 'field__error'; p.id = id;
      p.textContent = messages[field.name] || messages.other;
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', ((field.getAttribute('aria-describedby') || '') + ' ' + id).trim());
      field.parentNode.appendChild(p);
    };

    $$('input, select, textarea', form).forEach(function (f) {
      f.addEventListener('input', function () { if (f.getAttribute('aria-invalid') && f.checkValidity()) clearError(f); });
      f.addEventListener('change', function () { if (f.getAttribute('aria-invalid') && f.checkValidity()) clearError(f); });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      statusBox.hidden = true;

      var invalid = $$('input, select, textarea', form).filter(function (f) {
        if (f.name === '_gotcha') return false;
        var ok = f.checkValidity();
        if (ok && f.name === 'phone') ok = f.value.replace(/\D/g, '').length >= 10;
        if (ok) clearError(f); else setError(f);
        return !ok;
      });
      if (invalid.length) { invalid[0].focus(); return; }

      // bots fill the hidden field; quietly drop the submission
      if ($('#f-company').value) return;

      var endpoint = CONFIG.formEndpoint.trim();

      submit.disabled = true;
      var label = submit.textContent;
      submit.textContent = T.sending;
      var data = new FormData(form);
      data.append('_subject', T.subject + (data.get('service') || 'Website'));

      fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          form.reset();
          $$('[aria-invalid]', form).forEach(clearError);
          showStatus('success', '<p>' + T.success + '<a href="' + TEL + '">' + PHONE + '</a>.</p>');
        })
        .catch(function () {
          showStatus('error', '<p>' + T.failed + '<a href="' + TEL + '">' + PHONE + '</a>.</p>');
        })
        .then(function () {
          submit.disabled = false;
          submit.textContent = label;
          statusBox.focus && statusBox.setAttribute('tabindex', '-1');
          statusBox.focus();
        });
    });
  }

  /* ---------- small things ---------- */
  $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  // Optional analytics hook: pushes CTA clicks to a dataLayer if one is installed.
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="tel:"], [data-directions]');
    if (!a || !window.dataLayer) return;
    window.dataLayer.push({
      event: a.hasAttribute('data-directions') ? 'directions_click' : 'call_click',
      cta_location: a.getAttribute('data-cta') || 'directions'
    });
  });
})();
