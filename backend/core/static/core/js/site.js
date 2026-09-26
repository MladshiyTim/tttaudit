/* Sayt JS: menyu, «Maxsus imkoniyatlar» rejimi, skan koʻrgich, hero slayd-shousi, loyihalar xaritasi. Vidjetlar alohida (widgets.js). */
(function () {
  "use strict";
  var root = document.documentElement;

  // --- Maxsus imkoniyatlar: katta shrift + kulrang rejim, localStorage'da saqlanadi
  var A11Y_KEY = "ttt-a11y";
  function applyA11y(on) {
    root.setAttribute("data-a11y", on ? "on" : "off");
    document.querySelectorAll("[data-a11y-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }
  var saved = false;
  try { saved = localStorage.getItem(A11Y_KEY) === "on"; } catch (e) { saved = false; }
  applyA11y(saved);
  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-a11y-toggle]");
    if (!btn) return;
    var on = root.getAttribute("data-a11y") !== "on";
    applyA11y(on);
    try { localStorage.setItem(A11Y_KEY, on ? "on" : "off"); } catch (e) { /* xususiy rejim */ }
  });

  // --- Mobil menyu
  document.addEventListener("click", function (event) {
    var toggle = event.target.closest("[data-nav-toggle]");
    if (!toggle) return;
    var nav = document.getElementById(toggle.getAttribute("aria-controls"));
    if (!nav) return;
    var open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  // --- Skan koʻrgich: <a data-lightbox data-alt="..." href="scan.png">
  var box = document.getElementById("lightbox");
  if (box && typeof box.showModal === "function") {
    var img = box.querySelector("img");
    document.addEventListener("click", function (event) {
      var link = event.target.closest("[data-lightbox]");
      if (link) {
        event.preventDefault();
        img.src = link.getAttribute("href");
        img.alt = link.getAttribute("data-alt") || "";
        box.showModal();
      } else if (event.target === box || event.target.closest("[data-lightbox-close]")) {
        box.close();
      }
    });
  }

  // --- Hero slayd-shou: JS'siz faqat birinchi slayd. Avto-almashish 6 s, hover/fokusda pauza,
  //     «kamroq harakat» rejimida avto-almashish yoʻq. aria-live faqat qoʻlda almashtirilganda.
  var SLIDE_DELAY = 6000;
  document.querySelectorAll("[data-slides]").forEach(function (box) {
    var slides = Array.prototype.slice.call(box.querySelectorAll("[data-slide]"));
    var nav = box.querySelector("[data-slides-nav]");
    var counter = box.querySelector("[data-slides-index]");
    var live = box.querySelector("[data-slides-live]");
    if (slides.length < 2 || !nav || !counter) return;
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
    var current = 0, timer = null, hovered = false, focused = false;

    function show(index, announce) {
      current = (index + slides.length) % slides.length;
      slides.forEach(function (slide, i) { slide.classList.toggle("is-active", i === current); });
      counter.textContent = (current < 9 ? "0" : "") + (current + 1);
      if (announce && live) {
        var cap = slides[current].querySelector("figcaption");
        var parts = cap ? Array.prototype.map.call(cap.children, function (el) { return el.textContent; }) : [];
        live.textContent = counter.textContent + " / " + (slides.length < 10 ? "0" : "") + slides.length + ". " + parts.join(" · ");
      }
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function start() {
      stop();
      if (reduce.matches || hovered || focused) return;
      timer = setInterval(function () { show(current + 1, false); }, SLIDE_DELAY);
    }
    function step(delta) { show(current + delta, true); }

    nav.hidden = false;
    box.classList.add("is-ready");
    box.querySelector("[data-slides-prev]").addEventListener("click", function () { step(-1); });
    box.querySelector("[data-slides-next]").addEventListener("click", function () { step(1); });
    box.addEventListener("keydown", function (event) {
      var delta = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
      if (!delta) return;
      event.preventDefault();
      step(delta);
    });
    box.addEventListener("mouseenter", function () { hovered = true; stop(); });
    box.addEventListener("mouseleave", function () { hovered = false; start(); });
    box.addEventListener("focusin", function () { focused = true; stop(); });
    box.addEventListener("focusout", function (event) {
      if (box.contains(event.relatedTarget)) return;
      focused = false;
      start();
    });
    if (reduce.addEventListener) reduce.addEventListener("change", start);
    start();
  });

  // --- Yoʻnalish tablari: JS'siz ikkala panel ketma-ket koʻrinadi
  document.querySelectorAll("[data-tabs]").forEach(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll("[data-tab]"));
    var list = box.querySelector("[data-tablist]");
    if (!tabs.length || !list) return;
    list.setAttribute("role", "tablist");
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        var panel = document.getElementById(t.getAttribute("data-tab"));
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.setAttribute("tabindex", on ? "0" : "-1");
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (tab, index) {
      var panel = document.getElementById(tab.getAttribute("data-tab"));
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", tab.getAttribute("data-tab"));
      if (panel) { panel.setAttribute("role", "tabpanel"); panel.setAttribute("aria-labelledby", tab.id); }
      tab.addEventListener("click", function (event) { event.preventDefault(); select(tab, false); });
      tab.addEventListener("keydown", function (event) {
        var step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (!step) return;
        event.preventDefault();
        select(tabs[(index + step + tabs.length) % tabs.length], true);
      });
    });
    select(tabs[0], false);
  });

  // --- Hujjat koʻrgich: roʻyxatdan tanlangan hujjat oʻng tomonda
  document.querySelectorAll("[data-docs]").forEach(function (box) {
    var links = Array.prototype.slice.call(box.querySelectorAll("[data-doc-tab]"));
    var panels = Array.prototype.slice.call(box.querySelectorAll("[data-doc-panel]"));
    if (!links.length || !panels.length) return;
    function show(id, scroll) {
      var found = false;
      panels.forEach(function (panel) { var on = panel.id === id; panel.hidden = !on; found = found || on; });
      if (!found) return false;
      links.forEach(function (link) {
        if (link.getAttribute("data-doc-tab") === id) link.setAttribute("aria-current", "true");
        else link.removeAttribute("aria-current");
      });
      if (scroll && window.matchMedia("(max-width: 900px)").matches) {
        box.querySelector(".docs__view").scrollIntoView({ block: "start" });
      }
      return true;
    }
    links.forEach(function (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        show(link.getAttribute("data-doc-tab"), true);
      });
    });
    var hash = window.location.hash.replace("#", "");
    if (!(hash && show(hash, false))) show(links[0].getAttribute("data-doc-tab"), false);
  });

  // --- Taqqoslash vedomosti: «Haqiqatda» ustuni tahrirlanadi, farq va jami qayta hisoblanadi
  document.querySelectorAll("[data-sheet]").forEach(function (sheet) {
    var lang = (root.getAttribute("lang") || "uz").slice(0, 2);
    var decimal = lang === "en" ? "." : ",";
    function fmt(value, signed) {
      var abs = Math.abs(value);
      var text = (Math.round(abs * 10) % 10 ? abs.toFixed(1) : abs.toFixed(0)).split(".");
      text[0] = text[0].replace(/\B(?=(\d{3})+(?!\d))/g, "\u00a0");
      var out = text.join(decimal);
      if (value < 0) return "\u2212" + out;
      return signed && value > 0 ? "+" + out : out;
    }
    var rows = Array.prototype.slice.call(sheet.querySelectorAll("[data-row]"));
    rows.forEach(function (row, index) {
      var cell = row.querySelector("[data-fact]");
      var input = document.createElement("input");
      input.value = fmt(parseFloat(cell.getAttribute("data-fact")), false);
      input.inputMode = "decimal";
      input.id = "sheet-fact-" + index;
      input.setAttribute("aria-label", cell.getAttribute("data-label"));
      cell.textContent = "";
      cell.appendChild(input);
    });
    function calc() {
      var total = 0;
      rows.forEach(function (row) {
        var doc = parseFloat(row.getAttribute("data-doc"));
        var price = parseFloat(row.getAttribute("data-price"));
        var raw = row.querySelector("input").value.replace(/[\s\u00a0]/g, "").replace(",", ".");
        var fact = parseFloat(raw);
        if (!isFinite(fact)) fact = doc;
        var diff = Math.round((fact - doc) * 1000) / 1000;
        var sum = Math.round(diff * price);
        var dCell = row.querySelector("[data-diff]");
        var sCell = row.querySelector("[data-diff-sum]");
        dCell.textContent = fmt(diff, true);
        sCell.textContent = fmt(sum, true);
        dCell.classList.toggle("neg", diff < 0);
        sCell.classList.toggle("neg", sum < 0);
        if (sum < 0) total -= sum;
      });
      sheet.querySelector("[data-sheet-total]").textContent = fmt(total, false);
    }
    sheet.addEventListener("input", calc);
  });

  // --- Loyihalar xaritasi: tooltip (hover/fokus), bosish/Enter — tanlov paneli, Esc — tozalash.
  //     Yoʻnalish tugmalari (data-live="1") sahifani qayta yuklamasdan filtrlaydi. JS'siz havolalar reestrga olib boradi.
  document.querySelectorAll("[data-uzmap]").forEach(function (box) {
    var source = box.querySelector("script[type='application/json']");
    var panel = box.querySelector("[data-uzmap-panel]");
    var tip = box.querySelector("[data-uzmap-tip]");
    var mapBox = box.querySelector(".geo__map");
    if (!source || !panel || !tip || !mapBox) return;
    var data = JSON.parse(source.textContent);
    var dept = data.dept || "";
    var selected = null;
    var regionLinks = Array.prototype.slice.call(box.querySelectorAll("[data-region]"));
    var markerLinks = Array.prototype.slice.call(box.querySelectorAll("[data-marker]"));
    var hint = panel.querySelector(".geo__hint");
    if (hint) hint.hidden = false;
    var initialPanel = panel.innerHTML;

    function visible(ids) {
      return ids.filter(function (id) { return !dept || data.projects[id].d === dept; });
    }
    function level(n) {
      return data.steps.filter(function (step) { return n >= step; }).length;
    }
    function countText(n) { return panel.getAttribute("data-t-count").replace("__N__", n); }
    function el(tag, cls, text) {
      var node = document.createElement(tag);
      if (cls) node.className = cls;
      if (text !== undefined) node.textContent = text;
      return node;
    }
    function regionUrl(key) { return data.registry + "?" + data.param + "=" + key + "#xarita"; }
    function idsOf(link) {
      return link.hasAttribute("data-marker")
        ? data.markers[link.getAttribute("data-marker")].ids
        : data.regions[link.getAttribute("data-region")].ids;
    }
    function nameOf(link) {
      return link.hasAttribute("data-marker")
        ? data.markers[link.getAttribute("data-marker")].name
        : data.regions[link.getAttribute("data-region")].name;
    }

    function renderTop() {
      panel.innerHTML = initialPanel;
      var list = panel.querySelector(".geo__top");
      if (!list) return;
      list.textContent = "";
      Object.keys(data.regions)
        .map(function (key) { return { key: key, name: data.regions[key].name, n: visible(data.regions[key].ids).length }; })
        .filter(function (r) { return r.n > 0; })
        .sort(function (a, b) { return b.n - a.n; })
        .slice(0, data.top)
        .forEach(function (r) {
          var a = el("a");
          a.href = regionUrl(r.key);
          a.appendChild(el("span", "", r.name));
          a.appendChild(el("b", "num", String(r.n)));
          var li = el("li");
          li.appendChild(a);
          list.appendChild(li);
        });
    }

    function renderPick() {
      var isRegion = selected.kind === "region";
      var entry = isRegion ? data.regions[selected.key] : data.markers[selected.key];
      if (!entry) { selected = null; renderTop(); return; }
      var ids = visible(entry.ids);
      panel.textContent = "";
      var head = el("p", "geo__pick-h");
      head.appendChild(el("b", "", entry.name));
      head.appendChild(el("span", "", countText(ids.length)));
      panel.appendChild(head);
      var list = el("ul", "geo__list");
      ids.forEach(function (id) {
        var p = data.projects[id];
        var li = el("li");
        li.appendChild(el("b", "", p.t));
        li.appendChild(el("span", "", [p.c, p.y, data.labels[p.d]].filter(Boolean).join(" · ")));
        list.appendChild(li);
      });
      panel.appendChild(list);
      var acts = el("div", "geo__acts");
      var more = el("a", "more", panel.getAttribute("data-t-view") + " →");
      more.href = regionUrl(isRegion ? selected.key : entry.region);
      acts.appendChild(more);
      var clear = el("button", "geo__clear", panel.getAttribute("data-t-clear"));
      clear.type = "button";
      clear.addEventListener("click", function () { select(null); });
      acts.appendChild(clear);
      panel.appendChild(acts);
    }

    function isSelected(kind, key) {
      return !!selected && selected.kind === kind && selected.key === key;
    }

    function refresh() {
      var cities = 0, regions = 0, onMap = {};
      regionLinks.forEach(function (link) {
        var key = link.getAttribute("data-region");
        var ids = visible(idsOf(link));
        ids.forEach(function (id) { onMap[id] = true; });
        if (ids.length) regions += 1;
        link.setAttribute("data-level", level(ids.length));
        link.setAttribute("aria-label", nameOf(link) + ": " + ids.length);
        if (ids.length) link.removeAttribute("tabindex"); else link.setAttribute("tabindex", "-1");
        link.classList.toggle("is-sel", isSelected("region", key));
      });
      markerLinks.forEach(function (link) {
        var key = link.getAttribute("data-marker");
        var n = visible(idsOf(link)).length;
        if (n) cities += data.markers[key].name.split(", ").length;
        link.classList.toggle("is-off", n === 0);
        link.classList.toggle("is-sel", isSelected("marker", key));
        link.setAttribute("aria-label", nameOf(link) + ": " + n);
        var label = box.querySelector('[data-label="' + key + '"]');
        if (label) label.classList.toggle("is-off", n === 0);
        var count = link.querySelector(".geo__n") || (label && label.querySelector(".geo__lc"));
        if (count) {
          count.textContent = n;
          count.classList.toggle("is-off", n < 2);
        }
      });
      var total = Object.keys(onMap).length;
      var stats = { projects: total, regions: regions, cities: cities, off: data.scope[dept] - total };
      Object.keys(stats).forEach(function (name) {
        var node = box.querySelector('[data-stat="' + name + '"]');
        if (node) node.textContent = stats[name];
      });
      box.querySelectorAll("[data-dept]").forEach(function (tab) {
        if (tab.getAttribute("data-dept") === dept) tab.setAttribute("aria-current", "true");
        else tab.removeAttribute("aria-current");
      });
      if (selected) renderPick(); else renderTop();
    }

    function select(next) {
      var same = next && selected && next.kind === selected.kind && next.key === selected.key;
      selected = same ? null : next;
      refresh();
    }

    function showTip(link) {
      var shape = link.querySelector(link.hasAttribute("data-marker") ? ".geo__dot" : "path");
      var rect = shape.getBoundingClientRect();
      var host = mapBox.getBoundingClientRect();
      tip.textContent = nameOf(link) + " — " + countText(visible(idsOf(link)).length);
      tip.hidden = false;
      // Tooltip markazda turadi (translate -50%), lekin xarita chetidan chiqmasin
      var half = tip.offsetWidth / 2;
      var x = Math.min(Math.max(rect.left + rect.width / 2 - host.left, half), host.width - half);
      tip.style.left = x + "px";
      tip.style.top = (rect.top - host.top) + "px";
    }
    function hideTip() { tip.hidden = true; }

    regionLinks.concat(markerLinks).forEach(function (link) {
      var kind = link.hasAttribute("data-marker") ? "marker" : "region";
      var key = link.getAttribute(kind === "marker" ? "data-marker" : "data-region");
      link.addEventListener("click", function (event) {
        event.preventDefault();
        hideTip();
        select({ kind: kind, key: key });
      });
      link.addEventListener("mouseenter", function () { showTip(link); });
      link.addEventListener("mouseleave", hideTip);
      link.addEventListener("focus", function () { showTip(link); });
      link.addEventListener("blur", hideTip);
    });
    box.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      hideTip();
      if (selected) select(null);
    });
    if (data.live) {
      box.querySelectorAll("[data-dept]").forEach(function (tab) {
        tab.addEventListener("click", function (event) {
          event.preventDefault();
          dept = tab.getAttribute("data-dept");
          if (window.history && history.replaceState) history.replaceState(null, "", tab.getAttribute("href"));
          refresh();
        });
      });
    }
    if (data.region && data.regions[data.region]) selected = { kind: "region", key: data.region };
    refresh();
  });
})();
